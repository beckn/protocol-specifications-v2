# Specification: Architecture, Design Philosophy and Principles
> Request for Comments

## Document Details

- **ID:** NFH-001
- **Status:** Draft.
- **Authors:**
  - [Ravi Prakash](https://github.com/ravi-prakash-v), [Networks for Humanity](https://networksforhumanity.org)
- **Created:** 2026-05-11
- **Updated:** 2026-05-19
- **Version history:** Draft-01 (2026-05-11): Initial publication. Draft-02 (2026-05-19): Simplified to overview, design principles, and v1→v2 delta; network topology and conformance detail migrated to NFH-003 and NFH-009.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Introduction.md).
- **Implementation report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Stress test report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Conformance impact:** Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main.
- **Security/privacy implications:** Defines security-by-design architecture constraints, including mandatory signature and receipt semantics.
- **Replaces / Relates to:** Supersedes the prior non-template version of `02_Design_Philosophy.md`; aligned with `api/v2.0.0/beckn.yaml` and Beckn architecture documentation.
- **Feedback - Issues:** Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22NFH-001%22).
- **Feedback - Discussions:** Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22NFH-001%22).
- **Feedback - Pull Requests:** Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22NFH-001%22).
- **Errata:** To be published.

## Abstract

This RFC defines the architectural philosophy and derived principles that guide Beckn Protocol v2 decisions. It establishes the design intent, documents the substantive changes from v1.x to v2.0, and identifies the transport behaviors that are stable and must remain so.

## Table of Contents

- [Specification: Architecture, Design Philosophy and Principles](#specification-architecture-design-philosophy-and-principles)
  - [Document Details](#document-details)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Design Principles](#design-principles)
  - [What changed in v2.0](#what-changed-in-v20)
  - [What hasn't changed since v1.0](#what-hasnt-changed-since-v10)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)

## Overview

Beckn Protocol is an open, decentralized standard for value-exchange across independently operated networks. It defines the transport contracts, interaction patterns, and schema conventions that allow Consumer Nodes, Provider Nodes, Discovery Services, and registry infrastructure to interoperate without prior bilateral agreements.

Version 2.0 formalises catalog-first discovery, introduces a contract-centric transaction model, and establishes a layered architecture in which transport behavior remains stable while schema semantics and vertical-specific payloads continue to evolve. The canonical artifact for v2.0 is `api/v2.0.0/beckn.yaml`, an OpenAPI 3.1.1 specification that defines all transport-level contracts. Network topology and actor responsibilities are defined in [NFH-003](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/The_Beckn_Protocol_Stack.md) (drafted on `draft` branch, undergoing review).

The design philosophy behind v2.0 is captured in seven principles below. These are normative constraints on how the specification evolves. Any proposed change that cannot be justified against at least one of these principles SHOULD be treated as out of scope.

## Design Principles

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described [here](./Keyword_Definitions.md).

1. **Decentralization**: Any evolution in the protocol MUST enable decentralization of the associated ecosystem. In the context of value-exchange, the further we move towards the edges of a value-exchange transaction, the more choice, optionality, and agency MUST emerge as a consequence.
2. **Fabric-driven:** Any evolution in the protocol MUST emerge as a consequence of evolution in the NFH Fabric. Any feature request MUST be a fabric feature request, not a protocol feature request. Based on discussions following the feature request, a decision on whether to support that feature as a run-time fabric feature or a protocol feature will be taken.
3. **Agent-first:** The protocol MUST first leverage AI for its evolution and also empower AI Agents to participate in trusted, value-exchange transactions. Any evolution in the protocol MUST primarily be enabled for AI Agents while keeping human-enablement secondary. This principle does NOT mean features are only usable by AI — it means AI usability comes first, with human usability required alongside it.
4. **Pragmatism:** Not all systems today are AI-native. Architecture decisions SHOULD keep in mind the practical implications on non-AI-native systems, current ecosystem tooling, and developer friendliness.
5. **Semantic interoperability:** Protocol concepts MUST be interpreted consistently across domains, regions, and implementations.
6. **Reusability via abstraction:** Core concepts MUST remain abstract enough to be reused across diverse domains and regional deployments.
7. **Trust by design:** Mandatory signatures and receipt acknowledgements via the `Signature` response header MUST remain baseline transport behavior.

## What changed in v2.0

The following are the substantive changes from Beckn Protocol v1.x to v2.0.

**Actor naming**
BAP (Beckn Application Platform) and BPP (Beckn Provider Platform) are replaced by **Consumer Node (CN)** and **Provider Node (PN)**. The new names are role-oriented and domain-neutral.

**Catalog-first discovery**
Discovery no longer relies on live multicast fan-out. CNs, PNs, and DS nodes are all nodes of the fabric — they collectively form it. A PN self-hosts and self-signs its own catalog data; a DS crawls and independently verifies it to build its own index; CNs call `discover` on DS nodes. See [NFH-003](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/The_Beckn_Protocol_Stack.md) for network topology and [NFH-014](https://github.com/beckn/protocol-specifications-v2/blob/decentralised-catalog/docs/Catalog_Publishing_and_Discovery.md) for the full catalog publishing and discovery mechanism (both undergoing review).

**Contract-centric transaction model**
The transaction lifecycle is centered on explicit `Contract`, `Offer`, and `Consideration` schema objects. `Consideration` is a domain-neutral representation of the value being exchanged — monetary, credits, service, or compliance — allowing the same transaction lifecycle to operate across verticals without modification.

**Linked Data schema layer**
JSON-LD semantics are formalized as a distinct layer in the protocol stack. Domain-specific extensions use `Attribute` containers with `@context` and `@type` for semantic interoperability across regions and verticals. See [NFH-005](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Linked_Data_Schema.md) (drafted on `draft` branch, undergoing review).

**Signature model**
`CounterSignature` in the `Ack` response body has been removed. Response authentication is now provided by a `Signature` HTTP response header carrying a signed digest of the response payload. This simplifies the Ack schema and keeps response signing at the transport layer. See [NFH-007](./Authentication_and_Trust.md).

**OpenAPI 3.1.1**
The canonical specification artifact (`api/v2.0.0/beckn.yaml`) is authored in OpenAPI 3.1.1, providing full JSON Schema draft-2020-12 compatibility and enabling strict schema validation tooling.

**Agent-First design**
AI agents are first-class participants in the value-exchange fabric. Schema authoring, API evolution, and specification review are expected to leverage AI, and the protocol is designed to be AI-navigable by construction. See [NFH-012](./Schema_Design_Guide.md).

## What hasn't changed since v1.0

The following protocol behaviors are preserved from v1.x and MUST remain stable.

**Async request / callback pattern**
Every forward request returns a synchronous `Ack` or `Nack`, and the business outcome is delivered asynchronously via the corresponding `on_*` callback. This pattern is unchanged.

**Context + message envelope**
All request bodies carry `context` and `message` at the top level. `context` carries correlation identifiers (`transactionId`, `messageId`), action semantics, and version. This envelope structure is unchanged.

**Core transaction lifecycle**
The sequence `discover → select → init → confirm → [status / update / cancel]* → rate → support` is unchanged. The actions and their semantic roles are the same as in v1.x.

**Ed25519 HTTP Signatures**
Request signing uses Ed25519 digital signatures over a canonical signing string. The cryptographic primitive, key registration model, and signature verification procedure are unchanged. The only change is where the response signature is carried (see Signature model above).

**Domain-neutral schema abstractions**
Core schema objects are designed to be domain-agnostic and reused across verticals. Vertical-specific semantics extend these abstractions through `Attribute` containers; the core layer does not encode domain knowledge.

**Registry for identity and trust resolution**
The Global Root Registry remains the authoritative source for participant identity, endpoint, and public key resolution. Trust lookup against the Registry before signature verification is unchanged.

## Acknowledgements

This RFC builds on the Beckn v2 OpenAPI contract, Beckn architecture documentation, and the broader Beckn community effort that shaped the protocol's transport, discovery, and trust model.

## References

- Keyword definitions: Click [here](./Keyword_Definitions.md)
- Canonical OpenAPI artifact: `api/v2.0.0/beckn.yaml`
- Beckn protocol overview: Click [here](https://docs.beckn.io/introduction-to-beckn/beckn-protocol)
- Universal Value-Exchange Fabric overview: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure)
- Catalog publishing reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/publish-catalogs-using-catalg)
- Trusted networks and registry reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/build-trusted-networks-using-registr)
