# Install SOC 2 Engineering Guardian

## Install from the public repository

Pick your agent; every command is copy-paste ready.

### Claude Code

**Plugin (recommended, updates with `/plugin`).** Run inside Claude Code:

```text
/plugin marketplace add CTO-Side-com/soc2-engineering-guardian
```

```text
/plugin install soc2-engineering-guardian@ctoside-soc2
```

**GitHub CLI** (gh 2.90 or later), for you or for one repository:

```bash
gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian --agent claude-code --scope user
```

```bash
gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian --agent claude-code --scope project
```

**Git only**, into `~/.claude/skills` (use `.claude/skills` instead for a single project):

```bash
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/CTO-Side-com/soc2-engineering-guardian.git "$tmp" && mkdir -p ~/.claude/skills && cp -R "$tmp/skills/soc2-engineering-guardian" ~/.claude/skills/ && rm -rf "$tmp"
```

> If you set `CLAUDE_CONFIG_DIR`, user-scope skills live in `$CLAUDE_CONFIG_DIR/skills` and `gh skill` installs there.

### GitHub Copilot

For you (`~/.copilot/skills`):

```bash
gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian --agent github-copilot --scope user
```

For one repository (installs to the shared `.agents/skills`):

```bash
gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian --agent github-copilot
```

Git only, into the repository's `.github/skills`:

```bash
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/CTO-Side-com/soc2-engineering-guardian.git "$tmp" && mkdir -p .github/skills && cp -R "$tmp/skills/soc2-engineering-guardian" .github/skills/ && rm -rf "$tmp"
```

### Cursor

For you (`~/.cursor/skills`):

```bash
gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian --agent cursor --scope user
```

For one repository (installs to the shared `.agents/skills`):

```bash
gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian --agent cursor
```

Git only, into the repository's `.cursor/skills`:

```bash
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/CTO-Side-com/soc2-engineering-guardian.git "$tmp" && mkdir -p .cursor/skills && cp -R "$tmp/skills/soc2-engineering-guardian" .cursor/skills/ && rm -rf "$tmp"
```

`gh skill install` also supports other agents: replace the `--agent` value (`gh skill install --help` lists them all).

## Copy the folder by hand

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
