"""Designed internal SOC 2 readiness report as PDF. Offline, stdlib-only, and never a SOC 2 report."""
import re
from common import BASE, clean, today
from pdf_writer import PDF, PAGE_H, PAGE_W, text_width, wrap
from render_report import ORDER, summarize

M = 54                    # side margin
CW = PAGE_W - 2 * M       # content width
TOP = 72                  # first baseline under the running header
BOTTOM = PAGE_H - 58      # lowest usable point above the footer

NAVY = '#101827'          # cover band, heading bars, link text
CYAN = '#39B9D0'          # thin rules only: too light for text
INK = '#0b0b0b'
INK_2 = '#52514e'
MUTED = '#8a8984'
HAIRLINE = '#e1e0d9'
AXIS = '#c3c2b7'
PANEL = '#f4f3ef'
WHITE = '#ffffff'
PRODUCT = 'SOC 2 Engineering Guardian'
NOTICE = 'Internal readiness assessment – not a SOC 2 report or auditor opinion'

# Status hues are reserved for state and always ship with a text label, never color alone.
STATUS = {
    'verified': ('Verified', 'Verified', '#0ca30c', WHITE),
    'partially_verified': ('Partially verified', 'Partial', '#fab219', INK),
    'failed': ('Failed', 'Failed', '#d03b3b', WHITE),
    'not_applicable': ('Not applicable', 'N/A', '#e1e0d9', INK),
    'insufficient_evidence': ('Insufficient evidence', 'Unverified', '#a8a79f', INK),
}
STATUS_ORDER = ['verified', 'partially_verified', 'failed', 'not_applicable', 'insufficient_evidence']
STATUS_MEANING = {
    'verified': ('A reviewer asserts the control is designed to meet the scoped need, with evidence cited.',
                 'A reviewer asserts it operated across the whole period, with a complete population and sampled exceptions.'),
    'partially_verified': ('The design exists but is incomplete; the gap is cited.',
                           'Operation is evidenced for part of the period or population; the uncovered part is cited.'),
    'failed': ('Specific evidence shows the design is missing or inadequate.',
               'Specific evidence shows the control did not operate as designed.'),
    'not_applicable': ('Outside scope, with a rationale and a named human approver.',
                       'Outside scope, with a rationale and a named human approver.'),
    'insufficient_evidence': ('Untested or unsupported. The artifact needed is listed under Evidence requests.',
                              'No period evidence or population recorded. The records needed are listed under Evidence requests.'),
}
SEVERITY = {
    'critical': ('Critical', '#d03b3b', WHITE),
    'high': ('High', '#ec835a', INK),
    'medium': ('Medium', '#fab219', INK),
    'low': ('Low', '#e1e0d9', INK),
}
BOUNDARIES = [
    'Repository inspection cannot establish staff practices, historical enforcement, provider settings or complete '
    'operational populations; current branch rules cannot prove earlier enforcement.',
    'Verified means reviewer-asserted support for the stated scope. Automated validation cannot prove that evidence is true.',
    'Recovery checks support risk mitigation, not an assessment of the Availability category. Only Security is in scope.',
    'Criteria mappings reference the 2017 Trust Services Criteria with 2022 points of focus, are interpretive and need '
    'engagement-specific review. Official criteria text is not reproduced.',
    'Only an independent CPA firm can issue a SOC 2 report, after its own examination.',
]
LIMITS = [
    'Scanner results are leads, never confirmed findings, and their absence proves nothing.',
    'Organizational controls need signed policy, contract or operating evidence confirmed by a human reviewer.',
    'Design evidence cannot show operation; operation needs records across the assessment period.',
    'PDF text uses built-in Western fonts; characters outside them print as ?. Use the Markdown report for full Unicode content.',
]
MODES = {'type1-readiness': 'Type 1 readiness', 'type2-readiness': 'Type 2 readiness'}
NOT_ASSESSED = 'Not assessed (Type 1 readiness)'


def _c(value, limit=3000):
    return clean('' if value is None else value, limit)


def _join(values):
    return '; '.join(_c(v, 200) for v in values) or 'None recorded'


def _span(pairs):
    return '\n'.join(f'{a} to {b}' for a, b in pairs) or 'None'


def _sources():
    """(label, url) rows and the review date from the source register shipped with the skill."""
    text = (BASE / 'references' / 'sources.md').read_text(encoding='utf-8')
    rows = re.findall(r'^\|\s*\[([^\]]+)\]\(([^)\s]+)\)', text, re.M)
    reviewed = re.search(r'Reviewed:\s*(\d{4}-\d{2}-\d{2})', text)
    return [(_c(label, 200), url) for label, url in rows], reviewed.group(1) if reviewed else ''


class Report:
    def __init__(self, data):
        self.doc = data
        self.s = summarize(data)
        self.type1 = self.s['type1']
        self.product = _c(data.get('product'), 80) or 'Unnamed product'
        self.pdf = PDF(title=f'SOC 2 readiness assessment: {self.product}', author=_c(data.get('assessor'), 80), subject=NOTICE)
        self.y = TOP
        self.gaps_ = [i for i in self.s['items'] if i['kind'] == 'gap']
        self.requests = [i for i in self.s['items'] if i['kind'] != 'gap']

    # Layout primitives

    def new_page(self):
        self.pdf.add_page()
        self.pdf.text(M, 34, self.product, 8, True, INK_2)
        label = 'CONFIDENTIAL'
        self.pdf.text(PAGE_W - M - text_width(label, 8, True), 34, label, 8, True, MUTED)
        self.pdf.line(M, 42, PAGE_W - M, 42, HAIRLINE, 0.5)
        self.y = TOP

    def need(self, height):
        if self.y + height > BOTTOM:
            self.new_page()

    def heading(self, title, intro=None):
        self.need(80)
        if self.y > TOP:
            self.y += 18
        self.pdf.rect(M, self.y - 15, 4, 19, fill=NAVY)
        self.pdf.text(M + 12, self.y, title, 17, True, INK)
        self.pdf.line(M + 12, self.y + 8, M + 52, self.y + 8, CYAN, 1)
        self.y += 26
        if intro:
            self.paragraph(intro, color=INK_2)
        self.y += 4

    def subheading(self, title):
        self.need(48)
        self.y += 8
        self.pdf.text(M, self.y, title, 11.5, True, INK)
        self.y += 16

    def paragraph(self, text, size=9.5, bold=False, color=INK, after=6):
        leading = size * 1.42
        for line in wrap(text, size, CW, bold):
            self.need(leading)
            self.pdf.text(M, self.y, line, size, bold, color)
            self.y += leading
        self.y += after

    def bullets(self, items, size=9.5, one_line=False):
        leading = size * 1.42
        for item in items:
            lines = wrap(item, size, CW - 14)
            if one_line and len(lines) > 1:
                lines = [self.ellipsize(lines[0], size, CW - 14)]
            self.need(leading * min(len(lines), 2))
            self.pdf.text(M + 2, self.y, '•', size, True, NAVY)
            for line in lines:
                self.need(leading)
                self.pdf.text(M + 14, self.y, line, size, False, INK)
                self.y += leading
            self.y += 2
        self.y += 4

    @staticmethod
    def ellipsize(line, size, width):
        while line and text_width(line + '…', size) > width:
            line = line[:-1]
        return line.rstrip() + '…'

    def chip(self, x, baseline, label, fill, ink, size=7.2):
        width = text_width(label, size, True) + 10
        self.pdf.rect(x, baseline - size * 0.75 - 3.2, width, size + 5, fill=fill, radius=3)
        self.pdf.text(x + 5, baseline, label, size, True, ink)
        return width

    def table(self, columns, rows, size=8.2):
        """Columns are (header, width); a cell is text or a ('chip', label, fill, ink) tuple."""
        pad, leading = 4, size * 1.35

        def header():
            height = leading + 2 * pad
            self.pdf.rect(M, self.y, CW, height, fill=PANEL)
            x = M
            for title, width in columns:
                self.pdf.text(x + pad, self.y + pad + size, title, size, True, INK_2)
                x += width
            self.y += height

        # A row is drawn whole, so a cell taller than a page is cut rather than run off the page.
        max_lines = int((BOTTOM - TOP - leading - 4 * pad) // leading)

        def fit(lines):
            return lines if len(lines) <= max_lines else lines[:max_lines - 1] + ['[continues in assessment.json]']

        self.need(3 * leading + 4 * pad)
        header()
        for row in rows:
            cells = [cell if isinstance(cell, tuple) else fit(wrap(cell, size, width - 2 * pad))
                     for (_, width), cell in zip(columns, row)]
            height = max(1 if isinstance(c, tuple) else len(c) for c in cells) * leading + 2 * pad
            if self.y + height > BOTTOM:
                self.new_page()
                header()
            x = M
            for (_, width), cell in zip(columns, cells):
                if isinstance(cell, tuple):
                    self.chip(x + pad, self.y + pad + size, *cell[1:])
                else:
                    for i, line in enumerate(cell):
                        self.pdf.text(x + pad, self.y + pad + size + i * leading, line, size, False, INK)
                x += width
            self.y += height
            self.pdf.line(M, self.y, M + CW, self.y, HAIRLINE, 0.5)
        self.y += 10

    def status_chip(self, status):
        _, short, fill, ink = STATUS[status]
        return ('chip', short, fill, ink)

    def severity_chip(self, severity):
        label, fill, ink = SEVERITY[severity]
        return ('chip', label, fill, ink)

    # Sections

    def cover(self):
        p = self.pdf
        p.add_page()
        p.rect(0, 0, PAGE_W, 318, fill=NAVY)
        p.text(M, 64, PRODUCT.upper(), 9, True, '#b7c2d3')
        p.line(M, 74, M + 36, 74, CYAN, 1)
        p.text(M, 140, 'SOC 2 Readiness', 32, True, WHITE)
        p.text(M, 176, 'Assessment', 32, True, WHITE)
        p.text(M, 204, 'Internal engineering readiness review for the Security category', 11, False, '#d5dce8')
        y = 252
        for line in wrap(self.product, 16, CW, True)[:2]:
            p.text(M, y, line, 16, True, WHITE)
            y += 20
        p.text(M, y + 2, 'Environment: ' + (_c(self.doc.get('environment'), 60) or 'unknown'), 9.5, False, '#d5dce8')

        n = len(self.s['controls'])
        period = self.doc['period']
        facts = [
            ('Assessor', _c(self.doc.get('assessor'), 80) or 'Unassigned'),
            ('Mode', MODES.get(self.doc.get('mode'), _c(self.doc.get('mode'), 40))),
            ('Period', f'{_c(period.get("start"), 10)} to {_c(period.get("end"), 10)}'),
            ('Framework mapping', _c(self.doc.get('framework_version'), 60)),
            ('Assessment created', _c(self.doc.get('created_on'), 20)),
            ('Report generated', today() + ' (UTC)'),
            ('Checks assessed', f'{n} ({"design only" if self.type1 else "design and operation"})'),
            ('Open items', f'{len(self.gaps_)} confirmed gaps, {len(self.requests)} evidence requests'),
        ]
        column = CW / 2
        for i, (label, value) in enumerate(facts):
            x, top = M + (i % 2) * column, 360 + (i // 2) * 42
            p.text(x, top, label.upper(), 7.2, True, MUTED)
            for j, line in enumerate(wrap(value, 10.5, column - 16)[:2]):
                p.text(x, top + 15 + j * 13, line, 10.5, False, INK)

        body = ('This document records engineering evidence for the scoped Security checks only. It does not certify '
                'compliance, and no count in it is a compliance score. A SOC 2 report is issued only by an independent '
                'CPA firm after its own examination; this readiness review does not replace one.')
        lines = wrap(body, 9, CW - 28)
        top = 548
        height = 40 + len(lines) * 12.8
        p.rect(M, top, CW, height, fill='#fbeeee', stroke='#d03b3b', line_width=1, radius=4)
        p.text(M + 14, top + 22, 'Not a SOC 2 report or auditor opinion', 11, True, '#8f1f1f')
        for i, line in enumerate(lines):
            p.text(M + 14, top + 40 + i * 12.8, line, 9, False, INK)
        p.text(M, top + height + 24, 'Confidential. Contains security findings: check for secrets and personal data before sharing.', 8.5, False, INK_2)

        credit, site = f'Generated with {PRODUCT}  ·  ', 'ctoside.com'
        p.text(M, PAGE_H - 70, credit, 8.5, False, MUTED)
        x = M + text_width(credit, 8.5)
        p.text(x, PAGE_H - 70, site, 8.5, True, NAVY)
        p.link(x, PAGE_H - 79, text_width(site, 8.5, True), 12, 'https://ctoside.com')

    def executive_summary(self):
        self.new_page()
        n = len(self.s['controls'])
        self.heading('Executive summary', (
            f'{n} checks were assessed for design' + ('.' if self.type1 else ' and operation.') +
            ' The counts below describe evidence coverage. They are not a compliance score.'))
        self.stat_row('Design statuses', self.s['design_counts'])
        if self.type1:
            self.not_assessed_panel('Operation statuses')
        else:
            self.stat_row('Operation statuses', self.s['operation_counts'])
        self.subheading('Evidence coverage by area')
        self.coverage_chart()
        self.subheading('Open items by urgency')
        rows = []
        for level in ORDER:
            gaps = sum(1 for i in self.gaps_ if i['severity'] == level)
            asks = sum(1 for i in self.requests if i['severity'] == level)
            rows.append([self.severity_chip(level), str(gaps), str(asks), str(gaps + asks)])
        self.table([('Urgency', 120), ('Confirmed gaps', 128), ('Evidence requests', 128), ('Total', 128)], rows)
        if not self.type1:
            self.y += 4
            rows = [r for r in self.s['period'] if r['operation_status'] in ('verified', 'partially_verified')]
            open_ = sum(1 for r in rows if r['uncovered'])
            self.paragraph(f'Period coverage: {len(rows)} {"check asserts" if len(rows) == 1 else "checks assert"} operation; '
                           f'{open_} {"has" if open_ == 1 else "have"} uncovered dates.', color=INK_2)
        top = (self.gaps_ or self.requests)[:5]
        # Keep the heading with its bullets: a half list stranded on the next page leaves that page nearly empty.
        self.need(24 + (len(top) - 1) * 15.5 + 14 if top else 48)
        self.subheading('Top priorities')
        if top:
            self.bullets([f'{i["key"]}  {i["summary"]} ({SEVERITY[i["severity"]][0]})' for i in top], one_line=True)
        else:
            self.paragraph('No open items are recorded.')

    def stat_row(self, caption, counts):
        self.need(100)
        self.pdf.text(M, self.y, caption.upper(), 7.2, True, MUTED)
        self.y += 8
        gap, height = 8, 50
        width = (CW - 4 * gap) / 5
        for i, key in enumerate(STATUS_ORDER):
            label, _, fill, _ = STATUS[key]
            x = M + i * (width + gap)
            self.pdf.rect(x, self.y, width, height, fill=PANEL, radius=4)
            self.pdf.rect(x + 10, self.y + 11, 7, 7, fill=fill, radius=1.5)
            for j, line in enumerate(wrap(label, 7.8, width - 30)[:2]):
                self.pdf.text(x + 21, self.y + 17.5 + j * 9.5, line, 7.8, False, INK_2)
            self.pdf.text(x + 10, self.y + 46, str(counts.get(key, 0)), 20, True, INK)
        self.y += height + 10

    def not_assessed_panel(self, caption):
        self.pdf.text(M, self.y, caption.upper(), 7.2, True, MUTED)
        self.y += 8
        self.pdf.rect(M, self.y, CW, 34, fill=PANEL, radius=4)
        self.pdf.text(M + 12, self.y + 21, NOT_ASSESSED, 10, True, INK_2)
        self.y += 46

    def coverage_chart(self):
        by_area = self.s['by_area']
        label_w, tip_w, bar_h, row_h = 112, 26, 8, 20
        x0 = M + label_w
        span = CW - label_w - tip_w
        peak = max(sum(a['design'].values()) for a in by_area.values()) or 1
        self.need(24 + row_h * len(by_area))
        x = x0
        for key in STATUS_ORDER:
            label, _, fill, _ = STATUS[key]
            self.pdf.rect(x, self.y - 7, 8, 8, fill=fill, radius=1.5)
            self.pdf.text(x + 11, self.y, label, 7.8, False, INK_2)
            x += 11 + text_width(label, 7.8) + 13
        self.y += 14
        start = self.y
        for area, dims in by_area.items():
            self.pdf.text(M, self.y + bar_h + 1, _c(area, 40), 8.5, False, INK)
            for row, (tag, key) in enumerate((('D', 'design'), ('O', 'operation'))):
                top = self.y + row * (bar_h + 2)
                self.pdf.text(x0 - 12, top + bar_h - 1, tag, 6.5, True, MUTED)
                if key == 'operation' and self.type1:
                    self.pdf.text(x0 + 2, top + bar_h - 1, 'Not assessed', 6.8, False, MUTED)
                    continue
                x, counts = x0, dims[key]
                for status in STATUS_ORDER:
                    count = counts.get(status, 0)
                    if not count:
                        continue
                    _, _, fill, ink = STATUS[status]
                    width = span * count / peak
                    self.pdf.rect(x, top, max(width - 2, 0.8), bar_h, fill=fill, radius=1.5)
                    label = str(count)
                    label_width = text_width(label, 6.5, True)
                    if label_width + 6 <= width - 2:
                        self.pdf.text(x + (width - 2 - label_width) / 2, top + bar_h - 1.5, label, 6.5, True, ink)
                    x += width
                self.pdf.text(x + 3, top + bar_h - 1, str(sum(counts.values())), 7, True, INK_2)
            self.y += row_h
        self.pdf.line(x0 - 1, start - 2, x0 - 1, self.y - 4, AXIS, 0.75)
        self.pdf.text(M, self.y + 4, 'D = design, O = operation', 7, False, MUTED)
        self.y += 10

    def scope(self):
        self.new_page()
        self.heading('Scope and boundary', 'What was assessed, under which assumptions, and how to read each status.')
        d = self.doc
        none_ = 'None recorded'
        rows = [
            ['Product', self.product],
            ['Environment', _c(d.get('environment'), 100) or 'unknown'],
            ['Mode', MODES.get(d.get('mode'), _c(d.get('mode'), 40))],
            ['Period', f'{_c(d["period"].get("start"), 10)} to {_c(d["period"].get("end"), 10)}'],
            ['Assessor', _c(d.get('assessor'), 100) or 'Unassigned'],
            ['In-scope systems', _join(d.get('in_scope_systems', []))],
            ['Exclusions', _join(d.get('excluded_systems', []))],
            ['Service commitments', _join(d.get('service_commitments', [])) if d.get('service_commitments') else 'Unknown; obtain management input.'],
            ['System requirements', _join(d.get('system_requirements', [])) if d.get('system_requirements') else 'Unknown; obtain management input.'],
            ['Scope unknowns', _join(d.get('scope_unknowns', [])) if d.get('scope_unknowns') else none_ + '; this does not prove scope completeness.'],
        ]
        if self.type1:
            rows.insert(3, ['Operation', NOT_ASSESSED])
        self.table([('Item', 120), ('Recorded value', CW - 120)], rows, size=8.8)
        self.subheading('How to read the statuses')
        cols = [('Status', 80), ('Design means', (CW - 80) / 2)]
        if self.type1:
            self.table(cols, [[self.status_chip(k), STATUS_MEANING[k][0]] for k in STATUS_ORDER], size=8.6)
            self.paragraph(NOT_ASSESSED + ': operation statuses are not recorded in this mode.', color=INK_2)
        else:
            self.table(cols + [('Operation means', (CW - 80) / 2)],
                       [[self.status_chip(k), *STATUS_MEANING[k]] for k in STATUS_ORDER], size=8.6)
        self.subheading('What this assessment cannot show')
        self.bullets(BOUNDARIES)

    def gaps(self):
        self.new_page()
        self.heading('Confirmed gaps', 'Failed and partially verified checks, ordered by status then urgency. '
                     'Close each one by applying the recommendation and re-running its verification test.')
        if not self.gaps_:
            self.paragraph('No confirmed gaps recorded. Missing evidence still prevents a supported conclusion.')
        for item in self.gaps_:
            self.gap_card(item)

    def gap_card(self, item):
        size, leading, label_w = 9, 12.6, 96
        pop = item['population']
        fields = [
            ('Criteria', ', '.join(item['criteria']) + ' (interpretive mapping)'),
            ('Observation', item['observation']),
            ('Recommendation', item['recommendation'] or 'Not recorded'),
            ('Owner', item['owner'] or 'Unassigned'),
            ('Due date', item['due_date'] or 'Not set'),
            ('Verification test', item['done_when'] or 'Not defined'),
            ('Evidence', item['evidence_refs'] or 'None recorded'),
        ]
        if item['dimension'] == 'operation':
            fields.append(('Period gaps', _span(item['period_gaps']).replace('\n', '; ')))
            fields.append(('Population', self.population(pop)))
        wrapped = [(label, wrap(value, size, CW - label_w)) for label, value in fields if value]
        height = 34 + sum(len(lines) * leading + 3 for _, lines in wrapped)
        self.need(min(height, BOTTOM - TOP))
        x = M
        for chip in (self.status_chip(item['status']), self.severity_chip(item['severity']),
                     ('chip', item['dimension'].title(), INK_2, WHITE)):
            x += self.chip(x, self.y - 1, *chip[1:]) + 5
        x += 4
        for line in wrap(f'{item["key"]}  {item["title"]}', 11, M + CW - x, True):
            self.pdf.text(x, self.y, line, 11, True, INK)
            self.y += 15
        self.y += 5
        for label, lines in wrapped:
            self.need(leading)
            self.pdf.text(M, self.y, label, 8, True, INK_2)
            for line in lines:
                self.need(leading)
                self.pdf.text(M + label_w, self.y, line, size, False, INK)
                self.y += leading
            self.y += 3
        self.pdf.line(M, self.y, M + CW, self.y, HAIRLINE, 0.5)
        self.y += 18

    @staticmethod
    def population(pop):
        if not pop or all(pop.get(k) is None for k in ('total', 'reviewed', 'exceptions')):
            return 'Not recorded'
        n = lambda k: 'n/a' if pop.get(k) is None else str(pop[k])
        out = f'total {n("total")}, reviewed {n("reviewed")}, exceptions {n("exceptions")}'
        for label, key in (('source', 'source'), ('selection', 'selection_method'), ('completeness', 'completeness_method')):
            if pop.get(key):
                out += f'; {label}: {pop[key]}'
        return out

    def period(self):
        if self.type1:
            return
        self.new_page()
        self.heading('Period coverage', f'Operation evidence against the assessment period '
                     f'{_c(self.doc["period"].get("start"), 10)} to {_c(self.doc["period"].get("end"), 10)}. '
                     'Uncovered dates have no operating evidence recorded. Population is total, reviewed and exceptions.')
        rows = []
        for r in self.s['period']:
            pop = '/'.join('n/a' if r[k] is None else str(r[k]) for k in ('total', 'reviewed', 'exceptions'))
            rows.append([f'{r["control_id"]} {r["title"]}', self.status_chip(r['operation_status']),
                         _span(r['covered']), _span(r['uncovered']), pop])
        if rows:
            self.table([('Check', 150), ('Operation', 62), ('Covered', 100), ('Uncovered dates', 100), ('Population', 92)], rows)
        else:
            self.paragraph('No operation evidence or conclusions are recorded.')

    def plan(self):
        self.new_page()
        self.heading('Remediation plan', 'Every open item, ordered by status then urgency. export_tasks.py writes the same '
                     'list and order for Jira, Notion and Slack.')
        rows = [[str(n), i['key'], i['summary'], self.severity_chip(i['severity']), i['owner'] or 'Unassigned', i['due_date'] or '–']
                for n, i in enumerate(self.s['items'], 1)]
        if rows:
            self.table([('#', 26), ('Item', 94), ('Task', 176), ('Urgency', 60), ('Owner', 88), ('Due', 60)], rows)
        else:
            self.paragraph('No open items are recorded.')

    def evidence_requests(self):
        self.new_page()
        self.heading('Evidence requests', 'These checks have no recorded determination. Collect the listed artifacts, '
                     'review them, and record the status with a named reviewer. A request is not a finding.')
        rows = [[i['control_id'], i['dimension'].title(), f'{i["title"]}\n{", ".join(i["criteria"])}', i['evidence_to_collect']]
                for i in self.requests]
        if rows:
            self.table([('Check', 56), ('Dimension', 62), ('Requirement and criteria', 190), ('Evidence to collect', CW - 308)], rows)
        else:
            self.paragraph('No evidence requests are recorded.')

    def matrix(self):
        self.new_page()
        self.heading('Appendix A: control matrix', 'Every check in the library with its recorded design and operation status.')
        if self.type1:
            self.paragraph('Operation: ' + NOT_ASSESSED + '.', color=INK_2)
        rows = []
        for cid, d in self.s['definitions'].items():
            c = self.s['controls'][cid]
            rows.append([cid, _c(d['title']), ', '.join(_c(x, 40) for x in d['criteria']), self.status_chip(c['design_status']),
                         'Not assessed' if self.type1 else self.status_chip(c['operation_status'])])
        self.table([('ID', 52), ('Check', 232), ('Criteria', 100), ('Design', 60), ('Operation', 60)], rows)

    def evidence_index(self):
        self.new_page()
        self.heading('Appendix B: evidence index', 'Evidence items referenced by the checks. References are locators, not copies of the evidence.')
        rows = []
        for e in self.doc['evidence']:
            p = e.get('period') or {}
            rows.append([_c(e['id'], 40), _c(e['type'], 40), _c(e['ref'], 400), _c(e['environment'], 60), _c(e['collected_on'], 10),
                         f'{_c(p["start"], 10)} to {_c(p["end"], 10)}' if p else '–', _c(e['reviewer'], 80)])
        if rows:
            self.table([('ID', 66), ('Type', 51), ('Reference', 146), ('Environment', 84), ('Collected', 52), ('Period', 60), ('Reviewer', 45)], rows)
        else:
            self.paragraph('No evidence items are recorded.')

    def closing(self):
        self.new_page()
        self.heading('Appendix C: limitations and sources')
        self.subheading('Limitations')
        self.bullets(LIMITS)
        self.subheading('Sources')
        sources, reviewed = _sources()
        for label, url in sources:
            label_lines, url_lines = wrap(label, 9, CW, True), wrap(url, 7.5, CW)
            self.need(len(label_lines) * 12 + len(url_lines) * 10 + 8)
            for line in label_lines:
                self.pdf.text(M, self.y, line, 9, True, NAVY)
                self.pdf.link(M, self.y - 9, text_width(line, 9, True), 12, url)
                self.y += 12
            for line in url_lines:
                self.pdf.text(M, self.y, line, 7.5, False, MUTED)
                self.y += 10
            self.y += 8
        self.y += 4
        self.paragraph('Recheck current official publications before relying on this report' +
                       (f' (source register reviewed {reviewed})' if reviewed else '') +
                       '. SOC 2 and associated marks belong to their respective owners; no affiliation or endorsement is claimed.', color=INK_2)
        self.paragraph('Before sharing it, perform an authorized manual check for secrets and personal data. '
                       'Redaction is limited and cannot find everything.', color=INK_2)

    def footers(self):
        total = len(self.pdf.pages)
        for i in range(total):
            self.pdf.line(M, PAGE_H - 44, PAGE_W - M, PAGE_H - 44, HAIRLINE, 0.5, page=i)
            self.pdf.text(M, PAGE_H - 30, f'{PRODUCT}  ·  {NOTICE}', 7.5, False, MUTED, page=i)
            label = f'Page {i + 1} of {total}'
            self.pdf.text(PAGE_W - M - text_width(label, 7.5), PAGE_H - 30, label, 7.5, False, MUTED, page=i)

    def build(self):
        self.cover()
        self.executive_summary()
        self.scope()
        self.gaps()
        self.period()
        self.plan()
        self.evidence_requests()
        self.matrix()
        self.evidence_index()
        self.closing()
        self.footers()
        return self.pdf.output()


def render_pdf(data):
    """Return the PDF bytes. `data` must already be validated (render() calls require_valid first)."""
    return Report(data).build()
