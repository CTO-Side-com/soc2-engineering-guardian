# SOC 2 Engineering Guardian
Internal engineering readiness assessment. Not a SOC 2 report, certification, or auditor opinion.

Product: Synthetic SaaS / Demonstration
Environment: synthetic-production
Period: 2026-08-01 to 2026-10-31
Mode: type2-readiness
Framework mapping: AICPA-TSC-2017-POF-2022

## Assessment boundary
Assessor: Synthetic example, not a real assessment
Systems: Synthetic API, Synthetic PostgreSQL database, Synthetic GitHub release workflow
Exclusions: No real customer systems were assessed
Service commitments: Synthetic confidentiality commitment
System requirements: Synthetic authorization and approved deployment requirements
Scope unknowns: Synthetic organizational and runtime evidence has not been supplied.
These original checks support Security readiness. They are not the full criteria, an audit program, or a compliance score.
Verified means reviewer-asserted support for the stated scope. Automated validation cannot prove evidence truth.
Recovery checks support risk mitigation; this pack does not assess the Availability category.
PDF text uses built-in Western fonts; use Markdown for full Unicode content.

## Evidence status counts
Design: failed=2, insufficient_evidence=43, not_applicable=3, partially_verified=2, verified=3
Operation: insufficient_evidence=47, not_applicable=3, partially_verified=2, verified=1

## Status by area
Legend: V verified, P partially verified, F failed, NA not applicable, E insufficient evidence.
| Area | Checks | Design V/P/F/NA/E | Operation V/P/F/NA/E |
| --- | --- | --- | --- |
| Governance | 15 | 0/0/0/0/15 | 0/0/0/0/15 |
| Access | 8 | 1/0/1/0/6 | 0/0/0/0/8 |
| Changes | 8 | 1/1/0/0/6 | 0/1/0/0/7 |
| Data | 6 | 0/1/1/0/4 | 0/0/0/0/6 |
| Monitoring | 7 | 0/0/0/0/7 | 0/1/0/0/6 |
| Recovery | 3 | 1/0/0/0/2 | 1/0/0/0/2 |
| Vendors | 3 | 0/0/0/0/3 | 0/0/0/0/3 |
| AI engineering | 3 | 0/0/0/3/0 | 0/0/0/3/0 |

## Open items by urgency
| Urgency | Confirmed gaps | Evidence requests | Total |
| --- | --- | --- | --- |
| critical | 1 | 7 | 8 |
| high | 2 | 36 | 38 |
| medium | 2 | 46 | 48 |
| low | 1 | 1 | 2 |

## Period coverage
| Check | Operation | Covered | Uncovered | Population total/reviewed/exceptions |
| --- | --- | --- | --- | --- |
| CHG-001 Require independent review of production code changes | partially_verified | 2026-09-01 to 2026-10-31 | 2026-08-01 to 2026-08-31 | 18/18/2 |
| MON-004 Review vulnerabilities and configuration changes | partially_verified | 2026-08-01 to 2026-09-30 | 2026-10-01 to 2026-10-31 | 9/9/1 |
| REC-001 Back up critical data and monitor backup failures | verified | 2026-08-01 to 2026-10-31 | None | 92/92/0 |
| AI-001 Enforce authorization independently of model output | not_applicable | None | 2026-08-01 to 2026-10-31 | n/a/n/a/n/a |
| AI-002 Limit model data egress and cross-user memory | not_applicable | None | 2026-08-01 to 2026-10-31 | n/a/n/a/n/a |
| AI-003 Review AI behavior changes and action auditability | not_applicable | None | 2026-08-01 to 2026-10-31 | n/a/n/a/n/a |

## Confirmed gaps and next actions
IAM-002-design | critical | Protect privileged access with strong authentication | Owner: Synthetic Platform Lead | Require multi-factor authentication for every administrator and privileged service account.
DAT-001-design | high | Protect sensitive traffic with authenticated encryption | Owner: Synthetic Engineering Owner | Enable certificate verification and test certificate rejection.
MON-004-operation | high | Review vulnerabilities and configuration changes | Owner: Synthetic Security Lead | Collect the October review records and add the missing triage record.
CHG-001-operation | medium | Require independent review of production code changes | Owner: Synthetic Release Owner | Collect August release records and resolve the two approval exceptions.
CHG-002-design | medium | Protect release branches and review bypass permissions | Owner: Synthetic Release Owner | Remove the bypass permission from the release branch and record any exception.
DAT-006-design | low | Limit sensitive information in logs and telemetry | Owner: Synthetic Engineering Owner | Redact payload fields on the remaining route and add a logging test.

## Control assessment

### GOV-001 | Assign accountable security and control owners
Supporting criteria: CC1.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace each critical system to an accountable owner.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-002 | Maintain security policies and staff acknowledgment
Supporting criteria: CC1.1, CC2.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review acknowledgments against the staff population.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-003 | Review personnel screening and onboarding evidence
Supporting criteria: CC1.4 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Sample hires without reading sensitive personnel records.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-004 | Train personnel for their security responsibilities
Supporting criteria: CC1.4, CC2.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile completed training with in-scope personnel.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-005 | Review risk assessments and treatment decisions
Supporting criteria: CC3.1, CC3.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace material risks to owners and decisions.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-006 | Evaluate control performance and unresolved deficiencies
Supporting criteria: CC4.1, CC4.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Sample deficiencies through resolution or accepted risk.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-007 | Communicate security commitments and reporting channels
Supporting criteria: CC2.1, CC2.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Compare customer commitments with implemented controls.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-008 | Maintain scoped inventories and system description inputs
Supporting criteria: CC2.1, CC3.4 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile inventory with deployed systems and vendors.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-001 | Authenticate application and administrative users
Supporting criteria: CC6.1 (interpretive mapping)
Design: verified; Operation: insufficient_evidence
Rationale: Synthetic example of scoped authentication test support. No historical operation is asserted.
Evidence: EX-AUTH
Reviewer: Synthetic Reviewer; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Attempt protected operations without a valid identity.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-002 | Protect privileged access with strong authentication
Supporting criteria: CC6.1 (interpretive mapping)
Design: failed; Operation: insufficient_evidence
Rationale: Synthetic example: the administrator console accepts a password alone, with no second factor for privileged accounts.
Evidence: EX-ADMIN
Reviewer: Synthetic Reviewer; Owner: Synthetic Platform Lead
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Require multi-factor authentication for every administrator and privileged service account.
Verification: An administrator sign-in without a second factor is rejected in an isolated test.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-003 | Enforce server-side roles and object permissions
Supporting criteria: CC6.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Attempt cross-role and cross-object actions with synthetic users.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-004 | Isolate tenant data across services and retrieval
Supporting criteria: CC6.1, CC6.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Attempt cross-tenant access using synthetic records.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-005 | Approve provisioning and remove departed users
Supporting criteria: CC6.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile personnel changes with granted and revoked access.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-006 | Review access rights and service identities periodically
Supporting criteria: CC6.2, CC6.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile all privileged identities with reviewed entries.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-007 | Limit and rotate service credentials
Supporting criteria: CC6.1, CC6.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Inspect credential metadata without exposing values.
Population: total=None; reviewed=None; exceptions=None; method=

### IAM-008 | Constrain sessions and invalidate revoked access
Supporting criteria: CC6.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Replay an expired or revoked session.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-001 | Require independent review of production code changes
Supporting criteria: CC8.1 (interpretive mapping)
Design: insufficient_evidence; Operation: partially_verified
Rationale: Synthetic review covers September and October; August is missing and two releases lack sufficient approval evidence.
Evidence: EX-CHANGES
Reviewer: Synthetic Reviewer; Owner: Synthetic Release Owner
Period gaps: [["2026-08-01", "2026-08-31"]]
Next action: Collect August release records and resolve the two approval exceptions.
Verification: Reconcile all production release paths with reviews of the deployed commits.
Population: total=18; reviewed=18; exceptions=2; method=All synthetic releases

### CHG-002 | Protect release branches and review bypass permissions
Supporting criteria: CC8.1 (interpretive mapping)
Design: partially_verified; Operation: insufficient_evidence
Rationale: Synthetic example: the main branch is protected, but one release branch lets administrators bypass required review.
Evidence: EX-BRANCH
Reviewer: Synthetic Reviewer; Owner: Synthetic Release Owner
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Remove the bypass permission from the release branch and record any exception.
Verification: A direct push to the release branch by an administrator is rejected in an isolated test.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-003 | Run required checks before production deployment
Supporting criteria: CC8.1 (interpretive mapping)
Design: verified; Operation: insufficient_evidence
Rationale: Synthetic pipeline configuration requires passing tests before production deployment. No historical operation is asserted.
Evidence: EX-CI
Reviewer: Synthetic Reviewer; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile deployed commits with successful required checks.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-004 | Restrict and trace production deployments
Supporting criteria: CC6.3, CC8.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace releases to authorized actors and immutable commits.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-005 | Control emergency changes and retrospective review
Supporting criteria: CC8.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile exceptions with production release history.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-006 | Test database migrations and recovery paths
Supporting criteria: CC8.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Apply representative migrations to an isolated synthetic database.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-007 | Pin and protect build inputs and dependencies
Supporting criteria: CC8.1, CC6.8 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace a deployed artifact to reviewed source and dependencies.
Population: total=None; reviewed=None; exceptions=None; method=

### CHG-008 | Separate production credentials and development access
Supporting criteria: CC6.1, CC8.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Check development identities cannot access production secrets.
Population: total=None; reviewed=None; exceptions=None; method=

### DAT-001 | Protect sensitive traffic with authenticated encryption
Supporting criteria: CC6.7 (interpretive mapping)
Design: failed; Operation: insufficient_evidence
Rationale: Synthetic example: an API client disables certificate verification.
Evidence: EX-TLS
Reviewer: Synthetic Reviewer; Owner: Synthetic Engineering Owner
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Enable certificate verification and test certificate rejection.
Verification: A request using an untrusted certificate fails in an isolated test.
Population: total=None; reviewed=None; exceptions=None; method=

### DAT-002 | Protect stored information and encryption keys
Supporting criteria: CC6.1, CC6.7 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile sensitive stores with encryption and key controls.
Population: total=None; reviewed=None; exceptions=None; method=

### DAT-003 | Prevent secrets from entering source and build output
Supporting criteria: CC6.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Run an approved scanner without copying detected secrets.
Population: total=None; reviewed=None; exceptions=None; method=

### DAT-004 | Restrict public storage and network exposure
Supporting criteria: CC6.6 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review exposure against approved service requirements.
Population: total=None; reviewed=None; exceptions=None; method=

### DAT-005 | Control retention, disposal and backup deletion
Supporting criteria: CC6.5 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace a synthetic deletion across stores and backup policy.
Population: total=None; reviewed=None; exceptions=None; method=

### DAT-006 | Limit sensitive information in logs and telemetry
Supporting criteria: CC6.7 (interpretive mapping)
Design: partially_verified; Operation: insufficient_evidence
Rationale: Synthetic example: most routes redact personal fields, but one request logger records full payloads.
Evidence: EX-LOGS
Reviewer: Synthetic Reviewer; Owner: Synthetic Engineering Owner
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Redact payload fields on the remaining route and add a logging test.
Verification: A logged request on that route shows no personal field values in an isolated test.
Population: total=None; reviewed=None; exceptions=None; method=

### MON-001 | Record security events with usable identity and context
Supporting criteria: CC7.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Verify actor, target, outcome and timestamp on critical events.
Population: total=None; reviewed=None; exceptions=None; method=

### MON-002 | Protect audit logs from unauthorized alteration
Supporting criteria: CC6.1, CC7.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Attempt unauthorized modification in a safe test environment.
Population: total=None; reviewed=None; exceptions=None; method=

### MON-003 | Test security alerts and escalation delivery
Supporting criteria: CC7.2, CC7.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trigger a synthetic alert and confirm assigned response.
Population: total=None; reviewed=None; exceptions=None; method=

### MON-004 | Review vulnerabilities and configuration changes
Supporting criteria: CC7.1 (interpretive mapping)
Design: insufficient_evidence; Operation: partially_verified
Rationale: Synthetic weekly vulnerability reviews cover August and September; October is missing and one review has no triage record.
Evidence: EX-VULN
Reviewer: Synthetic Reviewer; Owner: Synthetic Security Lead
Period gaps: [["2026-10-01", "2026-10-31"]]
Next action: Collect the October review records and add the missing triage record.
Verification: Reconcile every weekly review in the period against its triage record.
Population: total=9; reviewed=9; exceptions=1; method=All scheduled reviews

### MON-005 | Track vulnerability remediation and accepted exceptions
Supporting criteria: CC7.1, CC7.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Sample findings through closure or approved exception.
Population: total=None; reviewed=None; exceptions=None; method=

### MON-006 | Evaluate incidents and exercise response procedures
Supporting criteria: CC7.3, CC7.4 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace a simulated event through classification and response.
Population: total=None; reviewed=None; exceptions=None; method=

### MON-007 | Document recovery and lessons after incidents
Supporting criteria: CC7.5 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Verify recovery evidence and tracked improvements.
Population: total=None; reviewed=None; exceptions=None; method=

### REC-001 | Back up critical data and monitor backup failures
Supporting criteria: CC9.1 (interpretive mapping)
Design: verified; Operation: verified
Rationale: Synthetic backup settings and a run log covering the whole period; every daily run was reconciled and no failure went unalerted.
Evidence: EX-BACKUP-CFG, EX-BACKUP-RUNS
Reviewer: Synthetic Reviewer; Owner: Unassigned
Period gaps: []
Next action: Collect and review scoped evidence.
Verification: Reconcile every daily backup run and failure alert across the period.
Population: total=92; reviewed=92; exceptions=0; method=All daily runs

### REC-002 | Exercise restores in an isolated environment
Supporting criteria: CC9.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Restore synthetic data and verify application usability.
Population: total=None; reviewed=None; exceptions=None; method=

### REC-003 | Define recovery dependencies and continuity responsibilities
Supporting criteria: CC9.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Walk through loss of a critical provider or operator.
Population: total=None; reviewed=None; exceptions=None; method=

### VEN-001 | Inventory critical vendors and assess relevant risks
Supporting criteria: CC9.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Reconcile deployed integrations with reviewed vendors.
Population: total=None; reviewed=None; exceptions=None; method=

### VEN-002 | Review vendor commitments and shared responsibilities
Supporting criteria: CC9.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Identify responsibilities that remain with the SaaS operator.
Population: total=None; reviewed=None; exceptions=None; method=

### VEN-003 | Reassess vendor changes and termination procedures
Supporting criteria: CC9.2, CC3.4 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace a vendor change to a documented risk decision.
Population: total=None; reviewed=None; exceptions=None; method=

### AI-001 | Enforce authorization independently of model output
Supporting criteria: CC6.1, CC6.3 (interpretive mapping)
Design: not_applicable; Operation: not_applicable
Rationale: Synthetic product has no AI features; scope approved by the Synthetic Security Lead.
Evidence: None
Reviewer: Synthetic Reviewer; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Inject synthetic instructions requesting an unauthorized action.
Population: total=None; reviewed=None; exceptions=None; method=

### AI-002 | Limit model data egress and cross-user memory
Supporting criteria: CC6.3, CC6.7 (interpretive mapping)
Design: not_applicable; Operation: not_applicable
Rationale: Synthetic product has no AI features; scope approved by the Synthetic Security Lead.
Evidence: None
Reviewer: Synthetic Reviewer; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Attempt synthetic exfiltration and cross-user retrieval.
Population: total=None; reviewed=None; exceptions=None; method=

### AI-003 | Review AI behavior changes and action auditability
Supporting criteria: CC8.1, CC7.2 (interpretive mapping)
Design: not_applicable; Operation: not_applicable
Rationale: Synthetic product has no AI features; scope approved by the Synthetic Security Lead.
Evidence: None
Reviewer: Synthetic Reviewer; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Trace a released AI configuration to review and evaluations.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-009 | Review independent oversight of security decisions
Supporting criteria: CC1.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-010 | Evaluate accountability for assigned control responsibilities
Supporting criteria: CC1.5 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-011 | Assess fraud and deliberate control circumvention risks
Supporting criteria: CC3.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-012 | Select controls in response to assessed risks
Supporting criteria: CC5.1 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-013 | Review technology control responsibilities and dependencies
Supporting criteria: CC5.2 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-014 | Implement approved control procedures and review execution
Supporting criteria: CC5.3 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

### GOV-015 | Review physical access responsibilities and provider evidence
Supporting criteria: CC6.4 (interpretive mapping)
Design: insufficient_evidence; Operation: insufficient_evidence
Rationale: No reviewer conclusion recorded.
Evidence: None
Reviewer: Unassigned; Owner: Unassigned
Period gaps: [["2026-08-01", "2026-10-31"]]
Next action: Collect and review scoped evidence.
Verification: Review scoped records with the responsible human owner; repository contents alone are insufficient.
Population: total=None; reviewed=None; exceptions=None; method=

## Evidence index
EX-TLS | code | synthetic/api/client.py:12 | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic example representing a traced disabled TLS setting
EX-AUTH | test | synthetic/tests/test_auth.py:1 | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic passing authentication test record; not an actual test run
EX-CHANGES | operational | synthetic/change-review-register.json | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic release review with two exceptions
EX-ADMIN | configuration | synthetic/admin-console/auth-settings.json | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic export of the administrator sign-in settings showing a password-only policy
EX-CI | configuration | synthetic/ci/required-checks.yml | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic pipeline configuration requiring tests before production deployment
EX-BRANCH | configuration | synthetic/repo/branch-protection.json | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic branch protection export; one release branch allows administrator bypass
EX-LOGS | code | synthetic/api/logging.py:48 | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic example of a request logger that records full payloads on one route
EX-BACKUP-CFG | configuration | synthetic/ops/backup-policy.json | collected 2026-11-01 | reviewer Synthetic Reviewer | method Synthetic backup schedule, retention and failure alert settings
EX-BACKUP-RUNS | operational | synthetic/ops/backup-run-log.json | collected 2026-11-05 | reviewer Synthetic Reviewer | method Synthetic daily backup run log with alert reconciliation
EX-VULN | operational | synthetic/security/vulnerability-reviews.json | collected 2026-11-03 | reviewer Synthetic Reviewer | method Synthetic weekly vulnerability review records for August and September
