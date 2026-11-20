# SOC 2 Engineering Guardian v1.1 Implementation Plan

**Code:** SG

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give SOC 2 Engineering Guardian a designed PDF report, import-ready tracker exports and a public-release package, adapted from hipaa-guardian.

**Architecture:** One `summarize()` in `render_report.py` turns a validated assessment into ordered open items (one per check and dimension); the Markdown report, risk register, new `pdf_report.py` and reworked `export_tasks.py` all render from it. Corrections (symlink guard, scanner), templates, references and the README ship as separate tasks.

**Tech Stack:** Python 3.9+ standard library only; existing `pdf_writer.py` (built-in Helvetica, zlib streams); `unittest`. Pillow and `pdftoppm` only for the one-off README preview image, never imported by the skill or its tests.

**Spec:** `docs/superpowers/specs/2026-11-20-soc2-guardian-v1-1-design.md` (approved 2026-11-20). Read it with this plan.

## Global Constraints

- Python 3.9+, standard library only. No new dependency in `skills/` or `tests/`.
- Assessment `schema_version` stays `1.0`; control library `version` stays `1.0.0`; plugin and SKILL.md metadata version `1.1.0`.
- Signatures kept: `render(data, out, pdf=False) -> list[str]`, `export(data, out, formats=FORMATS, gaps_only=False) -> int`, `lines(data) -> list[str]`.
- Task summaries exactly `Fix: [Design] <title>` / `Collect evidence: [Operation] <title>` (dimension title-cased).
- Default texts, verbatim from today's `export_tasks.py`:
  - design action `Collect scoped implementation evidence and obtain reviewer judgment.`
  - operation action `Collect relevant operating records across the assessment period and reconcile the complete source population.`
  - operation done-when `A responsible reviewer evaluates period coverage, population completeness, selection and exceptions; record the supported conclusion.`
  - design done-when: the library check's `verification_test`.
- PDF footer notice on every page: `Internal readiness assessment – not a SOC 2 report or auditor opinion`. Task notice: `Internal readiness item, not an audit finding or opinion.`
- Output file names unchanged: `SOC2-READINESS.md|pdf`, `evidence-index.csv`, `risk-register.csv`, `assessment-redacted.json`, `handoff-manifest.json`, `tasks-jira.csv`, `tasks-notion.csv`, `tasks-slack-list.csv`, `tasks-slack.txt`, `tasks.md`.
- Every string that reaches an output passes through `common.clean()`; every CSV cell through `common.csv_safe()`.
- No percentages, scores, "compliant" or "certified" wording in any output.
- Style: new modules follow `repo_scan.py` / `pdf_writer.py` (readable); edits inside `common.py`, `render_report.py`, `validate_assessment.py` keep their compact style.
- Each task writes its tests in its **own** test file (named per task) so parallel tasks never edit the same file; `test_guardian.py` is touched only by SG-1.
- Suite command: `python3 -m unittest discover -s skills/soc2-engineering-guardian/tests -v` (zero tests collected is a failure). From SG-8 on also `python3 -m unittest discover -s tests -v` at the repo root.
- Commits: Conventional Commits, lowercase imperative subject, trailer `Task: SG-N` in the last paragraph with Co-Authored-By. Never push.

## Review Focus

1. **An assessment with no open items** (every check verified or not applicable): Markdown, PDF and every export must still render, saying "No open items are recorded."; CSVs are header-only. Tests in SG-3, SG-4, SG-5.
2. **Very long text** (a 3,000-character rationale, 200 in-scope systems, 60 evidence items): no PDF text below the footer, cells cut with `[continues in assessment.json]`. Tests in SG-4.
3. **Non-Latin, emoji and lone-surrogate text** in product, owner or recommendation: the PDF writes without crashing; the CSVs and Slack text are valid UTF-8. Tests in SG-4, SG-5.
4. **A Type 1 assessment end to end**: no operation items, no Period coverage section, operation shown as "Not assessed (Type 1 readiness)". Tests in SG-3, SG-4, SG-5.
5. **An output path through a macOS alias** (`/var/...` while the working directory resolves to `/private/var/...`) **with a symlink planted inside the working directory**: the write is refused. Test in SG-1.

## Execution and risk

| Task | Risk | Agent | Depends on |
|---|---|---|---|
| SG-1 symlink guard + CSV guard | security-critical | general-purpose, opus, high effort, ≤2 fix rounds | — |
| SG-2 scanner rules | standard | implementer + reviewer | SG-1 |
| SG-3 priority hints + summary model + Markdown + risk register | standard | implementer + reviewer | SG-1 |
| SG-4 PDF report | standard | implementer + reviewer | SG-3 |
| SG-5 task exports | standard | implementer + reviewer | SG-3 |
| SG-6 enriched example + example docs | standard | implementer + reviewer | SG-4, SG-5 |
| SG-7 templates, references, SKILL.md | standard | implementer + reviewer | SG-1 |
| SG-8 README, infographics, preview, manifests, CI | standard | implementer + reviewer | SG-2, SG-6, SG-7 |
| SG-9 final whole-branch review | security-critical | general-purpose, opus, high effort | all |

Each task runs on branch `sg-N-<slug>` in a worktree under `~/Developer/soc2-guardian-wt/sg-N`, branched from current `main`; the orchestrator merges to `main` after the review passes. No more than 3 agents at once. SG-2, SG-3, SG-7 run in parallel after SG-1; SG-4 and SG-5 in parallel after SG-3.

---

### Task SG-1: Narrow the output symlink guard; harden the CSV guard

**Files:**
- Modify: `skills/soc2-engineering-guardian/scripts/common.py:28-33` (`target`), `:48-50` (`csv_safe`)
- Test: `skills/soc2-engineering-guardian/tests/test_guardian.py` (append)

**Interfaces:**
- Produces: `target(path) -> Path` with the narrowed rule; `csv_safe(value) -> str` that also prefixes a cell starting with tab or CR. Signatures unchanged.

- [ ] **Step 1: Record the red baseline.** Run the suite on macOS. Expected: `Ran 66 tests … FAILED (errors=5)`, all five `ValueError: Refusing symlink output path` (`test_end_to_end_outputs`, `test_export_redacts_and_neutralizes_slack_mentions`, `test_null_optional_period_is_supported_for_design`, `test_report_preserves_scope_context`, `test_tasks_separate_fix_and_period_evidence`). Paste it.

- [ ] **Step 2: Write tests** (each chdirs into a fresh `TemporaryDirectory` and restores the old working directory with `addCleanup`):
  - `test_planted_symlink_folder_inside_cwd_is_refused`: make `out/real`, symlink `out/link -> out/real`; `write('out/link/report.json', {})` raises `ValueError`; `out/real` stays empty.
  - `test_planted_symlink_deeper_in_path_is_refused`: `out/link -> out/real`, `out/real/sub` exists; `write('out/link/sub/report.json', {})` raises; nothing written under `out/real/sub`.
  - `test_alias_path_to_planted_symlink_is_refused`: same layout, but pass the **absolute** path built from the unresolved `TemporaryDirectory` name (`/var/...` on macOS), `<tmp>/out/link/sub/report.json`; raises.
  - `test_dotdot_cannot_sidestep_guard`: `write('out/real/../link/sub/report.json', {})` raises.
  - `test_csv_safe_neutralizes_leading_tab_and_cr`: `csv_safe('\tfoo').startswith("'")` and `csv_safe('\r=1+1').startswith("'")`.

- [ ] **Step 3: Run the new tests on the old code.** Expected: the four symlink tests PASS (the old guard is stricter; they pin that the narrowed guard keeps refusing planted symlinks), `test_csv_safe_neutralizes_leading_tab_and_cr` FAILS. Paste both.

- [ ] **Step 4: Implement `target(path)`** in `common.py`, keeping the error message and the `mkdir(parents=True, exist_ok=True)`:

```python
p = Path(os.path.abspath(path))                 # lexical: '..' collapsed before checking
root = os.path.realpath(os.getcwd())
def inside(a):                                  # a lies strictly below the working directory
    r = os.path.realpath(a.parent)
    return r == root or r.startswith(root + os.sep)
if p.is_symlink() or p.parent.is_symlink() or any(a.is_symlink() for a in p.parents if inside(a)):
    raise ValueError('Refusing symlink output path')
```

  `csv_safe`: prefix `'` when the cleaned text starts with `=`, `+`, `-`, `@`, tab or CR, or does so after leading spaces (keep today's `lstrip()` behaviour); the CR/LF→space replacement inside the cell stays.

- [ ] **Step 5: Run the full suite.** Expected: all tests pass on macOS (66 + 5). Paste the `Ran` and `OK` lines. Then `python3 docs/build_example.py` succeeds.

- [ ] **Step 6: Commit** `fix(common): only refuse symlinks inside the output path, not system folders` with `Task: SG-1`.

**As built (2026-11-20):** merged `6c51cf7..1608a80`. Review found a case-variant bypass in the string-based `inside()` (macOS disks ignore case); fixed by comparing ancestry with `os.path.samestat` against `os.stat(os.getcwd())`. Three tests added beyond the brief: case-variant path, symlinked parent outside the working directory, `..` normalised before checking. Suite 74/74.

### Task SG-2: Scanner rules for SOC 2

**Files:**
- Modify: `skills/soc2-engineering-guardian/scripts/repo_scan.py:31-60` (`PATTERNS`), `:124` (`scope_notice`)
- Test: create `skills/soc2-engineering-guardian/tests/test_scan.py` (same `sys.path` insert as `test_guardian.py`)

**Interfaces:**
- Consumes: `scan(repo, max_files, max_bytes, max_findings) -> dict` (unchanged); `common.library()`.
- Produces: `PATTERNS` with 17 rules; finding schema unchanged.

- [ ] **Step 1: Write tests.** Helper `hits(line, name='app.py')` writes `line` to a temp repo file and returns the set of `rule_id`s found. Each new or renamed rule gets a positive and a negative test; assert `rule_id` and `control_id`:

| Rule (control) | Positive line(s) | Negative line(s) |
|---|---|---|
| `sensitive-log-candidate` (DAT-006) | `logger.info("login password=%s", pw)` | `logger.info("user logged in")` |
| `credential-in-url` (DAT-006) | `url = "https://api.test/v1?api_key=" + key` | `url = "https://api.test/v1?page=2"` |
| `unpinned-action-ref` (CHG-007), file `.github/workflows/ci.yml` | `      - uses: actions/checkout@main` | `- uses: actions/checkout@v4`; `- uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3`; `- uses: ./.github/actions/build`; `- uses: docker://alpine:3.20` |
| `pull-request-target-trigger` (CHG-007), `.yml` | `  pull_request_target:`; `on: [push, pull_request_target]` | `  pull_request:` |
| `postgres-ssl-disabled` (DAT-001) | `DATABASE_URL = "postgres://db.internal/app?sslmode=disable"`; `sslmode: allow` | `?sslmode=require`; `sslmode: verify-full` |
| `sentry-default-pii` (DAT-006) | `sentry_sdk.init(dsn=DSN, send_default_pii=True)`; `Sentry.init({ sendDefaultPii: true })` | `send_default_pii=False` |

  Plus: `test_rule_count_is_17`; `test_every_rule_maps_to_a_library_check`; `test_no_patient_wording_or_typo` (no `patient` in `scope_notice`, no `esensitive` and no rule id containing `phi`/`patient` in `PATTERNS`).

- [ ] **Step 2: Run them.** Expected: the new-rule tests and the count test FAIL; paste.

- [ ] **Step 3: Implement** per spec §7: replace `phi-log-candidate` and `patient-identifier-in-url`, add the four rules, fix "esensitive", reword `scope_notice` to "excludes common data, upload and fixture directories". Keep every `SKIP_DIRS` entry. Regexes stay single-line, case-insensitive where the table implies.

- [ ] **Step 4: Run** `test_scan.py` then the full suite. Expected: all pass; existing scanner tests in `test_guardian.py` still pass.

- [ ] **Step 5: Commit** `fix(scan): replace hipaa rules with soc 2 rules and add ci/cd checks` with `Task: SG-2`. (README/SKILL.md rule counts are updated by SG-7 and SG-8.)

**As built (2026-11-20):** merged `a7bb94c`; approved first review, no fix round. `sensitive-log-candidate` also matches `<prefix>_password`-style names (`(?:\w*_)?`), beyond the spec list. Suite 86/86.

### Task SG-3: Priority hints, shared summary model, Markdown and risk register

**Files:**
- Modify: `skills/soc2-engineering-guardian/references/controls.json` (add `priority_hint` to all 53 checks)
- Modify: `skills/soc2-engineering-guardian/scripts/render_report.py:1-63` (add `ORDER`, `DEFAULTS`, `summarize`; extend `lines`), `:87-110` (`render`: risk register)
- Modify: `skills/soc2-engineering-guardian/references/methodology.md` (one line on hints)
- Test: create `skills/soc2-engineering-guardian/tests/test_summary.py`

**Interfaces:**
- Produces (in `render_report.py`):
  - `ORDER = ['critical', 'high', 'medium', 'low']`
  - `summarize(data: dict) -> dict` with keys `definitions` {id: library entry}, `controls` {id: entry}, `type1` (bool), `design_counts` / `operation_counts` (Counter), `by_area` {area: {'design': Counter, 'operation': Counter}} in library first-appearance order (`Governance, Access, Changes, Data, Monitoring, Recovery, Vendors, AI engineering`), `items` (list), `period` (list).
  - Item dict keys: `key` (`<ID>-<dimension>`), `control_id`, `dimension` (`design`|`operation`), `area`, `title`, `criteria` (list[str]), `status`, `kind` (`gap`|`evidence_request`), `summary`, `severity`, `observation`, `recommendation`, `done_when`, `owner`, `due_date`, `evidence_refs` (str, `'; '.join('<evidence id> <ref>')`), `evidence_to_collect` (str), `period_gaps` (list of `[start, end]`), `population` (dict for operation items, `None` for design).
  - Period row keys: `control_id`, `title`, `operation_status`, `covered` (list of `[start, end]` from typed operation evidence), `uncovered` (`gaps_for` output), `total`, `reviewed`, `exceptions`.
- Consumes: `common.clean`, `common.csv_safe`, `common.coverage`, existing `gaps_for`.

- [ ] **Step 1: Write tests** in `test_summary.py` (build assessments with `init_assessment.create`; reuse the shapes from `test_guardian.py`'s `evidence()` / `operating()` helpers by copying them):
  - `test_every_check_has_a_priority_hint`: each library entry's `priority_hint` in `ORDER`; `IAM-002`, `IAM-003`, `IAM-004`, `DAT-003`, `AI-001` are `critical`.
  - `test_blank_type2_has_106_evidence_requests` and `test_blank_type1_has_53_design_items_only`.
  - `test_items_ordered_gaps_then_urgency_then_id`: a failed low, a partially_verified critical and a failed high → keys ordered failed-high, failed-low, partial-critical, then evidence requests.
  - `test_evidence_request_never_inherits_fix_text`: design `failed` with severity `high`, owner `Owner`, due `2026-12-01`, verification `Fix test`, recommendation `Repair` → its operation item has `done_when` == the operation done-when default, `recommendation` == the operation action default, `due_date == ''`, `owner == 'Owner'`, `severity == 'high'`, `kind == 'evidence_request'`; the design item has `done_when == 'Fix test'` and `due_date == '2026-12-01'`.
  - `test_unreviewed_item_takes_priority_hint`.
  - `test_period_rows_show_uncovered_dates`: operation `partially_verified` with operational evidence `2026-09-01..2026-10-31` in a `2026-08-01..2026-10-31` period → period row `uncovered == [['2026-08-01', '2026-08-31']]`; the item's `period_gaps` equal it. Type 1 → `period == []`.
  - `test_item_text_is_redacted`: rationale containing `person@example.com` → `[REDACTED_EMAIL]` in `observation`.
  - `test_no_open_items`: a Type 1 assessment with every check design `verified`, all citing one shared `code` evidence item, with rationale and reviewer → `items == []`; `render` writes a header-only risk register and the Markdown contains `No open items are recorded.` (SG-4 and SG-5 reuse this fixture shape.)
  - `test_markdown_has_no_score`: for the Type 2 fixture with gaps, the Markdown contains no `%` and none of `compliant`, `certified`, `score:` (case-insensitive).
  - `test_risk_register_one_row_per_item`: render to a temp dir; header exactly `['Item','Control','Dimension','Title','Criteria','Finding','Kind','Urgency','Owner','Due','Action','Done when','Evidence']`; data rows == `len(items)`, same order as `items` keys.
  - `test_markdown_sections`: type 2 Markdown has `## Status by area`, `## Open items by urgency`, `## Period coverage`; type 1 has the first two, no `## Period coverage`, and contains `Not assessed (Type 1 readiness)`.

- [ ] **Step 2: Run** `test_summary.py`. Expected: FAIL (`summarize` / `priority_hint` missing). Paste.

- [ ] **Step 3: Add `priority_hint`** to every check in `controls.json` per spec §2 (pinned criticals above; the rest by the spec's guidance). Do not change `version`, IDs, criteria or any other field.

- [ ] **Step 4: Implement `summarize(data)`** per spec §1 and the Interfaces above. Item rules: `kind` is `gap` for `failed`/`partially_verified`; severity = check `severity` or the hint; `observation` = rationale for gaps, `Evidence required` for requests; `recommendation`/`done_when` = check values for gaps, the defaults for requests; `due_date` blank for requests; Type 1 produces no operation items. Sort key: (status rank failed 0, partially_verified 1, insufficient_evidence 2; `ORDER.index(severity)`; `control_id`; design before operation). `evidence_to_collect` = `'; '.join(evidence_examples) + ' (suggested type: <suggested_evidence_type>)'` for requests, `''` for gaps. Pass every text field through `clean()`.

- [ ] **Step 5: Extend `lines(data)`** keeping every existing line: after the status counts add `## Status by area` (`| Area | Checks | Design V/P/F/NA/E | Operation V/P/F/NA/E |`, with a legend line; Type 1 operation cells read `not assessed`), `## Open items by urgency` (`| Urgency | Confirmed gaps | Evidence requests | Total |`), and for Type 2 `## Period coverage` (`| Check | Operation | Covered | Uncovered | Population total/reviewed/exceptions |`). In Type 1 the boundary block gains `Operation: Not assessed (Type 1 readiness)`. "Confirmed gaps and next actions" lists `gap` items as `<key> | <severity> | <title> | Owner: <owner> | <recommendation>`; with no open items at all it prints `No open items are recorded.` alongside the existing no-gaps sentence.

- [ ] **Step 6: Rewrite the risk register** in `render()` as one row per item with the header above (`Criteria` joined with `, `; `Finding` = status; `Kind` = `Confirmed gap`/`Evidence request`; `Action` = recommendation; `Evidence` = `evidence_refs`).

- [ ] **Step 7: Add to `methodology.md`** under Remediation and closure: `priority_hint` values are urgency defaults for unreviewed items, not risk ratings; a reviewer's `severity` replaces them.

- [ ] **Step 8: Run** `test_summary.py`, then the full suite, then `python3 docs/build_example.py`. Expected: all pass.

- [ ] **Step 9: Commit** `feat(report): add shared summary model, urgency hints and per-item risk register` with `Task: SG-3`.

### Task SG-4: Designed PDF report

**Files:**
- Create: `skills/soc2-engineering-guardian/scripts/pdf_report.py` (adapt `~/Projects/Skills/hipaa-guardian/skills/hipaa-guardian/scripts/pdf_report.py`)
- Modify: `skills/soc2-engineering-guardian/scripts/render_report.py` (delete the old `pdf_report()` function; `render(..., pdf=True)` writes `render_pdf(data)` to `SOC2-READINESS.pdf`)
- Test: create `skills/soc2-engineering-guardian/tests/test_pdf.py` (adapt hipaa-guardian `tests/test_exports.py` class `PdfReportTests`)

**Interfaces:**
- Consumes: `summarize`, `ORDER` (SG-3); `pdf_writer.PDF, PAGE_W, PAGE_H, text_width, wrap, encode`; `common.clean`, `common.library`.
- Produces: `render_pdf(data: dict) -> bytes`.

- [ ] **Step 1: Write tests** (helper `synthetic()` builds a Type 2 assessment with: a design `failed` critical gap whose rationale holds `jane.doe@example.com`, an operation `partially_verified` gap with Sep–Oct evidence and population 18/18/2, a design `verified` check, an AI check `not_applicable` with `approved_by`; helper `streams(pdf)` decompresses content streams):
  - `test_xref_table_points_at_every_object`, `test_page_count_matches_page_tree` (≥ 7 pages), `test_every_page_carries_the_notice` (`b'not a SOC 2 report or auditor opinion'` in every page stream, cover included), `test_pdf_redacts_and_keeps_findings` (no `jane.doe`; `[REDACTED_EMAIL]` present; the partial gap's rationale present), `test_non_latin_and_surrogates_do_not_crash` (product `'Cloud کلینیک \U0001F9B7 \ud800 (\\) test'`), `test_delete_character_is_not_drawn`, `test_wrap_is_linear_and_terminates` (subprocess, as hipaa), `test_long_text_stays_on_page` (200 in-scope systems, a 3,000-char rationale, 60 evidence items; every `Td` y ≥ 25).
  - `test_type2_has_period_coverage_section` (`b'Period coverage'` and `b'2026-08-01'` present); `test_type1_has_no_period_section` (no `b'Period coverage'`; `b'Not assessed'` present).
  - `test_no_open_items_renders` (`b'No open items are recorded.'`).
  - `test_render_cli_writes_pdf_and_markdown` (subprocess `render_report.py --assessment … --out … --pdf`; both files exist, PDF starts `%PDF-1.4`, manifest lists the PDF).

- [ ] **Step 2: Run** `test_pdf.py`. Expected: FAIL (`No module named 'pdf_report'`). Paste.

- [ ] **Step 3: Implement `render_pdf(data)`**: sections, order and content exactly as spec §3 (cover, executive summary, scope and boundary, confirmed gaps, period coverage (Type 2 only), remediation plan, evidence requests, appendices A–C). Brand navy `#101827` for the cover band, heading bars and links; cyan `#39B9D0` only for thin rules; status and urgency colours as hipaa-guardian, always with a text label. Header from page 2: product left, `CONFIDENTIAL` right. Footer on every page, cover included: `SOC 2 Engineering Guardian  ·  ` + the notice, and `Page N of M`. Type 1: operation tiles and chips replaced by `Not assessed (Type 1 readiness)`. Appendix C sources come from the `references/sources.md` table (label and URL). All text through `clean()`.

- [ ] **Step 4: Wire it in `render()`** and delete the old `pdf_report()`; `render()` return value and manifest unchanged.

- [ ] **Step 5: Run** `test_pdf.py`, the full suite, `python3 docs/build_example.py`. Render `docs/example/SOC2-READINESS.pdf` pages to PNG in your scratch folder (`pdftoppm -r 60 -png`) and look at every page: nothing overlaps, nothing runs off the page. Do not commit the PNGs. Report the page count.

- [ ] **Step 6: Commit** `feat(report): add designed pdf report` with `Task: SG-4`.

### Task SG-5: Import-ready task exports

**Files:**
- Modify: `skills/soc2-engineering-guardian/scripts/export_tasks.py` (rewrite; adapt hipaa-guardian `scripts/export_tasks.py`)
- Test: create `skills/soc2-engineering-guardian/tests/test_exports.py`

**Interfaces:**
- Consumes: `summarize`, `ORDER` (SG-3); `validate_assessment.require_valid`; `common.clean`, `common.csv_safe`, `common.target`.
- Produces: `FORMATS = ('jira', 'notion', 'slack', 'markdown')`; `export(data, out, formats=FORMATS, gaps_only=False) -> int` (task count); CLI `--assessment`, `--out`, `--format` (comma list or `all`, default `all`), `--gaps-only`.

- [ ] **Step 1: Write tests:**
  - `test_one_task_per_item_in_summary_order` (Jira rows' keys == `summarize` item keys).
  - `test_gaps_only_drops_evidence_requests`.
  - `test_jira_columns_and_priorities`: header exactly `['Summary','Issue Type','Priority','Labels','Labels','Labels','Labels','Due Date','Description']`; `Issue Type` all `Task`; priorities in `{Highest, High, Medium, Low}` mapped from critical/high/medium/low; labels `soc2`, `soc2-<area slug>` (e.g. `soc2-ai-engineering`), `confirmed-gap`|`evidence-request`, lower-case check ID.
  - `test_notion_and_slack_list_headers`: Notion header `['Task','Status','Priority','Finding','Dimension','Control','Area','Criteria','Owner','Due','Recommendation','Done when','Evidence to collect','Item ID']`; Slack list `['Task','Priority','Status','Owner','Due date','Control','Notes']`.
  - `test_no_csv_cell_can_be_a_formula` (recommendation `=HYPERLINK(...)`, owner `@ops`, a leading tab: no cell in any CSV starts with `= + - @ \t \r`).
  - `test_exports_redact_contact_details`; `test_slack_message_cannot_ping_or_link` (`<!channel> @here <https://x>` in a recommendation → no `@`, `<`, `>` from user text in `tasks-slack.txt`).
  - `test_markdown_checklist_grouped_by_urgency` (`- [ ]` count == tasks; `## Critical (n)` headings appear in ORDER).
  - `test_type1_blank_exports_53`; `test_no_open_items_writes_header_only_csvs`; `test_unicode_text_writes_utf8`.
  - `test_cli_unknown_format_writes_nothing` (exit code 2; output dir has no task files); `test_format_subset_writes_only_those_files` (`--format jira,markdown` → exactly `tasks-jira.csv`, `tasks.md`).

- [ ] **Step 2: Run** `test_exports.py`. Expected: FAIL. Paste.

- [ ] **Step 3: Implement** per spec §5: columns and Slack/Markdown shapes as specified; Jira description lines in this order: `SOC 2 Guardian <key>: <Finding>, <urgency> urgency`, `Control: <id> (<Dimension>), criteria <criteria> (interpretive mapping)`, `Observation: …`, `Recommendation: …`, `Evidence to collect: …` (requests), `Period gaps: …` (operation items with gaps), `Done when: …`, `Owner: …` (if set), then the task notice. Area slug: lower-case, non-alphanumerics → `-`. Validation before any file is written; unknown formats rejected before any file is written. Keep the existing `test_guardian.py` export tests passing (106, `Fix: [Design]`, `Collect evidence: [Operation]`, `complete source population`, Slack mention neutralising, invalid assessment writes nothing).

- [ ] **Step 4: Run** `test_exports.py`, the full suite, `python3 docs/build_example.py`.

- [ ] **Step 5: Commit** `feat(tasks): export import-ready jira, notion, slack and markdown tasks` with `Task: SG-5`.

### Task SG-6: Enriched synthetic example

**Files:**
- Modify: `skills/soc2-engineering-guardian/assets/assessment-example.json`
- Regenerate: `docs/example/*` via `python3 docs/build_example.py`
- Create: `docs/example/README.md`
- Test: create `skills/soc2-engineering-guardian/tests/test_example.py`

**Interfaces:**
- Consumes: `validate`, `summarize`, `render`, `export`.

- [ ] **Step 1: Write tests:** `test_example_validates`; `test_example_shows_every_section` (≥ 5 `gap` items across both dimensions and ≥ 3 urgencies; DAT-001 and CHG-001 among them; ≥ 2 checks with design `verified`; ≥ 1 check with operation `verified` whose evidence covers the full period with a population; AI-001..AI-003 `not_applicable` with `approved_by`; Type 2); `test_example_is_synthetic` (every `reviewer`, `assessor` and `product` contains `Synthetic`; no `@` in the file).

- [ ] **Step 2: Run.** Expected: FAIL on composition. Paste.

- [ ] **Step 3: Edit the example** per spec §9; dates within `2026-08-01..2026-10-31`, collection dates ≤ `2026-11-19`.

- [ ] **Step 4: Rebuild** `python3 docs/build_example.py`; write `docs/example/README.md` (table of every file and what it is; "everything is synthetic"; regenerate command; real assessments belong in a git-ignored `soc2-output/`).

- [ ] **Step 5: Run** the full suite. Open the example PDF pages as PNGs in scratch and check every section shows content.

- [ ] **Step 6: Commit** `docs(example): enrich synthetic assessment and regenerate example outputs` with `Task: SG-6`.

### Task SG-7: Templates, references and SKILL.md

**Files:**
- Create: `skills/soc2-engineering-guardian/assets/SYSTEM-DESCRIPTION.md`, `assets/SUBSERVICE-VENDOR-REGISTER.md`, `references/ai-saas-threats.md`, `references/installation.md`
- Modify: `skills/soc2-engineering-guardian/SKILL.md`
- Test: create `skills/soc2-engineering-guardian/tests/test_skill_docs.py`

**Interfaces:**
- Consumes (documents, does not call): `export_tasks.py --format/--gaps-only` (SG-5), `render_report.py --pdf` (SG-4), 17 scanner rules (SG-2), recheck semantics as they are today.

- [ ] **Step 1: Write tests:** `test_frontmatter` (parse the `---` block line by line: `name: soc2-engineering-guardian`, `license: MIT`, metadata `version: "1.1.0"`, description ≤ 1024 characters and contains `SOC 2`); `test_relative_links_resolve` (every `](relative/path)` in SKILL.md and `references/*.md` exists inside the skill folder); `test_templates_are_marked_unverified` (both templates contain `INTERNAL / UNVERIFIED TEMPLATE`); `test_skill_body_under_500_lines`; `test_skill_states_rule_count` (`17` scanner rules mentioned; no `13 regex`).

- [ ] **Step 2: Run.** Expected: FAIL. Paste.

- [ ] **Step 3: Write the four documents and update SKILL.md** per spec §8. Keep every existing SKILL.md rule and safety sentence; add the frontmatter fields, widened description, `report --pdf` and `tasks <format>` modes, an Outputs section with the tracker import paths, links to the templates and the AI reference.

- [ ] **Step 4: Run** `test_skill_docs.py` and the full suite.

- [ ] **Step 5: Commit** `docs(skill): add templates, ai threat model, install guide and outputs` with `Task: SG-7`.

### Task SG-8: Public README, infographics, preview, manifests, CI

**Files:**
- Modify: `README.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.github/workflows/tests.yml`
- Create: `docs/images/workflow.svg`, `docs/images/evidence-model.svg`, `docs/images/control-library.svg`, `docs/images/outputs.svg`, `docs/images/report-preview.png`
- Test: create `tests/test_repo.py` (repo root, not inside the skill: these files are not installed with the skill)

**Interfaces:**
- Consumes: example PDF (SG-6), rule count 17 (SG-2), SKILL.md metadata version (SG-7).

- [ ] **Step 1: Write tests:** `test_readme_links_and_images_resolve` (every relative link and `<img src>` exists); `test_svgs_are_accessible` (each SVG parses with `xml.etree.ElementTree`, has `<title>` and `<desc>`); `test_manifests` (both JSON parse; plugin and marketplace entry version `1.1.0`, equal to SKILL.md metadata version; marketplace `name == 'ctoside-soc2'`; plugin `name == 'soc2-engineering-guardian'`; homepage and repository `https://github.com/CTO-Side-com/soc2-engineering-guardian`; `category: security`); `test_ci_pins_runner` (`ubuntu-24.04`, `fail-fast: false`, `3.9`, and a step running `tests` at the repo root); `test_readme_is_current` (no `bundle`, no `Publication was not completed`, mentions `17`, contains `/plugin install soc2-engineering-guardian@ctoside-soc2`).

- [ ] **Step 2: Run** `python3 -m unittest discover -s tests -v`. Expected: FAIL. Paste.

- [ ] **Step 3: Manifests and CI:** per spec §10; CI gains a step `python -m unittest discover -s tests -v`; keep the matrix 3.9 / 3.11 / 3.13 and action versions from hipaa-guardian's green workflow (`actions/checkout@v7`, `actions/setup-python@v7`); drop the `paths:` filters so README and manifest changes are tested too.

- [ ] **Step 4: Infographics:** four hand-written SVGs per spec §9, in hipaa-guardian's `docs/images/*.svg` style (read them first), SOC 2 palette (navy `#101827`, cyan `#39B9D0` rules, status colours as the PDF).

- [ ] **Step 5: Preview:** render pages 1, 2 and the first Confirmed gaps page of `docs/example/SOC2-READINESS.pdf` with `pdftoppm -r 110 -png` into your scratch folder; compose them side by side on a light background with Pillow (from a scratch script, not committed) into `docs/images/report-preview.png`, under 400 KB. Put the exact two commands in your report for HANDOFF.

- [ ] **Step 6: README** in hipaa-guardian's structure per spec §9 (ASCII-art banner reading SOC 2 / GUARDIAN in the same block font as hipaa-guardian's, badges, IMPORTANT box, sections in the spec's order, the four SVGs and the preview, install for plugin marketplace / `gh skill` / git one-liners for Claude Code, Copilot, Cursor, other agents, and local `claude --plugin-dir .` from a ZIP). Keep the current Boundaries text. Test counts: write the numbers from your own final run; the orchestrator refreshes them at sprint end.

- [ ] **Step 7: Run** both suites and `python3 docs/build_example.py`. Render each SVG to PNG in scratch (`qlmanage -t -s 960 -o <scratch> <file>.svg`) and look at it: no clipped or overlapping text. Report what you checked.

- [ ] **Step 8: Commit** `docs(readme): public readme with infographics, preview and install guide` with `Task: SG-8`.

### Task SG-9: Final whole-branch review

- [ ] **Step 1:** Orchestrator records the time and the review dispatch in HANDOFF.md, then dispatches `general-purpose` on opus at high effort with: the spec, this plan, `git diff c4abed9..main`, and the Review Focus list. Scope: correctness, redaction leaks, symlink guard, Type 1 handling, PDF layout on the example, CSV import shapes.
- [ ] **Step 2:** Reviewer plants at most 3 defects in one batch in a throwaway worktree (one apply → test → revert script, results table): drop the ancestor loop in `target()`; let one Jira description line skip `clean()`; emit operation items in Type 1. Each must be caught by a test failing on its own assertion. The worktree is removed after.
- [ ] **Step 3:** Up to 2 fix rounds; findings the reviewer marks minor go under HANDOFF `## Follow-ups`.
- [ ] **Step 4 (orchestrator, sprint end):** refresh README test counts and the HANDOFF `tests:` line from one full run of both suites; tick SG rows; `git status --short` clean except `soc2-corrections-prompts.md`; `git check-ignore` on every created file prints nothing. Commit `docs: record v1.1 state in handoff`.
