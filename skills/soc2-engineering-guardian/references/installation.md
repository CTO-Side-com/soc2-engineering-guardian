# Install SOC 2 Engineering Guardian

The skill is the folder `skills/soc2-engineering-guardian` in this repository. Copy that folder into the location your agent reads skills from.

| Agent | Project scope | User scope |
|---|---|---|
| Claude Code | `.claude/skills/soc2-engineering-guardian` | `~/.claude/skills/soc2-engineering-guardian` (`$CLAUDE_CONFIG_DIR/skills` when set) |
| GitHub Copilot | `.github/skills/soc2-engineering-guardian` | `~/.copilot/skills/soc2-engineering-guardian` |
| Cursor | `.cursor/skills/soc2-engineering-guardian` | `~/.cursor/skills/soc2-engineering-guardian` |

Example for Claude Code, project scope, run from the repository you want to assess:

```bash
mkdir -p .claude/skills
cp -R <path-to-this-repo>/skills/soc2-engineering-guardian .claude/skills/
```

`SKILL_DIR` below means the folder you copied.

## Choose a private output folder first

Decide where evidence artifacts will be written before running anything. Prefer `soc2-output/` and add it to the assessed repository's `.gitignore`: assessments, redacted exports and task files describe your security posture and belong outside public version control. Start with read-only static scans. Avoid real customer data, production credentials, uploading source to unfamiliar services, and auto-fixing code.

## Example prompts

> Use SOC 2 Engineering Guardian to assess this SaaS for Security readiness. Scope: production, 2026-08-01 through 2026-10-31, Type 2 preparation. Start read-only: no production data, no secrets, no network calls. Run the offline scanner, inspect code and configuration, and tell me which evidence you need. Ask before writing under soc2-output/ or changing source.

- Narrow follow-up: `triage <finding>` on one scanner lead.
- Plan: "Turn the confirmed gaps into a prioritized plan with owners and done-when tests."
- Deliverables: "Render the SOC 2 readiness report as a PDF" and "export the open items for Jira" (or Notion, Slack, Markdown).
- After changes: "Recheck against the files changed since the baseline."

## Limits to keep in mind

- Keep production secrets and customer records outside the working directory.
- Do not run production pentests automatically. Use written authorization and an isolated environment.
- The agent interprets the skill. It does not authenticate your evidence, issue an auditor opinion or certify anything. A SOC 2 report comes only from an independent CPA engagement.

## Test the installation

```bash
python3 -m unittest discover -s <SKILL_DIR>/tests -v
python3 <SKILL_DIR>/scripts/init_assessment.py --product "Test App" --environment production --start 2026-08-01 --end 2026-10-31 --out soc2-output/assessment.json
python3 <SKILL_DIR>/scripts/validate_assessment.py --assessment soc2-output/assessment.json
python3 <SKILL_DIR>/scripts/render_report.py --assessment soc2-output/assessment.json --out soc2-output/handoff --pdf
```

The blank assessment intentionally contains no verified controls. The scripts need Python 3.9+ and its standard library only.
