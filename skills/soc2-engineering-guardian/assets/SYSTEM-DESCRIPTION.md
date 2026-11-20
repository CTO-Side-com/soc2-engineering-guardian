# System description engineering input (INTERNAL / UNVERIFIED TEMPLATE)

Product: [PRODUCT]
Prepared by: [OWNER]
Date: [DATE]
Assessment period: [START] to [END]

This is engineering input for the people who write the system description. It is not the management description of the system. The AICPA description criteria are authoritative for what that description must contain; read them before drafting. Fill every field from evidence you can point to. Write `Unknown` rather than guessing, and do not paste secrets, customer records or raw logs.

## 1. Services in scope

| Service | What it does for customers | Environments | Owner |
|---|---|---|---|
| [Enter service] | [Unknown] | [production] | [Unassigned] |

## 2. Service commitments and system requirements

| Commitment or requirement | Where it is stated (contract, SLA, public security page) | Engineering control that supports it | Evidence |
|---|---|---|---|
| [Enter commitment] | [Unknown] | [Unknown] | None |

## 3. System components

| Component type | Inventory | Source of the inventory |
|---|---|---|
| Infrastructure (cloud accounts, networks, clusters, databases) | [Unknown] | [Unknown] |
| Software (applications, services, CI/CD, internal tools) | [Unknown] | [Unknown] |
| People (teams with production access or change authority) | [Unknown] | [Unknown] |
| Procedures (deploy, access review, incident response, backup restore) | [Unknown] | [Unknown] |
| Data (categories stored, where, retention, encryption) | [Unknown] | [Unknown] |

## 4. Boundary and exclusions

In scope: [INCLUDED SYSTEMS]

Excluded: [EXCLUSIONS], with the reason for each exclusion.

## 5. Subservice organizations

Record the method for each: carve-out (their controls are excluded and listed as complementary subservice organization controls) or inclusive (their controls are described as part of the system). Details live in [SUBSERVICE-VENDOR-REGISTER.md](SUBSERVICE-VENDOR-REGISTER.md).

| Subservice organization | Service we rely on | Method (carve-out or inclusive) |
|---|---|---|
| [Enter vendor] | [Enter exact service] | [Not decided] |

## 6. Complementary subservice organization controls relied on

| Control we expect the subservice organization to operate | Vendor | Where we test or obtain assurance |
|---|---|---|
| [Enter control] | [Enter vendor] | [Unknown] |

## 7. Complementary user entity controls

Controls customers must operate for our commitments to hold (for example, removing departed users, protecting API keys).

| Customer responsibility | Where we tell customers | 
|---|---|
| [Enter responsibility] | [Unknown] |

## 8. Significant changes during the period

| Date | Change (architecture, vendor, ownership, scope) | Effect on controls |
|---|---|---|
| [DATE] | [None recorded] | [Unknown] |

## 9. Incident summary (redacted)

Summarize security incidents during the period without customer names, personal data, hostnames or credentials. If there were none, state how that was established and by whom.

[None recorded]

## Open questions

[List anything above that you could not support with evidence.]
