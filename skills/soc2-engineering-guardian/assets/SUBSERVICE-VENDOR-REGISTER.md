# Subservice and vendor register (INTERNAL / UNVERIFIED TEMPLATE)

Product: [PRODUCT]
Date: [DATE]
Responsible reviewer: [OWNER]

One row per exact service. A vendor that supplies two services gets two rows.

| Vendor | Exact service | Data processed | Subservice organization? | Method | SOC report on file | Bridge letter | CSOCs relied on and where we test them | Our CUEC responses | Owner | Next review |
|---|---|---|---|---|---|---|---|---|---|---|
| [Enter vendor] | [Enter exact service] | Unknown | Unknown | Not decided | None | None | Not reviewed | Not reviewed | Unassigned | [DATE] |

## Column notes

- **Subservice organization?** Yes when its controls are needed to meet our service commitments; the system description must then address it.
- **Method.** Carve-out or inclusive.
- **SOC report on file.** Type (1 or 2), period covered, auditor opinion, exceptions noted, who reviewed it and when. Write `None` when there is no report.
- **Bridge letter.** A vendor management assertion covering the time since the report period ended. It is not an auditor opinion and does not extend the opinion period. Record the date and signer.
- **CSOCs relied on.** The complementary subservice organization controls we assume the vendor operates, and the evidence we gather ourselves for each (for example, our own access logs).
- **Our CUEC responses.** The vendor's complementary user entity controls we must operate, with the evidence that we do.

## Decision rule

A vendor's SOC 2 badge or marketing page is not evidence. Coverage is: the report must cover the exact service we use, in the environment and region we use, for the period we depend on, with an unmodified opinion, or exceptions we have assessed. Where the report is missing, stale, or covers a different service, record an evidence request and treat the reliance as unverified until a human reviewer closes it.
