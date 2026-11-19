---
status: active
phase: v1.1 · Designed PDF report, tracker exports, public-release prep
next: Write the v1.1 plan (code SG)
tests: unit 61/66 on macOS (5 errors: symlink guard rejects /var temp dirs), CI green on Linux (2026-11-20)
updated: 2026-11-20 03:15 +0400
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

- 5 tests error on macOS: `common.target()` refuses a path if any ancestor is a symlink, and
  `/var`, `/tmp` are symlinks on macOS. Linux CI passes.
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

## Next steps

1. Write the plan in `docs/superpowers/plans/2026-11-20-soc2-guardian-v1-1.md` (code `SG`).
2. Dispatch tasks per the plan.
