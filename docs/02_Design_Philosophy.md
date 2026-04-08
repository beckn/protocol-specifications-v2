# RFC-002: Beckn Architecture Design Philosophy and Principles
## CWG Working Draft - 2026-04-07

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-03 | Initial architecture philosophy draft |
| Draft-02 | 2026-04-07 | Restructured to RFC template; aligned with v2.0.0 `beckn.yaml` and docs.beckn.io |

## 1.2 Latest editor's draft
- ./02_Design_Philosophy.md

## 1.3 Implementation report
- Not applicable (architecture principles RFC).

## 1.4 Stress Test Report
- Inputs for stress testing strategy are captured in derived principles.

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Ravi Prakash

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-002%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-002%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-002%22

## 1.8 Errata
- To be published.

<!-- TOC START -->
## Table of Contents

- [RFC-002: Beckn Architecture Design Philosophy and Principles](#rfc-002-beckn-architecture-design-philosophy-and-principles)
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
  - [Table of Contents](#table-of-contents)
- [2. Context](#2-context)
  - [Abstract](#abstract)
  - [1. Context](#1-context)
  - [2. Problem](#2-problem)
  - [3. Motivation](#3-motivation)
  - [4. Design Principles](#4-design-principles)
  - [5. Specification (Normative)](#5-specification-normative)
    - [5.1 Philosophical Baseline](#51-philosophical-baseline)
    - [5.2 Architectural Principles Derived from Philosophy](#52-architectural-principles-derived-from-philosophy)
    - [5.3 Architecture and Actor Topology](#53-architecture-and-actor-topology)
    - [5.4 API Surface and Interaction Model](#54-api-surface-and-interaction-model)
    - [5.5 Alignment Notes for v2.0.0](#55-alignment-notes-for-v200)
  - [6. Examples](#6-examples)
    - [Example 1 - Layered Architecture View](#example-1---layered-architecture-view)
    - [Example 2 - Protocol Path Grouping from `beckn.yaml`](#example-2---protocol-path-grouping-from-becknyaml)
  - [7. Conformance Requirements](#7-conformance-requirements)
  - [8. Security Considerations](#8-security-considerations)
  - [9. Migration Notes](#9-migration-notes)
  - [10. Open Questions](#10-open-questions)
  - [11. References](#11-references)
  - [12. Changelog](#12-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):** Ravi Prakash  
**Created:** 2026-03-03  
**Updated:** 2026-04-07  
**Conformance impact:** Informative (normative guidance for architecture decisions)  
**Security/privacy implications:** Defines security-by-design architecture constraints, including signature and receipt semantics.  
**Replaces / Relates to:** Supersedes prior non-template version of `02_Design_Philosophy.md`; aligned with `api/v2.0.0/beckn.yaml` and `docs.beckn.io` architecture pages.

---

## Abstract

This RFC defines the architectural philosophy and derived principles that guide Beckn Protocol v2 decisions. It establishes how minimal transport contracts, async interaction patterns, catalog-first discovery, and contract-centric domain modeling work together as one coherent architecture. It aligns the philosophy with the current OpenAPI surface in `api/v2.0.0/beckn.yaml` and Beckn Fabric positioning on `docs.beckn.io`. This RFC is the reference baseline for evaluating future architecture changes.

---

## 1. Context

Beckn has evolved from a smaller transaction interface into a multi-service value exchange fabric that now includes discovery, transaction, fulfillment, post-fulfillment, and catalog infrastructure APIs. Simultaneously, documentation and implementation narratives have expanded across protocol repositories and `docs.beckn.io`. A stable architecture philosophy is needed so future API, schema, and infrastructure changes remain coherent and do not drift into ad hoc design.

---

## 2. Problem

Without a formal, RFC-structured architectural baseline, changes to API surface, actor responsibilities, and schema semantics risk becoming locally optimal but globally inconsistent, leading to interoperability degradation across Beckn participants and infrastructure services.

---

## 3. Motivation

This RFC provides a durable decision framework for protocol evolution. It reduces ambiguity across working groups, creates a shared interpretation of v2.0 architecture, and improves consistency between implementation artifacts (`beckn.yaml`) and explanatory documentation (`docs.beckn.io`).

---

## 4. Design Principles

- **Semantic Interoperability:** The protocol design MUST ensure that every concept defined in it MUST be interpreted in the same way across the globe
- **Fabric-Enabled:** The protocol MUST extensively leverage the ***[Universal Value-Exchange Fabric](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure)*** containing essential building blocks for ***addresability***, ***discoverability***, ***trust***, ***non-repudiation***, and other essential factors to create *value-exchange at scale*
- **Reusability via Abstraction:** All concepts in the protocol MUST be designed to be abstract enough to be reusable across the maximum number of use cases across domains and regions
- **Optimal Ignorance:** Every layer defined the protocol must have as little awareness of other layers to allow smooth evolution 
- **Security by design:** Mandatory signatures and `CounterSignature` acknowledgements are baseline transport behavior.

---

## 5. Specification (Normative)

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in [00_Keyword_Definitions.md](./00_Keyword_Definitions.md).

### 5.1 Philosophical Baseline

1. **Minimalism:** Beckn architecture MUST keep transport behavior explicit and uniform across actions.
2. **Future-readiness:** Protocol design MUST accommodate new actors and value-exchange patterns without core structural redesign.
3. **Pragmatism:** Architecture decisions SHOULD prioritize implementability with current ecosystem tooling.
4. **Optimal ignorance:** Each layer MUST avoid embedding concerns owned by other layers.

### 5.2 Architectural Principles Derived from Philosophy

1. `api/v2.0.0/beckn.yaml` MUST be treated as the canonical v2.0.x interoperability artifact.
2. Beckn APIs SHOULD remain action-addressable (named paths per action) to preserve implementability and observability.
3. Discovery SHOULD remain catalog-first (indexed) rather than relying on runtime multicast fan-out.
4. Forward requests SHOULD be acknowledged synchronously and business outcomes MAY be returned asynchronously via `on_*` callbacks.
5. Transport security MUST require request signatures and MUST support signed acknowledgements (`CounterSignature`).
6. The transaction model SHOULD remain centered on generalized `Contract` entities and related abstractions for cross-domain compatibility.
7. Schema semantics SHOULD remain composable through JSON-LD-compatible extension containers.

### 5.3 Architecture and Actor Topology

Beckn v2 architecture is defined as a layered stack:

1. Network Architecture
2. API Specification
3. Composable Linked-Data Schema
4. Communication Protocol
5. Workflows

Core roles in v2 include BAP, BPP, Catalog Service (CS), Discovery Service (DS), and Registry.

High-level interaction shape:

```text
BPP -> CS -> DS -> BAP discovery
BAP <-> BPP transaction lifecycle
All actors <-> Registry for trust resolution
```

### 5.4 API Surface and Interaction Model

The v2.0.0 OpenAPI contract currently defines 30 paths grouped as:

- Discovery
- Transaction
- Fulfillment
- Post-Fulfillment
- Catalog Publishing
- Catalog Subscription
- Catalog Pull
- Master Resource Search

The request envelope MUST include `context` and `message`. Implementations MUST enforce `Authorization` signature validation and MUST support standard response families: `Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, `ServerError`.

### 5.5 Alignment Notes for v2.0.0

1. Action aliases (for example slash and underscore variants) MAY be supported for compatibility where explicitly defined in `beckn.yaml`.
2. `context.try` behavior is currently operation-documented for selected flows (`update`, `cancel`, `rate`, `support`) and SHOULD be interpreted as a two-phase preview/commit interaction model.
3. Deployment route prefixes (for example `/beckn/...`) MAY vary by participant runtime, while operation semantics remain governed by the OpenAPI path/action contract.

---

## 6. Examples

### Example 1 - Layered Architecture View

```text
Network Architecture
  -> API Specification
    -> Composable Linked-Data Schema
      -> Communication Protocol
        -> Workflows
```

### Example 2 - Protocol Path Grouping from `beckn.yaml`

```text
Discovery: /discover, /on_discover
Transaction: /select, /on_select, /init, /on_init, /confirm, /on_confirm
Fulfillment: /status, /on_status, /track, /on_track, /update, /on_update, /cancel, /on_cancel
Post-Fulfillment: /rate, /on_rate, /support, /on_support
Catalog Infra: /catalog/publish, /catalog/on_publish, /catalog/subscription, /catalog/pull, /catalog/master/*
```

---

## 7. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-002-01 | Architecture-level protocol changes to envelope/security/ACK semantics MUST be reviewed as interoperability-impacting changes. | MUST |
| CON-002-02 | Implementations MUST treat `api/v2.0.0/beckn.yaml` as the source contract for v2.0.x endpoint and envelope behavior. | MUST |
| CON-002-03 | Beckn deployments SHOULD preserve async-first request/callback semantics for lifecycle actions. | SHOULD |
| CON-002-04 | Infrastructure capabilities (publish/subscribe/pull/search) SHOULD be implemented as protocol-visible APIs where applicable. | SHOULD |

---

## 8. Security Considerations

This RFC reinforces security-by-design through mandatory request signatures and signed acknowledgements. No new cryptographic primitive is introduced by this document. The main security risk addressed is trust ambiguity caused by inconsistent transport semantics across implementations.

---

## 9. Migration Notes

No protocol wire migration is introduced by this RFC. This update is editorial-structural: it moves the architecture philosophy into the standard RFC template and aligns wording with existing v2.0.0 behavior.

---

## 10. Open Questions

1. Should slash/underscore action aliasing be formally deprecated over a defined release window?
2. Should `context.try` be made explicitly normative in base `Context` schema semantics?
3. Should actor capability profiles (BAP/BPP/CS/DS) be published as a separate normative RFC?

---

## 11. References

- [00_Keyword_Definitions.md](./00_Keyword_Definitions.md)
- `api/v2.0.0/beckn.yaml`
- https://docs.beckn.io/introduction-to-beckn/beckn-protocol
- https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure
- https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/publish-catalogs-using-catalg
- https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/build-trusted-networks-using-registr

---

## 12. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2026-03-03 | Ravi Prakash | Initial draft |
| Draft-02 | 2026-04-07 | Kilo | Reworked into RFC template structure and aligned to v2.0.0 architecture artifacts |
