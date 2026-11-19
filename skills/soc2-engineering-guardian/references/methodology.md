# Assessment methodology

## Scope and interpretation

Treat the 53 original objectives as engineering aids with supporting, interpretive mappings to common criteria. They are neither the complete Trust Services Criteria nor a universal prescribed checklist. Keep service commitments, system requirements, organization-specific risks and the auditor-agreed boundary visible. Security common criteria include organizational and physical controls that cannot be established from application code.

The framework baseline is the 2017 Trust Services Criteria with revised points of focus from 2022. Criteria IDs are references; objective wording and test suggestions are original CTOside material. The published AICPA criteria remain authoritative. Review content-reuse permissions before adding official criteria text, logos or licensed audit materials.

## Evidence model

An evidence item has `id`, `type`, `ref`, `method`, `reviewer`, `environment`, `collected_on`, and optional `period: {start,end}` and `sha256`. References should point to access-controlled artifacts. Hashes detect changes only when independently compared; the validator checks their format, not the artifact. Do not include credentials in URLs or raw evidence in assessment text.

Design and operation reference independent evidence-ID arrays. A single item may support multiple objectives only when its relevance and scope are explained. A configuration snapshot supports a point-in-time claim; it does not establish earlier enforcement. Evidence dated after the assessment period can summarize historical records when the covered interval and provenance are clear.

`verified` is a reviewer assertion with minimum structural support, not an automated assurance opinion. `failed` means a substantiated gap. `insufficient_evidence` means no supported conclusion, including inaccessible APIs. A scanner lead remains unconfirmed until reviewed. Exceptions and incomplete coverage require a partial or insufficient conclusion. Type 1 mode does not assert period operation.

## Population review

For an operational conclusion, record population source, total and reviewed counts, selection rationale, a completeness reconciliation, exceptions and reviewer. For recurring controls, reconcile scheduled occurrences with actual execution records. For event-based controls, reconcile source systems and alternative event paths. A selected sample need not include every event, but the period and population basis must be supported. The tool does not prescribe sample sizes or judge audit sufficiency.

An evidence interval must describe relevant records across that interval, not merely the dates entered in a form. Merge overlapping inclusive intervals to calculate uncovered dates. Coverage by dates does not establish a complete population, relevance, test quality or effectiveness.

## Remediation and closure

Give each confirmed gap a severity, accountable owner, action and done-when test. Keep evidence collection tasks separate from engineering fixes. Test changes in a synthetic isolated environment. Retain the baseline and historic exceptions; rechecks invalidate assertions rather than silently carrying them forward. Human reviewers decide closure and auditor handoff.

## Sharing and limitations

The PDF/Markdown report, evidence index, risk register and handoff manifest contain references and reviewed summaries, not raw evidence files. The manifest hashes the generated report files. Task exports do not contact trackers. Security-sensitive assessments belong outside public repositories. Redaction covers common email/identifier/token patterns only; manual review is required. Repository file paths and reference URLs can themselves reveal sensitive information.
