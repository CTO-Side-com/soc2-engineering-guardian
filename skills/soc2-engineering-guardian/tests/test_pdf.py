"""Offline tests for the designed PDF report."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from init_assessment import create
from pdf_report import render_pdf
from pdf_writer import encode
from validate_assessment import validate


def evidence(kind='operational', start='2026-08-01', end='2026-10-31', eid='E1'):
    return {'id': eid, 'type': kind, 'ref': 'controlled-records/review.json', 'method': 'Reviewed synthetic records',
            'reviewer': 'Synthetic Reviewer', 'environment': 'production', 'collected_on': '2026-11-01',
            'period': {'start': start, 'end': end}}


def check(doc, cid):
    return next(c for c in doc['controls'] if c['id'] == cid)


def gap(doc, cid, dimension, status, severity, rationale, evidence_ids):
    c = check(doc, cid)
    c.update({dimension + '_status': status, dimension + '_evidence': list(evidence_ids), 'rationale': rationale,
              'reviewer': 'Synthetic Reviewer', 'owner': 'Synthetic Owner', 'severity': severity,
              'recommendation': 'Repair ' + cid, 'verification_test': 'Retest ' + cid, 'due_date': '2026-12-01'})
    return c


def synthetic(mode='type2-readiness'):
    doc = create('Synthetic SaaS', 'production', '2026-08-01', '2026-10-31', mode)
    doc['assessor'] = 'Synthetic Assessor'
    doc['in_scope_systems'] = ['api', 'web']
    doc['evidence'] = [evidence('code', eid='E1'), evidence('operational', '2026-09-01', '2026-10-31', 'E2')]
    gap(doc, 'CHG-001', 'design', 'failed', 'critical', 'Release path skips review; contact jane.doe@example.com', ['E1'])
    c = gap(doc, 'IAM-001', 'operation', 'partially_verified', 'high', 'Access reviews exist for September and October only', ['E2'])
    c['population'].update(source='Synthetic review log', total=18, reviewed=18, exceptions=2,
                           selection_method='All items', completeness_method='Log reconciled', reviewer='Synthetic Reviewer')
    v = check(doc, 'GOV-001')
    v.update(design_status='verified', design_evidence=['E1'], rationale='Owners assigned', reviewer='Synthetic Reviewer')
    na = check(doc, 'AI-001')
    na.update(design_status='not_applicable', rationale='No AI features in scope', reviewer='Synthetic Reviewer', approved_by='Synthetic Approver')
    return doc


def streams(pdf):
    return [zlib.decompress(m.group(1)) for m in re.finditer(rb'stream\n(.*?)\nendstream', pdf, re.S)]


PAGE_W, PAGE_H = 612.0, 792.0
BODY_FLOOR = 58.0  # pdf_report.BOTTOM measured from the page bottom; the footer sits below it


def body_text_ops(stream):
    """(x, y, text) for each text run except the footer's, whose baseline is below the body floor by design."""
    ops = re.findall(rb'(-?[\d.]+) (-?[\d.]+) Td \((.*?)\) Tj ET', stream)
    return [(float(x), float(y), t) for x, y, t in ops
            if not (t.startswith(b'SOC 2 Engineering Guardian') and b'auditor opinion' in t)
            and not re.fullmatch(rb'Page \d+ of \d+', t)]


def five_gaps(long_rationale=True):
    doc = synthetic()
    doc['evidence'] += [evidence('code', eid='E3')]
    for cid in ('CHG-002', 'IAM-002', 'MON-001'):
        gap(doc, cid, 'design', 'failed', 'high', ('Long finding text. ' * 40) if long_rationale else 'Short', ['E3'])
    return doc


def text_of(doc):
    return b'\n'.join(streams(render_pdf(doc)))


class PdfReportTests(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual([], validate(synthetic()))

    def test_xref_table_points_at_every_object(self):
        data = render_pdf(synthetic())
        self.assertTrue(data.startswith(b'%PDF-1.4'))
        self.assertTrue(data.rstrip().endswith(b'%%EOF'))
        startxref = int(re.search(rb'startxref\s+(\d+)\s+%%EOF', data).group(1))
        self.assertEqual(data[startxref:startxref + 4], b'xref')
        header = re.match(rb'xref\n0 (\d+)\n', data[startxref:])
        entries = data[startxref + header.end():].split(b'\n')[:int(header.group(1))]
        self.assertEqual(entries[0].strip(), b'0000000000 65535 f')
        for number, entry in enumerate(entries[1:], 1):
            self.assertTrue(data[int(entry[:10]):].startswith(f'{number} 0 obj'.encode()), f'object {number} offset is wrong')

    def test_page_count_matches_page_tree(self):
        data = render_pdf(synthetic())
        pages = len(re.findall(rb'/Type /Page\b(?!s)', data))
        declared = int(re.search(rb'/Type /Pages /Kids \[[^\]]*\] /Count (\d+)', data).group(1))
        self.assertEqual(pages, declared)
        self.assertGreaterEqual(pages, 7)

    def test_every_page_carries_the_notice(self):
        found = streams(render_pdf(synthetic()))
        self.assertTrue(found)
        for stream in found:
            self.assertIn(b'not a SOC 2 report or auditor opinion', stream)

    def test_pdf_redacts_and_keeps_findings(self):
        text = text_of(synthetic())
        self.assertNotIn(b'jane.doe', text)
        self.assertIn(b'[REDACTED_EMAIL]', text)
        self.assertIn(b'Access reviews exist for September and October only', text)

    def test_non_latin_and_surrogates_do_not_crash(self):
        doc = synthetic()
        doc['product'] = 'Cloud کلینیک \U0001F9B7 \ud800 (\\) test'
        data = render_pdf(doc)
        self.assertTrue(data.startswith(b'%PDF'))
        self.assertIn(b'\\(\\\\\\) test', b'\n'.join(streams(data)))

    def test_delete_character_is_not_drawn(self):
        self.assertEqual(encode('a\x7fb'), b'a b')
        doc = synthetic()
        doc['product'] = 'Del\x7fCloud'
        self.assertNotIn(b'\\177', text_of(doc))

    def test_wrap_is_linear_and_terminates(self):
        script = (
            'import sys, time; sys.path.insert(0, sys.argv[1]); from pdf_writer import wrap\n'
            'start = time.time(); lines = wrap("a" * 20000, 9, 300)\n'
            'assert "".join(lines) == "a" * 20000\n'
            'assert time.time() - start < 1.5, time.time() - start\n'
            'for width in (0, -1): wrap("abc def", 9, width)\n'
        )
        try:
            result = subprocess.run([sys.executable, '-c', script, str(SCRIPTS)], capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            self.fail('wrap() did not terminate')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_long_text_stays_on_page(self):
        doc = synthetic()
        doc['in_scope_systems'] = [f'Service number {i} with a fairly long descriptive name' for i in range(200)]
        doc['evidence'] += [evidence('code', eid=f'X{i}') for i in range(60)]
        gap(doc, 'CHG-002', 'design', 'failed', 'high', 'Long finding text. ' * 160, [f'X{i}' for i in range(60)])
        self.assertEqual([], validate(doc))
        for stream in streams(render_pdf(doc)):
            for x, y, _ in body_text_ops(stream):
                self.assertGreaterEqual(y, BODY_FLOOR, 'body text drawn into the footer zone or off the page')
                self.assertLessEqual(y, PAGE_H, 'text drawn above the page')
                self.assertTrue(0 <= x <= PAGE_W, f'text starts off the page at x={x}')

    def test_header_on_every_page_after_cover(self):
        found = streams(render_pdf(synthetic()))
        self.assertNotIn(b'CONFIDENTIAL', found[0])
        for number, stream in enumerate(found[1:], 2):
            self.assertIn(b'CONFIDENTIAL', stream, f'page {number} has no running header')

    def test_page_numbers_count_every_page(self):
        found = streams(render_pdf(synthetic()))
        total = len(found)
        self.assertGreaterEqual(total, 7)
        joined = b'\n'.join(found)
        for n in range(1, total + 1):
            self.assertEqual(1, joined.count(f'(Page {n} of {total})'.encode()), f'Page {n} of {total}')
        self.assertNotIn(f'Page {total + 1} of'.encode(), joined)

    def test_oversized_cell_is_cut_with_pointer(self):
        doc = synthetic()
        doc['in_scope_systems'] = [f'system {i} ' + 'word ' * 38 for i in range(150)]  # ~30,000 characters in one cell
        gap(doc, 'CHG-002', 'design', 'failed', 'high', 'word ' * 4000, ['E1'])
        self.assertEqual([], validate(doc))
        found = streams(render_pdf(doc))
        self.assertIn(b'continues in assessment.json', b'\n'.join(found))
        for stream in found:
            for x, y, _ in body_text_ops(stream):
                self.assertTrue(BODY_FLOOR <= y <= PAGE_H and 0 <= x <= PAGE_W, f'text off the page at {x},{y}')

    def test_exec_summary_fits_one_page_with_five_gaps(self):
        doc = five_gaps()
        self.assertEqual([], validate(doc))
        found = streams(render_pdf(doc))
        page2, page3 = found[1], found[2]
        keys = ('CHG-001-design', 'IAM-001-operation', 'CHG-002-design', 'IAM-002-design', 'MON-001-design')
        self.assertIn(b'Top priorities', page2)
        for key in keys:
            self.assertIn(key.encode(), page2, f'{key} missing from the executive summary page')
            self.assertNotIn(key.encode(), page3, f'{key} spilled onto page 3')

    def test_evidence_index_does_not_split_words(self):
        doc = json.loads(json.dumps(synthetic()).replace('"E2"', '"EX-CHANGES"'))
        doc['environment'] = 'synthetic-production'
        for e in doc['evidence']:
            e['environment'] = 'synthetic-production'
        doc['evidence'][0]['ref'] = 'synthetic/change-review-register.json'
        self.assertEqual([], validate(doc))
        runs = {t for stream in streams(render_pdf(doc)) for _, _, t in body_text_ops(stream)}
        for whole in (b'synthetic-production', b'controlled-records/review.json', b'synthetic/change-review-register.json',
                      b'operational', b'EX-CHANGES', b'2026-09-01 to', b'Synthetic', b'Reviewer'):
            self.assertIn(whole, runs, f'{whole!r} was split across lines')

    def test_example_evidence_index_keeps_values_whole(self):
        example = json.loads((SCRIPTS.parent / 'assets' / 'assessment-example.json').read_text(encoding='utf-8'))
        self.assertEqual([], validate(example))
        page = next(s for s in streams(render_pdf(example)) if b'Appendix B: evidence index' in s)
        runs = {t for _, _, t in body_text_ops(page)}
        for e in example['evidence']:
            for key in ('id', 'type', 'ref', 'environment'):
                self.assertIn(e[key].encode(), runs, f'{e["id"]} {key} {e[key]!r} was split across lines')

    def test_type2_has_period_coverage_section(self):
        text = text_of(synthetic())
        self.assertIn(b'Period coverage', text)
        self.assertIn(b'2026-08-01', text)

    def test_type1_has_no_period_section(self):
        doc = synthetic('type1-readiness')
        self.assertEqual([], validate(doc))
        text = text_of(doc)
        self.assertNotIn(b'Period coverage', text)
        self.assertIn(b'Not assessed', text)

    def test_no_open_items_renders(self):
        doc = create('Synthetic SaaS', 'production', '2026-08-01', '2026-10-31', 'type1-readiness')
        doc['evidence'] = [evidence('code')]
        for c in doc['controls']:
            c.update(design_status='verified', design_evidence=['E1'], rationale='Synthetic design reviewed', reviewer='Synthetic Reviewer')
        self.assertEqual([], validate(doc))
        self.assertIn(b'No open items are recorded.', text_of(doc))

    def test_render_cli_writes_pdf_and_markdown(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / 'a.json').write_text(json.dumps(synthetic()), encoding='utf-8')
            subprocess.run([sys.executable, str(SCRIPTS / 'render_report.py'), '--assessment', str(base / 'a.json'),
                            '--out', str(base / 'out'), '--pdf'], check=True, capture_output=True, text=True, cwd=root)
            self.assertTrue((base / 'out' / 'SOC2-READINESS.md').exists())
            self.assertTrue((base / 'out' / 'SOC2-READINESS.pdf').read_bytes().startswith(b'%PDF-1.4'))
            manifest = json.loads((base / 'out' / 'handoff-manifest.json').read_text(encoding='utf-8'))
            self.assertIn('SOC2-READINESS.pdf', [f['path'] for f in manifest['files']])


if __name__ == '__main__':
    unittest.main()
