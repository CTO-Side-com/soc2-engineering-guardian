"""Redaction of secrets and personal data before any report or export is written."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import test_pdf  # module import only: importing its TestCase names here would run them twice
from common import clean
from export_tasks import FORMATS, export
from init_assessment import create
from render_report import render
from validate_assessment import validate

# Synthetic values, split so secret scanners do not flag this file.
PASSWORD = 'Hunter2' + 'Synthetic'
STRIPE = 'sk_' + 'live_SYNTHETIC0000000000'
TOKEN = 'SYNTH' + 'tok123456'
PROBES = [  # (text, value that must not survive)
    ('key ' + STRIPE + ' leaked', STRIPE),
    ('key ' + 'sk_' + 'test_SYNTHETIC0000000000', 'sk_' + 'test_SYNTHETIC0000000000'),
    ('restricted ' + 'rk_' + 'live_SYNTHETIC0000000000', 'rk_' + 'live_SYNTHETIC0000000000'),
    ('restricted ' + 'rk_' + 'test_SYNTHETIC0000000000', 'rk_' + 'test_SYNTHETIC0000000000'),
    ('Rotate access_token=' + TOKEN, TOKEN),
    ('client_secret=' + 'SYNTHsecret123', 'SYNTHsecret123'),
    ('commits DB_PASSWORD=' + PASSWORD + ' to git', PASSWORD),
    ('{"password": "' + PASSWORD + '"}', PASSWORD),
    ("{'password': '" + 'Synth Spaced Pw' + "'}", 'Spaced Pw'),
    ('passwd=' + 'SynthPasswd1', 'SynthPasswd1'),
    ('pwd: ' + 'SynthPwd1', 'SynthPwd1'),
    ('aws ' + 'AKIA' + 'SYNTHETIC0000000', 'AKIA' + 'SYNTHETIC0000000'),
    ('slack ' + 'xox' + 'b-0000-SYNTHETIC-token', 'xox' + 'b-0000-SYNTHETIC-token'),
    ('jwt ' + 'eyJ' + 'hbGciOiJIUzI1NiJ9.' + 'eyJ' + 'zdWIiOiJzeW50aCJ9.SYNTHsig0000', 'SYNTHsig0000'),
    ('dsn postgres://app:' + 'SynthDbPw1' + '@localhost:5432/db', 'SynthDbPw1'),
    ('dsn postgres://app:' + 'SynthDbPw2' + '@db.example.com/app', 'SynthDbPw2'),
    ('-----BEGIN ' + 'PRIVATE KEY-----\nMIISYNTHETICKEYBODY\n-----END PRIVATE KEY-----', 'MIISYNTHETICKEYBODY'),
    ('-----BEGIN RSA ' + 'PRIVATE KEY-----\nMIISYNTHETICRSABODY\n-----END RSA PRIVATE KEY-----', 'MIISYNTHETICRSABODY'),
    ('call +1 415 555 0100 now', '555 0100'),
    ('call +44 20 7946 0958 now', '7946 0958'),
    ('call +14155550100 now', '4155550100'),
    ('call (415) 555-0100 now', '555-0100'),
    ('Authorization: Bearer ' + 'SYNTHbearer000', 'SYNTHbearer000'),
    ('mail jane.doe@example.com', 'jane.doe@example.com'),
    ('ssn 123-45-6789', '123-45-6789'),
]
ORDINARY = ['2026-08-01', 'Period 2026-08-01 to 2026-10-31', 'Population 92/92/0', 'IAM-002-design', 'v1.1.0',
            'See https://example.com/runbook', 'The password policy requires rotation every 90 days.',
            'Period gaps: [["2026-08-01", "2026-10-31"]]', 'Done when: reviewer signs off']


def evidence(kind='code', eid='E1'):
    return {'id': eid, 'type': kind, 'ref': 'controlled-records/review.json', 'method': 'Reviewed synthetic records',
            'reviewer': 'Synthetic Reviewer', 'environment': 'production', 'collected_on': '2026-11-01',
            'period': {'start': '2026-08-01', 'end': '2026-10-31'}}


def assessment(rationale, recommendation='Repair DAT-003'):
    doc = create('Synthetic SaaS', 'production', '2026-08-01', '2026-10-31')
    doc['evidence'] = [evidence()]
    c = next(c for c in doc['controls'] if c['id'] == 'DAT-003')
    c.update(design_status='failed', design_evidence=['E1'], rationale=rationale, reviewer='Synthetic Reviewer',
             owner='Synthetic Owner', severity='critical', recommendation=recommendation,
             verification_test='Retest DAT-003', due_date='2026-12-01')
    return doc


class RedactionTests(unittest.TestCase):
    def test_clean_redacts_common_secret_shapes(self):
        for probe, value in PROBES:
            with self.subTest(probe=probe):
                self.assertNotIn(value, clean(probe))

    def test_clean_keeps_scheme_and_host_of_credential_urls(self):
        out = clean('dsn postgres://app:' + 'SynthDbPw1' + '@localhost:5432/db')
        self.assertIn('postgres://', out)
        self.assertIn('@localhost:5432/db', out)

    def test_clean_leaves_ordinary_text(self):
        for text in ORDINARY:
            with self.subTest(text=text):
                self.assertEqual(text, clean(text))

    def test_secret_in_rationale_reaches_no_output(self):
        doc = assessment('config/prod.env commits DB_PASSWORD=' + PASSWORD + ' and ' + STRIPE,
                         'Rotate access_token=' + TOKEN)
        self.assertEqual([], validate(doc))
        with tempfile.TemporaryDirectory() as root:
            names = render(doc, root, pdf=True)
            export(doc, root, FORMATS)
            files = sorted(p for p in Path(root).iterdir())
            expected = set(names) | {'handoff-manifest.json', 'tasks-jira.csv', 'tasks-notion.csv', 'tasks-slack-list.csv',
                                     'tasks-slack.txt', 'tasks.md'}
            self.assertEqual(expected, {p.name for p in files})
            for path in files:
                data = path.read_bytes()
                text = b'\n'.join(test_pdf.streams(data)) if path.suffix == '.pdf' else data
                self.assertGreater(len(text), 0, path.name)
                for secret in (PASSWORD, STRIPE, TOKEN):
                    with self.subTest(file=path.name, secret=secret[:6]):
                        self.assertNotIn(secret.encode(), text)

    def test_redacted_assessment_redacts_keys(self):
        doc = assessment('Synthetic finding')
        doc['controls'][0]['f@leak.example.com'] = 'extra'
        self.assertEqual([], validate(doc))
        with tempfile.TemporaryDirectory() as root:
            render(doc, root)
            text = Path(root, 'assessment-redacted.json').read_text(encoding='utf-8')
        self.assertNotIn('leak.example.com', text)
        self.assertIn('[REDACTED_EMAIL]', json.loads(text)['controls'][0])

    def test_jira_description_lines_flatten_user_newlines(self):
        doc = assessment('a\n=1+1', 'b\n@SUM(1)')
        labels = ('SOC 2 Guardian ', 'Control: ', 'Observation: ', 'Recommendation: ', 'Evidence to collect: ',
                  'Period gaps: ', 'Done when: ', 'Owner: ', 'Internal readiness item, not an audit finding or opinion.')
        with tempfile.TemporaryDirectory() as root:
            export(doc, root, ('jira',))
            with Path(root, 'tasks-jira.csv').open(newline='', encoding='utf-8') as f:
                rows = list(csv.reader(f))[1:]
        for row in rows:
            for line in row[-1].split('\n'):
                self.assertTrue(line.startswith(labels), row[0] + ' has an unlabelled Description line: ' + repr(line))
        gap = next(r for r in rows if r[0].startswith('DAT-003-design '))
        self.assertIn('Observation: a =1+1', gap[-1])


if __name__ == '__main__':
    unittest.main()
