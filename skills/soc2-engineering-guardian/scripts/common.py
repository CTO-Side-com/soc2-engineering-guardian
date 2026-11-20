"""Shared offline assessment primitives. No compliance conclusions are automated."""
import hashlib
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATUSES = {'verified', 'partially_verified', 'failed', 'not_applicable', 'insufficient_evidence'}
TYPES = {'code', 'test', 'configuration', 'operational', 'policy', 'contract', 'external_report'}
NOTICE = 'Internal engineering readiness assessment. Not a SOC 2 report, certification, or auditor opinion.'

def today():
    return datetime.now(timezone.utc).date().isoformat()

def load(path):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream)

def library():
    return load(BASE / 'references' / 'controls.json')

def iso(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Expected YYYY-MM-DD')
    return date.fromisoformat(value)

def target(path):
    # System aliases above the working directory (macOS /var -> /private/var) are trusted;
    # a symlink planted inside it, or as the file or its folder, is not.
    p = Path(os.path.abspath(path))  # lexical: '..' collapsed before checking
    root = os.stat(os.getcwd())
    def inside(a):  # a lies strictly below the working directory; by file identity, as names can differ in case
        r = Path(os.path.realpath(a.parent))
        return any(os.path.exists(x) and os.path.samestat(os.stat(x), root) for x in (r, *r.parents))
    if p.is_symlink() or p.parent.is_symlink() or any(a.is_symlink() for a in p.parents if inside(a)):
        raise ValueError('Refusing symlink output path')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def write(path, data, overwrite=True):
    with target(path).open('w' if overwrite else 'x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=True)
        stream.write('\n')

def clean(value, limit=3000):
    text = str(value).encode('utf-8', 'replace').decode('utf-8')
    # A key body spans lines no single-token rule reaches; an unterminated block is masked to the end.
    text = re.sub(r'(?s)-----BEGIN [A-Z ]*PRIVATE KEY-----(?:.*?-----END [A-Z ]*PRIVATE KEY-----|.*)', '[REDACTED_SECRET]', text)
    # Before the email rule, which would take pw@host.tld and lose the host.
    text = re.sub(r'(?i)\b([a-z][a-z0-9+.-]*://)[^/\s:@]+:[^/\s@]+@', r'\1[REDACTED_SECRET]@', text)
    text = re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', '[REDACTED_EMAIL]', text)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_ID]', text)
    # Only shapes no date, range, population, check ID or version can take: a leading + or a bracketed area code.
    text = re.sub(r'(?<![\w+])\+\d(?:[ .()-]{0,2}\d){6,14}\b|\(\d{3}\) ?\d{3}-\d{4}\b', '[REDACTED_PHONE]', text)
    # \b cannot precede the keyword in DB_PASSWORD or access_token, since _ is a word character.
    text = re.sub(r'''(?i)\bbearer\s+\S+|(?<![A-Za-z0-9])(?:\w*_)?(?:token|passw(?:or)?d|pwd|secret|api_?key|access_?key|private_?key)["']?\s*[:=]\s*(?:"[^"\n]*"?|'[^'\n]*'?|\S+)''', '[REDACTED_SECRET]', text)
    text = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,}|[sr]k_(?:live|test)_[A-Za-z0-9]+|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]+|eyJ[\w-]+\.eyJ[\w-]+\.[\w-]+)\b', '[REDACTED_SECRET]', text)
    return text[:limit]

def csv_safe(value):
    head = clean(value)  # checked before CR is flattened, so a leading tab or CR still counts
    text = head.replace('\r', ' ').replace('\n', ' ')
    return "'" + text if head.lstrip(' ').startswith(('\t', '\r')) or text.lstrip().startswith(('=', '+', '-', '@')) else text

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def coverage(intervals, start, end):
    """Return uncovered inclusive date ranges; overlapping evidence is merged."""
    lo, hi = iso(start).toordinal(), iso(end).toordinal()
    if lo > hi:
        raise ValueError('Period start must precede end')
    spans = sorted((max(lo, iso(a).toordinal()), min(hi, iso(b).toordinal())) for a, b in intervals)
    gaps, cursor = [], lo
    for a, b in spans:
        if a > b or b < cursor:
            continue
        if a > cursor:
            gaps.append([date.fromordinal(cursor).isoformat(), date.fromordinal(a-1).isoformat()])
        cursor = max(cursor, b+1)
    if cursor <= hi:
        gaps.append([date.fromordinal(cursor).isoformat(), date.fromordinal(hi).isoformat()])
    return gaps
