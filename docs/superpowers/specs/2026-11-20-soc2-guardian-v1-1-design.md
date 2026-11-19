# SOC 2 Engineering Guardian v1.1: designed report, tracker exports, public release prep

Date: 2026-11-20 · Status: draft for approval · Model project: `~/Projects/Skills/hipaa-guardian` (public v1.0)

## Intent

SOC 2 Engineering Guardian is going public as an open-source agent skill next to HIPAA Guardian,
from the same publisher (CTOside). Its assessment engine is sound (53 checks, separate design and
operation conclusions, period-gap detection, population fields, recheck, GitHub metadata), but the
two things people actually hand around are weak: the PDF is a plain text dump of the Markdown, and
the task exports are one flat row shape that no tracker imports well. HIPAA Guardian already solved
both. This release brings them across, adapted to SOC 2's model, and finishes the parts a public
release needs (install docs, README with infographics, templates, CI that works).

Success: a founder or engineering lead runs an audit, gets a PDF they would forward to their
leadership or auditor without embarrassment, and imports the task list into Jira, Notion or Slack
in one step. The repository looks and installs like HIPAA Guardian.

## Goals

1. Designed PDF report (`render_report.py --pdf`) adapted from hipaa-guardian `pdf_report.py`.
2. Import-ready task exports (`export_tasks.py`) adapted from hipaa-guardian `export_tasks.py`.
3. One shared summary model so Markdown, PDF, risk register and tasks never disagree.
4. Fix the macOS test failures (output symlink guard), CI runner, scanner leftovers from HIPAA.
5. Templates, AI threat-model reference, installation reference, SKILL.md and README for a public
   release, with ASCII art, four SVG infographics and a rendered report preview.

## Non-goals

- No new assessment semantics: statuses, validator rules, period coverage and population rules stay
  as they are (except the symlink guard, decided below).
- No Availability, Confidentiality, Processing Integrity or Privacy categories. Security only.
- No network calls from any script beyond the existing opt-in `github_evidence.py --allow-network`.
- No live tracker integration: exports are files; nothing is sent.
- Not publishing: creating the GitHub repo and pushing wait for an explicit "push".

## Anti-goals (would make this a failure even if it works)

- Any output that reads as a SOC 2 report, certification, compliance score or auditor opinion.
  Every PDF page carries the not-a-SOC-2-report notice; no percentages anywhere.
- An evidence request turning into a "violation" or "fix" ticket. Missing evidence stays a
  "Collect evidence" task.
- A report or export leaking an email, token or identifier that `common.clean()` would have
  redacted in the Markdown.
- A third-party runtime dependency. Scripts stay Python 3.9+ standard library only.
- Copying official AICPA criteria text or logos into the report or README.

## Constraints

- Python 3.9+, stdlib only, offline. `pdf_writer.py` is already identical to hipaa-guardian's
  (only the Producer string differs); reuse it unchanged apart from that.
- Assessment schema stays `1.0`; control library `version` stays `1.0.0` (adding `priority_hint`
  is advisory metadata, not a change to the checks; bumping would invalidate every existing
  assessment through the validator's version check). Plugin version becomes `1.1.0`.
- Public signatures kept, because tests and `docs/build_example.py` call them:
  `render(data, out, pdf=False) -> list[str]`, `export(data, out) -> int` (task count; a blank
  assessment gives 106 = 53 checks × 2 dimensions), `lines(data)`.
- Existing behaviours pinned by tests stay: task summaries `Fix: [Design] <title>` and
  `Collect evidence: [Operation] <title>`; the default operation action mentions the
  "complete source population"; Slack text cannot form `@channel` mentions or `<links>`;
  reports and tasks refuse invalid assessments and write nothing; CSV formula guard.
- File names stay: `SOC2-READINESS.md|pdf`, `evidence-index.csv`, `risk-register.csv`,
  `assessment-redacted.json`, `handoff-manifest.json`, `tasks-jira.csv`, `tasks-notion.csv`,
  `tasks-slack-list.csv`, `tasks-slack.txt`, `tasks.md`.
- Code style: new modules follow the readable style of `repo_scan.py` and `pdf_writer.py`
  (the same style as the hipaa-guardian code being adapted); edits inside the compact modules
  (`common.py`, `render_report.py`, `validate_assessment.py`) keep their compact style.

## Approaches considered

1. **Adapt HIPAA Guardian's report and exporter (chosen).** Port `pdf_report.py` and
   `export_tasks.py`, rework them around SOC 2's two dimensions, period coverage and populations.
   Proven layout code, tested PDF writer already shared, same CTOside family look, fastest.
2. Design a new SOC 2 report from scratch. More freedom, but re-solves pagination, tables and chips
   that already work, and the two products would look unrelated.
3. Generate HTML and convert to PDF. Better typography, but needs a browser or a third-party
   library: breaks the stdlib-only, offline constraint.

The user chose the HIPAA-derived direction ("learn from hipaa-guardian"); 2 and 3 were not
pursued.

## Decisions made by the user (2026-11-20)

- Public open-source release next to HIPAA Guardian.
- Narrow the output symlink guard (below).
- Scanner: replace the two HIPAA rules; add four CI/CD and data-protection rules (below).
- Extras: SYSTEM-DESCRIPTION and SUBSERVICE-VENDOR-REGISTER templates, AI threat-model reference,
  README preview image, README ASCII art and infographics.

## Design

### 1. Shared summary model (`render_report.summarize`)

One function feeds Markdown, PDF and tasks. Returns:

- `definitions` {id: library entry}, `controls` {id: assessment entry}
- `design_counts`, `operation_counts`: status counters over the 53 checks
- `by_area`: {area: {'design': Counter, 'operation': Counter}}; areas from `controls.json`
  (`Governance`, `Identity and access`, ... whatever the `area` field holds)
- `items`: one **open item per (check, dimension)** whose status is not `verified` or
  `not_applicable`, in this order: failed, partially_verified, insufficient_evidence; then urgency
  critical → low; then check ID; design before operation. Each item:
  - `key` `<ID>-<dimension>` (e.g. `CHG-001-operation`, the current export label)
  - `control_id`, `dimension` (`design`|`operation`), `area`, `title`, `criteria` (list),
    `status`, `kind` (`gap` for failed/partial, `evidence_request` otherwise)
  - `severity`: the check's `severity` if set, else the library `priority_hint`
  - `observation`: the check's `rationale`, or "Evidence required" for an evidence request
  - `recommendation`: the check's `recommendation` for a gap; for evidence requests **always** the
    existing default texts (design: "Collect scoped implementation evidence and obtain reviewer
    judgment."; operation: the "complete source population" text)
  - `done_when`: for a gap, the check's `verification_test`; for an evidence request **always** the
    existing defaults (design: the library `verification_test`; operation: the
    reviewer-evaluates-period-coverage text). `recommendation`, `verification_test`, `severity`,
    `owner` and `due_date` are stored once per check, not per dimension, and describe the gap's
    fix; an evidence request in the other dimension must not inherit the fix test, or it reads
    like a fix ticket (anti-goal). This matches today's exporter.
  - `owner`: the check's owner for both kinds (accountable for the whole check); `due_date`: the
    check's due date for gaps only, blank for evidence requests (the stored date belongs to the
    fix)
  - **Type 1 readiness:** operation is not assessed in `type1-readiness` (methodology.md, SKILL.md),
    so no operation items are produced in that mode: a blank Type 1 assessment yields 53 items, a
    blank Type 2 yields 106. Reports show operation as "Not assessed (Type 1 readiness)" instead of
    status tiles and chips for that dimension.
  - `evidence_refs`: that dimension's evidence IDs with their `ref`, redacted
  - `evidence_to_collect`: library `evidence_examples` + `suggested_evidence_type` (evidence
    requests only)
  - `period_gaps` (operation items in `type2-readiness` mode): output of the existing `gaps_for`
  - `population`: the check's population object (operation items)
- `period`: for `type2-readiness`, one row per check that has operation evidence or a non-default
  operation status: check, operation status, covered intervals, uncovered ranges, population
  total/reviewed/exceptions. Empty for `type1-readiness`.

All text passes through `common.clean()` before any renderer sees it.

### 2. `controls.json`: `priority_hint`

Add `priority_hint` (`critical|high|medium|low`) to all 53 checks so evidence requests sort by
urgency instead of all landing at Medium. Builder's call, as a starting point a reviewer can
change: critical for tenant isolation and authorization-independent-of-model-output
(IAM-004, AI-001), privileged access (IAM-002), server-side authorization (IAM-003), secrets out of
source (DAT-003); high for most IAM, CHG, DAT, MON-001..005, REC-001..002; medium for governance
evidence, vendors, recovery planning; low for none unless clearly cosmetic. A test asserts every
check has a valid hint. `references/methodology.md` gets one line: hints are urgency defaults for
unreviewed items, not risk ratings.

### 3. PDF report (`scripts/pdf_report.py`, new; `render_report.py --pdf` calls it)

US Letter, built-in Helvetica via `pdf_writer.py`. Brand: navy `#101827` (cover band, heading
bars, link text), cyan `#39B9D0` for thin rules only (too light for text). Status and urgency
colours as hipaa-guardian (green/amber/red/grey), always with a text label. Running header on every
page after the cover: product left, `CONFIDENTIAL` right. Footer on **every** page including the
cover: `SOC 2 Engineering Guardian · Internal readiness assessment – not a SOC 2 report or auditor
opinion` and `Page N of M`.

Sections, in order:

```
[1 Cover]        navy band: SOC 2 ENGINEERING GUARDIAN / "SOC 2 Readiness Assessment" /
                 "Internal engineering readiness review for the Security category"
                 product, environment
                 facts grid: Assessor · Mode (Type 1/Type 2 readiness) · Period · Framework mapping
                   · Assessment created · Report generated · Checks assessed (53) · Open items
                 red box: "Not a SOC 2 report or auditor opinion" + independent CPA sentence
                 "Generated with SOC 2 Engineering Guardian · ctoside.com" (link)
[2 Executive     two rows of five stat tiles: Design statuses / Operation statuses
   summary]      coverage chart by area: per area two stacked bars (D, O) by status
                 open items by urgency table: urgency · confirmed gaps · evidence requests · total
                 period coverage line (type2): "N checks assert operation; M have uncovered dates"
                 top priorities: up to 5 confirmed gaps, else top evidence requests
[3 Scope and     table: product, environment, mode, period, assessor, in-scope systems,
   boundary]     exclusions, service commitments, system requirements, scope unknowns
                 how to read the statuses (design vs operation meaning per status)
                 what this assessment cannot show (bullets from README Boundaries)
[4 Confirmed     one card per gap item: [status chip][urgency chip][Design|Operation] KEY title
   gaps]         Criteria (interpretive) · Observation · Recommendation · Owner · Due ·
                 Verification · Evidence · Period gaps · Population (operation only)
[5 Period        type2 only, skipped otherwise: table check · operation status · covered ·
   coverage]     uncovered dates · population total/reviewed/exceptions
[6 Remediation   every open item: # · key · task summary · urgency chip · owner · due
   plan]         (same list and order export_tasks.py writes)
[7 Evidence      evidence-request items: check · dimension · requirement + criteria ·
   requests]     evidence to collect
[Appendix A]     control matrix: ID · check · criteria · design chip · operation chip
[Appendix B]     evidence index: ID · type · reference · environment · collected · period · reviewer
[Appendix C]     limitations, sources (sources.md register), "recheck sources" and
                 "review before sharing" notes
```

Text reaching the PDF goes through `clean()`; non-Latin text must not crash (the writer already
substitutes). Table cells taller than a page are cut with `[continues in assessment.json]`
(as hipaa-guardian does).

### 4. Markdown report and risk register

`risk-register.csv` becomes one row per open item from `summarize()['items']`, in the same order
as the PDF remediation plan and the task files, so the three can be cross-referenced by item key.
Columns: Item, Control, Dimension, Title, Criteria, Finding (status), Kind (confirmed gap or
evidence request), Urgency, Owner, Due, Action, Done when, Evidence. All cells through
`csv_safe()`. A row count test ties it to the task count.

Keep every existing line and section of `lines(data)` (tests read them). Add after
"Evidence status counts": a status-by-area table (design and operation), "Open items by urgency",
and for type2 a "Period coverage" section built from `summarize()['period']`. The confirmed-gaps
list switches to `summarize()` items so order matches the PDF and tasks.

### 5. Task exports (`export_tasks.py`, reworked)

Built from `summarize()['items']`. Each item becomes one task. Summary
`Fix: [Design] <title>` / `Collect evidence: [Operation] <title>` (unchanged).

| File | Columns |
|---|---|
| `tasks-jira.csv` | Summary (`<key> <summary>`), Issue Type (`Task`), Priority (Highest/High/Medium/Low), Labels, Labels, Labels, Labels (`soc2`, `soc2-<area-slug>`, `confirmed-gap`\|`evidence-request`, `<id lowercase>`), Due Date, Description |
| `tasks-notion.csv` | Task, Status (`Not started`), Priority, Finding, Dimension, Control, Area, Criteria, Owner, Due, Recommendation, Done when, Evidence to collect, Item ID |
| `tasks-slack-list.csv` | Task, Priority, Status, Owner, Due date, Control, Notes |
| `tasks-slack.txt` | Slack mrkdwn: title, counts line with the not-an-audit-opinion notice, groups by urgency, `• *key* summary (owner, due)` and `_Next:_` line for gaps; `@ < >` replaced with look-alikes |
| `tasks.md` | Checklist grouped by urgency: `- [ ] **key** summary (control, criteria)`, then Recommendation, Evidence to collect, Done when, Owner · Due |

Description (Jira) lines: key with finding and urgency; control, dimension and criteria
("interpretive mapping"); observation; recommendation; evidence to collect; period gaps (operation);
done when; owner; notice "Internal readiness item, not an audit finding or opinion.".

CLI: `--format jira,notion,slack,markdown|all` (default all), `--gaps-only` (drop evidence
requests). Unknown format → argparse error, nothing written. Validation failure → error, nothing
written (current behaviour). `export(data, out, formats=FORMATS, gaps_only=False)` returns the task
count. Every CSV cell goes through `csv_safe()`; `csv_safe()` also neutralises a leading tab or CR
(OWASP list), matching hipaa-guardian.

### 6. Output symlink guard (`common.target`)

Today it refuses a path if **any** ancestor is a symlink, so every output under `/tmp` or `/var` on
macOS fails (5 test errors). New rule (decided): refuse when the file itself is a symlink, when
its parent folder is a symlink, or when any folder between the working directory and the file
(working directory excluded) is a symlink. Normalise the path lexically first
(`os.path.abspath`), so `..` segments cannot sidestep the check. Folders outside the working
directory are the user's own choice and are not checked.

Tests: the 5 current errors go green on macOS; a symlinked folder nested inside a temporary
working directory (`out/link/report.md`, `link → elsewhere`) is still refused and nothing is
written at the link target; existing file-symlink tests still pass.

### 7. Scanner (`repo_scan.py`)

Replace (keep rule count honest in docs):

| Old rule | New rule | Check | Severity | Matches |
|---|---|---|---|---|
| `phi-log-candidate` | `sensitive-log-candidate` | DAT-006 | high | a log/print call whose line names `password`, `passwd`, `secret`, `api_key`/`apikey`, `access_token`/`refresh_token`, `authorization`, `card_number`/`credit_card`, `cvv`, `ssn` |
| `patient-identifier-in-url` | `credential-in-url` | DAT-006 | medium | `[?&](access_token|api_key|apikey|token|password|secret|client_secret|session_id|sessionid)=` |

Add:

| Rule | Check | Severity | Matches | Must not match |
|---|---|---|---|---|
| `unpinned-action-ref` | CHG-007 | medium | `uses: owner/repo@main|master|latest|head|dev|develop|trunk` | `@v4`, `@<40-hex sha>`, `uses: ./local`, `docker://` |
| `pull-request-target-trigger` | CHG-007 | medium | a workflow trigger `pull_request_target` (key or in an `on:` list) | `pull_request:` |
| `postgres-ssl-disabled` | DAT-001 | high | `sslmode=disable` / `sslmode: allow` (any quoting) | `sslmode=require`, `verify-full` |
| `sentry-default-pii` | DAT-006 | medium | `send_default_pii=True`, `sendDefaultPii: true` | `False`/`false` |

Total 17 rules. Each new or replaced rule gets a positive and a negative test. Fix the
"esensitive" typo; drop "patient" from messages and the scope notice (keep the privacy-protective
skip directories, including `patient_data`). Scanner output schema unchanged.

### 8. Templates and references

- `assets/SYSTEM-DESCRIPTION.md`: engineering input for the system description, marked
  INTERNAL / UNVERIFIED TEMPLATE: services, service commitments and system requirements,
  components (infrastructure, software, people, procedures, data), boundary and exclusions,
  subservice organizations and the method (carve-out or inclusive), complementary subservice
  organization controls relied on, complementary user entity controls, significant changes during
  the period, redacted incident summary. States that the AICPA description criteria are
  authoritative and that this is not the management description. No official text copied.
- `assets/SUBSERVICE-VENDOR-REGISTER.md`: vendor · exact service · data processed · subservice
  org? · method · SOC report on file (type, period, opinion, exceptions noted, reviewed by) ·
  bridge letter · CSOCs relied on and where we test them · our CUEC responses · owner · next
  review; decision rule paragraph (a vendor's SOC 2 badge is not evidence; coverage of the exact
  service and period is).
- `references/ai-saas-threats.md`: scenario · check (AI-001..003, IAM-004, DAT-006, MON-001,
  CHG-001) · proof to seek · negative test with synthetic tenants. Covers prompt injection to tool
  calls, tool overreach, cross-tenant retrieval, model/provider egress and retention, telemetry
  leakage, prompt and model change control, AI action audit trail, broad agent autonomy. States
  these are engineering checks, not separate SOC 2 requirements.
- `references/installation.md`: per-agent install paths table (Claude Code, Copilot, Cursor),
  private output folder advice, example prompts, test-the-install commands (adapted from
  hipaa-guardian).
- `SKILL.md`: frontmatter adds `license: MIT` and `metadata` (author, version `1.1.0`); description
  widened to trigger on plain asks ("are we SOC 2 ready?", Type 1/Type 2 prep, auditor evidence
  requests, access reviews, change management evidence, SOC 2 tickets/report/PDF); modes table adds
  `report --pdf` and `tasks <format>`; an Outputs section lists every file with tracker import
  paths (Jira: Filters → Search work items → ••• → Import work items from CSV, map repeated Labels,
  date format `yyyy-MM-dd`; Notion: Settings → Import → CSV; Slack Lists: New → Import a CSV;
  Slack message: paste); links templates and the AI reference. Existing rules and safety text stay.

### 9. Example and docs

- Enrich `assets/assessment-example.json` (synthetic) so the report shows every section: about 5
  confirmed gaps across urgencies and both dimensions (keep DAT-001 and CHG-001), 2-3 checks with
  verified design, one check with verified operation over the full period with a population, AI
  checks `not_applicable` with a named approver (synthetic product has no AI features), the rest
  evidence requests. Must pass the validator. `docs/build_example.py` regenerates `docs/example/`.
- `docs/example/README.md`: what each file is, "everything is synthetic", regenerate command.
- README rewritten in hipaa-guardian's structure: centred ASCII-art banner (SOC 2 / GUARDIAN in the
  same block style) with tagline, badges (tests, MIT, Python 3.9+ stdlib, offline by default,
  agents), IMPORTANT not-a-SOC-2-report box, What it does, How an audit runs, Design vs operation,
  Control library, Install (plugin marketplace, `gh skill`, git one-liners for Claude Code, Copilot,
  Cursor, other agents; plus local `claude --plugin-dir .` from a downloaded ZIP), Use it, Reports
  (with preview image), Task exports (import table), GitHub evidence, Rechecks, Safety model,
  Boundaries (keep the current text), Repository layout, Development, Credits, License.
- Four SVG infographics in `docs/images/`, hand-written SVG in hipaa-guardian's style (960 px
  wide, light card background, system font stack, `<title>`/`<desc>` for accessibility) with the
  SOC 2 palette: `workflow.svg` (scope → boundary/templates → scan → GitHub evidence → design
  review → operation and period review → validate → report/tasks → recheck loop),
  `evidence-model.svg` (two dimensions × five statuses, what each needs; period coverage bar with
  a gap), `control-library.svg` (53 checks by area: GOV 15, IAM 8, CHG 8, MON 7, DAT 6, REC 3,
  VEN 3, AI 3), `outputs.svg` (inputs → assessment.json → reports, registers, task files).
- `docs/images/report-preview.png`: three PDF pages (cover, executive summary, confirmed gaps) side
  by side, rendered from the example PDF with local `pdftoppm` and Pillow as a one-off docs asset.
  Neither becomes a dependency of the skill; the regenerate command goes in HANDOFF.md.

### 10. Packaging and CI

- `plugin.json` / `marketplace.json`: version `1.1.0`, homepage and repository
  `https://github.com/CTO-Side-com/soc2-engineering-guardian`, keywords, `category: security`.
  Marketplace name: **open** (see below).
- CI: `runs-on: ubuntu-24.04` (setup-python has no 3.9 on ubuntu-latest), `fail-fast: false`,
  matrix 3.9 / 3.11 / 3.13, same action versions as hipaa-guardian's green CI, steps: unit tests,
  `python docs/build_example.py`.
- `.gitignore` already ignores `soc2-output/`.

## Open

- **Marketplace name.** Both plugins declare `ctoside`. Claude Code docs
  (code.claude.com/docs/en/plugins/marketplace-reference.md): "Each user registers one marketplace
  per `name`, so a user can't have two marketplaces with the same name registered at once."
  Options: (a) rename this repo's marketplace, e.g. `ctoside-soc2`, install line
  `soc2-engineering-guardian@ctoside-soc2` (recommended: self-contained, HIPAA users unaffected);
  (b) add this plugin to hipaa-guardian's `ctoside` marketplace with
  `{"source": "github", "repo": "CTO-Side-com/soc2-engineering-guardian"}` (one add for both, but
  the hipaa repo must change and be republished). Only `marketplace.json` and README install lines
  depend on it; build with (a) until decided.

## Calls made after the builder check (for the reader to confirm)

1. Type 1 readiness produces no operation items; operation shows as "Not assessed" (§1).
2. Evidence requests always use the default action and done-when, never the other dimension's
   fix text; they get no due date (§1).
3. `risk-register.csv` becomes one row per open item, same order and keys as the tasks (§4).
4. Marketplace builds with `ctoside-soc2` until you decide (Open).

## Left to the builder

- Exact `priority_hint` per check within the guidance in §2.
- Pixel layout of the PDF sections within the sketch in §3, chart geometry, column widths.
- Wording of template headings and threat-model rows within §8.
- SVG composition within §9.

## Verification

- `python3 -m unittest discover -s skills/soc2-engineering-guardian/tests -v` green on macOS and
  in CI (3.9, 3.11, 3.13); zero collected tests is a failure.
- `python3 docs/build_example.py` regenerates every example file; the example PDF opens, every
  page carries the notice, page count matches the page tree, cross-reference table is valid.
- Ported PDF tests (xref, page count, notice on every page, redaction, non-Latin text, DEL glyph,
  linear wrap, tall rows, CLI) and export tests (order, gaps-only, Jira columns and priorities,
  Notion/Slack first column, formula guard, redaction, Slack mentions and links, Markdown
  checkboxes, unknown format, all formats) adapted to SOC 2.
- Each new check is watched failing before its fix (pipeline rule).
- Final whole-branch review: general-purpose agent, strongest model, high effort; at most 3
  planted defects in one batch.
