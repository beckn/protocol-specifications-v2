# Resolving Disputes

## Document Details
- **ID:** NFH-014
- **Status:** Draft
- **Authors:**
  - [Ravi Prakash](https://github.com/ravi-prakash-v), [Networks for Humanity](https://networksforhumanity.org)
- **Created:** 2026-06-03
- **Updated:** 2026-06-03
- **Version history:** Link to commit history of this document on GitHub
- **Latest editor's draft:** This document
- **Implementation report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Stress test report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Conformance impact:** Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main.
- **Security/privacy implications:** To be documented. Dispute records may carry sensitive grievance details and evidence; handling and retention implications will be classified before this RFC advances to Candidate.
- **Replaces / Relates to:** Relates to [NFH-006 — Beckn API Endpoints](./API.md) and [NFH-015 — Invoicing and Settlements](./Invoicing_and_Settlements.md).
- **Feedback:**
  - Issues: Click [here](#)  (link to discussions page with this RFC's ID as label)
  - Discussions: Click [here](#)  (link to discussions page with this RFC's ID as label)
  - Pull Requests: Click [here](#)  (link to discussions page with this RFC's ID as label)
- **Errata:** To be published.

## Abstract

> A short abstract about this RFC describing the context, problem, and solution. Should be less than 50 words.

This document defines how a dispute may be raised against a confirmed contract or its associated entities, and how the counterparty opens, tracks, and resolves a dispute case. It specifies the `/dispute` and `/on_dispute` endpoints and the `Dispute` data model.

## Table of Contents

- [Resolving Disputes](#resolving-disputes)
  - [Document Details](#document-details)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Context](#context)
  - [Specification](#specification)
    - [Definitions](#definitions)
    - [Normative Requirements](#normative-requirements)
      - [Dispute lifecycle](#dispute-lifecycle)
      - [Endpoints](#endpoints)
      - [Data model](#data-model)
    - [Conformance Requirements](#conformance-requirements)
    - [Cross-cutting considerations](#cross-cutting-considerations)
    - [Migration Notes](#migration-notes)
    - [Examples](#examples)
      - [Example 1](#example-1)
  - [Conclusion](#conclusion)
    - [Open Questions](#open-questions)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)

## Context

> Provide a concise introduction that combines context, problem, and motivation in one place.

Value exchange does not always complete cleanly. A consumer may contest a charge, a provider may contest a chargeback, and either party may contest the quality or completion of a fulfillment. Beckn v2 today has no first-class, interoperable mechanism for raising and resolving such grievances against a contract. This RFC introduces a dispute lifecycle so that either network participant — the CN or the PN — can raise a dispute and the counterparty can open, track, and resolve a case in an interoperable way.

> **This document is a DRAFT STUB.** The endpoints and schema it describes are introduced as stubs in `api/v2.0.0/beckn.yaml` and are subject to change before release. Section bodies below are scaffolding to be completed.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described [here](./Keyword_Definitions.md). These definitions aim to ensure that the terms are understood precisely and consistently to avoid confusion in the interpretation of standards, specifications, and protocols.

### Definitions

- **Normative:** Requirements that define conformance and interoperability behavior.
- **Informative:** Explanatory guidance that does not by itself define conformance.
- **Dispute:** A record representing a grievance raised by a network participant against a confirmed contract or one of its associated entities.
- **Initiating NP:** The network participant (CN or PN) that raises the dispute by calling `/dispute`.
- **Receiving NP:** The counterparty that opens or links the dispute case and responds via `/on_dispute`.
- **Conformance impact:** Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main.
- **Migration notes:** Operational guidance required to adopt the change safely.
- **Errata:** Post-publication corrections and clarifications.

### Normative Requirements

> Describe the protocol, data model, state transition, API, or behavioral requirements introduced by this RFC.

#### Dispute lifecycle

> Define the state machine for a dispute case (OPEN → UNDER_REVIEW → RESOLVED | REJECTED), the permitted transitions, and which NP may trigger each transition. _To be completed._

#### Endpoints

> `/dispute` (POST) — either NP raises a dispute against a confirmed contract or associated entity by submitting a `DisputeAction` carrying a `Dispute`. `/on_dispute` (POST) — the receiving NP returns the opened or linked dispute case via an `OnDisputeAction`. Both are defined in the canonical OpenAPI contract; see [NFH-006](./API.md). _Normative request/response and correlation rules to be completed._

> **Endpoints are not actor-exclusive.** Since either NP may raise a dispute, **both nodes MUST implement `dispute`/`on_dispute`** (and their `on_*` callbacks). This is not specific to disputes: endpoints are not exclusive to a particular actor anywhere in the protocol — including the contracting lifecycle and [invoicing](./Invoicing_and_Settlements.md) — so both the CN and the PN MUST implement the complete set of action and callback endpoints. See [NFH-006](./API.md).

#### Data model

> Define the `Dispute` schema fields (`id`, `contractId`, `descriptor`, `status`, `disputeAttributes`), their cardinality, and validation rules. _To be completed._

### Conformance Requirements

> Enumerate the machine-verifiable conformance requirements introduced by this RFC. Each requirement should be testable.

| ID | Requirement | Level |
|---|---|---|
| CON-014-01 | A `/dispute` request MUST carry a `DisputeAction` with a `Dispute` referencing a confirmed contract. | MUST |
| CON-014-02 | The receiving NP SHOULD respond to a `/dispute` with an `/on_dispute` callback carrying the opened or linked case. | SHOULD |

### Cross-cutting considerations

_Describe the security and privacy implications of this RFC._ Dispute records may carry sensitive grievance details and supporting evidence; access control, retention, and redaction requirements are to be documented before this RFC advances to Candidate.

### Migration Notes

> Describe the migration impact. The `/dispute` and `/on_dispute` endpoints are additive; existing implementations are unaffected until they adopt dispute handling. _To be completed._

### Examples

> Provide at least one concrete runtime example.

#### Example 1

```json
{
}
```

## Conclusion

> Summarize the intended outcome of this RFC, the expected implementation effect, and the criteria for advancing the proposal through review and adoption. _To be completed._

### Open Questions

_List any unresolved issues or design choices that require further discussion before this RFC can move to Candidate status._

1. Should dispute resolution outcomes be able to trigger a corrective settlement via a new or superseding `/invoice` (see [NFH-015](./Invoicing_and_Settlements.md))?
2. What evidence-attachment mechanism should the `Dispute` schema support?
3. Is a neutral third party (e.g. a fabric-level arbiter) ever a participant in the dispute exchange?

## Acknowledgements

> Acknowledge contributors, reviewers, working groups, and implementers whose feedback informed this RFC.

## References
- **Governance:** Click [here](../GOVERNANCE.md).
- **Keyword definitions:** Click [here](./Keyword_Definitions.md).
- **Beckn API Endpoints:** [NFH-006](./API.md).
- **Invoicing and Settlements:** [NFH-015](./Invoicing_and_Settlements.md).
- **Additional references:** _Add any external standards, prior art, or related RFCs here._
