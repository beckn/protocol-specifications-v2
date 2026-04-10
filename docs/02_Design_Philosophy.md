# RFC-002: Beckn Architecture Design Philosophy and Principles

# 1. Document Details

- **Status:** Draft.
- **Authors:** Ravi Prakash.
- **Created:** 2026-03-03.
- **Updated:** 2026-04-07.
- **Version history:** No commits found on `main` for `docs/02_Design_Philosophy.md`.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/02_Design_Philosophy.md).
- **Implementation report:** Not applicable (architecture principles RFC).
- **Stress test report:** Inputs for stress testing strategy are captured in derived principles.
- **Conformance impact:** Informative for architecture decisions, with normative guidance inside Section 5.
- **Security/privacy implications:** Defines security-by-design architecture constraints, including signature and receipt semantics.
- **Replaces / Relates to:** Supersedes the prior non-template version of `02_Design_Philosophy.md`; aligned with `api/v2.0.0/beckn.yaml` and Beckn architecture documentation.
- **Feedback - Issues:** Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-002%22).
- **Feedback - Discussions:** Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-002%22).
- **Feedback - Pull Requests:** Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-002%22).
- **Errata:** To be published.

# 2. Abstract

This RFC defines the architectural philosophy and derived principles that guide Beckn Protocol v2 decisions, aligning transport contracts, asynchronous interaction patterns, catalog-first discovery, and contract-centric modeling with the canonical v2 artifacts and documentation.

# 3. Table of Contents

- [RFC-002: Beckn Architecture Design Philosophy and Principles](#rfc-002-beckn-architecture-design-philosophy-and-principles)
- [1. Document Details](#1-document-details)
- [2. Abstract](#2-abstract)
- [3. Table of Contents](#3-table-of-contents)
- [4. Introduction](#4-introduction)
- [5. Specification](#5-specification)
  - [5.1 Philosophical Baseline](#51-philosophical-baseline)
  - [5.2 Architecture and Actor Topology](#52-architecture-and-actor-topology)
  - [5.3 API Surface and Interaction Model](#53-api-surface-and-interaction-model)
  - [5.4 Conformance Requirements and Alignment Notes](#54-conformance-requirements-and-alignment-notes)
  - [5.5 Security, Migration, and Evolution Notes](#55-security-migration-and-evolution-notes)
  - [5.6 Examples](#56-examples)
- [6. Conclusion](#6-conclusion)
- [7. Acknowledgements](#7-acknowledgements)
- [8. References](#8-references)

# 4. Introduction

Beckn has evolved into a multi-service value-exchange fabric spanning discovery, transaction, fulfillment, post-fulfillment, and infrastructure APIs. Without a formal architectural baseline, changes to API surface, actor roles, transport behavior, and schema semantics can drift across implementations. This RFC provides that baseline so protocol evolution remains coherent and aligned with the canonical v2 artifacts.

The architectural intent is to keep transport behavior explicit, preserve semantic interoperability across domains and regions, and allow new actor roles and value-exchange patterns to emerge without redesigning the core structure. This motivates a catalog-first discovery model, asynchronous business workflows with synchronous acknowledgements, and generalized contract abstractions that remain reusable across use cases.

# 5. Specification

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in Click [here](./00_Keyword_Definitions.md).

## 5.1 Philosophical Baseline

1. **Fabric-enabled design:** The protocol MUST leverage the Universal Value-Exchange Fabric to support addressability, discoverability, trust, non-repudiation, and exchange at scale.
2. **Agent-empowering:** The protocol MUST leverage AI for its evolution _and_ also empower AI Agents to participate in trusted value-exchange transactions via unstructure
3. **Minimalism:** Beckn architecture MUST keep its features as minimal as possible and only use handles and pointers to services offered by Fabric
4. **Future-readiness:** Protocol design MUST accommodate new actors and value-exchange patterns without core structural redesign.
5. **Pragmatism:** Architecture decisions SHOULD prioritize implementability and developer friendliness with current ecosystem tooling.
6. **Optimal ignorance:** Each layer MUST avoid embedding concerns owned by other layers.
7. **Semantic interoperability:** Protocol concepts MUST be interpreted consistently across domains, regions, and implementations.
8. **Reusability via abstraction:** Core concepts MUST remain abstract enough to be reused across diverse domains and regional deployments.
9. **Trust by design:** Mandatory signatures and `CounterSignature` acknowledgements MUST remain baseline transport behavior.

## 5.2 Architecture and Actor Topology

Beckn v2 architecture is defined as a layered stack:

1. Network Architecture
2. API Specification
3. Composable Linked-Data Schema
4. Communication Protocol
5. Workflows

Core roles in v2 include BAP, BPP, Catalog Service (CS), Discovery Service (DS), and Registry.

High-level interaction shape:

```text
BPP -> CP -> DS -> BAP discovery
BAP <-> BPP transaction lifecycle
All actors <-> Registry for trust resolution
```

This topology preserves separation of concerns: infrastructure actors resolve discovery and trust, while transaction participants execute the lifecycle using shared transport and schema rules.

## 5.3 API Surface and Interaction Model

`api/v2.0.0/beckn.yaml` MUST be treated as the canonical v2.0.x interoperability artifact.

The v2.0.0 OpenAPI contract currently defines 30 paths grouped as:

- Discovery
- Transaction
- Fulfillment
- Post-Fulfillment
- Catalog Publishing
- Catalog Subscription
- Catalog Pull
- Master Resource Search

Beckn APIs SHOULD remain action-addressable through named paths per action to preserve implementability and observability. Discovery SHOULD remain catalog-first rather than relying on runtime multicast fan-out. Forward requests SHOULD be acknowledged synchronously, and business outcomes MAY be returned asynchronously through `on_*` callbacks.

The request envelope MUST include `context` and `message`. Implementations MUST enforce `Authorization` signature validation and MUST support standard response families: `Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, and `ServerError`. The transaction model SHOULD remain centered on generalized `Contract` entities and related abstractions for cross-domain compatibility. Schema semantics SHOULD remain composable through JSON-LD-compatible extension containers.

## 5.4 Conformance Requirements and Alignment Notes

Architecture-level protocol changes to envelope, security, or acknowledgement semantics MUST be reviewed as interoperability-impacting changes. Implementations MUST treat `api/v2.0.0/beckn.yaml` as the source contract for v2.0.x endpoint and envelope behavior. Beckn deployments SHOULD preserve asynchronous request and callback semantics for lifecycle actions. Infrastructure capabilities such as publish, subscribe, pull, and search SHOULD be implemented as protocol-visible APIs where applicable.

The following alignment notes apply to v2.0.0:

1. Action aliases, including slash and underscore variants, MAY be supported for compatibility where explicitly defined in `beckn.yaml`.
2. `context.try` behavior is currently operation-documented for selected flows (`update`, `cancel`, `rate`, and `support`) and SHOULD be interpreted as a two-phase preview and commit interaction model.
3. Deployment route prefixes, for example `/beckn/...`, MAY vary by participant runtime, while operation semantics remain governed by the OpenAPI path and action contract.

## 5.5 Security, Migration, and Evolution Notes

This RFC reinforces security-by-design through mandatory request signatures and signed acknowledgements. No new cryptographic primitive is introduced by this document. The main security risk addressed is trust ambiguity caused by inconsistent transport semantics across implementations.

No protocol wire migration is introduced by this RFC. This update is editorial and structural: it aligns architecture philosophy with the standard RFC structure and with existing v2.0.0 behavior.

The following evolution questions remain open and inform future work:

1. Slash and underscore action aliasing may need formal deprecation over a defined release window.
2. `context.try` may need to become explicitly normative in the base `Context` schema semantics.
3. Actor capability profiles for BAP, BPP, CS, and DS may need publication as a separate normative RFC.

## 5.6 Examples

Example layered architecture view:

```text
Network Architecture
  -> API Specification
    -> Composable Linked-Data Schema
      -> Communication Protocol
        -> Workflows
```

Example protocol path grouping from `beckn.yaml`:

```text
Discovery: /discover, /on_discover
Transaction: /select, /on_select, /init, /on_init, /confirm, /on_confirm
Fulfillment: /status, /on_status, /track, /on_track, /update, /on_update, /cancel, /on_cancel
Post-Fulfillment: /rate, /on_rate, /support, /on_support
Catalog Infra: /catalog/publish, /catalog/on_publish, /catalog/subscription, /catalog/pull, /catalog/master/*
```

# 6. Conclusion

This RFC establishes a durable architectural baseline for Beckn Protocol v2 by consolidating the philosophy, topology, interaction model, and conformance expectations into a single structure. It does not introduce wire-level migration; relative to the initial draft, this revision primarily restructures the RFC and aligns its wording with the canonical v2.0.0 architecture artifacts.

# 7. Acknowledgements

This RFC builds on the Beckn v2 OpenAPI contract, Beckn architecture documentation, and the broader Beckn community effort that shaped the protocol's transport, discovery, and trust model.

# 8. References

- Keyword definitions: Click [here](./00_Keyword_Definitions.md)
- Canonical OpenAPI artifact: `api/v2.0.0/beckn.yaml`
- Beckn protocol overview: Click [here](https://docs.beckn.io/introduction-to-beckn/beckn-protocol)
- Universal Value-Exchange Fabric overview: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure)
- Catalog publishing reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/publish-catalogs-using-catalg)
- Trusted networks and registry reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/build-trusted-networks-using-registr)
