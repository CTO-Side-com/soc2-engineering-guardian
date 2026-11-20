#!/usr/bin/env python3
"""Conservative offline *heuristic* scan. Emits line metadata, never source contents."""
import argparse
import hashlib
import os
import re
from pathlib import Path
from common import BASE, today, write as write_json

# Installs under .agents/, .cursor/ or .github/skills/ sit inside the audited repo; the skill's own
# test fixtures would otherwise surface as findings.
SKILL_ROOT = BASE

SKIP_DIRS = {
    '.git', '.claude', '.venv', 'venv', 'node_modules', '__pycache__',
    'dist', 'build', 'coverage', '.next', '.nuxt', '.terraform', 'vendor',
    'target', 'soc2-output', '.idea', '.vscode', '.pytest_cache',
    'data', 'datasets', 'uploads', 'exports', 'backups', 'logs', 'fixtures',
    'samples', 'records', 'patient_data', 'storage',
}
SKIP_SUFFIXES = ('.min.js', '.map', '.lock', '.snap', '.sqlite', '.db')
SKIP_NAMES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'Cargo.lock'}
TEXT_SUFFIXES = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs', '.java', '.cs', '.rb',
    '.php', '.sh', '.yml', '.yaml', '.json', '.toml', '.ini', '.conf', '.tf',
    '.hcl', '.dockerfile', '.env.example', '.properties', '.xml'
}
SPECIAL_NAMES = {'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', 'Caddyfile', 'nginx.conf', 'package.json', 'tsconfig.json', 'appsettings.json', 'composer.json'}

# High-confidence detection is impossible with regex. All results require human triage.
PATTERNS = [
    ('tls-verification-disabled', r'(?i)(verify\s*=\s*False\b|rejectUnauthorized\s*:\s*false\b|insecureSkipVerify\s*:\s*true\b)',
     'high', 'DAT-001', 'Potentially disabled TLS certificate validation'),
    ('insecure-cookie-flags', r'(?i)(secure\s*[:=]\s*false\b|httponly\s*[:=]\s*false\b)',
     'medium', 'IAM-001', 'Cookie/session security flags may be disabled'),
    ('permissive-cors', r'(?i)(allow_origins\s*=\s*\[\s*[\x27\x22]\*[\x27\x22]|Access-Control-Allow-Origin\s*[\x27\x22:]\s*\*)',
     'medium', 'DAT-004', 'Potential wildcard CORS; verify credentials and data exposure'),
    ('possible-credential-literal', r'(?i)\b(api[_-]?key|client[_-]?secret|authorization[_-]?token|password)\s*[:=]\s*[\x27\x22][A-Za-z0-9_+/=.!@#$%^&*:-]{12,}[\x27\x22]',
     'high', 'DAT-003', 'Possible hardcoded credential; inspect locally without copying the value'),
    # An optional prefix (user_password, client_secret) is covered; \b alone would miss it since _ is a word character.
    ('sensitive-log-candidate', r'(?i)(console\.(log|debug|info|error)|logger\.(info|debug|warning|error)|logging\.(info|debug|warning|error)|print\()\s*\(?[^\n]{0,180}\b(?:\w*_)?(password|passwd|secret|api_?key|access_token|refresh_token|authorization|card_number|credit_card|cvv|ssn)\b',
     'high', 'DAT-006', 'Potential credential or sensitive identifier in a log statement; may be harmless'),
    ('insecure-ssl-context', r'(?i)(CERT_NONE\b|check_hostname\s*=\s*False\b|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[\x27\x22]?0\b)',
     'high', 'DAT-001', 'Potential TLS/SSL insecure configuration'),
    ('verbose-sql-echo', r'(?i)\b(create_engine\([^\n]{0,180}echo\s*=\s*True\b|logging\.getLogger\([\x27\x22]sqlalchemy\.engine)',
     'medium', 'DAT-006', 'Potential database statement logging; verify sensitive data in query parameters'),
    # Keys may be quoted (JSON) or CamelCase (CloudFormation), hence the optional underscores and quote.
    ('encryption-disabled-config', r'(?i)\b(storage_?encrypted|encrypted|encryption_?enabled|enable_?encryption|encrypt_?at_?rest|at_?rest_?encryption_?enabled)[\x27\x22]?\s*[:=]\s*[\x27\x22]?false\b',
     'high', 'DAT-002', 'Infrastructure or service setting may disable encryption at rest'),
    ('public-resource-exposure', r'(?i)(\bacl[\x27\x22]?\s*[:=]\s*[\x27\x22]public-read(-write)?[\x27\x22]|\baccess_?control[\x27\x22]?\s*[:=]\s*[\x27\x22]?public_?read|\bpublicly_?accessible[\x27\x22]?\s*[:=]\s*[\x27\x22]?true\b|\bblock_?public_?acls[\x27\x22]?\s*[:=]\s*[\x27\x22]?false\b)',
     'high', 'IAM-001', 'Storage bucket or database may be publicly reachable'),
    ('jwt-verification-disabled', r'(?i)([\x27\x22]verify_signature[\x27\x22]\s*:\s*False\b|algorithms\s*[:=]\s*\[\s*[\x27\x22]none[\x27\x22]|ignoreExpiration\s*:\s*true\b|jwt\.decode\([^\n]{0,200}verify\s*=\s*False\b)',
     'high', 'IAM-008', 'Token signature or expiry verification may be disabled'),
    ('debug-mode-enabled', r'(?i)(^\s*DEBUG\s*=\s*True\b|\.run\([^\n]{0,120}debug\s*=\s*True\b|^\s*FLASK_DEBUG\s*=\s*[\x27\x22]?1\b)',
     'medium', 'DAT-006', 'Debug mode may expose stack traces and request data containing sensitive data'),
    # XML namespace URIs and reserved documentation hosts are identifiers, not endpoints.
    ('plaintext-http-endpoint', r'(?i)[\x27\x22\x60]http://(?!localhost\b|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|www\.w3\.org/|schemas\.|json-schema\.org|maven\.apache\.org/|www\.springframework\.org/|java\.sun\.com/|xmlns\.|purl\.org/|example\.(com|org|net)\b|(?:[\w-]+\.)*(?:example|local|localhost)(?=[:/\x27\x22\x60]|$))[\w.-]+',
     'medium', 'DAT-001', 'Plaintext HTTP URL; confirm no sensitive data or credentials travel over it'),
    ('credential-in-url', r'(?i)[?&](access_token|api_key|apikey|token|password|secret|client_secret|session_id|sessionid)=',
     'medium', 'DAT-006', 'Possible credential in a URL query string; leaks into logs, referrers and analytics'),
    # Workflow files under .github/ are scanned like any other YAML. A branch-like ref is mutable; a tag or SHA is not.
    ('unpinned-action-ref', r'(?i)\buses\s*:\s*[\x27\x22]?[\w.-]+/[\w./-]+@(main|master|latest|head|dev|develop|trunk)(?![\w.-])',
     'medium', 'CHG-007', 'Workflow action pinned to a mutable branch ref; pin to a release tag or commit SHA'),
    # Anchored to a YAML key, list item or `on:` line so a comment or string mentioning the trigger does not match.
    ('pull-request-target-trigger', r'(?i)(^\s*[\x27\x22]?pull_request_target[\x27\x22]?\s*:|^\s*-\s*[\x27\x22]?pull_request_target\b|^\s*[\x27\x22]?on[\x27\x22]?\s*:[^#\n]*\bpull_request_target\b)',
     'medium', 'CHG-007', 'Workflow runs on pull_request_target with repository secrets; verify it never checks out untrusted code'),
    ('postgres-ssl-disabled', r'(?i)\bsslmode[\x27\x22]?\s*[:=]\s*[\x27\x22]?(disable|allow)\b',
     'high', 'DAT-001', 'Database connection may not require TLS (sslmode disable or allow)'),
    ('sentry-default-pii', r'(?i)(\bsend_default_pii[\x27\x22]?\s*[:=]\s*True\b|\bsendDefaultPii[\x27\x22]?\s*[:=]\s*true\b)',
     'medium', 'DAT-006', 'Sentry may send default PII such as IP addresses and request data'),
]
COMPILED = [(rid, re.compile(exp), sev, ctrl, summary) for rid, exp, sev, ctrl, summary in PATTERNS]


def candidates(repo, max_files):
    count = 0
    for base, dirs, files in os.walk(repo, followlinks=False):
        dirs[:] = sorted(
            d for d in dirs
            if d not in SKIP_DIRS and not (Path(base) / d).is_symlink() and (Path(base) / d).resolve() != SKILL_ROOT
        )
        for filename in sorted(files):
            path = Path(base) / filename
            if path.is_symlink() or filename.startswith('.env') or filename in SKIP_NAMES or filename.endswith(SKIP_SUFFIXES):
                continue
            if not (path.suffix.lower() in TEXT_SUFFIXES or filename in SPECIAL_NAMES):
                continue
            yield path
            count += 1
            if count >= max_files:
                return


def scan(repo, max_files=12000, max_bytes=524288, max_findings=1000):
    repo = Path(repo).expanduser().resolve(strict=True)
    if not repo.is_dir():
        raise ValueError('Repository path must be a directory')
    findings = []
    scanned = 0
    skipped_size = 0
    truncated = False
    for path in candidates(repo, max_files):
        try:
            if path.stat().st_size > max_bytes:
                skipped_size += 1
                continue
            data = path.read_bytes()
            if b'\x00' in data:
                continue
            content = data.decode('utf-8', errors='replace')
        except (OSError, UnicodeError):
            continue
        scanned += 1
        relative = path.relative_to(repo).as_posix()
        for number, line in enumerate(content.splitlines(), 1):
            for rid, compiled, severity, control_id, message in COMPILED:
                if compiled.search(line):
                    key = f'{rid}|{relative}|{number}'.encode('utf-8')
                    findings.append({
                        'id': 'SCAN-' + hashlib.sha256(key).hexdigest()[:12],
                        'rule_id': rid, 'file': relative, 'line': number,
                        'severity_hint': severity, 'control_id': control_id,
                        'message': message, 'status': 'unconfirmed_lead',
                    })
                    if len(findings) >= max_findings:
                        truncated = True
                        break
            if truncated:
                break
        if truncated:
            break
    return {
        'schema_version': '1.0', 'scanned_on': today(),
        'repo_label': repo.name, 'scanner_type': 'offline_heuristic',
        'scope_notice': 'Metadata-only static lead generation. Not exhaustive; excludes common data, upload and fixture directories; no negative compliance inference.',
        'files_scanned': scanned, 'files_skipped_due_to_size': skipped_size,
        'max_file_count_limit': max_files, 'may_have_reached_file_limit': scanned + skipped_size >= max_files,
        'truncated_findings': truncated,
        'findings': findings,
    }


def main():
    ap = argparse.ArgumentParser(description='Local metadata-only heuristic source scan')
    ap.add_argument('--repo', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--max-files', type=int, default=12000)
    ap.add_argument('--max-bytes', type=int, default=524288)
    ap.add_argument('--max-findings', type=int, default=1000)
    args = ap.parse_args()
    if min(args.max_files, args.max_bytes, args.max_findings) < 1:
        ap.error('Limits must be positive')
    try:
        result = scan(args.repo, args.max_files, args.max_bytes, args.max_findings)
        write_json(args.out, result)
    except (ValueError, OSError) as error:
        ap.exit(1, 'Scan failed: ' + str(error) + '\n')
    print(f"Scanned {result['files_scanned']} files; {len(result['findings'])} unconfirmed leads; wrote {args.out}")


if __name__ == '__main__':
    main()
