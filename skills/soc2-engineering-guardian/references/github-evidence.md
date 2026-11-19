# GitHub evidence workflow

## Offline mode

Use a local JSON object containing `pulls`, `deployments`, and `reviews`. `pulls` and `deployments` are REST arrays or arrays of paginated arrays. `reviews` maps PR numbers, as strings, to arrays or paginated arrays of review responses. Provide approved exports only; raw API responses may contain private titles, comments, repository details or identity information. The normalizer writes an allowlisted subset and pseudonymous actor identifiers, not those raw fields.

```bash
python3 <skill-dir>/scripts/github_evidence.py --repo owner/repository --start 2026-08-01 --end 2026-10-31 --input approved-export.json --out github-evidence.json
```

The output always declares population completeness unverified. Missing review collections are distinguishable from an empty successful review response. Independently document extraction queries, pagination, permissions, time boundaries and reconciliation. Add reviewed, scoped evidence references to the assessment manually; the importer never assigns a status.

## Optional live collection

When the user explicitly authorizes read-only GitHub collection and `gh` is already installed and authenticated, use `--allow-network` instead of `--input`. This invokes GET-only API calls for all paginated pull requests, reviews of PRs merged in the requested period, and deployment records. It does not access secrets, workflow logs, comments or source files. No package installation or authentication is performed by the script.

```bash
python3 <skill-dir>/scripts/github_evidence.py --repo owner/repository --start 2026-08-01 --end 2026-10-31 --allow-network --out github-evidence.json
```

Collection covers repository history and can be expensive for large repositories. Each API request has a 60-second process timeout. Request narrow repository access sufficient for pull-request metadata/reviews and deployment reads. Respect permission failures. Current branch-protection/ruleset snapshots, check runs, deployment statuses, bypass history and external release paths require separately approved collection; this script does not collect them. Never interpret missing permissions as failed controls.

## Required human analysis

Reconcile deployments with the complete production release population, including external CI, direct pushes, infrastructure changes and emergency procedures. Match each released artifact to the reviewed commit. Check review timing, dismissal and author independence. An approval associated with a PR is not automatically an approval of the deployed code. A deployment API object is not proof of a successful release. Current rules are not proof of their historical enforcement. Examine provider settings through the authorized connector when available; managed integrations may not have administration access.

## Primary references

- https://docs.github.com/en/rest/pulls/pulls
- https://docs.github.com/en/rest/pulls/reviews
- https://docs.github.com/en/rest/deployments/deployments
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://cli.github.com/manual/gh_api
