---
status: active
phase: v1.1 · Designed PDF report, tracker exports, public-release prep
next: SG-4 · SG-5 in parallel
tests: unit 61/66 on macOS (5 errors: symlink guard rejects /var temp dirs), CI green on Linux (2026-11-20)
updated: 2026-11-20 15:00 +0400
---

# SOC 2 Engineering Guardian: handoff

## Current state

- v1.0.0 is the initial commit `c4abed9`, created from `~/Downloads/SOC2_Engineering_Guardian.bundle`.
  `~/Downloads/SOC2_Engineering_Guardian_Source.zip` is the same tree except the README install
  section (zip wording: extract, `claude --plugin-dir .`).
- Not published. `origin` points at the local bundle; `CTO-Side-com/soc2-engineering-guardian`
  does not exist on GitHub yet.
- Model for this round: `~/Projects/Skills/hipaa-guardian` (public, v1.0, same CTOside family).

## What's working

- 53 original checks, separate design/operation statuses, period-gap detection, population
  fields, validator, recheck, GitHub metadata normalizer, scanner (13 rules), Markdown report,
  evidence index, risk register, hashed handoff manifest.
- PDF exists but is a plain text dump; task exports are one flat row shape for every tracker.

## Known problems

- ~~5 tests error on macOS: `common.target()` refused any symlinked ancestor (`/var`, `/tmp`).~~
  Fixed by SG-1 (merged 2026-11-20 14:45).
- Scanner still carries two HIPAA rules (`phi-log-candidate`, `patient-identifier-in-url`) and the
  typo "esensitive".
- CI runs `ubuntu-latest` with Python 3.9; hipaa-guardian found setup-python has no 3.9 build
  there (fixed by pinning `ubuntu-24.04`, hipaa commit `85eeb14`).
- Both this plugin and hipaa-guardian declare marketplace name `ctoside`.
- `recheck.py` fails open on nested changes: `PurePosixPath.match` never crosses a folder, so
  `watched_paths: ["backend/**"]` keeps a check verified when `backend/sub/x.py` changes (verified
  2026-11-20).
- `github_evidence.py` crashes with an `AttributeError` traceback on `"head": null` or a non-object
  review row (verified 2026-11-20).
- README install section is stale (git bundle, failed-publication sentence).

## Correction prompts

`soc2-corrections-prompts.md` (repo root, uncommitted: user asked for it as a suggestion, not run)
holds 7 self-contained prompts for Claude Code or Codex, one per defect above; prompt 7 (marketplace
rename) is gated on the Needs-you decision. If they are run before v1.1, the v1.1 plan drops spec
§6 (symlink guard), §7 (scanner) and the CI part of §10.

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

## Needs you

- [ ] 2026-11-20 · Marketplace name: both plugins say `ctoside`, and a user can register only one
      marketplace per name (Claude Code marketplace reference). Rename this one to `ctoside-soc2`,
      or list it inside hipaa-guardian's `ctoside` marketplace? (recommend rename; spec "Open")
- [ ] 2026-11-20 · Publish: create public `CTO-Side-com/soc2-engineering-guardian` and push once
      tests and the final review are green? (recommended; nothing is pushed until you say so)

## Tasks

| ID | Task | Status | Started | Finished |
|---|---|---|---|---|
| SG-1 | Narrow output symlink guard; CSV tab/CR guard (security-critical) | done | 2026-11-20 03:27 | 2026-11-20 14:45 |
| SG-2 | Scanner: SOC 2 rules, 17 total | done | 2026-11-20 14:46 | 2026-11-20 14:51 |
| SG-3 | Priority hints, summary model, Markdown, per-item risk register | done | 2026-11-20 14:46 | 2026-11-20 14:53 |
| SG-4 | Designed PDF report | review | 2026-11-20 14:53 | |
| SG-5 | Import-ready task exports | done | 2026-11-20 14:53 | 2026-11-20 15:00 |
| SG-6 | Enriched synthetic example | todo | | |
| SG-7 | Templates, references, SKILL.md | done | 2026-11-20 14:46 | 2026-11-20 14:52 |
| SG-8 | Public README, infographics, preview, manifests, CI | todo | | |
| SG-9 | Final whole-branch review (security-critical) | todo | | |

## Follow-ups

- SG-1 (minor, by design per spec §6): writing straight into `/tmp/x.json` on macOS is refused
  because the parent folder is the `/tmp` alias; a symlink deeper than the parent in a path
  outside the working directory is not checked; a no-permission folder raises `PermissionError`
  rather than `ValueError`; the check-then-open window is unchanged from v1.0.
- SG-2 (minor, scanner recall): `sensitive-log-candidate` misses `console.warn`, `logger.warn`,
  `log.info`, `secret_key`, `password_hash` and camelCase names, and its `<prefix>_password` match is
  untested; `credential-in-url` alternation is thinly tested and `?token=` pagination hits; the CI
  rules have no comment or multi-line tests.
- SG-7 (minor, carried into SG-8's contract): move SKILL.md `## Outputs` below the recheck and
  closing safety paragraphs; vendor register says "unmodified opinion" and that a bridge letter is a
  vendor assertion, not an auditor opinion, and does not extend the period; link test also scans
  `assets/*.md`; test that check IDs cited in `ai-saas-threats.md` exist. Left for hardening:
  Outputs file-name and forbidden-wording tests, rule-count test tied to the scanner list, unused
  `sys.path.insert` in `test_skill_docs.py`, trailing space in `SYSTEM-DESCRIPTION.md`.
- SG-3 (minor, test depth; SG-9 review focus): `test_item_text_is_redacted` checks `observation`
  only; no test for `csv_safe` on risk-register cells, for `code` evidence being excluded from period
  coverage, or for a reviewer `severity` overriding the hint on an evidence request. Pre-existing:
  `clean()` does not redact `sk_live_...` keys.
- SG-5 (minor; SG-9 review focus): no test pins the per-line `csv_safe()` inside the Jira
  Description (a planted skip survived); user newlines are not flattened in `tasks-slack.txt` and
  `tasks.md` (a recommendation can forge a bullet) and backtick fences survive in the Slack text.

## Next steps

1. Review SG-4 and SG-5 (reviewer agent) as each reports; merge; gate after each merge.
2. SG-6 (enriched example, commits regenerated docs/example) after both merge.
3. SG-8 (README, infographics, preview, manifests, CI; also the SG-7 doc minors and the
   install line), then SG-9 final whole-branch review (general-purpose, opus).

## In flight

- 2026-11-20 14:53 · base `3ecec96`, implementer agents (sonnet, high effort), hand-backs saved to
  `.superpowers/sdd/2026-11-20-soc2-guardian-v1-1/sg-N/report.md`:
  - SG-4 implement: branch `sg-4-pdf-report`, worktree `~/Developer/soc2-guardian-wt/sg-4`
  - SG-5 implement: branch `sg-5-task-exports`, worktree `~/Developer/soc2-guardian-wt/sg-5`
- Merged so far: SG-1 `afe94b7`, SG-2 `cfb3b2a`, SG-7 `0543f29`, SG-3 `3ecec96`, SG-5 (suite 122/122).
- SDD ledger and per-task scratch: `.superpowers/sdd/2026-11-20-soc2-guardian-v1-1/` (git-ignored);
  each task's hand-back is saved to `sg-N/report.md`, reviews to `sg-N/review-*.md`.
- Uncommitted on main: `soc2-corrections-prompts.md` (user asked for it as a suggestion; kept out of the repo for now).

