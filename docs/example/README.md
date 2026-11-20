# Synthetic example output

Everything in this folder is synthetic. The product, reviewers, owners, evidence references and dates
are invented for demonstration; no real company, system or person was assessed. The assessment is
an internal engineering readiness exercise, not a SOC 2 report, certification or auditor opinion.

The example is a Type 2 readiness assessment of a made-up SaaS product for 2026-08-01 to
2026-10-31. It shows six confirmed gaps across both dimensions and four urgencies, three checks with
verified design, one check with verified operation over the full period, three AI checks marked not
applicable with a named approver, and every remaining check as an evidence request.

| File | What it is |
| --- | --- |
| `SOC2-READINESS.pdf` | Designed report: cover, executive summary, scope, confirmed gaps, period coverage, remediation plan, evidence requests and appendices. |
| `SOC2-READINESS.md` | The same report as Markdown, with full Unicode text. |
| `risk-register.csv` | One row per open item (confirmed gaps and evidence requests) with owner, urgency and done-when. |
| `evidence-index.csv` | Evidence references with type, reviewer, collection date and covered period. |
| `assessment-redacted.json` | The assessment with free text redacted, suitable for sharing after review. |
| `handoff-manifest.json` | SHA-256 digest of each generated report file. |
| `tasks.md` | Open items as a Markdown checklist. |
| `tasks-jira.csv` | Open items for the Jira CSV work item import. |
| `tasks-notion.csv` | Open items for the Notion CSV import. |
| `tasks-slack-list.csv` | Open items for a Slack Lists CSV import. |
| `tasks-slack.txt` | A short Slack message summarising the open items, ready to paste. |

## Regenerate

The source is `skills/soc2-engineering-guardian/assets/assessment-example.json`. Never edit the
files here by hand. Rebuild all of them from the repository root:

```bash
python3 docs/build_example.py
```

## Real assessments

Keep real assessments out of version control. Write them to a git-ignored `soc2-output/` folder,
not to `docs/example/`.
