"""Scanner rule tests; every example line is synthetic."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from common import library
from repo_scan import PATTERNS, scan


def findings(line, name='app.py'):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(line + '\n', encoding='utf-8')
        return scan(tmp)['findings']


def hits(line, name='app.py'):
    return {f['rule_id'] for f in findings(line, name)}


class RuleTests(unittest.TestCase):
    def assert_rule(self, rule, control, line, name='app.py'):
        found = [f for f in findings(line, name) if f['rule_id'] == rule]
        self.assertEqual(len(found), 1, f'{rule} should match: {line!r}')
        self.assertEqual(found[0]['control_id'], control)

    def assert_no_rule(self, rule, line, name='app.py'):
        self.assertNotIn(rule, hits(line, name), f'{rule} must not match: {line!r}')

    def test_sensitive_log_candidate(self):
        self.assert_rule('sensitive-log-candidate', 'DAT-006', 'logger.info("login password=%s", pw)')
        self.assert_no_rule('sensitive-log-candidate', 'logger.info("user logged in")')

    def test_credential_in_url(self):
        self.assert_rule('credential-in-url', 'DAT-006', 'url = "https://api.test/v1?api_key=" + key')
        self.assert_no_rule('credential-in-url', 'url = "https://api.test/v1?page=2"')

    def test_unpinned_action_ref(self):
        wf = '.github/workflows/ci.yml'
        self.assert_rule('unpinned-action-ref', 'CHG-007', '      - uses: actions/checkout@main', wf)
        for line in (
            '- uses: actions/checkout@v4',
            '- uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3',
            '- uses: ./.github/actions/build',
            '- uses: docker://alpine:3.20',
        ):
            self.assert_no_rule('unpinned-action-ref', line, wf)

    def test_pull_request_target_trigger(self):
        wf = '.github/workflows/pr.yml'
        self.assert_rule('pull-request-target-trigger', 'CHG-007', '  pull_request_target:', wf)
        self.assert_rule('pull-request-target-trigger', 'CHG-007', 'on: [push, pull_request_target]', wf)
        self.assert_no_rule('pull-request-target-trigger', '  pull_request:', wf)

    def test_postgres_ssl_disabled(self):
        self.assert_rule('postgres-ssl-disabled', 'DAT-001', 'DATABASE_URL = "postgres://db.internal/app?sslmode=disable"')
        self.assert_rule('postgres-ssl-disabled', 'DAT-001', 'sslmode: allow', 'config.yml')
        self.assert_no_rule('postgres-ssl-disabled', 'DATABASE_URL = "postgres://db.internal/app?sslmode=require"')
        self.assert_no_rule('postgres-ssl-disabled', 'sslmode: verify-full', 'config.yml')

    def test_sentry_default_pii(self):
        self.assert_rule('sentry-default-pii', 'DAT-006', 'sentry_sdk.init(dsn=DSN, send_default_pii=True)')
        self.assert_rule('sentry-default-pii', 'DAT-006', 'Sentry.init({ sendDefaultPii: true })', 'app.js')
        self.assert_no_rule('sentry-default-pii', 'sentry_sdk.init(dsn=DSN, send_default_pii=False)')
        self.assert_no_rule('sentry-default-pii', 'Sentry.init({ sendDefaultPii: false })', 'app.js')

    def test_old_hipaa_rules_are_gone(self):
        found = hits('logger.info("patient dob")\nurl = "https://x.test/?patient_id=1"')
        self.assertFalse(found & {'phi-log-candidate', 'patient-identifier-in-url'})


class RegistryTests(unittest.TestCase):
    def test_rule_count_is_17(self):
        self.assertEqual(len(PATTERNS), 17)

    def test_rule_ids_are_unique(self):
        ids = [p[0] for p in PATTERNS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_rule_maps_to_a_library_check(self):
        known = {c['id'] for c in library()['controls']}
        for rid, _, severity, control_id, _ in PATTERNS:
            self.assertIn(control_id, known, rid)
            self.assertIn(severity, {'high', 'medium', 'low'}, rid)

    def test_no_patient_wording_or_typo(self):
        with tempfile.TemporaryDirectory() as tmp:
            notice = scan(tmp)['scope_notice']
        self.assertNotIn('patient', notice.lower())
        self.assertIn('excludes common data, upload and fixture directories', notice)
        for rid, _, _, _, summary in PATTERNS:
            self.assertNotIn('esensitive', summary)
            self.assertNotIn('patient', summary.lower())
            self.assertNotIn('phi', rid)
            self.assertNotIn('patient', rid)

    def test_privacy_skip_directories_kept(self):
        from repo_scan import SKIP_DIRS
        self.assertIn('patient_data', SKIP_DIRS)


if __name__ == '__main__':
    unittest.main()
