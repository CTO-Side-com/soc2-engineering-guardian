---
status: paused
phase: v1.1 · Built and reviewed on main, not published
next: Publish to GitHub (Needs you)
tests: unit 159/159 · repo 9/9 (2026-11-20, macOS, Python 3.13); CI not run yet (unpublished)
updated: 2026-11-20 17:01 +0400
---
# SOC 2 Engineering Guardian: handoff

## Current state

- v1.1.0 is built on `main` (sprint commits `afe94b7`..this one); v1.0.0 is the initial commit
  `c4abed9` from `~/Downloads/SOC2_Engineering_Guardian.bundle`.
- Not published. `origin` points at the local bundle; `CTO-Side-com/soc2-engineering-guardian`
  does not exist on GitHub yet. Nothing has been pushed.
- Sibling and model: `~/Projects/Skills/hipaa-guardian` (public, same CTOside family).

## What's working

- 53 checks (GOV 15, IAM 8, CHG 8, MON 7, DAT 6, REC 3, VEN 3, AI 3) with separate design and
  operation statuses, period-gap detection, populations, validator, recheck, GitHub metadata
  normalizer; Type 1 shows operation as not assessed everywhere.
- Scanner: 17 SOC 2 rules (secrets in logs and URLs, unpinned Actions, `pull_request_target`,
  Postgres `sslmode=disable`, Sentry `send_default_pii`, …), never records the matched text.
- Outputs: designed PDF (21 pages on the example), Markdown, evidence index, per-item risk
  register, redacted assessment, hashed manifest; tasks for Jira, Notion, Slack (list and text)
  and Markdown.
- Safety: pattern-based redaction of named shapes in every output (README lists them; all
  patterns linear), CSV formula guard incl. tab/CR, narrowed output symlink guard.
- Docs: README with banner, four infographics and PDF preview; install guide per agent;
  SYSTEM-DESCRIPTION and SUBSERVICE-VENDOR-REGISTER templates; AI SaaS threat model; enriched
  synthetic example in `docs/example/`. Manifests 1.1.0, marketplace `ctoside-soc2`. CI matrix
  Python 3.9/3.11/3.13 on `ubuntu-24.04`.

## Known problems

- `recheck.py` fails open on nested changes: `PurePosixPath.match` never crosses a folder, so
  `watched_paths: ["backend/**"]` keeps a check verified when `backend/sub/x.py` changes (verified
  2026-11-20; correction prompt 2).
- `github_evidence.py` crashes with an `AttributeError` traceback on `"head": null` or a non-object
  review row (verified 2026-11-20; correction prompt 5).
- The output symlink guard does not check folders outside the working directory beyond the output
  folder itself (Needs you).
- Fixed in v1.1: macOS symlink-guard test errors (SG-1), HIPAA scanner rules and the "esensitive"
  typo (SG-2), CI runner (SG-8), shared marketplace name (SG-8, `ctoside-soc2`), stale README
  install section (SG-8).

## Correction prompts

`soc2-corrections-prompts.md` (repo root, uncommitted: you asked for it as a suggestion, not run)
holds 7 self-contained prompts. Prompts 1 (symlink guard), 3 (scanner), 4 (CI), 6 (README install)
and 7 (marketplace) are now built by v1.1. Prompts 2 (recheck nested folders) and 5 (malformed
GitHub exports) are still open and still yours to run or drop.

## Decisions (2026-11-20)

- [x] Build on this repo; the zip is the same source. Adopt the zip's install wording where it fits.
- [x] Goal: public open-source release next to HIPAA Guardian.
- [x] Add a designed PDF report and import-ready task exports (Jira, Notion, Slack, Markdown),
      adapted from hipaa-guardian to SOC 2's design/operation/period model.
- [x] Narrow the output symlink guard: the file, its folder, and any folder inside the working
      directory (still blocks a symlink planted in the audited repo).
- [x] Scanner: replace the two HIPAA rules with secrets/credentials in logs and URLs; add unpinned
      GitHub Action refs, `pull_request_target`, Postgres `sslmode=disable`, Sentry
      `send_default_pii`, each with a positive and a negative test.
- [x] Extras: SYSTEM-DESCRIPTION and SUBSERVICE-VENDOR-REGISTER templates, AI threat-model
      reference, README preview image, README ASCII art and infographics.
- [x] v1.1 spec approved as written, including its 4 calls (Type 1 has no operation items;
      evidence requests never inherit fix text; risk register one row per open item;
      marketplace `ctoside-soc2` until decided).
- [x] Correction prompts: suggest only, do not run. Prompts 1, 3, 4 overlap the approved spec and
      are built by the plan; prompts 2 (recheck) and 5 (github export) are not in the spec and
      stay with the user.
- [x] Process: full pipeline (over ~1,000 lines); final review by general-purpose on the strongest
      model (redaction and the symlink guard are security-relevant).
- [x] Marketplace name stays `ctoside-soc2` (answered 2026-11-20 16:58).
- [x] SG-9 past its fix cap: apply the reviewer's one-line JWT fix (`(?<!-)` before `eyJ`) with a
      red-then-green timing test and a README note on camelCase names, then merge (answered 2026-11-20 16:58).

## Needs you

- [x] 2026-11-20 · Marketplace name: both plugins say `ctoside`, and a user can register only one
      marketplace per name (Claude Code marketplace reference). Rename this one to `ctoside-soc2`,
      or list it inside hipaa-guardian's `ctoside` marketplace? (recommend rename; spec "Open")
- [ ] 2026-11-20 · Publish: create public `CTO-Side-com/soc2-engineering-guardian` and push once
      tests and the final review are green? (recommended; nothing is pushed until you say so)
- [ ] 2026-11-20 · Symlink guard, one step further than the narrowed rule: also refuse a symlinked
      folder outside the working directory when it is not owned by root? The final review wrote
      through a planted `soc2-output` link when the audited repo was not the working directory;
      system aliases (`/tmp`, `/var`) are root-owned and would stay allowed. (recommend yes, as a
      v1.1.1 follow-up; v1.1 ships your approved rule)
- [x] 2026-11-20 · SG-9 is out of fix rounds (2/2) with one blocking item: the JWT pattern added to
      `clean()` in round 1 takes 7.7 s on 100k characters of `eyJ-` (bound 1 s; slowdown, not a
      leak). The reviewer checked a one-line fix (`(?<!-)` before `eyJ`: 41 ms, 159/159). Allow it as
      a third, orchestrator-applied fix (test red then green, both suites, then merge), merge as is
      with a follow-up, or hold? (recommend the one-line fix; main today still leaks secrets that the
      branch masks)

## Tasks

| ID | Task | Status | Started | Finished |
|---|---|---|---|---|
| SG-1 | Narrow output symlink guard; CSV tab/CR guard (security-critical) | done | 2026-11-20 03:27 | 2026-11-20 14:45 |
| SG-2 | Scanner: SOC 2 rules, 17 total | done | 2026-11-20 14:46 | 2026-11-20 14:51 |
| SG-3 | Priority hints, summary model, Markdown, per-item risk register | done | 2026-11-20 14:46 | 2026-11-20 14:53 |
| SG-4 | Designed PDF report | done | 2026-11-20 14:53 | 2026-11-20 15:11 |
| SG-5 | Import-ready task exports | done | 2026-11-20 14:53 | 2026-11-20 15:00 |
| SG-6 | Enriched synthetic example | done | 2026-11-20 15:11 | 2026-11-20 15:19 |
| SG-7 | Templates, references, SKILL.md | done | 2026-11-20 14:46 | 2026-11-20 14:52 |
| SG-8 | Public README, infographics, preview, manifests, CI | done | 2026-11-20 15:20 | 2026-11-20 15:33 |
| SG-10 | Skill doc fixes from SG-7 review; public install commands | done | 2026-11-20 15:20 | 2026-11-20 15:24 |
| SG-9 | Final whole-branch review (security-critical) | done | 2026-11-20 15:33 | 2026-11-20 17:00 |

## Follow-ups

- SG-1 (minor, by design per spec §6): writing straight into `/tmp/x.json` on macOS is refused
  because the parent folder is the `/tmp` alias; a symlink deeper than the parent in a path
  outside the working directory is not checked; a no-permission folder raises `PermissionError`
  rather than `ValueError`; the check-then-open window is unchanged from v1.0.
- SG-2 (minor, scanner recall): `sensitive-log-candidate` misses `console.warn`, `logger.warn`,
  `log.info`, `secret_key`, `password_hash` and camelCase names, and its `<prefix>_password` match is
  untested; `credential-in-url` alternation is thinly tested and `?token=` pagination hits; the CI
  rules have no comment or multi-line tests.
- SG-7 (minor): Outputs placement, opinion wording, asset link scan and cited-ID test fixed by
  SG-10. Left for hardening: Outputs file-name and forbidden-wording tests, rule-count test tied to
  the scanner list, trailing space in `SYSTEM-DESCRIPTION.md`.
- SG-3 (minor, test depth; SG-9 review focus): `test_item_text_is_redacted` checks `observation`
  only; no test for `csv_safe` on risk-register cells, for `code` evidence being excluded from period
  coverage, or for a reviewer `severity` overriding the hint on an evidence request. Pre-existing:
  `clean()` does not redact `sk_live_...` keys.
- SG-5 (minor; SG-9 review focus): no test pins the per-line `csv_safe()` inside the Jira
  Description (a planted skip survived); user newlines are not flattened in `tasks-slack.txt` and
  `tasks.md` (a recommendation can forge a bullet) and backtick fences survive in the Slack text.
- SG-4 (minor): page 2 is dense with five priorities (chart rows 20 pt, footnote close to the
  next heading); top-priority lines repeat the dimension (`CHG-001-design Fix: [Design] ...`);
  the "cannot show" list in the PDF is hardcoded from README Boundaries and must be edited with it;
  non-Latin text prints as `?` (documented in Appendix C).
- SG-6 (minor): `pdf_writer.wrap()` splits words longer than a column by character, so free-form
  evidence IDs over ~14 characters or `external_report` still split in Appendix B (the example's
  values are whole and pinned); prefer breaks after `-`, `/`, `_`. Regenerating the example on a
  later day changes the PDF's generated-on line and its digest in `handoff-manifest.json`.
- SG-10 (minor): `test_install_guide_has_public_commands` checks two substrings only (misses a
  stray `--scope project` on Copilot/Cursor, a wrong `--agent`, a missing git destination); the
  Outputs-placement test proves only "not under Outputs" (assert `## Recheck and summarize`);
  installation.md's "other agents" line names none (sibling names Codex, Gemini CLI).
- SG-8 (minor; SG-9 review focus for 1-3): `tests/test_repo.py` asserts `'17'`, which "2017 TSC"
  satisfies, so the rule count is untested; the Boundaries test checks only the heading (and the
  PDF's list in `pdf_report.py` is a paraphrase, not the same text); `'3.9'` and
  `'fail-fast: false'` are substring checks. CI rebuilds the example without diffing it (the PDF
  carries a generated-on date). README says gaps become "Fix: ..." while the Jira summary carries
  the item key first. `claude --plugin-dir .` is in the README but not in `installation.md`.
- SG-9 (minor, later): the PDF running header has no width limit (an 80-character product name of
  wide letters overlaps CONFIDENTIAL); user newlines are not flattened in `tasks.md`,
  `tasks-slack.txt` or the Markdown report, so a recommendation can forge a task line, and backtick
  fences survive in the Slack text; PDF Appendix A follows `controls.json` order (GOV-009..015 print
  after AI-003).
- SG-9 (minor, later): redaction does not catch `Authorization: Basic`, `ASIA…` key IDs, unsigned
  JWTs, camelCase labels (`dbPassword=`), a JWT straight after a hyphen, or phone numbers without a
  `+` or brackets (README says so); `scrub()` drops one entry when two keys redact to the same
  string; commit `b990383` alone has the repo count test red (merge is green).

## Regenerate the README preview

`docs/images/report-preview.png` is PDF pages 1, 2 and 4 of `docs/example/SOC2-READINESS.pdf`.
Pillow is used only here, in a scratch script, never in committed code. With `$S` a scratch folder:

```bash
for p in 1 2 4; do pdftoppm -r 110 -png -f $p -l $p docs/example/SOC2-READINESS.pdf "$S/page"; done
python3 "$S/compose_preview.py" "$S" docs/images/report-preview.png   # keep it under 400 KB
```

`$S/compose_preview.py`:

```python
import sys
from PIL import Image, ImageDraw, ImageFilter
scratch, out = sys.argv[1], sys.argv[2]
pages = [scratch + '/page-%s.png' % n for n in ('01', '02', '04')]
PW, PAD, GAP, BG = 470, 32, 26, (244, 243, 239)
ims = []
for p in pages:
    im = Image.open(p).convert('RGB')
    ims.append(im.resize((PW, round(im.height * PW / im.width)), Image.LANCZOS))
H = max(i.height for i in ims) + 2 * PAD
W = 2 * PAD + 3 * PW + 2 * GAP
shadow = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(shadow)
x = PAD
for im in ims:
    d.rectangle([x + 3, PAD + 5, x + im.width + 3, PAD + im.height + 5], fill=(214, 212, 204))
    x += PW + GAP
canvas = shadow.filter(ImageFilter.GaussianBlur(5))
x = PAD
d = ImageDraw.Draw(canvas)
for im in ims:
    canvas.paste(im, (x, PAD))
    d.rectangle([x, PAD, x + im.width - 1, PAD + im.height - 1], outline=(225, 224, 217))
    x += PW + GAP
canvas = canvas.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
canvas.save(out, optimize=True)
```

## Next steps

1. Your call (Needs you): create public `CTO-Side-com/soc2-engineering-guardian` and push; then
   check CI on Linux for 3.9/3.11/3.13 and that the README badge and images resolve on GitHub.
2. v1.1.1: the symlink-guard question in Needs you; then a hardening pass over `## Follow-ups`
   (redaction gaps listed under SG-9, newline flattening in `tasks.md` and Slack text, PDF header
   width, test-depth items).
3. Correction prompts 2 and 5 if you want them.

## In flight

- Nothing running. All v1.1 tasks merged: SG-1 `afe94b7`, SG-2 `cfb3b2a`, SG-7 `0543f29`, SG-3
  `3ecec96`, SG-5 `f67a64a`, SG-4 `1d72225`, SG-6 `7ab9c2d`, SG-10 `85cf220`, SG-8 `a1cb2a5`, SG-9
  `ed443fd`. Each merge commit body carries its task report, review and cost.
- Uncommitted on main: `soc2-corrections-prompts.md` (you asked for it as a suggestion; kept out of
  the repo).
