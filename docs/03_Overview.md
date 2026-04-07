# RFC-003: Beckn Protocol Overview
## CWG Working Draft - 2026-04-07

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-04-07 | Initial overview migrated to RFC template |

## 1.2 Latest editor's draft
- ./03_Overview.md

## 1.3 Implementation report
- Not applicable (overview RFC).

## 1.4 Stress Test Report
- Not applicable (overview RFC).

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Beckn Protocol contributors.

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-003%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-003%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-003%22

## 1.8 Errata
- To be published.

<!-- TOC START -->
## Table of Contents

  - [CWG Working Draft - 2026-04-07](#cwg-working-draft---2026-04-07)
- [1. Document Details](#1-document-details)
  - [1.1 Version History](#11-version-history)
  - [1.2 Latest editor's draft](#12-latest-editors-draft)
  - [1.3 Implementation report](#13-implementation-report)
  - [1.4 Stress Test Report](#14-stress-test-report)
  - [1.5 Editors](#15-editors)
  - [1.6 Authors](#16-authors)
  - [1.7 Feedback](#17-feedback)
    - [1.7.1 Issues](#171-issues)
    - [1.7.2 Discussions](#172-discussions)
    - [1.7.3 Pull Requests](#173-pull-requests)
  - [1.8 Errata](#18-errata)
- [2. Context](#2-context)
  - [Abstract](#abstract)
  - [1. Context](#1-context)
  - [2. Problem](#2-problem)
  - [3. Motivation](#3-motivation)
  - [4. Design Principles](#4-design-principles)
  - [5. Specification (Normative)](#5-specification-normative)
    - [5.1 Protocol Positioning](#51-protocol-positioning)
    - [5.2 Layered Stack](#52-layered-stack)
    - [5.3 Core Actor Model](#53-core-actor-model)
    - [5.4 API Model in This Repository](#54-api-model-in-this-repository)
    - [5.5 Action Groups in v2.0.0](#55-action-groups-in-v200)
    - [5.6 Transport Guarantees](#56-transport-guarantees)
    - [5.7 Scope of Use](#57-scope-of-use)
  - [6. Examples](#6-examples)
    - [Example 1 - Layered Stack View](#example-1---layered-stack-view)
    - [Example 2 - Action Group Snapshot](#example-2---action-group-snapshot)
  - [7. Conformance Requirements](#7-conformance-requirements)
  - [8. Security Considerations](#8-security-considerations)
  - [9. Migration Notes](#9-migration-notes)
  - [10. Open Questions](#10-open-questions)
  - [11. References](#11-references)
  - [12. Changelog](#12-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):** Beckn Protocol contributors  
**Created:** 2026-04-07  
**Updated:** 2026-04-07  
**Conformance impact:** Informative  
**Security/privacy implications:** Summarizes baseline transport trust requirements.  
**Replaces / Relates to:** Replaces `03_OVERVIEW.md` with RFC-template-aligned structure.

---

## Abstract

This RFC provides a concise overview of Beckn v2.0.0 architecture and protocol surface. It summarizes the layered stack, actor model, action groups, and transport guarantees implemented in `api/v2.0.0/beckn.yaml`. The document is informative and acts as an entry point for readers before detailed RFCs.

---

## 1. Context

Beckn v2.0.0 is used as an interoperable value-exchange protocol across multiple sectors. The protocol is peer-to-peer in design but operates at internet scale through a supporting fabric that provides discoverability, trust, and policy-aware coordination. This document captures the common mental model used across protocol and infrastructure documents.

---

## 2. Problem

Without a canonical overview aligned with the current OpenAPI profile, implementers and reviewers can misinterpret actor roles, action coverage, and transport guarantees, which leads to inconsistent implementations.

---

## 3. Motivation

This RFC provides a stable orientation document for contributors, implementers, and auditors. It links high-level architecture to concrete protocol artifacts and reduces ambiguity before readers move into detailed normative RFCs.

---

## 4. Design Principles

- **Interoperability-first:** Overview statements map to the authoritative v2.0.0 API contract.
- **Abstraction over specificity:** Domain-agnostic framing is used where possible.
- **Optimal ignorance:** Actor, transport, and schema concerns are separated.
- **Security by design:** Signature-based trust is treated as foundational.
- **Reusability before novelty:** Existing Beckn action lifecycle remains the organizing frame.

---

## 5. Specification (Normative)

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in [00_Keyword_Definitions.md](./00_Keyword_Definitions.md).

### 5.1 Protocol Positioning

Beckn v2.0.0 is an open protocol for exchanging value across discovery, contracting, fulfillment, and post-fulfillment lifecycles. Implementations MAY add sector-specific semantics through schema composition while preserving transport interoperability.

### 5.2 Layered Stack

The protocol stack is defined bottom-to-top as:

1. Network Interface
2. API Specification
3. Composable Linked-Data Schema
4. Communication Protocol
5. Workflows

### 5.3 Core Actor Model

A minimal Beckn network includes:

- BAP (demand-side applications)
- BPP (supply-side applications)
- PS (catalog publishing)
- DS (catalog discovery)
- Registry (identity, endpoint, and key discovery)

### 5.4 API Model in This Repository

The authoritative API profile for v2.0.0 is defined in `api/v2.0.0/beckn.yaml`. The profile is action-specific and endpoint-explicit.

### 5.5 Action Groups in v2.0.0

- Discovery: `/discover`, `/on_discover`
- Contracting: `/select`, `/on_select`, `/init`, `/on_init`, `/confirm`, `/on_confirm`
- Fulfillment: `/status`, `/on_status`, `/track`, `/on_track`, `/update`, `/on_update`, `/cancel`, `/on_cancel`
- Post-fulfillment: `/rate`, `/on_rate`, `/support`, `/on_support`
- Catalog publishing: `/catalog/publish`, `/catalog/on_publish`
- Catalog extension APIs:
  - `/catalog/subscription`, `/catalog/subscriptions`, `/catalog/subscription/{subscriptionId}`
  - `/catalog/pull`, `/catalog/pull/result/{requestId}/{filename}`
  - `/catalog/master/search`, `/catalog/master/schemaTypes`, `/catalog/master/{masterItemId}`

### 5.6 Transport Guarantees

- Every request MUST be signed in `Authorization`.
- `Ack` MUST include `CounterSignature`.
- `Context` MUST carry routing identity and action metadata.
- `message` MUST carry business payload.
- Error responses SHOULD capture technical and business error details.
- Asynchronous callbacks MAY be used across the lifecycle.

### 5.7 Scope of Use

Beckn is designed for interoperable value exchange across sectors including retail, mobility, logistics, energy, healthcare, skilling, financial services, and hiring.

---

## 6. Examples

### Example 1 - Layered Stack View

```text
Network Interface
  -> API Specification
    -> Composable Linked-Data Schema
      -> Communication Protocol
        -> Workflows
```

### Example 2 - Action Group Snapshot

```text
Discovery: /discover, /on_discover
Contracting: /select, /on_select, /init, /on_init, /confirm, /on_confirm
Fulfillment: /status, /on_status, /track, /on_track, /update, /on_update, /cancel, /on_cancel
Post-fulfillment: /rate, /on_rate, /support, /on_support
```

---

## 7. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-003-01 | Implementers MUST treat `api/v2.0.0/beckn.yaml` as the authoritative v2.0.0 API profile. | MUST |
| CON-003-02 | Implementations MUST support request signatures and `Ack` counter-signatures. | MUST |
| CON-003-03 | Implementations SHOULD preserve lifecycle grouping semantics when mapping capabilities. | SHOULD |

---

## 8. Security Considerations

This overview introduces no new security mechanism. It summarizes baseline security posture: signed requests, signed acknowledgements, and identity/key discovery through registry infrastructure.

---

## 9. Migration Notes

No protocol-level migration is introduced. This change renames and reformats the overview document to align with the RFC template.

---

## 10. Open Questions

1. Should this overview include role-specific conformance matrices in a future revision?
2. Should naming be aligned from PS to CS in this document to mirror newer docs nomenclature?

---

## 11. References

- [00_Keyword_Definitions.md](./00_Keyword_Definitions.md)
- `api/v2.0.0/beckn.yaml`
- [02_Design_Philosophy.md](./02_Design_Philosophy.md)
- https://docs.beckn.io/introduction-to-beckn/beckn-protocol

---

## 12. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2026-04-07 | Kilo | Renamed and restructured overview into RFC template |
