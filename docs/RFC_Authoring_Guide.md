# RFC Authoring Guide

## Status of this document

This document is a Working Draft of the Beckn Protocol Specification, published by the members of the Core Working Group of Beckn using contributions from the open-source community of Beckn. It is subject to change without notice. Feedback may be submitted via the channels linked in the Document Details section.

## Copyright Notice

Copyright © 2026 Networks for Humanity Foundation. Licensed under [CC-BY-NC-SA 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Document Details

| Field | Value |
|---|---|
| **ID** | NFH-010 |
| **Publication Status** | Draft |
| **Authors** | [Ravi Prakash](https://github.com/ravi-prakash-v), [Networks for Humanity](https://networksforhumanity.org) |
| **Created** | 2026-05-11 |
| **Updated** | 2026-05-11 |
| **Version history** | Draft-01 (2026-05-11): Initial publication. |
| **Latest editor's draft** | [github.com/beckn/protocol-specifications-v2/blob/draft/docs/RFC_Authoring_Guide.md](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/RFC_Authoring_Guide.md) |
| **Implementation report** | Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main. |
| **Stress test report** | Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main. |
| **Conformance impact** | Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main. |
| **Security/privacy implications** | Incomplete RFCs produce incomplete security models. This guide reduces the risk of insecure protocol features entering the specification unexamined. |
| **Replaces / Relates to** | Supplements [NFH-009 Specification Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md) (drafted on `draft` branch, undergoing review) · [GOVERNANCE.md](https://github.com/beckn/protocol-specifications/blob/master/GOVERNANCE.md) · [CONTRIBUTING.md](https://github.com/beckn/protocol-specifications-v2/blob/main/CONTRIBUTING.md). Does NOT replace any of these documents. |
| **Feedback** | See subheadings below. |
| **Errata** | To be published. |

### Feedback

#### Issues

- [Open issues labelled NFH-010](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22NFH-010%22)

#### Discussions

- [NFH Fabric Support Forum — RFC Writing Guide](https://discuss.nfh.global/c/beckn/rfc-writing-guide) *(primary discussion channel)*
- [GitHub Discussions labelled NFH-010](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22NFH-010%22)

#### Pull Requests

- [Pull requests labelled NFH-010](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22NFH-010%22)

---

## Abstract

Beckn Protocol evolves through a fabric-driven Request for Comments (RFC) process managed by the Core Working Group. This RFC establishes normative requirements for the authorship, structure, content, and pre-submission quality of all RFCs submitted to the Beckn Protocol repositories. It defines what an RFC is and what it is NOT; how each of the seven Beckn design principles constrains RFC authorship; what sections MUST appear in every RFC and why each exists; how normative language MUST be applied; and what authoring anti-patterns MUST be avoided. An RFC is a necessary but NOT sufficient artifact for a protocol change — it MUST be accompanied by schema and API specification artifacts of equal quality. The normative quality bar is set by IETF and W3C process standards, consistent with the governance model described in [GOVERNANCE.md](https://github.com/beckn/protocol-specifications/blob/master/GOVERNANCE.md).

## Disclaimer

A number of RFCs submitted to the Beckn Protocol repositories prior to the adoption of this guide do NOT conform to the requirements stated here. Such documents SHOULD be treated as **legacy submissions** and do NOT invalidate this guide. Legacy submissions will be evaluated for revision in future working group cycles. Until formally revised, they MUST NOT be used as models for new RFC authorship.

---

## Table of Contents

- [RFC Authoring Guide](#rfc-authoring-guide)
  - [Status of this document](#status-of-this-document)
  - [Copyright Notice](#copyright-notice)
  - [Document Details](#document-details)
    - [Feedback](#feedback)
      - [Issues](#issues)
      - [Discussions](#discussions)
      - [Pull Requests](#pull-requests)
  - [Abstract](#abstract)
  - [Disclaimer](#disclaimer)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Specification](#specification)
    - [Definitions](#definitions)
  - [Scope and Audience](#scope-and-audience)
  - [What an RFC Is and Is NOT](#what-an-rfc-is-and-is-not)
    - [What an RFC Is](#what-an-rfc-is)
    - [What an RFC Is NOT](#what-an-rfc-is-not)
  - [Core Principles Applied to RFC Authorship](#core-principles-applied-to-rfc-authorship)
    - [1. Decentralization](#1-decentralization)
    - [2. Fabric-driven](#2-fabric-driven)
    - [3. Agent-first](#3-agent-first)
    - [4. Pragmatism](#4-pragmatism)
    - [5. Semantic Interoperability](#5-semantic-interoperability)
    - [6. Reusability via Abstraction](#6-reusability-via-abstraction)
    - [7. Trust by Design](#7-trust-by-design)
  - [Mandatory RFC Structure](#mandatory-rfc-structure)
    - [Section 1 — Document Details](#section-1--document-details)
      - [✓ Preferred — Document Details block](#-preferred--document-details-block)
      - [✗ Avoid — Missing or partial Document Details](#-avoid--missing-or-partial-document-details)
    - [Section 2 — Abstract](#section-2--abstract)
      - [✓ Preferred — Abstract](#-preferred--abstract)
      - [✗ Avoid — Abstract](#-avoid--abstract)
    - [Section 3 — Disclaimer](#section-3--disclaimer)
    - [Section 4 — Introduction](#section-4--introduction)
    - [Section 7 — Motivation](#section-7--motivation)
      - [✓ Preferred — Motivation section](#-preferred--motivation-section)
      - [✗ Avoid — Missing Motivation](#-avoid--missing-motivation)
    - [Section 8 — Design Goals and Non-Goals](#section-8--design-goals-and-non-goals)
    - [Section 9 — Roles and Actors](#section-9--roles-and-actors)
    - [Section 10 — Protocol Flows](#section-10--protocol-flows)
      - [10.1 One flow per subsection](#101-one-flow-per-subsection)
      - [10.2 Sequence diagrams for async flows](#102-sequence-diagrams-for-async-flows)
      - [10.3 State machines for lifecycle resources](#103-state-machines-for-lifecycle-resources)
      - [10.4 Error flows are first-class flows](#104-error-flows-are-first-class-flows)
      - [10.5 Normative language is mandatory](#105-normative-language-is-mandatory)
      - [10.6 Async trigger conditions MUST be specified](#106-async-trigger-conditions-must-be-specified)
      - [10.7 AI Agent exercisability MUST be demonstrated](#107-ai-agent-exercisability-must-be-demonstrated)
      - [✓ Preferred — Normative flow statement](#-preferred--normative-flow-statement)
      - [✗ Avoid — Informal flow description](#-avoid--informal-flow-description)
    - [Section 11 — Schema Changes](#section-11--schema-changes)
    - [Section 12 — Security Considerations](#section-12--security-considerations)
    - [Section 13 — Privacy Considerations](#section-13--privacy-considerations)
    - [Section 14 — Breaking Changes and Migration](#section-14--breaking-changes-and-migration)
    - [Section 15 — Open Questions](#section-15--open-questions)
    - [Section 16 — Conformance Requirements](#section-16--conformance-requirements)
    - [Section 17 — Security and Interoperability Considerations](#section-17--security-and-interoperability-considerations)
    - [Section 18 — Prior Art](#section-18--prior-art)
    - [Section 19 — References](#section-19--references)
    - [Appendix A — Worked Examples (Informative)](#appendix-a--worked-examples-informative)
    - [Appendix B — Pre-Submission Checklist](#appendix-b--pre-submission-checklist)
    - [Appendix C — Version History](#appendix-c--version-history)
  - [Anti-Pattern Catalog](#anti-pattern-catalog)
    - [AP-01 — Submitting Before the Document Is Ready](#ap-01--submitting-before-the-document-is-ready)
    - [AP-02 — Internal Implementation Terminology in Normative Text](#ap-02--internal-implementation-terminology-in-normative-text)
    - [AP-03 — Duplicating `beckn.yaml` in the RFC Body](#ap-03--duplicating-becknyaml-in-the-rfc-body)
    - [AP-04 — Absent or Incomplete Motivation](#ap-04--absent-or-incomplete-motivation)
    - [AP-05 — Undeclared Non-Goals](#ap-05--undeclared-non-goals)
    - [AP-06 — Security Treated as an Afterthought](#ap-06--security-treated-as-an-afterthought)
    - [AP-07 — Informal Normative Language](#ap-07--informal-normative-language)
    - [AP-08 — Examples That Do NOT Validate](#ap-08--examples-that-do-not-validate)
    - [AP-09 — Perfunctory Prior Art](#ap-09--perfunctory-prior-art)
    - [AP-10 — Designing Around a Specific Deployment](#ap-10--designing-around-a-specific-deployment)
    - [AP-11 — Missing State Machine for Lifecycle Resources](#ap-11--missing-state-machine-for-lifecycle-resources)
    - [AP-12 — No AI Agent Exercisability Statement](#ap-12--no-ai-agent-exercisability-statement)
  - [RFC Lifecycle and Working Group Process](#rfc-lifecycle-and-working-group-process)
  - [Conformance Requirements](#conformance-requirements)
  - [Security and Interoperability Considerations](#security-and-interoperability-considerations)
  - [Conclusion](#conclusion)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)
    - [Normative References](#normative-references)
    - [Informative References](#informative-references)
  - [Appendix A — Worked Examples (Informative)](#appendix-a--worked-examples-informative-1)
    - [Example 1 — Conformant Motivation Requirements Block](#example-1--conformant-motivation-requirements-block)
    - [Example 2 — Conformant Normative Flow Statement](#example-2--conformant-normative-flow-statement)
  - [Appendix B — Pre-Submission Checklist](#appendix-b--pre-submission-checklist-1)
  - [Appendix C — Version History](#appendix-c--version-history-1)

## Introduction

The Beckn Protocol is adopted across diverse regions, domains, and languages. It is implemented by teams who may have no shared background, no common toolchain, and no direct communication channel. The only artifact that bridges those implementations is the specification itself. When a specification is ambiguous, incomplete, or inconsistent, the result is divergent implementations that cannot interoperate — a direct failure of the protocol's primary purpose.

RFCs are the mechanism by which the Beckn Protocol evolves. A well-written RFC enables a working-group reviewer to evaluate a proposed change on its merits, understand the trade-offs accepted, assess conformance with the design principles, and predict the impact on existing implementations.

An RFC is a necessary but NOT sufficient artifact for any protocol change. Every RFC MUST be accompanied by a corresponding schema and/or API specification artifact — authored to the same quality standard — before the change may be considered for merge. An RFC without a conformant specification artifact describes intent without delivery. A specification artifact without an RFC lacks the reasoning that makes the change auditable and reversible.

This guide is normative. The requirements it places on RFC authors carry the same force as conformance requirements in any other Beckn specification document. An RFC that does NOT meet these requirements MUST NOT be merged, regardless of the quality of the accompanying schema artifacts.

---

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described [here](./Keyword_Definitions.md). These definitions aim to ensure that the terms are understood precisely and consistently to avoid confusion in the interpretation of standards, specifications, and protocols.

### Definitions

- **RFC (Request for Comments):** A reasoning document submitted to the Beckn Core Working Group proposing an addition to or change in the Beckn Protocol specification. The primary question an RFC answers is: *Should this feature or change exist in the Beckn Protocol, in this specific form, at this time?*
- **Machine contract:** Authoritative machine-readable artifacts (`attributes.yaml`, `schema.json`) that define enforceable structure. An RFC MUST NOT duplicate the content of machine contracts in its normative body.
- **Normative statement:** A requirement placed on an implementer using the keywords MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY as defined in [Keyword Definitions](./Keyword_Definitions.md).
- **Informative statement:** Background, rationale, or example content that aids understanding but places no requirement on an implementer.
- **Corrigendum:** A correction to an error in normative text that, if left uncorrected, would cause non-conformant implementations. Published as an addendum to the original RFC without modifying original text.
- **Errata:** A correction to an editorial error (spelling, formatting, or non-normative prose). Does NOT require a full working-group review cycle.
- **Normative reference:** A document that an implementer MUST read and conform to. Referenced in the RFC body with a normative keyword.
- **Informative reference:** Background reading that aids understanding but is NOT required for conformance.
- **Legacy submission:** An RFC submitted before the adoption of this guide that does NOT conform to its requirements.
- **Fabric:** The Universal Value-exchange Fabric hosted by the Networks for Humanity Foundation, as defined in [NFH-009](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md).
- **AI Agent:** An autonomous software entity capable of participating in protocol interactions without direct human instruction at the time of the interaction.

---

## Scope and Audience

This RFC applies to:

- Any person or organization proposing a change to any Beckn Protocol repository (`protocol-specifications-v2`, `schemas`, or domain-specific repositories indexed at [schema.beckn.io](https://schema.beckn.io))
- Core Committers reviewing RFC submissions on behalf of the working group
- Working Group Administrators who manage the review lifecycle and declare consensus
- Any community member contributing feedback on open RFC submissions

Readers are expected to have working knowledge of the Beckn Protocol, familiarity with the [NFH-009 Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md), and the ability to read and write OpenAPI 3.1 YAML.

---

## What an RFC Is and Is NOT

### What an RFC Is

An RFC is a **reasoning document**. Its job is to answer, for the working group, a single question:

> *Should this feature or change exist in the Beckn Protocol, in this specific form, at this time?*

Once that question is answered affirmatively and the RFC is accepted, the normative requirements it contains migrate into `beckn.yaml`, schema packs, and JSON-LD artifacts. The RFC becomes the permanent, human-readable record of *why* the specification is the way it is. Future implementers and future working-group members MUST be able to find the reasoning for every design decision in the corresponding RFC.

An RFC:

- States the problem being solved and demonstrates that the problem is real
- Explains the design decisions made and the trade-offs accepted
- Justifies why the chosen design satisfies the Beckn design principles
- Provides normative requirements that implementers MUST satisfy
- Documents what was considered and rejected, and why
- Establishes the security, privacy, and backward-compatibility posture of the change

### What an RFC Is NOT

**An RFC is NOT a changelog.** A list of what changed is NOT an RFC. It belongs in the Breaking Changes section at the end of one.

**An RFC is NOT a duplicate of `beckn.yaml`.** Do NOT reproduce endpoint descriptions, field names, or response code tables from the machine contract in the RFC body. The YAML is the machine-readable authority. The RFC explains *why* those definitions exist.

**An RFC is NOT a tutorial.** A walkthrough of how to call an API is an implementation guide. It belongs in developer documentation. Worked examples belong in an informative appendix, clearly labelled as non-normative.

**An RFC is NOT complete without its companion artifact.** Every RFC MUST be accompanied by conformant schema and/or API specification artifacts. An RFC without a companion machine-readable artifact MUST NOT be merged.

**An RFC is NOT an internal design document.** Remove all references to internal infrastructure — internal service names, implementation-specific thresholds, internal field name conventions, hardcoded environment values, or proprietary tooling. An RFC specifies observable, interoperable behavior at the protocol boundary only.

---

## Core Principles Applied to RFC Authorship

Every RFC MUST affirmatively demonstrate compliance with the Beckn design principles stated below. These principles are NOT aspirations — they are gates. A proposal that cannot demonstrate compliance with each applicable principle MUST NOT be submitted for working-group review.

All features of Beckn Protocol in *this* repository MUST be abstracted to apply across diverse domains, regions, and use cases globally. Any feature that is domain-specific MUST reside in the respective domain-specific repository outside this repository. Terms such as "order", "seller", "buyer", "product", or "item" belong in domain-specific repositories indexed at [schema.beckn.io](https://schema.beckn.io) and MUST NOT appear in the normative text of any core protocol RFC.

---

### 1. Decentralization

Any evolution in the protocol MUST enable decentralization of the associated ecosystem. In the context of value-exchange, the further a transaction moves towards the edges of the network, the more choice, optionality, and agency MUST emerge as a consequence. A feature that concentrates control, creates a mandatory central coordinator, or reduces implementer autonomy MUST be rejected or redesigned before submission.

> **RFC authorship test:** For every proposed feature, the author MUST answer: does this feature give the edges of the network more or less autonomy than they had before? If less, the feature requires explicit working-group justification before it may proceed.

> **Failure mode:** Introducing a required central registry lookup that all participants MUST complete synchronously before transacting, where the registry is operated by a single entity with no fallback path.

---

### 2. Fabric-driven

Any evolution in the protocol MUST emerge as a consequence of evolution in the NFH fabric. Any feature request MUST originate as a fabric feature request, NOT a protocol feature request. Based on discussions following the feature request, a decision will be made whether to support the feature as a run-time fabric capability or a protocol-level specification change. Protocol changes that do NOT have a traceable fabric requirement MUST NOT be accepted.

> **RFC authorship test:** The RFC MUST identify the fabric capability or fabric service evolution that motivates the protocol change. If no fabric requirement is cited, the RFC is incomplete.

> **Failure mode:** Proposing a new endpoint to solve a developer convenience problem that has NOT been raised as a fabric service requirement and has NOT been discussed in the NFH fabric Support Forum.

---

### 3. Agent-first

The protocol MUST first leverage AI for its evolution *and* empower AI Agents to participate in trusted, value-exchange transactions. Any evolution in the protocol MUST primarily be designed for AI Agents, with human-enablement as a secondary consideration. This principle does NOT mean that all features are ONLY usable by AI — features MUST be usable by both AI Agents and human-driven systems. However, the design MUST first be validated for AI Agent use, then for human use. Both are required.

> **RFC authorship test:** The RFC MUST state how the proposed feature is exercised by an AI Agent operating without direct human instruction. If the feature cannot be exercised by an AI Agent, it requires explicit working-group justification.

> **Failure mode:** Designing a flow that requires real-time human approval as a mandatory protocol step, with no machine-executable alternative defined.

---

### 4. Pragmatism

NOT all systems today are AI-native. While Beckn requires an AI-first approach to its evolution, it does NOT eliminate the need for human-driven implementations. Architecture decisions SHOULD keep in mind the practical implications on non-AI-native systems, current ecosystem tooling, and developer accessibility. A feature that is theoretically sound but operationally impractical for the current ecosystem SHOULD be phased or accompanied by a transition path.

> **RFC authorship test:** The RFC MUST acknowledge where the proposed feature places implementation burden on non-AI-native systems and SHOULD state what accommodations or transition paths are provided.

> **Failure mode:** Requiring LLM inference at every protocol interaction step without providing a deterministic fallback path for rule-based implementations.

---

### 5. Semantic Interoperability

Protocol concepts MUST be interpreted consistently across domains, regions, and implementations. A term defined in one RFC MUST mean the same thing in every domain-specific extension that uses it. RFCs MUST define all normative terms in a Definitions section and link to canonical schema definitions for all named types. Any term that could be interpreted differently across cultural or domain contexts MUST be accompanied by an explicit, normative definition.

> **RFC authorship test:** Read every normative term in the RFC in the context of three different industries and three different regions. If the term acquires a different meaning in any of those contexts, it is NOT yet precise enough and MUST be redefined.

> **Failure mode:** Using the term "subscription" without qualification when it could mean a commercial service subscription or a pub/sub channel registration depending on the domain.

---

### 6. Reusability via Abstraction

Core concepts MUST remain abstract enough to be reused across diverse domains and regional deployments. Before proposing any new schema, new endpoint, or new message type, the author MUST demonstrate that existing schemas at [schema.beckn.io](https://schema.beckn.io) or in `beckn.yaml` cannot be composed or extended to meet the requirement. A new schema that duplicates the structure of an existing one is a reusability violation.

> **RFC authorship test:** Can the proposed feature be expressed as a composition of existing Beckn schema types? If yes, the RFC MUST use composition, NOT a new schema. If no, the RFC MUST demonstrate why existing types cannot serve.

> **Failure mode:** Introducing two new error response schemas that are structurally identical to an existing error schema but carry different semantic labels, when an `errorCode` enumeration on the existing schema would serve the same purpose with less surface area.

---

### 7. Trust by Design

Mandatory signatures and acknowledgements MUST remain baseline transport behavior for all Beckn protocol interactions. Any RFC that relaxes signature requirements, makes authentication optional, or introduces unsigned message flows MUST provide a detailed security justification and MUST obtain explicit working-group approval. Trust mechanisms are NOT optional extensions — they are the foundation on which all other protocol guarantees rest.

> **RFC authorship test:** For every message introduced by the RFC, the author MUST identify: who signs it, who verifies the signature, what key material is used, and what happens if verification fails. If any of these cannot be answered, the RFC is NOT ready for review.

> **Failure mode:** Introducing a callback flow where the receiving actor is expected to process the payload without verifying the sender's signature, justified by performance considerations.

---

## Mandatory RFC Structure

Every RFC submitted to a Beckn repository MUST include the following sections, in the order specified. Sections may be expanded but MUST NOT be omitted. A section may be marked "NOT applicable" only where this guide explicitly permits it, with a brief justification stated inline.

This document is itself an RFC and demonstrates the required structure.

---

### Section 1 — Document Details

The Document Details block is the first content block in the RFC, appearing before the Abstract. It MUST be formatted as a table. The Feedback field MUST use the structured subheading format shown in this document's own Document Details section — three subheadings (Issues, Discussions, Pull Requests) with one or more bulleted links each. Discussions MUST include at least one link to the NFH Fabric Support Forum.

| Required Field | Notes |
|---|---|
| ID | Use `NFH-TBD` during draft stages. RFC numbers in the format `NFH-NNN` are auto-assigned by the CWG upon merge to `main`. |
| Publication Status | One of: `Draft` · `Proposed Standard` · `Recommended Standard` · `Required Standard` |
| Authors | Full name and affiliation for all authors. |
| Created | ISO 8601 date (`YYYY-MM-DD`). |
| Updated | ISO 8601 date. MUST be updated on every substantive revision. |
| Version history | One line per draft: `Draft-NN (YYYY-MM-DD): summary of changes.` If `main` does NOT yet contain this document, write `Draft-01 (YYYY-MM-DD): Initial publication.` |
| Latest editor's draft | GitHub URL to the file on the target branch. |
| Implementation report | Link if applicable; `NOT applicable` for governance RFCs, with justification inline. |
| Stress test report | Either `Untested: <reason>` or `Stress test ongoing: <link to card in NFH Fabric Engineering project — card status MUST reflect current status in the Protocol V2.0 GitHub project>`. |
| Conformance impact | One sentence stating what this RFC requires of implementers. |
| Security/privacy implications | One sentence summary. MUST NOT be left blank. |
| Replaces / Relates to | MUST link to at least one existing or new RFC document. |
| Feedback | Row value: "See subheadings below." Full content in Issues / Discussions / Pull Requests subheadings immediately after the table. |
| Errata | `To be published` at Draft stage. Updated on acceptance. |

> **Why this exists:** Without a Document Details block, a reader cannot determine whether an RFC is actively under review, accepted, or superseded. The RFC MUST carry its own provenance.

#### ✓ Preferred — Document Details block

The Document Details block in this document is the preferred form. It uses `NFH-TBD` as the draft ID placeholder, states `Untested` with a reason for the stress test field, uses structured subheadings for Feedback with a required NFH Fabric Support Forum link under Discussions, and records a single-line version history for an initial publication.

#### ✗ Avoid — Missing or partial Document Details

**Variant A — No Document Details block**

An RFC that opens directly with an Abstract, with no status information, no author attribution, and no issue-tracking links. The reader cannot determine whether the RFC is current, draft, or superseded without checking git blame.

**Variant B — Bare author and date only**

```
Author: Jane Smith
Date: May 2026
```

This provides authorship and a date but omits: publication status, version history, stress test report, conformance impact, security/privacy implications, Feedback subheadings, NFH Fabric Support Forum link, and errata. The working group cannot manage review without these fields.

**Variant C — Feedback as a single table row with no subheadings**

```
| Feedback | Issues: [link] · Discussions: [link] · PRs: [link] |
```

This format does NOT allow multiple links per category and does NOT surface the NFH Fabric Support Forum as a distinct, required channel. Use the subheading format instead.

---

### Section 2 — Abstract

The Abstract MUST be a single, self-contained paragraph of 100–200 words. It MUST be comprehensible to a working-group member who has read nothing else about the proposal.

The Abstract MUST answer:
- What problem does this RFC address?
- What mechanism does it introduce or modify?
- What is explicitly out of scope?
- Where is the companion schema/API artifact?

The Abstract MUST NOT use forward references to sections of the RFC body. It MUST NOT assume the reader knows the prior state of the API. It MUST NOT be a table-of-contents stub.

#### ✓ Preferred — Abstract

> This RFC establishes a decentralized model for catalog publishing and discovery for Beckn Protocol v2.0.0. Currently, a Provider Node depends on a centrally-operated Cataloging Service to make its catalogs discoverable, which is a single point of failure for catalog reach and gives a Discovery Service no independent way to verify a catalog's origin. This RFC specifies that a Provider Node self-hosts signed catalog files and a signed catalog index on infrastructure it already controls, discoverable through one field on its existing Registry record; a Discovery Service crawls and independently verifies that data to build its own index. This RFC does NOT address restricted or access-gated catalogs, a specific crawler implementation, or changes to `/discover`/`/on_discover`. It MUST be read alongside the companion schema changes in PR #NNN.

The problem is stated. The motivation is named. The mechanism is specified. The out-of-scope is explicit. The companion artifact is referenced.

#### ✗ Avoid — Abstract

**Variant A — Table-of-contents stub:**

> "This RFC introduces changes to the Pull API. Section 3 describes the motivation. Section 4 describes the design."

This is navigation, NOT a summary. A reader learns nothing about the change.

**Variant B — Protocol background:**

> "Beckn Protocol is an open, domain-agnostic protocol for interoperable commerce. It decouples demand-side infrastructure from supply-side services."

RFC readers know what Beckn is. This paragraph wastes the Abstract with preamble.

---

### Section 3 — Disclaimer

The Disclaimer section SHOULD be included when the RFC introduces features that interact with or depart from existing behavior that has known limitations or legacy exceptions. It MUST be placed after the Abstract and before the Table of Contents.

The Disclaimer MUST NOT be used to excuse non-conformant content within the RFC itself. If no disclaimer is needed, this section MAY be omitted.

---

### Section 4 — Introduction

The Introduction MUST explain why this area of the protocol matters, what the current state is, and why the working group should engage with this RFC. It MUST NOT restate the Abstract. It MUST NOT contain normative requirements. It MUST NOT begin with a paragraph explaining what Beckn Protocol is.

---

### Section 7 — Motivation

The Motivation section is the primary justification for the working group to spend review time on the proposal.

The Motivation section MUST contain four subsections:

**7.1 Current State.** A precise description of what the protocol currently does or lacks. Reference specific endpoint names, schema names, or protocol behaviors.

**7.2 Identified Problems.** The specific failure modes, limitations, or gaps. For each: who is affected, under what conditions it manifests, and what the observable consequence is.

**7.3 Why the Current Design Cannot Be Extended.** Why the existing protocol cannot be amended at the margins. This justifies the scope of the proposal.

**7.4 Requirements.** A numbered list of what the new design MUST achieve, expressed as verifiable, testable requirements. Every numbered requirement MUST be demonstrably satisfied by the Protocol Flows section.

#### ✓ Preferred — Motivation section

> **7.1 Current State.** The `/confirm` endpoint in Beckn Protocol v2.0.0 returns a synchronous `Ack` and subsequently triggers `/on_confirm` on the CN's callback URI. The PN is responsible for constructing the `Contract` object and transmitting it in the callback. Currently, no mechanism exists for either party to signal that the contract terms require renegotiation after `on_init` but before `on_confirm`.
>
> **7.2 Identified Problems.** (1) When the PN detects an inventory change between `on_init` and `on_confirm`, it has no protocol-level path to propose revised terms — it can only confirm or Nack. (2) An AI Agent acting as CN cannot autonomously renegotiate; it receives a Nack and must re-initiate the full select/init cycle with no information about why the terms changed. (3) This creates unnecessary latency in high-frequency AI Agent transactions where minor term adjustments are common.
>
> **7.3 Why the Current Design Cannot Be Extended.** Adding an optional field to the `/on_confirm` payload to carry revised terms would conflate confirmation with counter-proposal, violating the protocol invariant that `/on_confirm` MUST carry a binding commitment. A new exchange is required.
>
> **7.4 Requirements.** (R1) The PN MUST be able to propose revised terms after `on_init` without abandoning the active transaction. (R2) The CN MUST be able to accept or reject revised terms without re-initiating the full select/init cycle. (R3) An AI Agent acting as CN MUST be able to evaluate and respond to revised terms without human input. (R4) The mechanism MUST NOT alter the semantics of the existing `/confirm` and `/on_confirm` exchange.

#### ✗ Avoid — Missing Motivation

**Variant A — Changelog masquerading as Motivation:**

> "This RFC adds the following: (1) new `/negotiate` endpoint. (2) new `CounterProposal` schema. (3) updated `/confirm` to reference prior negotiation."

This describes what changed, NOT why.

**Variant B — Generic problem statement:**

> "The current confirm flow has some limitations that affect performance. This RFC improves it."

"Some limitations" is NOT a problem statement. No actor is named, no failure mode is described, no Fabric requirement is cited.

---

### Section 8 — Design Goals and Non-Goals

**Design Goals** MUST be written as numbered, verifiable outcome statements, each mapping to at least one numbered requirement in Section 7.4.

**Non-Goals** MUST state for each excluded item why it is excluded — wrong scope, deferred to a future RFC, deliberate simplification, or NOT implementable within the current architecture. "Out of scope" alone is NOT sufficient.

---

### Section 9 — Roles and Actors

Every actor participating in any flow introduced or modified by this RFC MUST be defined in a table stating: the actor's protocol identity, their role in this RFC's flows, which endpoints they invoke, and which endpoints they implement. Any actor whose identity is established through a specific mechanism MUST have that mechanism stated here.

Permissible actors in core protocol RFCs targeting this repository are: CN, PN, DS, NFO, CS, Fabric. The BG (Beckn Gateway) has been removed from the v2.0.0 architecture and MUST NOT appear in new RFCs targeting this repository.

---

### Section 10 — Protocol Flows

#### 10.1 One flow per subsection

Each distinct end-to-end interaction MUST have its own subsection. Two interactions that use the same endpoint with different parameters are two flows, NOT one.

#### 10.2 Sequence diagrams for async flows

Any flow involving an asynchronous callback MUST include a sequence diagram showing: all participating actors, all messages with endpoint names and HTTP methods, message direction, the synchronous ACK, the explicitly labelled async gap, and the callback message.

#### 10.3 State machines for lifecycle resources

Any resource with a lifecycle MUST be accompanied by a state machine diagram showing all valid states, all valid transitions, the trigger and responsible actor for each transition, any guard conditions, and explicitly invalid transitions.

#### 10.4 Error flows are first-class flows

Every reachable error condition MUST be documented with: the trigger condition, the response schema, which actor sends the error, and what the receiving actor MUST do in response.

#### 10.5 Normative language is mandatory

Every statement that places a requirement on an implementer MUST use MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY as defined in [Keyword Definitions](./Keyword_Definitions.md). The following are NOT normative and MUST NOT be used in place of these keywords: "will", "shall", "can", "is expected to", "typically", "usually".

#### 10.6 Async trigger conditions MUST be specified

For any flow where one actor delivers a message to another without an explicit prior request from the receiver, the RFC MUST specify: what event triggers the message, who decides when to send it, what the receiver can expect about timing and ordering, and what the sender MUST do if delivery fails.

#### 10.7 AI Agent exercisability MUST be demonstrated

For every flow, the RFC MUST confirm that an AI Agent can participate without human input at any protocol step. Where the flow requires structured decision-making, the RFC MUST state what input the AI Agent receives and in what format.

#### ✓ Preferred — Normative flow statement

> Upon receiving a `POST /confirm` request, the PN MUST validate the Beckn HTTP Signature as specified in [Authentication and Trust](./Authentication_and_Trust.md). If signature validation fails, the PN MUST return `NackUnauthorized` (HTTP 401) and MUST NOT invoke the callback. If the `transactionId` in the request `context` does NOT correspond to an active initialized transaction, the PN MUST return `NackBadRequest` (HTTP 400). Upon successful validation and processing, the PN MUST return `Ack` synchronously and MUST subsequently invoke `POST /on_confirm` on the CN's registered callback URI, carrying a confirmed `Contract` object in the `message` field. An AI Agent acting as CN MUST be able to process the `Contract` object in the callback and determine next-step actions without human input, based solely on the fields defined in the `Contract` schema.

#### ✗ Avoid — Informal flow description

**Variant A — Missing normative language:**

> "After the PN gets the confirm request, it will validate it and send back a callback with the contract. The CN can then proceed."

"Will validate" and "can then proceed" are NOT normative. An implementer cannot determine their obligations from this.

**Variant B — Missing error flows:**

> "The PN confirms the order and returns the contract in the callback."

This describes only the happy path. What happens if the signature is invalid? If the transaction ID is unknown? If the PN cannot reach the CN callback URI? None of these are specified.

---

### Section 11 — Schema Changes

For every new or modified schema introduced by this RFC:

**For new schemas:** State the schema name and justify why an existing schema at [schema.beckn.io](https://schema.beckn.io) or in `beckn.yaml` cannot be reused or extended. Provide a description that opens with the real-world concept the schema models — NOT its structural composition. State every property with: what it represents, who assigns its value, any constraints beyond JSON type, and for enumerations, what each value means in this context. All NFH-009 conformance requirements (CON-005-01 through CON-005-15) apply to all new schemas.

**For modified schemas:** State what was changed and why. State whether the change is backward-compatible. If NOT, provide the migration path per Section 14.

**Cross-artifact alignment:** If new named terms are introduced in `beckn.yaml`, the RFC MUST identify which terms require corresponding entries in `context.jsonld` and `vocab.jsonld`, and MUST link to a companion PR in the `schemas` repository. No RFC that introduces new named terms MAY be merged without a cross-artifact alignment plan.

---

### Section 12 — Security Considerations

Security considerations for all Beckn Protocol interactions are cross-cutting concerns governed by the [Authentication and Trust](./Authentication_and_Trust.md) document. RFC authors MUST read and apply that document in full before specifying any protocol flow.

This section MUST NOT reproduce the general security model from [Authentication and Trust](./Authentication_and_Trust.md). Instead, it MUST:

1. Confirm that all endpoints and flows introduced by this RFC conform to the authentication and signing requirements in [Authentication and Trust](./Authentication_and_Trust.md).
2. Identify any security considerations *specific* to this RFC's features that are NOT already addressed by the general model — such as integrity verification for externally-referenced objects, or access-control constraints specific to a resource this RFC introduces.
3. State explicitly if this RFC introduces NO security considerations beyond those covered by [Authentication and Trust](./Authentication_and_Trust.md).

---

### Section 13 — Privacy Considerations

For each data field introduced by this RFC, evaluate whether it can carry Personally Identifiable Information (PII). If any field may carry PII, this section MUST state: what the field represents, which actors receive the value, under what conditions they may retain or forward it, and whether the protocol enforces the privacy constraint or relies on operator policy.

If no fields introduced by this RFC can carry PII, this section MUST state that explicitly. It MUST NOT be omitted.

---

### Section 14 — Breaking Changes and Migration

Required when the RFC removes, renames, or changes the meaning of any existing endpoint, schema, property, or enumeration value.

| Changed Artifact | Replacement | Migration Path | Target Removal Version |
|---|---|---|---|
| `GET /example/result/{id}` | `resultUrl` in callback payload | Implementers MUST implement the callback endpoint; the CS MUST include `resultUrl` in all callback responses | v2.1.0 |

The migration path MUST be specific enough that an independent implementer can execute it. "Update your implementation" is NOT a migration path. The preferred change sequence from [NFH-009](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md) applies: add the new artifact while retaining the old, mark the old as deprecated with `owl:deprecated` in `vocab.jsonld`, publish migration notes, and remove the old artifact only in a planned major release.

---

### Section 15 — Open Questions

List every unresolved design question with a statement of what information or decision is needed to resolve it. This section is removed when the RFC reaches Recommended Standard status. If there are no open questions, this section MUST state that explicitly.

---

### Section 16 — Conformance Requirements

Every normative requirement introduced in the RFC body MUST be assigned a conformance ID and restated in a summary table. Use `CON-TBD-NN` during draft stages; IDs are finalized when the RFC number is assigned upon merge to `main`.

| ID | Requirement | Level |
|---|---|---|
| CON-TBD-01 | [Requirement text] | MUST / SHOULD / MAY |

---

### Section 17 — Security and Interoperability Considerations

Distinct from Section 12, this section addresses the aggregate impact of the RFC on the protocol's security and interoperability posture as a whole: new trust relationships, new failure modes for existing interactions, or new cross-implementation ambiguities introduced by this RFC.

---

### Section 18 — Prior Art

The RFC MUST survey the existing landscape of related work, including at minimum:

- Relevant IETF RFCs
- Relevant W3C specifications
- Relevant domain standards
- Other open protocol specifications that have addressed similar problems

For each surveyed work, the RFC MUST state in one sentence what it does and in one sentence why it was adopted, adapted, or rejected. "This design follows standard patterns" with no citations is NOT a Prior Art section.

---

### Section 19 — References

**Normative References** — documents that implementers MUST read to conform. Each MUST be cited at least once in the body with a normative keyword and a bracketed citation label.

**Informative References** — background reading, NOT required for conformance.

Every citation label used in the body MUST have a corresponding entry here.

---

### Appendix A — Worked Examples (Informative)

All examples are non-normative and MUST be labelled as such. Every example MUST be validated against the current schema before submission. An example that fails schema validation is NOT an informative illustration — it is an error that MUST be resolved before submission.

---

### Appendix B — Pre-Submission Checklist

See [Appendix B — Pre-Submission Checklist](#appendix-b--pre-submission-checklist-1) at the end of this document.

---

### Appendix C — Version History

A human-readable table of every draft revision, distinct from git commit history.

| Version | Date | Changes |
|---|---|---|
| Draft-01 | YYYY-MM-DD | Initial publication. |
| Draft-02 | YYYY-MM-DD | [Summary of substantive changes.] |

---

## Anti-Pattern Catalog

This section catalogs authoring failures observed in RFC submissions to the Beckn Protocol repositories. Each anti-pattern is described, its consequence is stated, and the conformant approach is specified.

---

### AP-01 — Submitting Before the Document Is Ready

**Description:** The RFC is marked ready for review with incomplete sections, missing flows, or broken examples that are discovered and corrected during the review period.

**Consequence:** The working group performs authorial work during review, delaying acceptance and placing unfair burden on reviewers. Changes made under review pressure rather than deliberate design are less likely to be correct.

**Conformant approach:** The author MUST complete the Pre-Submission Checklist (Appendix B) in full before marking the PR ready for review. If any item is unchecked, the PR MUST remain in Draft status.

---

### AP-02 — Internal Implementation Terminology in Normative Text

**Description:** RFC normative text includes references to internal service names, proprietary infrastructure, hardcoded environment values, internal field names, or implementation-specific behavior that is NOT observable at the protocol boundary.

**Examples of anti-pattern text:**
- *"...the result is stored in the canonical repository under a system-generated key..."*
- *"...delivery is guaranteed via retry queues with configurable backoff..."*
- *"...the record identifier used internally to track the request..."*
- *"...the configured inline threshold determines whether object delivery is used..."*

**Consequence:** Independent implementations cannot conform to a specification that references proprietary internal state.

**Conformant approach:** Every normative sentence MUST pass this test: *Can an independent implementer with no knowledge of any specific implementation build a conformant system based solely on this sentence?* If the answer is NO, rewrite the sentence to describe only observable behavior at the protocol boundary.

---

### AP-03 — Duplicating `beckn.yaml` in the RFC Body

**Description:** The RFC body reproduces endpoint descriptions, field definitions, response code tables, or schema property lists already defined in `beckn.yaml`.

**Consequence:** Creates a maintenance burden, introduces ambiguity about which document is authoritative, and dilutes the RFC's value as a reasoning document.

**Conformant approach:** The RFC MAY reference specific schema names and field names by citation. It MUST NOT reproduce their definitions. Write: *"The `resultUrl` field (defined in `beckn.yaml` §components/schemas) MUST be verified by the CN before processing."*

---

### AP-04 — Absent or Incomplete Motivation

**Description:** The RFC describes what changed without explaining why the prior design was insufficient, what failure modes were observed, or what requirements the new design satisfies.

**Consequence:** The working group cannot evaluate whether the design is correct without knowing the problem.

**Conformant approach:** Write Section 7 (Motivation) before designing anything. The Motivation section MUST state a concrete, observable failure mode in the current design and MUST cite a traceable Fabric requirement. A Motivation section that cannot do both is NOT complete.

---

### AP-05 — Undeclared Non-Goals

**Description:** The RFC does NOT state what is out of scope, causing reviewers to request additions the author deliberately excluded.

**Consequence:** Review cycles are spent on scope the author never intended to address.

**Conformant approach:** Section 8 MUST address every significant design question that might arise during review — either by including it or by explicitly excluding it with justification.

---

### AP-06 — Security Treated as an Afterthought

**Description:** Section 12 is absent at initial submission, consists only of a reference to [Authentication and Trust](./Authentication_and_Trust.md) without addressing feature-specific considerations, or is added only after reviewer requests.

**Consequence:** The working group cannot approve an RFC whose feature-specific security implications are unknown.

**Conformant approach:** Section 12 MUST confirm conformance with [Authentication and Trust](./Authentication_and_Trust.md) and identify any considerations NOT covered by that document. It MUST be present at initial submission.

---

### AP-07 — Informal Normative Language

**Description:** RFC normative requirements use informal language: "will", "shall", "can", "is expected to", "typically", "usually", or lowercase "should".

**Examples:**
- *"The receiver will process the callback when it arrives."*
- *"The status typically becomes ACTIVE after creation."*
- *"Implementations can choose to retry on failure."*

**Consequence:** Informal language is ambiguous and produces incompatible implementations.

**Conformant approach:** Every statement placing a requirement on an implementer MUST use MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY. If a requirement is conditional, state the condition explicitly.

---

### AP-08 — Examples That Do NOT Validate

**Description:** Worked examples contain missing required fields, incorrect field names, wrong action values, or structures that do NOT match their schema.

**Consequence:** Invalid examples signal that the RFC was NOT tested end-to-end before submission.

**Conformant approach:** Every example MUST pass `npx @redocly/cli lint` (or equivalent) before the PR is submitted. If an example cannot be made valid, either the example is wrong or the schema is wrong — resolve the conflict before submission.

---

### AP-09 — Perfunctory Prior Art

**Description:** The Prior Art section mentions "standard patterns" with no specific citations, no analysis, and no statement of what was adopted, adapted, or rejected.

**Consequence:** The working group cannot assess whether the RFC reinvents a solved problem.

**Conformant approach:** Name specific documents. For each: one sentence on what it does, one sentence on why it was adopted, adapted, or rejected. Prior art is NOT optional.

---

### AP-10 — Designing Around a Specific Deployment

**Description:** RFC normative text references specific hostnames, specific registry operators, or configuration values that vary between deployments.

**Examples:**
- *"...resolved from the registry at [specific hostname]..."*
- *"...uses the threshold configured by the network administrator..."*

**Consequence:** The RFC specifies a deployment, NOT a protocol. Implementations using different configurations cannot conform.

**Conformant approach:** Refer to actors by protocol role, refer to registries by function, and treat all deployment-variable values as operator-defined parameters with stated constraints discoverable through the protocol.

---

### AP-11 — Missing State Machine for Lifecycle Resources

**Description:** The RFC introduces a resource with named lifecycle states but describes the lifecycle only in passing prose.

**Consequence:** Implementers make different choices about valid state transitions, producing incompatible implementations.

**Conformant approach:** Every resource with named lifecycle states MUST have a formal state machine diagram showing all valid states, all valid transitions, the trigger and responsible actor for each transition, and explicitly invalid transitions.

---

### AP-12 — No AI Agent Exercisability Statement

**Description:** The RFC introduces a flow that requires human input at some mandatory protocol step with no machine-executable alternative, and does NOT address this in the design.

**Consequence:** The feature violates the Agent-first design principle. An AI Agent cannot participate in the flow without breaking the protocol contract.

**Conformant approach:** Section 10 MUST explicitly confirm that every flow is exercisable by an AI Agent without human input at any protocol step. Where structured data or decisions are required, the RFC MUST specify the format in which the AI Agent receives them.

---

## RFC Lifecycle and Working Group Process

To understand the RFC lifecycle — including submission stages, working group voting, and acceptance criteria — refer to [CONTRIBUTING.md](https://github.com/beckn/protocol-specifications-v2/blob/main/CONTRIBUTING.md).

To understand working group processes — including meeting cadence, role definitions, consensus mechanisms, and branch governance — refer to [GOVERNANCE.md](https://github.com/beckn/protocol-specifications/blob/master/GOVERNANCE.md).

---

## Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-TBD-01 | Every RFC MUST include a Document Details block as the first content element, containing all fields specified in this document, with Feedback as structured subheadings. | MUST |
| CON-TBD-02 | RFC IDs MUST use `NFH-TBD` as a placeholder during draft stages. The final `NFH-NNN` number is auto-assigned by the CWG upon merge to `main`. | MUST |
| CON-TBD-03 | The Feedback section MUST include Issues, Discussions, and Pull Requests as subheadings with bulleted links. Discussions MUST include at least one link to the NFH Fabric Support Forum. | MUST |
| CON-TBD-04 | Every RFC MUST include an Abstract of 100–200 words that is self-contained, states the problem, mechanism, and out-of-scope, and references the companion schema/API artifact. | MUST |
| CON-TBD-05 | The Stress Test Report field MUST state either `Untested: <reason>` or `Stress test ongoing: <link to card in NFH Fabric Engineering project>`. | MUST |
| CON-TBD-06 | The Replaces / Relates to field MUST link to at least one existing or new RFC document. | MUST |
| CON-TBD-07 | Every RFC MUST include a Motivation section with subsections for Current State, Identified Problems, Why the Current Design Cannot Be Extended, and numbered Requirements. | MUST |
| CON-TBD-08 | The Motivation section MUST cite a traceable Fabric requirement that motivates the protocol change. | MUST |
| CON-TBD-09 | Section 12 (Security Considerations) MUST confirm conformance with [Authentication and Trust](./Authentication_and_Trust.md) and identify any feature-specific security considerations NOT covered by that document. | MUST |
| CON-TBD-10 | Section 12 MUST NOT reproduce the general security model from [Authentication and Trust](./Authentication_and_Trust.md). | MUST NOT |
| CON-TBD-11 | Every RFC MUST include a Privacy Considerations section, even if it states that no fields introduced by the RFC can carry PII. | MUST |
| CON-TBD-12 | Every async flow MUST include a sequence diagram. | MUST |
| CON-TBD-13 | Every lifecycle resource MUST include a state machine diagram. | MUST |
| CON-TBD-14 | All normative statements MUST use MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY as defined in [Keyword Definitions](./Keyword_Definitions.md). | MUST |
| CON-TBD-15 | RFC normative text MUST NOT reference internal implementation details, proprietary infrastructure, or deployment-specific values. | MUST NOT |
| CON-TBD-16 | RFC normative text MUST NOT reproduce field definitions or schema property lists already defined in `beckn.yaml` or schema packs. | MUST NOT |
| CON-TBD-17 | Every worked example MUST be validated against the current schema before the PR is submitted for review. | MUST |
| CON-TBD-18 | All examples MUST be labelled as informative (non-normative). | MUST |
| CON-TBD-19 | The Prior Art section MUST name at least three specific prior works with analysis of adoption, adaptation, or rejection. | MUST |
| CON-TBD-20 | Every breaking change MUST be documented in Section 14 with a specific, executable migration path. | MUST |
| CON-TBD-21 | Every RFC introducing new named terms in `beckn.yaml` MUST link a cross-artifact alignment plan for `context.jsonld` and `vocab.jsonld`. | MUST |
| CON-TBD-22 | A PR MUST NOT be marked ready for review until all items in the Pre-Submission Checklist (Appendix B) are satisfied. | MUST |
| CON-TBD-23 | All RFC schema designs MUST comply with NFH-009 conformance requirements CON-005-01 through CON-005-15. | MUST |
| CON-TBD-24 | Every RFC MUST include a Roles and Actors table. The BG (Beckn Gateway) MUST NOT appear in new RFCs targeting this repository. | MUST |
| CON-TBD-25 | Every protocol flow MUST include a statement confirming that the flow is exercisable by an AI Agent without human input at any protocol step. | MUST |
| CON-TBD-26 | Domain-specific vocabulary — including "order", "seller", "buyer", "product", and "item" — MUST NOT appear in the normative text of any core protocol RFC. | MUST NOT |

---

## Security and Interoperability Considerations

Incomplete, ambiguous, or structurally non-conformant RFCs introduce systemic risk to the Beckn Protocol. An RFC with a superficial security section may allow a protocol feature to be accepted whose security implications are unknown — and insecure protocol features, once deployed in production implementations, are difficult or impossible to correct without breaking backward compatibility.

This guide reduces that risk by requiring that Section 12 be drafted before Protocol Flows, by anchoring security requirements to [Authentication and Trust](./Authentication_and_Trust.md) as the single authoritative cross-cutting source, and by requiring that feature-specific security gaps be identified explicitly.

Ambiguity in normative text — through missing normative keywords, undefined actor obligations, unspecified error recovery, or absent state machine definitions — produces divergent implementations that cannot interoperate. This guide addresses that risk by establishing normative language and structural completeness as merge gates, NOT post-review recommendations.

---

## Conclusion

This RFC establishes a normative authoring standard for Beckn Protocol RFCs, grounded in the seven Beckn design principles and modelled on the quality bar of IETF and W3C process documents. The standard is NOT aspirational — it is a merge gate. An RFC that does NOT satisfy the requirements stated here MUST NOT be merged, regardless of the quality of its accompanying schema changes.

An RFC is a necessary but NOT sufficient artifact for any protocol change. The schema and API specification artifacts that accompany it carry equal weight and are subject to the quality standard governed by [NFH-009](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md).

The working group is encouraged to treat this document as a living specification. Where gaps, ambiguities, or missing guidance are identified, contributors are invited to propose improvements via the feedback channels in the Document Details section.

---

## Acknowledgements

This document reflects input from Beckn Protocol contributors and the Core Working Group. It is grounded in the design principles established in [GOVERNANCE.md](https://github.com/beckn/protocol-specifications/blob/master/GOVERNANCE.md) and the authoring standards of [NFH-009](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md).

---

## References

### Normative References

- **[NFH-009]** Ravi Prakash V, *Specification Design Guide*, Networks for Humanity Foundation, 2026. [Design_Guide.md](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md) (drafted on `draft` branch, undergoing review)
- **[AUTH-TRUST]** Beckn Core Working Group, *Authentication and Trust*. [Authentication_and_Trust.md](./Authentication_and_Trust.md)
- **[GOVERNANCE]** Beckn Core Working Group, *Specification Governance*. [GOVERNANCE.md](https://github.com/beckn/protocol-specifications/blob/master/GOVERNANCE.md)
- **[CONTRIBUTING]** Beckn Core Working Group, *Contributing to Beckn Protocol*. [CONTRIBUTING.md](https://github.com/beckn/protocol-specifications-v2/blob/main/CONTRIBUTING.md)
- **[KEYWORDS]** Beckn Core Working Group, *Keyword Definitions*. [Keyword_Definitions.md](./Keyword_Definitions.md)
- **[RFC 2119]** S. Bradner, *Key words for use in RFCs to Indicate Requirement Levels*, IETF, March 1997. [rfc-editor.org/rfc/rfc2119](https://www.rfc-editor.org/rfc/rfc2119)

### Informative References

- **[RFC 4122]** P. Leach, M. Mealling, R. Salz, *A Universally Unique IDentifier (UUID) URN Namespace*, IETF, July 2005. [rfc-editor.org/rfc/rfc4122](https://www.rfc-editor.org/rfc/rfc4122)
- **[RFC 9110]** R. Fielding, M. Nottingham, J. Reschke, *HTTP Semantics*, IETF, June 2022. [rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110)
- **[WEBSUB]** J. Genestoux, A. Julliard, *WebSub*, W3C Recommendation, January 2018. [w3.org/TR/websub](https://www.w3.org/TR/websub/)
- **[DCAT]** R. Albertoni et al., *Data Catalog Vocabulary (DCAT) — Version 3*, W3C Recommendation. [w3.org/TR/vocab-dcat-3](https://www.w3.org/TR/vocab-dcat-3/)
- **[OPENAPI-GOV]** OpenAPI Initiative, *Governance Model*. [openapis.org/participate/how-to-contribute/governance](https://www.openapis.org/participate/how-to-contribute/governance)
- **[W3C-PROCESS]** W3C, *World Wide Web Consortium Process Document*. [w3.org/Consortium/Process](https://www.w3.org/Consortium/Process/)

---

## Appendix A — Worked Examples (Informative)

*This appendix is non-normative. All examples illustrate the normative sections above.*

### Example 1 — Conformant Motivation Requirements Block

> **7.4 Requirements.**
> - **R1:** The PN MUST be able to signal revised contract terms to the CN after `on_init` without abandoning the active transaction.
> - **R2:** The CN MUST be able to accept or reject revised terms without re-initiating the full select/init cycle.
> - **R3:** An AI Agent acting as CN MUST be able to evaluate and respond to revised terms without human input at any step.
> - **R4:** The mechanism MUST NOT alter the semantics of the existing `/confirm` and `/on_confirm` exchange.
> - **R5:** The flow MUST be scoped to an active transaction identified by `context.transactionId`.

Each requirement is testable, actor-attributed, and directly traceable to a problem in Section 7.2.

### Example 2 — Conformant Normative Flow Statement

> Upon receiving `POST /confirm`, the PN MUST validate the Beckn HTTP Signature as specified in [Authentication and Trust](./Authentication_and_Trust.md). If validation fails, the PN MUST return `NackUnauthorized` (HTTP 401) and MUST NOT invoke the callback. If the `transactionId` does NOT correspond to an active initialized transaction, the PN MUST return `NackBadRequest` (HTTP 400). Upon successful validation, the PN MUST return `Ack` synchronously and MUST subsequently invoke `POST /on_confirm` on the CN's registered callback URI with a confirmed `Contract` object. An AI Agent acting as CN MUST be able to process the `Contract` object and determine next-step actions without human input, based solely on the fields defined in the `Contract` schema.

---

## Appendix B — Pre-Submission Checklist

The author MUST complete this checklist before marking a PR ready for review. If any item is unchecked, the PR MUST remain in Draft status.

**Document Identity and Completeness**
- [ ] ID field uses `NFH-TBD` as placeholder
- [ ] All Document Details fields populated, including Stress Test Report with `Untested: <reason>` or `Stress test ongoing: <link to card>`
- [ ] Replaces / Relates to links to at least one RFC document
- [ ] Feedback section uses Issue / Discussion / Pull Request subheadings with at least one NFH Fabric Support Forum link under Discussions
- [ ] Abstract is 100–200 words, self-contained, references companion schema/API artifact
- [ ] Table of Contents is present with accurate links
- [ ] All mandatory sections are present or explicitly marked NOT applicable with justification

**Design Principle Compliance**
- [ ] Decentralization: RFC states how the feature increases autonomy at the network edges
- [ ] Fabric-driven: a traceable Fabric requirement is cited in Section 7
- [ ] Agent-first: every flow is confirmed exercisable by an AI Agent without human input
- [ ] Pragmatism: implications for non-AI-native systems are acknowledged
- [ ] Semantic interoperability: all normative terms are defined in Section 5 and are domain-neutral
- [ ] Reusability via abstraction: evidence that schema.beckn.io was surveyed before new schemas are proposed
- [ ] Trust by design: Section 12 confirms authentication conformance per [Authentication and Trust](./Authentication_and_Trust.md)

**Flows and Diagrams**
- [ ] Every async flow has a sequence diagram
- [ ] Every lifecycle resource has a state machine diagram
- [ ] Every error condition has a trigger, a response schema, and a MUST statement for the caller
- [ ] Every flow has an AI Agent exercisability statement

**Normative Language**
- [ ] All normative statements use MUST / MUST NOT / SHOULD / SHOULD NOT / MAY
- [ ] No informal substitutes appear as normative requirements
- [ ] No domain-specific vocabulary ("order", "seller", "buyer", "product", "item") in normative text
- [ ] No internal implementation terminology in normative text
- [ ] BG (Beckn Gateway) does NOT appear in any actor definition or flow

**Cross-Artifact and Schema**
- [ ] All new schemas comply with NFH-009 (CON-005-01 through CON-005-15)
- [ ] JSON-LD alignment plan or companion PR linked for all new named terms
- [ ] Section 14 (Breaking Changes) is complete with specific, executable migration paths

**Examples**
- [ ] All examples pass schema validation (`@redocly/cli lint` or equivalent)
- [ ] All examples are labelled as informative (non-normative)
- [ ] No required fields missing from any example

**Prior Art and References**
- [ ] Prior Art section names at least three specific prior works with analysis
- [ ] All citation labels in the body appear in Section 19 (References)
- [ ] Normative and informative references are in separate subsections

**Process**
- [ ] RFC is linked to a GitHub Issue and at least one NFH Fabric Support Forum discussion before this PR was opened
- [ ] Open Questions section is present and complete, or explicitly states no open questions exist
- [ ] Version History (Appendix C) has been started with a Draft-01 entry

---

## Appendix C — Version History

| Version | Date | Changes |
|---|---|---|
| Draft-01 | 2026-05-11 | Initial publication. |