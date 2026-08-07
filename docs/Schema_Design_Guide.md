# Schema Design Guide

## Status of this document

This document is a Working Draft of the Beckn Protocol Specification, published by the Networks for Humanity Foundation. It is subject to change without notice. Feedback may be submitted via the issue tracker linked in the Document Details section.

## Copyright Notice

Copyright © 2026 Networks for Humanity Foundation. Licensed under [CC-BY-NC-SA 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Document Details

| Field | Value |
|---|---|
| **ID** | NFH-012 |
| **Publication Status** | Draft |
| **Authors** | [Ravi Prakash](https://github.com/ravi-prakash-v), [Networks for Humanity](https://networksforhumanity.org) |
| **Created** | 2026-05-12 |
| **Updated** | 2026-05-12 |
| **Version history** | Draft-01 (2026-05-12): Initial publication as `Managing_Schemas.md`. Draft-02 (2026-05-12): Renamed to `Schema_Design_Guide.md`. Added [Principle 3: Agent-First Design](#principle-3-agent-first-design) and its closing [What it all means…](#what-it-all-means) subsection framing the architectural inversion from AI-wrapped-over-tools to tools-wrapped-over-AI, the [Authoring with AI](#authoring-with-ai) subsection establishing AI as the primary instrument for schema authoring, the [Anti-pattern: Overdesigning schemas in an AI-first world](#anti-pattern-overdesigning-schemas-in-an-ai-first-world) section arguing for thin `Attributes` containers and dense `Descriptor` content (with the recommendation that `Attributes` be reserved for regulatory / legal / compliance facts), the [Alignment with modern discovery paradigms](#alignment-with-modern-discovery-paradigms-non-normative) non-normative subsection framing products as multi-platform living organisms with their handles in the publisher's database, and the [Context Engineering](#context-engineering) subsection framing schema design as context engineering at the protocol layer (a separate RFC on *Context Engineering for Fabric-Enabled Ecosystems* is in preparation). CON-012-26, CON-012-27, and CON-012-28 added. |
| **Latest editor's draft** | [github.com/beckn/protocol-specifications-v2/blob/draft/docs/Schema_Design_Guide.md](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Schema_Design_Guide.md) |
| **Implementation report** | Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main. |
| **Stress test report** | Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main. |
| **Conformance impact** | Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main. |
| **Security/privacy implications** | Unmanaged schema publication creates semantic ambiguity that can be exploited to misinterpret or spoof payload meaning across networks. |
| **Replaces / Relates to** | Supplements [NFH-004 Core Data Schema](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Core_Data_Schema.md) · [NFH-005 Linked Data Schema](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Linked_Data_Schema.md) · [NFH-009 Specification Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md) (NFH-004, NFH-005, NFH-009 drafted on `draft` branch, undergoing review) · [GOVERNANCE.md](../GOVERNANCE.md). Does NOT replace any of these documents. |
| **Feedback** | See subheadings below. |
| **Errata** | To be published. |

### Feedback

#### Issues

- [Open issues labelled NFH-012](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22NFH-012%22)

#### Discussions

- [GitHub Discussions labelled NFH-012](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22NFH-012%22)

#### Pull Requests

- [Pull requests labelled NFH-012](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22NFH-012%22)

---

## Abstract

This RFC defines how Beckn schemas are designed, authored, published, and consumed. It establishes the design principles that govern the schema layer — **Semantic Invariance**, **Unification over Standardization**, and **Agent-First Design** — and applies them across the schema lifecycle: when a schema needs to be created or changed (abstraction → composition → extension → creation), where it may be published, who is authorised to publish it, and how production implementations validate and apply it. Schema authoring under this guide is an AI-leveraged discipline; the curatorial role of the human author is made explicit throughout. The RFC is normative for all schema artifacts published in `beckn/schemas` and `beckn/DEG`.

---

## Table of Contents

- [Schema Design Guide](#schema-design-guide)
  - [Status of this document](#status-of-this-document)
  - [Copyright Notice](#copyright-notice)
  - [Document Details](#document-details)
    - [Feedback](#feedback)
      - [Issues](#issues)
      - [Discussions](#discussions)
      - [Pull Requests](#pull-requests)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Specification](#specification)
    - [Definitions](#definitions)
    - [Design Principles](#design-principles)
      - [Principle 1: Semantic Invariance across regions](#principle-1-semantic-invariance-across-regions)
      - [Principle 2: Unification over Standardization](#principle-2-unification-over-standardization)
      - [Principle 3: Agent-First Design](#principle-3-agent-first-design)
        - [What it all means…](#what-it-all-means)
      - [Anti-pattern: Overdesigning schemas in an AI-first world](#anti-pattern-overdesigning-schemas-in-an-ai-first-world)
        - [Why tree-shaped schemas hinder AI agents](#why-tree-shaped-schemas-hinder-ai-agents)
        - [The shift already in `beckn.yaml`](#the-shift-already-in-becknyaml)
        - [What this means for schema authoring](#what-this-means-for-schema-authoring)
        - [Worked comparison — a portable Bluetooth speaker](#worked-comparison--a-portable-bluetooth-speaker)
- [Anti-pattern: dense tree, opinionated structure, closed enums.](#anti-pattern-dense-tree-opinionated-structure-closed-enums)
        - [Alignment with modern discovery paradigms (non-normative)](#alignment-with-modern-discovery-paradigms-non-normative)
        - [Worked comparison — `GroceryItem` today, evolving forward](#worked-comparison--groceryitem-today-evolving-forward)
        - [Where to draw the line](#where-to-draw-the-line)
        - [The trajectory](#the-trajectory)
      - [Context Engineering](#context-engineering)
        - [What context engineering is](#what-context-engineering-is)
        - [Why this is a schema concern, not just an application concern](#why-this-is-a-schema-concern-not-just-an-application-concern)
        - [Context engineering takes precedence over object-oriented design](#context-engineering-takes-precedence-over-object-oriented-design)
        - [A separate RFC is underway](#a-separate-rfc-is-underway)
    - [Why do schemas need to be created or changed](#why-do-schemas-need-to-be-created-or-changed)
      - [1. Abstraction (preferred)](#1-abstraction-preferred)
      - [2. Composition](#2-composition)
      - [3. Extension](#3-extension)
      - [4. Creation (last resort)](#4-creation-last-resort)
      - [What does NOT justify a schema change](#what-does-not-justify-a-schema-change)
    - [Where schemas are published](#where-schemas-are-published)
      - [The Beckn Schema Registry](#the-beckn-schema-registry)
      - [The `beckn/schemas` repository](#the-becknschemas-repository)
      - [The `beckn/DEG` repository](#the-beckndeg-repository)
      - [NFO schema registries — NOT RECOMMENDED](#nfo-schema-registries--not-recommended)
      - [Publication venue selection](#publication-venue-selection)
    - [How NFOs can help](#how-nfos-can-help)
      - [Network-specific JSON-LD context and vocabulary](#network-specific-json-ld-context-and-vocabulary)
    - [Who can publish and extend schemas](#who-can-publish-and-extend-schemas)
      - [Core Working Group](#core-working-group)
      - [DEG Working Group](#deg-working-group)
      - [Network Facilitator Organizations (NFOs)](#network-facilitator-organizations-nfos)
        - [NFOs as external collaborators on `beckn/schemas`](#nfos-as-external-collaborators-on-becknschemas)
        - [Promotion to schema.beckn.io administrator](#promotion-to-schemabecknio-administrator)
      - [Community contributors](#community-contributors)
      - [Summary of authorization by venue](#summary-of-authorization-by-venue)
    - [How schemas are created and extended](#how-schemas-are-created-and-extended)
      - [Design principles for schema authors](#design-principles-for-schema-authors)
        - [Core design principles](#core-design-principles)
        - [Authoring with AI](#authoring-with-ai)
          - [Naming](#naming)
          - [Drafting descriptions](#drafting-descriptions)
          - [Semantic mapping and superset identification](#semantic-mapping-and-superset-identification)
          - [Vocabulary alignment](#vocabulary-alignment)
          - [What AI does not (yet) do](#what-ai-does-not-yet-do)
          - [A note on attribution](#a-note-on-attribution)
        - [Naming a schema](#naming-a-schema)
        - [NOT RECOMMENDED — generic suffixes such as `Attributes`, `Item`, `Offer`, `Resource`](#not-recommended--generic-suffixes-such-as-attributes-item-offer-resource)
          - [Expressing the carrier without polluting the name](#expressing-the-carrier-without-polluting-the-name)
        - [Describing a schema](#describing-a-schema)
        - [JSON-LD conventions](#json-ld-conventions)
        - [Validation gates](#validation-gates)
        - [Artifact precedence](#artifact-precedence)
        - [Managing offending schemas](#managing-offending-schemas)
      - [Schema pack structure](#schema-pack-structure)
      - [Creating a new schema](#creating-a-new-schema)
      - [Extending an existing schema](#extending-an-existing-schema)
      - [Versioning requirements](#versioning-requirements)
      - [Breaking vs. non-breaking changes](#breaking-vs-non-breaking-changes)
      - [Contribution process](#contribution-process)
    - [How schemas are used in production](#how-schemas-are-used-in-production)
      - [Schema discovery](#schema-discovery)
        - [Contributor recognition](#contributor-recognition)
      - [Referencing a schema from a payload](#referencing-a-schema-from-a-payload)
      - [Validation sequence](#validation-sequence)
      - [Version pinning in production](#version-pinning-in-production)
      - [Schema trust and security](#schema-trust-and-security)
      - [Worked example — UAE retail network](#worked-example--uae-retail-network)
        - [Setup](#setup)
        - [Architectural layers](#architectural-layers)
        - [Wire payload — `/discover` request](#wire-payload--discover-request)
        - [Wire payload — `/on_discover` callback](#wire-payload--on_discover-callback)
        - [Why `@context` is a single string](#why-context-is-a-single-string)
        - [Sequence diagram — end-to-end translation](#sequence-diagram--end-to-end-translation)
        - [Pseudocode — edge processing](#pseudocode--edge-processing)
- [This network context internally imports](#this-network-context-internally-imports)
- [https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld](#httpsrawgithubusercontentcombecknschemasmainschemagroceryitemv20contextjsonld)
        - [The Souq Connect network context document](#the-souq-connect-network-context-document)
        - [The Souq Connect vocabulary document](#the-souq-connect-vocabulary-document)
        - [Roundtrip stability](#roundtrip-stability)
      - [Worked example — Composing a combo product](#worked-example--composing-a-combo-product)
        - [The correct approach — express the bundle using `beckn.yaml` primitives](#the-correct-approach--express-the-bundle-using-becknyaml-primitives)
        - [Wire payload — `/on_discover` callback carrying the combo offer](#wire-payload--on_discover-callback-carrying-the-combo-offer)
        - [When a `ComboProduct` relationship schema IS justified](#when-a-comboproduct-relationship-schema-is-justified)
        - [Summary — anti-patterns and indicators](#summary--anti-patterns-and-indicators)
    - [Conformance requirements](#conformance-requirements)
  - [Conclusion](#conclusion)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)
    - [Beckn Protocol and governance](#beckn-protocol-and-governance)
    - [Context engineering — contemporary industry guidance](#context-engineering--contemporary-industry-guidance)

## Introduction

Beckn Protocol is intentionally domain-agnostic. The same transport layer, the same message envelope, and the same core data objects serve commerce, mobility, healthcare, energy, and any other value-exchange domain. This generality is the protocol's primary design goal — and it creates an immediate tension. General-purpose core objects cannot carry the full semantic detail that any specific domain requires. A `Resource` used in a healthcare transaction needs attributes that are meaningless in a ride-hailing context. A `Consideration` in a financial transaction needs precision that would be over-specified for a food-delivery use case.

Beckn resolves this tension through its schema extension mechanism. Core objects carry `Attributes` containers — designated extension points whose semantics are defined externally, through JSON-LD schema artifacts, and published in recognized repositories. The core protocol does not change. Domain-specific meaning is layered on top of the stable structural foundation.

This separation is load-bearing. It is the reason a protocol change is not required every time a new domain or use case is added to the ecosystem. It is also the reason the schema layer itself must be governed carefully: schemas are shared semantic contracts, not private implementation details. A vocabulary term published in a shared schema affects every participant that reads it, in every domain and region that references that schema version. Careless schema publication creates the same kind of silent semantic divergence that careless protocol changes create.

This RFC governs the full schema lifecycle for all Beckn schema artifacts, from the initial question of whether a schema is needed at all, through creation, publication, extension, versioning, and production use.

A note on authoring. Beckn's architectural premise, defined in [NFH-001](./Introduction.md), is that AI agents are first-class participants in value-exchange transactions. The schema layer is the surface those agents reason over — and, by direct consequence, AI is also the appropriate instrument for *authoring* that surface. This RFC treats schema authoring as an AI-leveraged discipline. The expectations on contributors and the criteria by which reviewers evaluate schema contributions are set with that posture as the default, not as an option. See [Principle 3: Agent-First Design](#principle-3-agent-first-design) and [Authoring with AI](#authoring-with-ai) for the normative shape of this expectation.

---

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [NFH-002 Keyword Definitions](./Keyword_Definitions.md).

### Definitions

**Schema artifact**: A versioned set of files that define the structural and semantic contract for a Beckn domain extension. A schema artifact consists of at minimum an `attributes.yaml` (structural), a `schema.json` (JSON Schema), a `context.jsonld` (JSON-LD context), and a `vocab.jsonld` (vocabulary).

**Schema pack**: A complete versioned directory containing all required and optional schema artifact files for a specific version of a domain schema.

**Attributes container**: A property typed as `Attributes` in the core data model (for example, `offerAttributes`, `resourceAttributes`, `providerAttributes`). This is the designated extension point for domain-specific payload data. It MUST carry a `@context` and `@type` that resolve to a published schema artifact.

**Schema registry**: The index service at `schema.beckn.io` that catalogs published schema artifacts from recognized repositories and makes them discoverable by implementers and validators.

**Core Working Group (CWG)**: The governance body responsible for the `protocol-specifications-v2` repository and for authorizing changes to the core data model.

**DEG Working Group**: The working group that governs schema artifacts in the `beckn/DEG` repository. It exists because the Digital Energy Grid (DEG) initiative was founded and is housed under the Networks for Humanity Foundation. No equivalent working group exists for any other domain — all non-DEG schemas are maintained as a standard open-source project, open to contributions from the global community and reviewed by the maintainers of the `beckn/schemas` repository under CWG oversight.

**Network Facilitator Organization (NFO)**: An entity that operates a Beckn-conformant network. NFOs are encouraged to participate as external collaborators in the `beckn/schemas` repository to help maintain and evolve the schemas most relevant to the networks they manage.

**Master catalog**: A canonical product catalog published by a manufacturer or upstream supplier that downstream implementers reference when building their own catalogs. A master catalog MAY include attached policy-as-code files declaring which attributes implementers SHOULD surface when cataloging the manufacturer's products.

**Policy-as-code**: Executable policy files (typically written in Rego, the language of the Open Policy Agent) that declare constraints on payload structure or content. A Discovery Service, or any other node in the network, MAY validate a catalog against any policy-as-code attached to referenced master catalogs before indexing or relying on it.

---

### Design Principles

Three principles underpin every other rule in this RFC. Authors and reviewers of schema contributions SHOULD return to these whenever a specific design question is unclear. They are the foundational design principles of the Beckn schema layer; the more granular authoring rules in [Design principles for schema authors](#design-principles-for-schema-authors) are derived from them.

These principles are direction-setting heuristics, not universal optimizations. Real schema design involves balancing tradeoffs: semantic flexibility against deterministic interoperability, inferred semantics against explicit structure, lightweight schemas against machine-comparable modeling, semantic stability against managed evolution. The principles below describe where Beckn schemas should generally aim; how to balance them in a specific case is a judgment call that may vary by domain maturity. Emerging domains often need exploratory modeling before stable abstractions settle; mature domains benefit from tighter unification. Ecosystems also evolve through transitional compatibility phases (dual publishing, migration windows, semantic deprecation, phased convergence) rather than clean replacement boundaries; the principles below assume such transitions are managed, not absent.

#### Principle 1: Semantic Invariance across regions

A schema's semantics do not change across regions, languages, or networks. A property named `screenSize` on a `Television` schema means the same physical dimension whether the catalog is published in Indonesia, Morocco, or Amsterdam. A `countryOfOrigin` field on a `Resource` carries the same meaning everywhere it appears. **Local policies may differ — one network may require `countryOfOrigin` for regulatory compliance while another treats it as optional — but the meaning of the term itself is invariant.**

This invariance is what makes a single shared schema usable across the entire ecosystem. It is also why NFOs almost never need to publish a forked schema. The variations NFOs encounter — different mandatory fields, different language labels, different category codes, different units of display — are policy-layer, vocabulary-layer, or presentation-layer concerns, not semantic ones. Beckn handles each of them at the right layer:

- **Mandatory-vs-optional variations** are handled by the **policy layer** (network policy, manufacturer master-catalog policy-as-code).
- **Language and naming variations** are handled by the **vocabulary layer** (network-specific `context.jsonld` aliases that resolve to the canonical IRIs).
- **Display-unit variations** (inches vs. centimetres, kWh vs. joules) are handled by the **presentation layer** in CNs and PNs at runtime.

When a contributor encounters a perceived need for a regional schema, the right move is to investigate which of these layers the actual variation belongs to. In nearly every real-world case the underlying semantic concept is invariant, and the variation lives in policy, vocabulary, or presentation.

**Invariance is across space, not across time.** Semantic Invariance discourages ungoverned, silent semantic drift across regions or networks; it does not preclude managed semantic evolution over time. As domains mature, controlled narrowing, splitting, deprecation, or refinement of concepts is sometimes required and is governed through the RFC and schema contribution process, not the invariance principle.

#### Principle 2: Unification over Standardization

Beckn has followed one architectural principle for schema evolution since its 1.0 specification: **unification over standardization**. The principle states that the ecosystem does NOT pre-emptively standardize narrow, prescriptive schemas. Instead, it begins with the broadest meaningful concept, lets attributes accumulate organically as the ecosystem evolves, and abstracts **upward** — never downward into rigid hierarchies imposed from above.

**Attributes accumulate, and that is a good thing.** A schema's attribute set is expected to grow over time. Suppose `beckn/schemas/Television/v1.0.0` is published today with 15 attributes. Five years from now, after every major manufacturer has contributed the attributes exposed in its master catalog, the same schema may carry 80 attributes. Ten years from now, 200. **This is the intended trajectory.** A rich, expressive schema serves the ecosystem better than a narrow one that forces every implementer to add private extensions.

The cost of attribute growth is mitigated by two architectural choices:

1. **No attribute is mandatory by default.** The shared schema enumerates what *can* be expressed, not what *must* be expressed. Networks choose, via policy, which attributes are required for publishing on their network. A UAE retail network may require `countryOfOrigin` and `manufacturerWarranty` on televisions; a Moroccan network may require `energyEfficiencyClass` and `localCertificationCode`. Both networks reference the same `Television` schema.

2. **Manufacturers may attach policy-as-code to their master catalogs.** A manufacturer publishing a master catalog MAY attach Rego policy files declaring which attributes implementers SHOULD surface when cataloging the manufacturer's products. A Discovery Service, or any other node in the network, MAY validate a catalog against these Rego policies before indexing or relying on it. This allows a manufacturer to enforce its catalog requirements without bilateral coordination with every implementer.

**Abstraction upward, not subdivision downward.** When attributes on a single schema cluster naturally around technology- or category-specific concerns, the schema author MAY break them out into **derived schemas** that specialize the parent — for example, `Television` may eventually be specialized into `CRTTelevision`, `LEDTelevision`, `3DTelevision`. Attributes shared by all of these (display diagonal, resolution, refresh rate) get abstracted **upward** into a parent schema such as `DisplayDevice`. This abstraction continues as the ecosystem matures:

```mermaid
flowchart BT
    CRTTelevision --> Television
    LEDTelevision --> Television
    ThreeDTelevision["3DTelevision"] --> Television
    Television --> DisplayDevice
    DisplayDevice --> ConsumerElectronics
    ConsumerElectronics --> ConsumerAppliance
    ConsumerAppliance --> Appliance
    Appliance --> Device
    Device --> Tool

    classDef leaf fill:#fff8e1,stroke:#b8860b,stroke-width:1px;
    classDef root fill:#e8f0fe,stroke:#1d4e89,stroke-width:2px;
    class CRTTelevision,LEDTelevision,ThreeDTelevision leaf;
    class Tool root;
```

At every level, the more general schema is the canonical reference for properties that apply to all its descendants. A property declared on `Device` is automatically available to `Tool`, `Appliance`, `ConsumerElectronics`, `Television`, and every leaf type below. A JSON-LD processor that understands only `Device` can still meaningfully process a payload describing a `3DTelevision` — it sees the terms it recognizes and ignores the rest, without semantic confusion.

This is **unification**: the ecosystem converges on shared, increasingly general concepts. The opposite — **standardization-by-decomposition** — would have a central authority decree exactly what a `Television` is, exactly which attributes are allowed, and forbid further evolution. That approach freezes the schema layer prematurely and forces every new use case into a fork or a bilateral extension. Beckn rejects it.

**Implications for schema authors:**

1. **Default to the broader concept.** If you are tempted to publish `OrganicCoffeeBean`, first consider whether `CoffeeBean` with an `organic: boolean` attribute is sufficient — and if `CoffeeBean` does not exist, whether `Bean` or `AgriculturalProduct` is the right starting point.
2. **Welcome attribute growth.** Resist the urge to gatekeep attributes. If a manufacturer or NFO proposes adding `displayBezelMaterial` to `Television`, the default disposition is to accept it unless it semantically duplicates an existing attribute or violates the design principles.
3. **Watch for abstraction opportunities.** When the same attribute appears across multiple sibling schemas (`Television.refreshRate`, `Monitor.refreshRate`, `Projector.refreshRate`), that is a signal that it belongs on the common ancestor (`DisplayDevice.refreshRate`). Raise the abstraction in a follow-up contribution.
4. **Do not subdivide prematurely.** A schema with 30 attributes is not a problem to be solved by forking it into ten narrower schemas. A schema with 200 attributes used across three genuinely distinct product categories may be.

#### Principle 3: Agent-First Design

Beckn's architectural premise, established in [NFH-001](./Introduction.md), is that AI agents are first-class participants in value-exchange transactions. The protocol's evolution is required to be enabled for AI agents first, with human enablement following. **The schema layer is the surface those agents reason over** — every term they recognise, every relationship they traverse, every disambiguation they make depends on a schema vocabulary that is precise, complete, and well-named. Agent-First Design has two directions, and both are normative.

**Agent-First means agent-friendly, not agent-dependent.** Beckn schemas continue to serve non-AI-native consumers: deterministic validators, SDK generators, conformance tooling, rule engines, indexers, search and filter pipelines, and constrained implementations. Designing for AI agents is an additive capability that strengthens explicit structured interoperability, not a replacement for it. A schema that is agent-friendly should also remain parser-safe, validator-friendly, and tooling-friendly.

**Schemas MUST be designed for AI agents.** A schema that is comprehensible to a human reader but illegible to an AI agent fails this principle. Beckn's commitment to AI-first interoperability is not negotiable at the schema layer. Concretely:

- Schema and property descriptions MUST read as standalone semantic prose, not as abbreviated developer notes, and MUST identify the real-world concept the schema models, the actors that produce or consume it, and its position in the value-exchange lifecycle. See [Describing a schema](#describing-a-schema).
- Term names MUST align with industry vocabulary an agent has been exposed to. Coined names that have no precedent in published vocabularies SHOULD be replaced with industry-standard terms. See [Naming a schema](#naming-a-schema).
- `@context` and `@type` linkages MUST let an agent follow the semantic graph without prior knowledge of the specific term. `rdfs:subClassOf`, `skos:broader`, `owl:sameAs`, and equivalent constructs in `vocab.jsonld` are the fallback paths agents rely on when they encounter an unfamiliar IRI.
- Network-specific terms MUST link back to the most specific superset concept in the domain-agnostic vocabulary. This is what allows an agent on one network to interpret a payload originating on another network without bilateral coordination.

**Schemas SHOULD be designed *with* AI agents.** The corollary follows directly. If schemas are the surface AI agents operate on, AI is also the appropriate instrument with which to author them. Naming a schema, mapping a domain vocabulary, drafting precise descriptions, identifying superset concepts, and aligning to industry-standard terminology are pattern-recognition and recall problems at which contemporary language models excel — and at which they consistently exceed what a single human author can produce by hand. The authoring posture this RFC asks of contributors is therefore:

1. **AI is the primary instrument**, not an optional convenience. Authors SHOULD use it to propose names, generate candidate descriptions, scan for industry-standard terms, suggest superset concepts, and check semantic alignment against published vocabularies. The model's suggestion is the starting draft, not the final word.
2. **The human role is curatorial.** The author validates suggestions against the principles in this RFC, ensures semantic stability across versions, enforces naming conventions, and confirms domain accuracy. This curation is precisely where human authorship now adds the most value — and where AI cannot yet operate unattended.
3. **Authoring without AI narrows the schema's reach.** A schema authored by hand tends to reflect the individual author's vocabulary, idiom, and direct exposure to industry conventions. That narrower reach has an ecosystem-wide cost: every counterparty that processes such a schema is implicitly working with the author's vocabulary rather than the broader semantic landscape AI assistance now surfaces. Authoring this way is not less rigorous, but it slows the ecosystem's convergence on shared meaning.
4. **The capability gap will widen.** AI's fluency in naming, vocabulary alignment, and semantic mapping is already substantial and is improving rapidly. Schema work done without AI assistance will look increasingly limited alongside schemas authored with it. This RFC encourages authors to incorporate AI into their authoring workflow rather than rely on manual authorship alone.

The point is not that AI replaces schema authors. It is that AI changes what schema authoring is. The discipline is now curatorial, not generative — and Beckn schemas authored under this RFC are expected to reflect that shift. See [Authoring with AI](#authoring-with-ai) for the concrete workflow.

##### What it all means…

Take the implications of Agent-First Design seriously enough, and the architecture of agentic commerce itself inverts. The dominant pattern of the last few years has been **AI wrapped over tools** — a thin language-model layer placed on top of conventional software systems, orchestrating tool calls, interpreting their structured outputs, and translating between human intent and pre-existing APIs. Under that pattern, the tools are the substrate; AI is the chrome.

The Agent-First architecture flips this. **Tools wrapped over AI** is the configuration this RFC is asking schema authors to design for. In it, AI is the substrate: it produces the semantic output — the description, the inference, the recommendation, the resolution of ambiguity, the interpretation of intent. The tools are the layer that runs *over* that semantic output: validating it, settling it, signing it, persisting it, routing it through the value-exchange lifecycle, and bubbling the result up into the user experience. The tools do not generate meaning; they marshal it.

The schema layer this RFC governs is the substrate on which that inversion stands or falls. If schemas are shaped for tools-over-AI, the consequences ripple outward: a `Resource` becomes a handle into a richly-described entity that the AI substrate already understands; a `Catalog` becomes a curated index of those handles; the toolchain — payment, settlement, signature, registry lookup, fulfilment tracking — wraps around the AI's semantic output rather than feeding it pre-digested rows. Conversely, a schema shaped for AI-over-tools (deep trees of structured attributes, closed enums, rigid hierarchies) commits the protocol to the older configuration and forecloses the newer one. This is why the principles, the anti-patterns, and the context-engineering framing in this RFC matter beyond the schemas they directly govern — they are the leading edge of an architectural inversion, and a Beckn schema authored today is either advancing it or quietly holding it back.

#### Anti-pattern: Overdesigning schemas in an AI-first world

The natural corollary of [Principle 3](#principle-3-agent-first-design) cuts in an unexpected direction. If AI agents are the primary consumers of the schema layer, the instinct to encode every domain nuance as a deeply-nested, strongly-typed tree is **the wrong design reflex** — even though it is the most common one inherited from the pre-AI era. Schema authors who continue to design as if the consumer were a deterministic parser produce schemas that are progressively worse fits for the agents that actually read them.

**Structured modeling is not the anti-pattern.** Many facts genuinely benefit from explicit structured representation: facts that participate in discovery, ranking, orchestration, comparison, matching, indexing, validation, or deterministic interoperability across participants. The anti-pattern is *premature rigidity*, encoding every domain nuance into deep nested trees and closed enums when an open vocabulary or descriptive content would serve the same purpose with more semantic reach. Authors should structure deliberately, not by default, modeling the facts that genuinely participate in deterministic flows and leaving softer attributes to descriptive content.

##### Why tree-shaped schemas hinder AI agents

Pre-AI integrations consumed schemas through fixed-path parsers: each property had a known location, a fixed type, and a fixed meaning, and the receiving code branched on those. A rich tree of `dimensions.height.value` with a `unit` enum and a `precision` constraint was a clean way to expose product geometry to such a client.

AI agents do not consume data that way. Modern language and multimodal models build representations of meaning in **high-dimensional vector spaces**, where the relationship between, for instance, "5.2 cm bezel" and "compact handheld device" emerges from statistical co-occurrence across enormous corpora — not from a parser hard-coded to read a `bezelWidthMm` field. A rigid tree fragments the signal: each leaf becomes a separate context that the model has to recompose, often without enough surrounding language to do so well. Properties that would carry continuous semantic meaning together when expressed as prose end up as disconnected leaves in an opinionated hierarchy.

Put differently: every additional level of nesting, and every fragmented field stripped of its surrounding context, is a small barrier between the agent and the semantic continuity it would otherwise infer. Schemas that were tight and elegant for deterministic parsers are now brittle for the consumers Beckn is actually serving.

##### The shift already in `beckn.yaml`

The core schemas in v2 — `Resource`, `Offer`, `Contract`, `Provider`, `Consideration` — were deliberately authored thin. Each carries an `id`, a `Descriptor`, a domain-specific `Attributes` extension container, and a small number of structural references. This shape is intentional. Compare it to what a maximally-structured prior generation of the same concepts would have looked like: per-attribute objects for every measurable property, nested enums for every categorical decision, an explicit type for every numeric range. v2 removed almost all of that.

The replacement is `Descriptor`. Per `api/v2.0.0/beckn.yaml`, `Descriptor` carries `name`, `shortDesc`, `longDesc`, `thumbnailImage`, `mediaFile[]` (each with `label`, `mimeType`, `uri`), and `docs[]` (signed `Document` references). **This is the highest-bandwidth channel from publisher to agent that Beckn provides.** A well-written `longDesc` paragraph plus a set of product `mediaFile` URLs and a `docs` link to a datasheet carries more usable meaning to a modern agent than a tree of two dozen typed leaves.

##### What this means for schema authoring

When designing a new schema or extending an existing one, authors SHOULD prefer:

- **A short list of properties whose meaning is obvious from the name alone.** If a property's purpose can only be understood by reading three layers of structure around it, it almost certainly belongs in `longDesc`, not in a nested type.
- **A rich, multi-paragraph `Descriptor.longDesc`** that an agent can read as natural language. Long descriptions are not bloat; they are the densest semantic signal a publisher can emit.
- **Image, document, and media URLs in `Descriptor.mediaFile[]` and `Descriptor.docs[]`** populated with content an agent can actually process: product photos, datasheets, specification PDFs, instructional videos. A vision-capable agent extracts more useful meaning from a single product photo than from a `color: enum [RED, BLUE, ...]` field.
- **JSON-LD vocabulary linkages in `vocab.jsonld`** rather than restrictive enums in `schema.json`. An open semantic linkage (`rdfs:subClassOf`, `skos:related`, `skos:broader`) gives the agent a reasoning path; a closed enum gives it a hard wall.

And SHOULD avoid:

- **Deep nesting "for cleanliness".** A `Product.specifications.physical.dimensions.length.value` style chain is the canonical anti-pattern. The same data placed inside `longDesc` as natural prose ("5.2 cm wide, weighs 200 g") is more useful to every agent that processes it.
- **Restricting types beyond what is genuinely needed for validation.** A `weight` field constrained to `integer ≥ 1` will reject "around 250 grams" — exactly the kind of value a merchant or agent might provide. If the value participates in arithmetic (e.g. shipping-cost calculation), keep the constraint. If it is informational, prefer a free-text representation alongside, or move it entirely into `Descriptor`.
- **Enums where vocabulary linkages would do.** `enum [SMALL, MEDIUM, LARGE]` forces every agent to interpret the literal strings without context. A vocabulary term with `rdfs:label` and `rdfs:comment` is self-describing — and other networks can subclass it.
- **Repeating in `Attributes` what is already in `longDesc`.** Duplication forces the publisher to keep two sources of the same truth in sync, and the agent to reconcile them on read. Pick one home for each fact — usually `longDesc` for descriptive facts, `Attributes` for facts that participate in machine-comparable filtering or arithmetic.

##### Worked comparison — a portable Bluetooth speaker

Suppose the use case is publishing a portable speaker product. A pre-AI design reflex might author a dense, deeply-nested schema:

```yaml
# Anti-pattern: dense tree, opinionated structure, closed enums.
PortableSpeakerProduct:
  id: string
  name: string
  brand:
    name: string
    country: string
  dimensions:
    length: { value: number, unit: enum [MM, CM, INCH] }
    width:  { value: number, unit: enum [MM, CM, INCH] }
    height: { value: number, unit: enum [MM, CM, INCH] }
  weight:   { value: number, unit: enum [G, KG, OZ, LB] }
  color:    enum [RED, BLUE, GREEN, BLACK, WHITE, SILVER, OTHER]
  batteryHours: integer
  waterResistance:
    rating: enum [IPX4, IPX5, IPX6, IPX7, IPX8]
  bluetoothVersion: enum [BT_4_0, BT_4_2, BT_5_0, BT_5_1, BT_5_2, BT_5_3]
  driverConfiguration:
    woofer:   { count: integer, sizeMm: number }
    tweeter:  { count: integer, sizeMm: number }
    radiator: { count: integer, sizeMm: number }
  features:
    - name: string
      value: string
```

An agent processing this Resource has to reassemble more than a dozen disconnected leaves into a coherent representation, and is forced into closed enums (`color`, `bluetoothVersion`, IP rating) that lose information at the boundary. Every new colour, every new Bluetooth revision, every new IP rating triggers a schema bump.

The Beckn-aligned design uses the canonical `Resource` from `beckn.yaml` with a thin `Attributes` extension and a rich `Descriptor`:

```json
{
  "id": "spk-aurora-portable-mini",
  "descriptor": {
    "name": "Aurora Portable Mini Bluetooth Speaker",
    "shortDesc": "Pocket-sized 360° Bluetooth speaker with 12-hour battery and IPX7 water resistance.",
    "longDesc": "The Aurora Portable Mini is a 200-gram pocket speaker that delivers omnidirectional sound through a dual-driver configuration — one 40 mm woofer and one 20 mm tweeter — paired with a passive bass radiator. The speaker is rated IPX7, meaning it is fully submersible in fresh water to one metre for up to thirty minutes, and supports Bluetooth 5.3 with Auracast multi-device pairing. Battery runtime is up to twelve hours at moderate volume, recharged in 90 minutes via USB-C fast charging. The aluminium chassis is finished in matte midnight-blue (the brand's Aurora Blue) with a recycled-fabric speaker grille. Suitable for outdoor and bathroom use; not designed for prolonged marine saltwater immersion.",
    "thumbnailImage": "https://cdn.merchanthub.ae/products/aurora-mini-front-256.jpg",
    "mediaFile": [
      { "label": "Front view",     "mimeType": "image/jpeg", "uri": "https://cdn.merchanthub.ae/products/aurora-mini-front.jpg" },
      { "label": "Side view",      "mimeType": "image/jpeg", "uri": "https://cdn.merchanthub.ae/products/aurora-mini-side.jpg" },
      { "label": "Lifestyle shot", "mimeType": "image/jpeg", "uri": "https://cdn.merchanthub.ae/products/aurora-mini-lifestyle.jpg" },
      { "label": "Feature reel",   "mimeType": "video/mp4",  "uri": "https://cdn.merchanthub.ae/videos/aurora-mini-feature.mp4" }
    ],
    "docs": [
      { "label": "Technical datasheet", "mimeType": "application/pdf", "url": "https://cdn.merchanthub.ae/datasheets/aurora-mini-spec.pdf" }
    ]
  },
  "resourceAttributes": {
    "@context": "https://souqconnect.ae/v2/context.jsonld",
    "@type": "audio:PortableSpeaker",
    "genericName": "Portable Bluetooth Speaker",
    "manufacturerName": "Aurora Audio Industries LLC",
    "countryOfOrigin": "AE"
  }
}
```

Notes on the differences:

1. **`Descriptor` carries the bulk of the semantic payload.** `longDesc` is a paragraph of natural-language prose, not a set of disconnected leaves. An agent reads it directly, with the relationships between weight, water resistance, driver configuration, and recommended use already in linguistic proximity. Specifications that a pre-AI schema would have hoisted into structured fields — weight, IP rating, Bluetooth version, battery life — stay in the prose where their relationships to each other are preserved.
2. **`mediaFile[]` and `docs[]` give multimodal agents real signal.** A vision-capable model extracts more useful information from a single product photo than from a `color` enum; a multimodal model that can read PDFs draws the full technical specification from the linked datasheet without the schema enumerating each spec line.
3. **`resourceAttributes` is reserved for facts mandated by law or trust.** Only `genericName`, `manufacturerName`, and `countryOfOrigin` are surfaced as structured attributes, and each is there because a *statutory* obligation — consumer-protection labelling, manufacturer disclosure, country-of-origin declaration — requires it to be machine-comparable, not because a descriptive nuance about the product needed a typed home. Everything else lives in `Descriptor`.
   > **Recommendation.** Treat `Attributes` as the surface for **regulatory, legal, and compliance facts** — the small set of fields a Beckn network or its regulator requires for filtering, audit, or settlement (statutory labelling, certifications, tax codes, hazard classes, KYC tokens, age-restriction flags). Resist the urge to add structured fields for marketing or descriptive content; that content belongs in `Descriptor`. A useful rule of thumb is to ask, for each candidate attribute: *"if this fact were missing, would a regulator, an auditor, or the network's settlement layer object?"* If yes, structure it. If no, write it into `longDesc` or link it via `mediaFile[]` / `docs[]`.
4. **Vocabulary linkage replaces enums.** The `audio:PortableSpeaker` IRI declares `rdfs:subClassOf` `schema:Product` and `rdfs:subClassOf` `audio:Loudspeaker` in `vocab.jsonld`. An agent that has never seen `audio:PortableSpeaker` follows the `subClassOf` chain and processes the resource as a speaker, then as a product — without the schema having to enumerate every possible category code.

##### Alignment with modern discovery paradigms (non-normative)

The case for thin `Attributes` and rich `Descriptor` is reinforced by where consumer product discovery has actually moved. Industry tracking in 2026 puts **more than 60% of consumer product discovery on short-form-video and social platforms** rather than on traditional retail catalogues. Live-commerce sales are projected to exceed **$1 trillion in Asia alone** in 2026; social-commerce gross merchandise value on the leading short-form-video platform alone is on track for roughly **$87B** at ~56% year-over-year growth; the global shoppable-video market is projected to reach **$55B by 2027**. The strongest-performing brands broadcast a single product simultaneously across their own website and across the major short-form-video, photo-social, and long-form-video platforms, with shoppable-video aggregators stitching those clips into a unified buying surface. Several major consumer platforms have shipped or announced AI shopping agents whose job is precisely to traverse those multi-platform product representations on the consumer's behalf.

This is a profound shift in *what a product is* for the purposes of discovery. The product no longer exists as a static row in a merchant's database with a fixed set of attribute columns. **It exists as a living organism distributed across the platforms where its potential customers already are**: a fifteen-second short-form video demo, a long-form video unboxing, a creator-led photo-social reel, a live-shopping session on a regional commerce platform, an audio review on a podcast, a sponsored short on a streaming service. The merchant's database holds, at most, the *handles* — the URLs, the embed codes, the campaign references — that point to where the product currently lives in the consumer's actual attention.

Beckn's schema layer has to speak this reality natively, or it will be bypassed by the agents that increasingly mediate consumer discovery. A `Resource` that publishes a tightly-typed tree of `dimensions`, `color`, and `bluetoothVersion` is describing the product as a database row. A `Resource` whose `Descriptor.mediaFile[]` carries the short-form-video demo URL, the long-form unboxing, the creator-led social reel, and the audio review, whose `Descriptor.docs[]` links the manufacturer datasheet and any verifiable credentials, and whose `longDesc` is the merchant's own narrative voice for the product, is describing the product as it actually exists in the market. The first is a static description; the second is a network of handles into the living organism. Contemporary AI shopping agents — whose job is precisely to traverse those handles, watch the videos, read the captions, and synthesise a recommendation — are built for the second shape, not the first.

The architectural implication runs deeper than schema fields. Where a traditional catalog assumed a `Catalog` object enumerated every product as structured data, an agent-era catalog increasingly looks like an indexed *map of handles* — pointers into platforms the publisher does not own and does not need to replicate. A PN may legitimately publish a `Catalog` whose `Resource` entries are little more than an `id`, a `Descriptor.name`, a `longDesc`, and a `Descriptor.mediaFile[]` array of social-platform URLs. That `Resource` is not impoverished — it is correctly shaped for a world where the product's semantic richness lives at the URLs, not in the publisher's database. Schemas in `beckn/schemas` and `beckn/DEG` SHOULD be reviewed for whether they make this multi-surface description easy to populate; new schemas that leave no good home for social URLs, live-shopping session references, or creator-led media are encoding a pre-2020 view of commerce into the protocol.

The paradigm shift this describes is non-normative for the present revision of this RFC — but it is the direction every empirical signal in the consumer surface is pointing, and the [Context Engineering](#context-engineering) RFC under preparation is expected to formalise the protocol-layer consequences (catalog publication as handle-aggregation, network-level retrieval across external surfaces, trust and provenance of off-platform media). For now, schema authors are asked to **design `Descriptor` as if it were the canonical map of where the product lives**, not as a verbose label for an entry in a private database.

##### Worked comparison — `GroceryItem` today, evolving forward

The existing [`GroceryItem`](https://github.com/beckn/schemas/tree/main/schema/GroceryItem/v2.0) schema in `beckn/schemas` carries nested sub-objects for `identity`, `physical`, and `nutrition`. That structure was a reasonable design at the time and remains valid. Under Agent-First Design, however, the productive evolution is to **thin the structured tree and thicken `Descriptor`**.

A v2.1 of the schema might:

- **Demote `physical` sub-fields into `longDesc` prose** for most cases — *"500 g pack of premium long-grain basmati rice; pack dimensions roughly 22 × 8 × 4 cm; aged for two years before milling"* — while keeping `weightGrams` as a top-level numeric attribute for filtering.
- **Move the entire `nutrition` block into a `docs[]` reference** to the regulatory nutrition-facts PDF, with a single top-level boolean (`hasNutritionLabel`) if filtering on presence is useful. A multimodal agent reads the PDF directly; a non-AI client falls back to the link.
- **Replace `regulatoryCategory` enum-style values with a JSON-LD term** (e.g. `souqconnect:HalalCertified`) that subclasses `beckn:productCategory`, so new regional categories can be added without schema bumps.

The same product, in v2.0 vs. an Agent-First v2.1, looks structurally smaller and semantically richer.

##### Where to draw the line

This is not a licence to abandon all structure. Properties that participate in **arithmetic** (price, quantity, duration, weight where used for shipping), in **deterministic filtering** (status codes with small, stable, semantically-loaded vocabularies such as `ACTIVE` / `CANCELLED` / `COMPLETED`), or in **cross-resource reference** (`coveredResourceId`, `compatibleWith[]`) belong in the structured `Attributes` container. The discipline is to ask, for each candidate property: *would an agent that has read a well-written `longDesc` and looked at the linked images still need this field in structured form, or is it already implicit?* If the latter, demote it to `Descriptor`.

##### The trajectory

As AI agents become more central to value-exchange, the productive direction for the Beckn schema layer is to get **leaner**, not richer. Future schema contributions to `beckn/schemas` and `beckn/DEG` are expected to follow this trajectory: thin `Attributes` containers, dense `Descriptor` content, JSON-LD vocabulary that opens up the semantic graph rather than enums that close it down. Authors who continue to layer nested structure under the well-meaning belief that it improves machine readability are working against the architecture of the consumers their schemas are actually serving.

Taken to its logical conclusion, the trajectory points somewhere stronger than "leaner `Attributes`". **An ideal Agent-First Beckn schema may not need to extend `Resource`, `Contract`, or `Offer` at all.** Everything an agent must understand about the entity — what it is, what it looks like, what its specifications are, what its terms are, what evidence backs it — can live inside the `Descriptor`: prose in `longDesc`, vision-ready imagery in `mediaFile[]`, machine-readable evidence in `docs[]`, and an open semantic anchor via the JSON-LD `@type` on the parent object. In that world, what looked like a missing schema is more often a missing paragraph in `longDesc` or a missing PDF in `docs[]`. **Context engineering takes precedence over object-oriented design** — see the next subsection for the framing.

#### Context Engineering

The Overdesigning anti-pattern points at a deeper architectural shift that Beckn schema authors are increasingly asked to internalise. The discipline that governs *what an AI agent sees, when, and in what form* has acquired its own name in the wider AI engineering community: **context engineering**.

##### What context engineering is

Context engineering is the discipline of curating and maintaining the optimal set of tokens an AI model operates on during inference, including the information that arrives there outside the explicit prompt. It is the explicit successor to prompt engineering. Where prompt engineering asked *"what is the right instruction to send the model?"*, context engineering asks *"what is the right configuration of information for the model to act on?"*

The shift matters because every recent empirical study of LLM performance points the same way: model accuracy degrades as the context window fills with low-signal content — a phenomenon now widely referred to as **context rot**. A canonical industry framework groups context-engineering strategies into four patterns that have become the lingua franca of the field:

| Pattern | What it means |
|---|---|
| **Write** | Store information outside the immediate context so an agent can retrieve it later (scratchpads, persistent memory, external knowledge stores). |
| **Select** | Pull precisely the right items into context when needed (semantic retrieval, tool selection, vocabulary lookup). |
| **Compress** | Keep only the tokens that carry signal (summarisation, trimming, distillation). |
| **Isolate** | Split work across sub-agents, sandboxes, or layered contexts so no single agent drowns in the full payload. |

These patterns are the operational vocabulary in which AI-engineering teams now talk about building reliable agents. Beckn schema authors authoring for those agents inherit the vocabulary whether they use the term or not.

##### Why this is a schema concern, not just an application concern

It is tempting to read context engineering as an application-layer concern — something a CN or PN does inside its agentic orchestration code. That reading is incomplete. **Every choice a schema author makes is a context-engineering choice at the protocol layer**, because the schema dictates the shape of the context that every downstream agent must construct from a Beckn payload. Concretely:

- A schema that puts product semantics in a 2000-character `longDesc` **writes** high-density context to a single field that agents can select wholesale.
- A schema that fragments the same semantics across forty nested leaves forces every downstream agent to **select** and **compress** before it can reason — and most will do this badly, with each agent making slightly different choices and producing slightly different downstream behaviour.
- A schema that links a datasheet via `Descriptor.docs[]` **isolates** the bulky technical detail outside the immediate context, available to be pulled in only when a specific agent task requires it.
- A `vocab.jsonld` that declares `rdfs:subClassOf` linkages gives agents a **select** path through the semantic graph; an enum gives them a closed wall.

Read this way, the Beckn schema layer is not a passive data contract — it is an explicit context-engineering surface that publishers and protocol authors share with the agents they intend to serve.

##### Context engineering informs schema design

The implication, taken to its logical conclusion, is the one foreshadowed in [The trajectory](#the-trajectory) above. When a contributor reaches for a new domain-specific `Attributes` schema, the design question is no longer *"what is the right class hierarchy for this concept?"* It is *"what is the right configuration of context to put in front of an agent that has to act on this concept?"*

These two questions have very different answers. The first leads to taxonomies, inheritance trees, and enum proliferation — the natural output of object-oriented design as practised by a generation of API authors raised on it. The second leads to dense descriptive content, well-curated media, open vocabulary links, and a `Descriptor` that does most of the semantic work — the shape that contemporary AI agents are best at consuming. In the schema layer, **context engineering should inform schema design**, alongside the structural rigour that deterministic validation, indexing, SDK generation, and non-agentic consumers still require. Authors should bring the same rigour they previously gave to class hierarchies to the curation of `Descriptor` content, and should reserve structured `Attributes` for the facts that genuinely participate in arithmetic, deterministic filtering, validation, comparison, or cross-resource reference.

##### A separate RFC is underway

The protocol-layer implications of context engineering reach well beyond schema design. Catalog publication and subscription, the `schemaContext` array on the Beckn envelope, JSON-LD context layering, Fabric-side retrieval, registry lookup as part of an agent's pre-flight context construction, and the lifecycle of `Descriptor` content as it flows between CNs, PNs, and downstream agents are all context-engineering concerns at the network level. A separate RFC, **Context Engineering for Fabric-Enabled Ecosystems**, is in preparation under the same NFH governance. It will define the protocol-level patterns (write / select / compress / isolate) as they apply to the Beckn Fabric and the broader open-network architecture.

This Schema Design Guide stays scoped to the schema-author side of that picture; the cross-layer concerns are deferred to the forthcoming RFC. Authors of new schemas SHOULD nonetheless author with the protocol-level RFC's direction in mind: a schema that respects [The trajectory](#the-trajectory) above is already aligned with where context-engineering guidance for Beckn is heading. For the contemporary industry framing that informs this subsection, see the [References](#references) section at the end of this RFC.

---

### Why do schemas need to be created or changed

When a contributor encounters a perceived gap in the schema layer, the response SHOULD follow the order of precedence below. Authors and reviewers SHOULD attempt each option in order and only proceed to the next when the previous is genuinely insufficient. This precedence is a heuristic that guards against unnecessary schema proliferation in mature domains; emerging domains where stable abstractions have not yet settled MAY justify direct creation of a new schema with explicit working-group review.

> **Order of precedence:** 1. Abstraction → 2. Composition → 3. Extension → 4. Creation.
>
> Authoring a new schema is the last resort, not the first.

Before any of these options is invoked, contributors MUST check [schema.beckn.io](https://schema.beckn.io) to verify that no existing schema already covers the use case. Duplicate or overlapping schemas fragment the semantic layer and undermine cross-network interoperability.

#### 1. Abstraction (preferred)

The first response to a perceived schema gap is to ask whether the use case can be expressed by **abstracting an existing schema upward** to a broader concept that subsumes the new requirement. Per [Principle 2: Unification over Standardization](#principle-2-unification-over-standardization), the ecosystem converges on increasingly general schemas. If `Television` exists and the use case is `Monitor`, the right move is often to abstract their shared attributes upward into `DisplayDevice` (or an existing parent like `ConsumerElectronics`) and let both be expressed as specializations — not to author a parallel `Monitor` schema.

Abstraction is preferred because it strengthens the shared vocabulary rather than fragmenting it. Every consumer that already understands the parent concept can immediately process the new specialization with no additional knowledge.

#### 2. Composition

If abstraction does not fit — the use case is genuinely a combination of distinct existing concepts, not a specialization of one — the next response is **composition** using the primitives already provided by `api/v2.0.0/beckn.yaml`. A bundle, kit, combo offer, or related-resources scenario MUST be expressed via:

- `Catalog.resources[]` and `Catalog.offers[]`
- `Offer.resourceIds` and `Offer.addOns[]` (where each `AddOn` is `oneOf [Resource, Offer]`)
- `Offer.considerations[]` for pricing or value terms
- `Resource.id` references inside `resourceAttributes` for inter-resource relationships

A new schema name MUST NOT fuse multiple existing concepts (anti-patterns like `XWithY`, `XAndY`, `XPlusY` are rejected at review). See [Worked example — Composing a combo product](#worked-example--composing-a-combo-product) for the full pattern.

#### 3. Extension

When neither abstraction nor composition fits, the next option is to **extend an existing schema** by adding a property, enum value, or descriptive clarification that closes the gap. Extending is preferred over creating because it preserves the canonical concept and the IRI identity that downstream consumers already process.

An extension is justified when:

- A new property is needed on an existing object type that is already represented in the schema (for example, adding a regulatory certification field to an existing healthcare resource schema).
- A new enumerated value is needed for an existing property (for example, a new payment method code in a financial schema).
- The description or constraint on an existing term needs correction or clarification without changing its meaning.

Extensions MUST NOT change the meaning of any existing term. A change that requires existing consumers to reinterpret a term they already process is a breaking change governed by the breaking-change requirements in [Versioning requirements](#versioning-requirements).

#### 4. Creation (last resort)

A new schema artifact is justified only when **none** of abstraction, composition, or extension can express the use case. Authors who arrive at this option MUST document in the proposal Discussion which of the prior three options were considered and why each was insufficient. A new schema proposal that does not show this reasoning SHOULD be returned to the author.

The most common legitimate reasons for a new schema are:

- **New domain entry.** A domain not previously represented in the Beckn ecosystem (for example, water distribution, carbon credits, legal services) requires a vocabulary that has no overlap with existing domain schemas.
- **New cross-domain standard.** An industry standard body (for example, GS1, HL7, IEC) has published a new vocabulary that Beckn participants in that domain are expected to reference, and no existing Beckn schema maps it.
- **New shared use-case pattern.** A pattern that appears across multiple independent networks in the same domain (for example, a common structure for slot-based appointment booking, or a standard format for regulated product certifications) needs a canonical schema so all networks can share the same vocabulary rather than each defining their own.

The requirement MUST also not be addressable by:

1. an on-Fabric implementation change (a network policy, NFO configuration, or application-layer rule), or
2. an adapter spec change (a translation layer between a domain-specific standard and the Beckn envelope).

#### What does NOT justify a schema change

The following are NOT sufficient justification for a new or modified schema, and proposals on these grounds SHOULD be rejected at the discussion stage:

- **A single network's internal requirement.** If the semantic need exists only within one NFO's network boundary and will not be referenced across networks, it belongs in a network-specific `context.jsonld` or `vocab.jsonld`, not a shared published schema.
- **Replication of an existing term under a different name.** Creating a synonym for an existing, well-named term fragments the vocabulary and breaks cross-network semantic alignment.
- **Encoding business logic or policy.** Schema artifacts define data shapes and vocabulary. They MUST NOT encode rules about what values are valid in a given context, what sequences of states are legal, or what responses are required. Those concerns belong in the Policy Layer.
- **Making an optional field required.** Changing the optionality of an existing field is a breaking change and cannot be addressed by extending the schema alone.

---

### Where schemas are published

The subsections that follow describe operational publication policy (which repositories host schemas for which domains, and how the Beckn Schema Registry indexes them) rather than schema design principles. The principles are in earlier sections of this RFC.

#### The Beckn Schema Registry

The Beckn Schema Registry at [schema.beckn.io](https://schema.beckn.io) is the canonical discovery index for all published Beckn schema artifacts. It is managed by the Networks for Humanity Foundation (NFH) through a schema administration console. The registry does not host schema files directly — it sources and indexes them from the `main` branches of recognized repositories. When a schema is merged to `main` in a recognized repository, a sync is triggered on the schema administration console, which publishes the artifact on the website.

Implementers SHOULD use the registry as their primary point of discovery. The registry ensures that only artifacts from recognized, governance-authorized sources at their formally released state are surfaced.

#### The `beckn/schemas` repository

The `beckn/schemas` repository at [github.com/beckn/schemas](https://github.com/beckn/schemas) is the primary publication venue for all domain-specific schema packs intended for broad ecosystem reuse. This includes schemas for all domains **except** energy. Schema packs are currently placed in the `schema/*` directory of this repository (full path: `beckn/schemas/schema/<SchemaName>/<version>/`). Schemas on the `main` branch of this repository are sourced and indexed by the Beckn Schema Registry.

> **Note on directory naming.** The current directory name `schema/` is acknowledged to be a poor choice — both the repository name and the directory name use the same noun. A future re-organisation of `beckn/schemas` is likely to introduce a more elegant naming scheme (for example, a structure that groups schema packs under a domain-neutral folder hierarchy). Schema authors and tooling implementers SHOULD watch the `beckn/schemas` repository for the announcement of this change and update their paths accordingly when it lands.

Schema packs in `beckn/schemas` MUST conform to the schema pack structure defined in [Schema pack structure](#schema-pack-structure) and MUST have passed the contribution process defined in [Contribution process](#contribution-process).

#### The `beckn/DEG` repository

The `beckn/DEG` (Digital Energy Grid) repository at [github.com/beckn/DEG](https://github.com/beckn/DEG) is the publication venue exclusively for **energy domain** schemas. It is governed by the DEG Working Group and was conceived by FIDE in collaboration with the International Energy Agency (IEA). Energy schema packs are placed in the `specification/schema/*` directory of this repository (full path: `beckn/DEG/specification/schema/<SchemaName>/<version>/`). Schemas on the `main` branch of `beckn/DEG` are sourced and indexed by the Beckn Schema Registry alongside those from `beckn/schemas`.

The `beckn/DEG` venue is a domain-specific governance arrangement reflecting the Digital Energy Grid's relationship with the International Energy Agency (IEA) and the FIDE/IEA collaboration that established it. It is not a precedent that domains should generally expect: the default publication venue for any new domain is `beckn/schemas`. A federated venue analogous to `beckn/DEG` MAY be considered for a future domain only with explicit Core Working Group approval and a clear demonstration that the domain's governance requires a separate working group and venue.

> **Note on directory naming.** As with `beckn/schemas`, the directory layout in `beckn/DEG` may be reorganised in a future release for greater clarity. Authors SHOULD watch the repository for announcements.

All non-energy domain schemas MUST be published to `beckn/schemas`, not to `beckn/DEG`.

#### NFO schema registries — NOT RECOMMENDED

The creation and publication of standalone, NFO-scoped schema artifacts is **NOT RECOMMENDED**. NFOs and implementers SHOULD instead:

1. **Analyze the use case carefully** and abstract it into its underlying domain-neutral form. A use case that appears locally unique on first inspection almost always shares its underlying structure with use cases already addressed elsewhere in the ecosystem.
2. **Search [schema.beckn.io](https://schema.beckn.io)** for an existing schema in `beckn/schemas` or `beckn/DEG` that already covers the abstraction. Use the existing schema instead of authoring a parallel one.
3. **Contribute extensions upstream.** If an existing schema is close to what is needed but lacks a property or vocabulary term, raise that extension as a contribution to `beckn/schemas` or `beckn/DEG` through the contribution process defined in this RFC.
4. **Propose new schemas upstream.** If no existing schema covers the use case, propose a new shared schema — not a private one.

Custom NFO-scoped schemas fragment the semantic layer, undermine cross-network interoperability, and force every counterparty to learn an NFO-specific vocabulary. The very objective of the Beckn schema registry is to allow domain semantics to evolve **once**, in the open, and be reused across networks. NFOs who prefer the short-term convenience of forking the vocabulary will, over time, recreate the isolated semantic islands that Beckn Protocol was explicitly designed to eliminate.

In the rare case where an NFO must run experimental schema work that has not yet completed the contribution process, the experimental artifact MUST be hosted on the NFO's own infrastructure, MUST NOT carry a `@context` URI that resolves to `schema.beckn.io` or any `beckn.org` domain, and MUST be retired once the corresponding upstream contribution is merged. A bounded transition window MAY be observed where existing integrations continue to resolve the NFO-hosted artifact alongside the upstream version; the NFO SHOULD document the migration window with a fixed end date and SHOULD migrate consumers within that window. Experimental artifacts MUST NOT be relied upon for production traffic between independent networks beyond the transition window.

#### Publication venue selection

The venue for a schema artifact is determined by its domain:

| Domain / scope | Repository / venue | Directory | Indexed by registry? |
|---|---|---|---|
| Energy | `beckn/DEG` | `specification/schema/*` | Yes |
| All other domains (shared ecosystem use) | `beckn/schemas` | `schema/*` | Yes |
| Network-local terminology / regional vocabulary | NFO-hosted `context.jsonld` + `vocab.jsonld` (NOT a forked schema), with the URL registered under the NFO's namespace on [dedi.global](https://dedi.global) | NFO-defined | No |
| Experimental / pre-proposal | Contributor's fork or staging environment | N/A | No |

A schema MUST NOT be merged to `main` in any shared venue before completing the contribution process, regardless of urgency.

> **dedi.global registration for network vocabularies.** Where an NFO publishes a network-specific `context.jsonld` and/or `vocab.jsonld` on its own infrastructure, the canonical URL of each artifact MUST be added as a registry entry under the NFO's namespace on [dedi.global](https://dedi.global). This is what allows counterparties on other networks to resolve the network's vocabulary deterministically and to verify, via the trust layer, that the URL is the one authorised by the NFO. See [How NFOs can help](#how-nfos-can-help) for the full pattern.

---

### How NFOs can help

NFOs are the operational backbone of a Beckn network. While they SHOULD NOT publish standalone schemas (see [NFO schema registries — NOT RECOMMENDED](#nfo-schema-registries--not-recommended)), there are two distinct ways they can contribute meaningfully to the schema layer without fragmenting it.

#### Network-specific JSON-LD context and vocabulary

> **Recommended pattern.** Where a network has legitimate localisation needs, NFOs SHOULD layer JSON-LD context and vocabulary on top of the domain-agnostic schemas — never fork them.

The legitimate need that often motivates NFO-scoped schemas — adapting the protocol to local terminology, regional regulatory categories, language localization, or NFO-internal naming — is best addressed not by forking the schema but by layering JSON-LD context and vocabulary on top of the domain-agnostic schema. This is the architecturally correct way to localize a Beckn network.

An NFO SHOULD publish two artifacts on its own infrastructure:

1. **A network-specific `context.jsonld`** that maps network-local term aliases — in any language, region, or NFO-specific naming convention — to the canonical IRIs of the domain-agnostic schema in `beckn/schemas` or `beckn/DEG`.
2. **A network-specific `vocab.jsonld`** that defines region-specific category codes, classification values, or controlled-vocabulary terms whose meaning is recognized only within the network's region. Each such term MUST link back to the most specific superset concept in the domain-agnostic vocabulary using `rdfs:subClassOf`, `skos:broader`, or an equivalent JSON-LD linkage.

The network MUST NOT publish a redefinition of any property or class that already exists in the domain-agnostic vocabulary. Network-specific artifacts EXTEND the domain-agnostic vocabulary; they do not replace it.

The URL of each published artifact MUST be registered under the NFO's namespace on [dedi.global](https://dedi.global) so that counterparties can resolve and trust it. See the row for network-local terminology in [Publication venue selection](#publication-venue-selection).

On the wire, **all messages exchanged on a Beckn network MUST use the domain-agnostic vocabulary**. The network-specific context is applied only at the **edges** — by the CN before sending and by the PN after receiving — using standard JSON-LD expansion and compaction. This gives every participant the freedom to use the vocabulary that fits its internal system without compromising cross-network interoperability.

This layering allows the protocol, the domain-agnostic schemas, the domain-specific schemas, and the network-specific vocabularies to evolve **independently with no code changes at any layer**. It is the classic JSON-LD architectural elegance applied to a federated commerce protocol. A worked end-to-end example is provided in [Worked example — UAE retail network](#worked-example--uae-retail-network).

---

### Who can publish and extend schemas

#### Core Working Group

The Core Working Group is the sole authority for changes to the core data model defined in [NFH-004](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Core_Data_Schema.md). Changes to core objects — adding or removing fields from `Context`, `Catalog`, `Contract`, `Intent`, `Offer`, `Resource`, `Commitment`, `Consideration`, `Performance`, `Settlement`, `Participant`, or `Descriptor` — require CWG approval through the RFC process defined in [NFH-010](./RFC_Authoring_Guide.md).

The CWG also serves as the final governance authority for all artifacts published to `beckn/schemas`. Day-to-day review is performed by the maintainers of the relevant repository under standard open-source contribution practices. The CWG retains the right to reject any artifact that introduces ecosystem-wide semantic risk.

#### DEG Working Group

The DEG Working Group is the sole domain-specific working group recognized by this RFC. It exists because the Digital Energy Grid initiative was founded and is housed under the Networks for Humanity Foundation, with a specific set of maintainers, subject matter experts, and reviewers documented in the `beckn/DEG` repository. The DEG Working Group reviews and approves all schema packs published to `beckn/DEG`.

No equivalent domain-specific working group exists for any other vertical. Mobility, healthcare, financial services, retail, agriculture, and every other non-DEG domain are maintained in `beckn/schemas` as a standard open-source project — open to contributions from the global community and reviewed by the repository's maintainers. Contributors with deep domain expertise are encouraged to step forward as maintainers through the standard open-source path, but no formal domain-specific governance body is required to propose, review, or approve a schema.

#### Network Facilitator Organizations (NFOs)

NFOs SHOULD NOT publish standalone, NFO-scoped schemas. Their primary obligation toward the schema layer is to **use and extend** the shared domain-agnostic schemas in `beckn/schemas` and `beckn/DEG`, contributing extensions upstream through the contribution process where existing schemas are insufficient.

NFOs MAY publish **network-specific `context.jsonld` and `vocab.jsonld`** files on their own infrastructure to localize terminology, expose region-specific category codes, or provide language aliases. These artifacts MUST link to the canonical domain-agnostic vocabulary and MUST NOT redefine its terms, as described in [How NFOs can help](#how-nfos-can-help). They do not require CWG approval, but they MUST conform to JSON-LD 1.1 processing rules so that any conformant JSON-LD processor can interpret payloads that reference them, and their URLs MUST be registered under the NFO's namespace on [dedi.global](https://dedi.global).

NFOs who discover, during the design of a network-specific vocabulary, that their need cannot be expressed as an alias or a subclass of an existing domain-agnostic concept MUST raise the gap as a contribution to `beckn/schemas` or `beckn/DEG`, not work around it with an NFO-scoped schema.

##### NFOs as external collaborators on `beckn/schemas`

To prevent bottlenecks in the evolution of the shared schema layer, **NFOs operating Beckn-conformant networks SHOULD be added as external collaborators to the `beckn/schemas` repository**. As external collaborators, NFO representatives obtain the rights to maintain, triage, and evolve the schemas most relevant to the networks they operate — opening Issues, reviewing PRs, labelling Discussions, and approving merges in the areas of their domain expertise.

This collaborator model is essential, not optional. It distributes day-to-day stewardship of the schema layer to the people who actually run networks and feel the operational impact of every schema decision first. **The Core Working Group does NOT review every schema PR.** The CWG's role is narrower and more focused: to uphold and enforce the **design principles** documented in [Design principles for schema authors](#design-principles-for-schema-authors) and in [NFH-009 Specification Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md). As long as a contribution adheres to the design principles, the repository's maintainers — including NFO collaborators — have the authority to merge it without waiting for CWG sign-off.

An NFO that wishes to be added as an external collaborator MUST nominate one or more representatives, document the schemas they intend to steward, and apply via Issue in the target repository. Removal of collaborator privileges follows the standard open-source path: extended inactivity, repeated design-principle violations, or governance-policy breach.

The same model applies in `beckn/DEG`, where the DEG Working Group already operates as the de facto collaborator pool — NFOs running energy networks SHOULD nominate representatives to participate in that working group on the same terms.

##### Promotion to schema.beckn.io administrator

NFOs that have demonstrated sustained active contribution to `beckn/schemas` or `beckn/DEG` and consistent adherence to the protocol and schema design principles MAY be promoted by the Core Working Group to **administrators on the `schema.beckn.io` administration console**. Administrator privileges include the ability to trigger registry syncs, manage indexing metadata for the schemas they steward, and curate the registry's discovery surface for their domain.

Promotion is at the discretion of the CWG and is awarded for **track record**, not tenure: an NFO that has merged conformant contributions, helped triage Issues and PRs, and consistently upheld the design principles is the kind of collaborator the CWG looks to elevate. Administrator status MAY be revoked under the same governance criteria that govern collaborator removal — extended inactivity, repeated design-principle violations, or governance-policy breach.

#### Community contributors

Any member of the Beckn community may propose a new schema or an extension to an existing schema by following the contribution process. Community contributors do not have direct merge authority — their proposals are reviewed by the maintainers of `beckn/schemas` (for all non-DEG domains) or by the DEG Working Group (for `beckn/DEG`), with CWG oversight.

Community contributors MUST have an active GitHub account and be invited as external collaborators on the relevant repository, or submit proposals through the GitHub Discussion and Issue flow without requiring direct repository access.

#### Summary of authorization by venue

| Venue | Who may propose | Who may approve and merge |
|---|---|---|
| `protocol-specifications-v2` core model | Any contributor | CWG only, via RFC process |
| `beckn/schemas` (all non-DEG domains) | Any contributor | `beckn/schemas` maintainers, with CWG oversight |
| `beckn/DEG` (energy domain only) | Any contributor | DEG Working Group, with CWG oversight |
| Network-specific `context.jsonld` / `vocab.jsonld` (NOT a schema) | NFO | NFO governance |
| Standalone NFO-scoped schema | NOT RECOMMENDED — see [NFO schema registries — NOT RECOMMENDED](#nfo-schema-registries--not-recommended) | N/A |

---

### How schemas are created and extended

#### Design principles for schema authors

Schema authoring is a design discipline. Authors of new or extended schemas in `beckn/schemas` or `beckn/DEG` MUST follow the design principles below. These principles are normative for all contributions and are the criteria by which maintainers — including NFO external collaborators — and the CWG evaluate every schema PR.

The full normative authoring rules are defined in [NFH-009 Specification Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md). This subsection summarizes the principles most directly relevant to schema authoring; the Design Guide remains authoritative for any detail not reproduced here.

##### Core design principles

1. **Semantic stability.** A schema's names and IRIs MUST preserve stable meaning across versions. Once `priceValue` means *the numeric price of an offer*, it MUST mean exactly that in every subsequent version until a major version explicitly retires the term.
2. **Composable evolution.** New terms MUST extend, not duplicate or redefine, existing semantics. If `Resource` already exists, do not introduce `Asset` to mean the same thing — extend `Resource` or, if it genuinely models a different concept, justify why.
3. **Backward-safe change.** Renames and removals MUST carry migration paths and ontology mappings using `owl:sameAs` or `owl:deprecated` constructs in `vocab.jsonld`.
4. **Unification over standardization.** Per [Principle 2: Unification over Standardization](#principle-2-unification-over-standardization), prefer broader-concept schemas that can absorb specialization, over narrow schemas that fragment the vocabulary.
5. **Composition over Extension.** When a use case appears to need a new schema that combines several existing concepts (X + Y + Z), the schema author MUST first attempt to express it using the composition primitives already provided by `api/v2.0.0/beckn.yaml` — `Offer.resourceIds`, `Offer.addOns`, `AddOn` (`oneOf [Resource, Offer]`), `Catalog.offers`, `Catalog.resources`, and `Resource.id` references. A new schema name MUST NOT be a fused combination of existing concepts. Names of the form `XWithY`, `XAndY`, `XPlusY`, or `XWithYAndZ` are anti-patterns and MUST be rejected at review. If a genuinely missing **relationship semantic** is identified (for example, "this Resource is a bundle of others"), publish a small, focused **relationship schema** that describes only the relationship — never a fused combination type. See [Worked example — Composing a combo product](#worked-example--composing-a-combo-product) for the full pattern.
6. **Agent-First Design.** Per [Principle 3: Agent-First Design](#principle-3-agent-first-design), schemas MUST be designed for AI agents (the primary consumers of the schema layer) and SHOULD be designed with AI agents (the appropriate authoring instrument). Concretely: descriptions read as standalone semantic prose, names align with industry vocabulary, JSON-LD relations let agents traverse the semantic graph without prior knowledge of any specific term, and the human author's posture is curatorial — validating, refining, and contextualising AI-generated drafts rather than producing them by hand. See [Authoring with AI](#authoring-with-ai) for the concrete workflow.

##### Authoring with AI

This subsection makes [Principle 3: Agent-First Design](#principle-3-agent-first-design) operational. The expectations below apply to every schema PR raised against `beckn/schemas` and `beckn/DEG`. They are not optional process notes — they are the criteria by which maintainers and the CWG evaluate the author's craft.

The intent throughout is unambiguous: **use AI as the primary instrument for naming, description, semantic mapping, and vocabulary alignment, and use human judgement to curate, validate, and finalise.** Reviewers MAY ask an author how each portion of a contribution was developed; an author who cannot articulate the AI workflow they used and the curatorial decisions they made on top of it is likely to be authoring in a pre-AI style that this RFC explicitly discourages.

###### Naming

Before submitting a proposed name, run the candidate through an AI naming pass. A workable prompt template:

> "I am authoring a Beckn Protocol schema for `<concept>`. Suggest an intuitive, industry-recognised name following these constraints: (1) a noun or noun-form-of-verb; (2) one or two words preferred; (3) industry-standard terminology takes precedence over coined names; (4) avoid generic suffixes such as `Item`, `Attributes`, `Resource`, `Offer`; (5) align with vocabularies in active use (schema.org, FHIR, GS1, IEC CIM, ISO standards). Provide three candidates with provenance for each — which vocabulary or standard uses this term and where."

Compare the suggestions against existing schemas at [schema.beckn.io](https://schema.beckn.io). The chosen name MUST satisfy the rules in [Naming a schema](#naming-a-schema); the AI's suggestion is the draft, not the conclusion. Record the provenance in the schema's `README.md`.

###### Drafting descriptions

Schema and property descriptions are read by AI agents as the primary signal of meaning. Use AI to generate a first-pass description that:

- Names the real-world concept the schema models.
- States which actor produces the value, which consumes it, and where in the value-exchange lifecycle the schema appears.
- Identifies relationships to related schemas (extends, composes, constrains).
- Avoids structural restatements such as "an object containing X and Y".

Then curate: ensure the description does not introduce undocumented assumptions, does not over-reach into domain claims the author cannot defend, and aligns with the existing vocabulary in `beckn/schemas`. Descriptions written in the LLM's voice are acceptable; descriptions written by an LLM but never read by the author are not.

###### Semantic mapping and superset identification

When proposing a new schema, ask an AI model: *"What is the most specific parent concept this schema could subclass from, drawing from JSON-LD vocabularies in active use (schema.org, FHIR, GS1, IEC CIM, etc.)? Show me the IRI of each candidate parent and the rationale for the match."*

This step often reveals an existing IRI the new schema can extend rather than a new term the author would otherwise have coined. The output belongs in `vocab.jsonld` as `rdfs:subClassOf`, `skos:broader`, or `owl:sameAs` relations. Authors are reminded that the absence of an explicit `subClassOf` relation is *itself* a design failure under [Principle 3](#principle-3-agent-first-design) — it removes a fallback path that agents on counterparty networks depend on.

###### Vocabulary alignment

For every new term, ask an AI model whether a standard term already exists in any industry vocabulary that maps to the same concept. Where a standard term exists, USE IT and document its provenance in `README.md`. Where no standard exists, the author still SHOULD record the search so reviewers can verify the gap is real.

###### What AI does not (yet) do

The author retains the judgement-bearing decisions that AI is not yet positioned to make autonomously:

- Semantic stability across versions ([Principle 1](#principle-1-semantic-invariance-across-regions)).
- Whether the proposed schema is the right level of abstraction ([Principle 2](#principle-2-unification-over-standardization)).
- Which existing primitives compose to express the use case ([Composition over Extension](#core-design-principles)).
- Which venue the contribution belongs in (`beckn/schemas`, `beckn/DEG`, or a network-specific overlay).
- The four-step precedence: abstraction → composition → extension → creation.

These remain the author's responsibility. AI's role is to widen the space of well-named, well-described candidates the author chooses from — not to make the choice on the author's behalf.

###### A note on attribution

Schemas authored with AI assistance are not less authored. The provenance of the contribution is the human author who curated, validated, and submitted the PR; that author is credited in `README.md` and in the schema's commit history. The model used (and the prompts that produced foundational naming or description decisions) MAY be recorded in `README.md` as supplementary provenance.

##### Naming a schema

The naming guidelines below aim to discourage semantically weak names (names that obscure what the schema models or that duplicate existing concepts). They are not intended to prohibit verbose or compositional naming patterns where those genuinely help, for example schemas in extension packs where a longer name communicates important compositional context. Authors SHOULD apply these guidelines with semantic clarity as the goal, not strict adherence to a single naming form.

1. **Part of speech.** Schemas MUST always be nouns or the noun form of verbs. A schema modelling an act MUST use the noun form with an `Action` suffix (e.g., `PaymentAction`, not `Pay`).
2. **Domain-agnostic naming.** Domain-agnostic schemas SHOULD use abstract but meaningful names. A reader SHOULD understand the concept from the name alone without consulting the description.
3. **Multi-word schemas.** Multi-word names like `FulfillmentAgent` or `PaymentMethod` are allowed. Prefer two-word names. Three or more components are strongly discouraged unless no shorter name preserves the meaning.
4. **Industry-standard terms take precedence.** When a widely adopted industry term exists, USE IT instead of coining a new one. For EV charging, use `ChargingPointOperator`, not `ChargingServiceProvider`. Authors SHOULD perform industry research before naming a new schema and document the term's provenance in the schema's `README.md`.
5. **Action schema naming.** A schema that describes an action MUST append the suffix `Action` (e.g., `PaymentAction`, not `Payment`) to disambiguate the act from the resulting state.
6. **Casing rules.**
   - Types and classes: `TitleCase`
   - Properties: `lowerCamelCase`
   - Enum values: `SCREAMING_SNAKE_CASE`
   - Reserved or ambiguous names such as `type` MUST be avoided, except for JSON-LD `@type`.

##### NOT RECOMMENDED — generic suffixes such as `Attributes`, `Item`, `Offer`, `Resource`

Schema authors SHOULD NOT suffix a schema name with a generic Beckn term (such as `Attributes`, `Item`, `Offer`, `Resource`, or `Product`) merely to signal *where the schema is intended to be carried* in a payload. Names like `GroceryItemAttributes`, `ElectronicsOffer`, or `FlightItem` violate the [naming conventions in NFH-009](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md#naming-the-schema):

- They **inflate the token count** of the schema name beyond the two-word recommendation (`Grocery` + `Item` + `Attributes` is three components).
- They **conflate the concept with its placement**. The concept is "a grocery product". Where it is carried in a Beckn envelope (the `resourceAttributes` field of `Resource`) is a separate, structural concern.
- They **leak the carrier into the IRI**. Every consumer that resolves `groc:GroceryItemAttributes` is forced to read a noun phrase that includes a Beckn primitive, even though the canonical concept they are modelling is just a grocery product.

The recommended naming pattern is to **name the concept itself** — `GroceryProduct`, `ElectronicsProduct`, `FlightSegment` — and to express the recommended carrier through metadata that does NOT pollute the schema name.

###### Expressing the carrier without polluting the name

Two complementary mechanisms exist to record "this schema is intended to be carried inside a `Resource` (or `Offer`, or `Consideration`)" without baking that into the name:

1. **A vendor extension on the schema definition.** In `attributes.yaml`, declare an `x-recommended-parent` (or similarly namespaced `x-*`) field that names the Beckn core type into which the schema is normally embedded. Vendor extensions are an OpenAPI/JSON Schema convention and do NOT affect structural validation.
2. **A JSON-LD relation in `vocab.jsonld`.** Declare the schema as a `rdfs:subClassOf`, `skos:broader`, or `rdfs:domain` of the relevant Beckn core class. This is the **authoritative** mechanism: it makes the relationship machine-readable to any conformant JSON-LD processor, and the same relationship surfaces on `schema.beckn.io` as part of the published vocabulary.

**Example — `GroceryProduct` instead of `GroceryItemAttributes`:**

`attributes.yaml` excerpt:

```yaml
components:
  schemas:
    GroceryProduct:
      type: object
      description: A consumable grocery product with identity, physical, and nutrition attributes.
      x-recommended-parent: Resource     # vendor extension — non-normative hint to authoring tools
      properties:
        identity: { $ref: "#/components/schemas/GroceryIdentity" }
        physical: { $ref: "#/components/schemas/GroceryPhysical" }
        nutrition: { $ref: "#/components/schemas/GroceryNutrition" }
```

`vocab.jsonld` excerpt:

```json
{
  "@context": {
    "rdfs":  "http://www.w3.org/2000/01/rdf-schema#",
    "skos":  "http://www.w3.org/2004/02/skos/core#",
    "beckn": "https://schema.beckn.io/LinkedData/v2.1/context.jsonld",
    "groc":  "https://schema.beckn.io/Grocery/v2.0/vocab#"
  },
  "@graph": [
    {
      "@id": "groc:GroceryProduct",
      "@type": "rdfs:Class",
      "rdfs:label": "GroceryProduct",
      "rdfs:comment": "A consumable grocery product.",
      "rdfs:subClassOf": { "@id": "beckn:Resource" },
      "skos:broader":    { "@id": "beckn:Resource" }
    }
  ]
}
```

A consumer that processes a `Resource` whose `resourceAttributes.@type` is `groc:GroceryProduct` can:

- **Structurally** validate it against the published `GroceryProduct` schema.
- **Semantically** treat it as a `beckn:Resource` even if it has never encountered `groc:GroceryProduct` before — because the `subClassOf` linkage is declared in `vocab.jsonld`.

**Examples — recommended vs. anti-pattern names:**

| Anti-pattern | Recommended | Why |
|---|---|---|
| `GroceryItemAttributes` | `GroceryProduct` | Concept name only; carrier expressed via `x-recommended-parent: Resource` + `rdfs:subClassOf beckn:Resource` in vocab |
| `ElectronicsOffer` | `ElectronicsProduct` (or `ConsumerElectronics`) | The Offer is a Beckn core type; the schema models the product, not the offer wrapper |
| `FlightItem` | `FlightSegment` | Concept name reflects the domain noun; placement is incidental |
| `HotelResource` | `HotelStay` (or `Accommodation`) | The Resource is a Beckn primitive; the schema models the stay |
| `PaymentConsideration` | `PaymentTerms` (or reuse `Consideration` directly) | If it adds nothing beyond `Consideration`, no new schema is needed |

> **Legacy exceptions.** Existing schemas in `beckn/schemas` such as `GroceryItem` (with its `groc:GroceryItemAttributes` type) are recognised as **offending schemas** per the [Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md#managing-exceptions-and-offending-schemas). They are not invalidated by this guidance — they MUST carry a migration path using `owl:sameAs` and `owl:deprecated` constructs in `vocab.jsonld` so that consumers can migrate to a conformant name. New schemas MUST NOT introduce these suffixes.

##### Describing a schema

Every schema and every property MUST carry a description written in formal technical prose. Descriptions MUST:

- Describe **what the real-world concept is**, NOT **what the data structure contains**. A `Contract` is *"a digitally agreed commitment between participants governing an exchange of value"* — not *"an object containing id, status, and participants."*
- Identify which actor produces the value, which consumes it, and where in the value-exchange lifecycle the schema appears.
- State the schema's relationship to other schemas it extends, composes, or constrains.
- Use normative keywords (`MUST`, `SHOULD`, `MAY`) only where the constraint is genuinely normative.
- Not assume domain-specific knowledge unless that knowledge is defined elsewhere in this specification with an inline hyperlink to its definition.

Property descriptions MUST state what the property represents, who assigns its value, and any constraints not captured by the JSON Schema type declaration. For enumerated properties, every enum value MUST be described in the context of the specific schema.

##### JSON-LD conventions

1. Every schema MUST include a `context.jsonld` mapping every term to an IRI in the `beckn:` namespace or a recognized external vocabulary (`xsd:`, `schema:`, `rdf:`, `rdfs:`, etc.).
2. `context.jsonld` and `vocab.jsonld` MUST remain aligned with the corresponding `attributes.yaml` and `schema.json` contracts.
3. Renamed terms SHOULD carry explicit ontology relations (`owl:sameAs`, `owl:deprecated`) and migration mappings in `vocab.jsonld`.
4. The schema's `@context` SHOULD declare `@version: 1.1` and `@protected: true` to prevent downstream context files from overriding term meanings and to guarantee stable semantic grounding across implementations.
5. Composition and extension objects MUST include `@context` and `@type`.

##### Validation gates

Every schema pack MUST pass:

- **OpenAPI validation** for `attributes.yaml`
- **JSON Schema validation** for `schema.json` against JSON Schema Draft 2020-12
- **JSON-LD 1.1 validation** for `context.jsonld` and `vocab.jsonld`

Core schema objects SHOULD default to `additionalProperties: false`. Extension containers (`Attributes`-typed properties) SHOULD remain open and carry explicit semantic metadata.

##### Artifact precedence

When schema artifacts conflict during review or implementation, the following precedence MUST be applied:

1. `attributes.yaml`
2. `schema.json`
3. `context.jsonld`
4. `vocab.jsonld`
5. `examples/`
6. `README.md`

##### Managing offending schemas

A schema that violates the design principles above is termed an **offending schema**. Offending schemas MAY exist temporarily due to legacy or timeline constraints, but they MUST carry a documented migration path to a conformant name using `owl:deprecated` and `owl:sameAs` constructs in `vocab.jsonld`. External contributors and NFO collaborators are encouraged to flag offending schemas as Issues so that the ecosystem retains visibility into outstanding deviations.

#### Schema pack structure

Every schema pack, regardless of venue, MUST include the following files in a versioned directory (for example, `schema/retail/v1.0.0/`):

| File | Description |
|---|---|
| `attributes.yaml` | OpenAPI-compatible YAML definition of the extension properties. This is the structural contract consumed by validators. |
| `schema.json` | JSON Schema representation of the extension. Used by generic JSON Schema validators. |
| `context.jsonld` | JSON-LD context file that maps property names to canonical IRI terms. Required for semantic validation. |
| `vocab.jsonld` | JSON-LD vocabulary file that defines the meaning of each term. Used by semantic processors and registries to expose human-readable definitions. |
| `README.md` | Human-readable description of the schema's purpose, scope, supported use cases, and change log. |

The following files are OPTIONAL but RECOMMENDED:

| File | Description |
|---|---|
| `examples/` | Directory of example payloads demonstrating correct use of the schema. |
| `renderer.json` | Rendering hints for UI frameworks that display schema-backed data. |
| `profile.json` | Profile constraints (for example, required fields, allowed value sets) for a specific network or deployment context. |

Optional files MUST NOT replace or substitute for any required file. A schema pack that omits `context.jsonld` in favour of a `renderer.json` is not a conformant schema pack.

#### Creating a new schema

To create a new schema:

1. **Verify the gap.** Search [schema.beckn.io](https://schema.beckn.io) for existing schemas that address the use case. Document the search and why existing schemas are insufficient.
2. **Define the vocabulary.** Identify the properties required. For each property, determine whether it maps to an existing standard vocabulary (schema.org, HL7 FHIR, GS1, IEC CIM, etc.) or requires a new term definition. Reuse existing IRIs wherever possible. New terms MUST be defined in `vocab.jsonld`.
3. **Author the schema pack.** Create all required files as defined in [Schema pack structure](#schema-pack-structure). Place them in a versioned directory.
4. **Validate structurally.** Validate `attributes.yaml` against OpenAPI 3.1 schema syntax. Validate `schema.json` against JSON Schema Draft 2020-12 meta-schema.
5. **Validate semantically.** Process `context.jsonld` and `vocab.jsonld` through a JSON-LD processor to verify there are no undefined terms, circular references, or conflicting prefixes.
6. **Draft examples.** Write at least one complete example payload in `examples/` that demonstrates correct usage.
7. **Follow the contribution process.** Open a Discussion, build consensus, create an Issue, and raise a PR as described in [Contribution process](#contribution-process).

#### Extending an existing schema

To extend an existing schema:

1. **Identify the target version.** Identify the specific published version of the schema being extended. Extensions MUST be based on an existing released version, not on an unpublished draft.
2. **Determine the extension type.** Determine whether the change is additive (new property, new enum value) or corrective (description clarification, constraint tightening). Additive extensions increment the minor version. Corrective extensions that do not affect validation increment the patch version.
3. **Verify non-breaking status.** Confirm that the change does not alter the meaning of any existing term, does not change the type of any existing property, and does not make any previously optional field required. If any of these apply, the change is breaking and must follow the breaking-change process in [Breaking vs. non-breaking changes](#breaking-vs-non-breaking-changes).
4. **Author the updated schema pack.** Produce a new versioned directory with updated files. Do not modify the previous version directory in place.
5. **Update `README.md`.** Record the change in the schema's change log with date, version, and a plain-language description of what changed and why.
6. **Follow the contribution process.**

#### Versioning requirements

Schema versions MUST follow Semantic Versioning (`MAJOR.MINOR.PATCH`):

| Version component | When to increment |
|---|---|
| `MAJOR` | Any breaking change: removal of a property, type change, meaning change, optionality change |
| `MINOR` | Any additive non-breaking change: new property, new enum value, new optional field |
| `PATCH` | Any corrective non-breaking change: description clarification, example update, constraint tightening that does not reject previously valid payloads |

A `MAJOR` version increment MUST be accompanied by a migration guide in the schema's `README.md` that describes how producers and consumers should update their implementations.

Schema versions MUST NOT be modified once published to a shared venue. A published `v1.2.0` directory is immutable. If a correction is needed, a new `v1.2.1` (or higher) version MUST be published.

#### Breaking vs. non-breaking changes

A change is **breaking** if any producer or consumer that was valid against the previous version would be invalid against the new version, or would silently change its behavior without any indication that the schema changed. Breaking changes require:

1. A `MAJOR` version increment.
2. A minimum notice period of ninety days before the previous version is formally deprecated, during which both versions are indexed by the registry.
3. A migration guide.
4. A deprecation notice placed in the old version's `README.md` pointing to the new version.

A change is **non-breaking** if existing valid payloads remain valid, and existing consumers that have not yet adopted the new version continue to process payloads correctly (they may simply ignore the new vocabulary). Non-breaking changes do not require a deprecation period.

#### Contribution process

The contribution process for all schemas in shared venues (`beckn/schemas` and `beckn/DEG`) is:

1. **Open a Discussion** in the target repository (GitHub Discussions) explaining the use case, the vocabulary gap, and the proposed schema design. Include a summary of the search for existing schemas at [schema.beckn.io](https://schema.beckn.io).
2. **Build consensus.** Allow a minimum of fourteen days for community review. Address all substantive objections. A schema proposal that has not achieved rough consensus MUST NOT proceed to an Issue.
3. **Open an Issue** linking to the Discussion. For `beckn/DEG`, confirm that the DEG Working Group has acknowledged the Issue. For `beckn/schemas`, an Issue may be opened once the Discussion has reached rough consensus — no formal working-group acknowledgement is required.
4. **Author the schema pack** in a fork or staging environment. Validate it structurally and semantically as described in [Creating a new schema](#creating-a-new-schema).
5. **Raise a PR to the `draft` branch** of the target repository (NEVER directly to `main` or `release`). The PR MUST include the complete schema pack, a `README.md` change log entry, and a link to the Issue.
6. **Await review.** Maintainers of the target repository — the DEG Working Group for `beckn/DEG`, and the repository maintainers for `beckn/schemas` — will review the PR for vocabulary quality, naming conventions, structural conformance, semantic correctness, and ecosystem impact.
7. **Merge to `draft`.** Once approved, the PR is merged to the `draft` branch for integration review.
8. **Raise a PR from `draft` to `release`.** After the stabilization period (minimum thirty days for MAJOR changes, fourteen days for MINOR changes), a PR is raised from `draft` to the `release` branch. This is reviewed and merged by the repository maintainers, with CWG oversight.
9. **Raise a PR from `release` to `main`.** The final step is a PR from `release` to `main`. Once merged, the schema version is on the `main` branch of the repository and is considered formally published.
10. **Registry sync.** Merging to `main` triggers a sync on the NFH schema administration console, which indexes the new schema version and makes it discoverable on [schema.beckn.io](https://schema.beckn.io). No manual registry action is required by the contributor.

> **Note on review authority.** Maintainers of the target repository — including external collaborators such as NFO representatives added to `beckn/schemas`, and members of the DEG Working Group for `beckn/DEG` — MAY approve and merge PRs at each branch transition (`draft`, `release`, `main`) **without waiting for CWG sign-off**, provided the contribution adheres to the principles in [Design principles for schema authors](#design-principles-for-schema-authors). The CWG's role is to uphold these design principles, not to act as a per-PR approval gate. This is what prevents schema evolution from bottlenecking on a single working group and what makes external collaboration genuinely productive.

---

### How schemas are used in production

#### Schema discovery

Implementations SHOULD resolve schema artifacts through the Beckn Schema Registry at [schema.beckn.io](https://schema.beckn.io). The registry is managed by NFH and indexes only artifacts that have been merged to the `main` branch of `beckn/schemas` or `beckn/DEG`, so any artifact discoverable through the registry has completed the full contribution and review process.

Direct resolution from source repository `main` branches is acceptable for production use, as `main` carries only formally published versions. Resolution from `draft`, `release`, or any other branch carries the risk of consuming unreleased artifacts and MUST NOT be used in production.

##### Contributor recognition

The schema administration console at `schema.beckn.io` will, in a forthcoming release, surface the **contributor list for each published schema** — acknowledging by name the individuals and organizations that contributed to its authorship and ongoing evolution. This recognition is intentional: schemas are open-source contributions like any other, and the people and organizations who shape them deserve the same public visibility as code contributors elsewhere in the ecosystem. NFO collaborators, manufacturer contributors, and individual community members will all be credited on the schemas they help maintain.

This feature is on the schema registry roadmap and is not yet live as of this draft of NFH-012. Once available, the contributor list for each schema will be derived from the commit history of the corresponding directory in `beckn/schemas` or `beckn/DEG`, and contributors MAY also be credited explicitly in the schema's `README.md`.

#### Referencing a schema from a payload

Domain-specific payload extensions are placed inside `Attributes` containers on the relevant core objects defined in `api/v2.0.0/beckn.yaml` — `resourceAttributes`, `offerAttributes`, `providerAttributes`, `commitmentAttributes`, `performanceAttributes`, `settlementAttributes`, `contractAttributes`, `participantAttributes`, `trackingAttributes`, `considerationAttributes`, and `targetAttributes`. The `Attributes` schema in `beckn.yaml` constrains the container to two REQUIRED properties — `@context` and `@type` — and permits additional properties as defined by the referenced JSON-LD context document.

**`@context` is a single string.** The `Attributes.@context` property in `beckn.yaml` is typed as `string`, not as an array. Each Beckn payload carries exactly one `@context` URL per `Attributes` container, and the referenced document is the canonical source from which all term mappings, type relationships, and vocabulary linkages for that container are resolved. A network or NFO that needs to layer multiple vocabularies MUST publish a single combined context document that internally references whatever other contexts it needs — only the single URL appears on the wire.

> Note — `@context` vs `schemaContext`. The `Attributes.@context` property is the JSON-LD reserved keyword and is a single string. The Beckn envelope's `Context.schemaContext` property (a different field, named without the `@` prefix) is an array of JSON-LD context URLs declared at the envelope level for tooling and discovery purposes. Do not conflate the two.

Example — a `Resource` carrying a `GroceryItem` extension via `resourceAttributes`, fully conformant with `beckn.yaml` and the [`GroceryItem` schema](https://github.com/beckn/schemas/tree/main/schema/GroceryItem) published in `beckn/schemas`:

```json
{
  "id": "ITEM-WHEAT-FLOUR-1KG",
  "descriptor": {
    "name": "Whole Wheat Flour 1kg"
  },
  "resourceAttributes": {
    "@context": "https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld",
    "@type": "groc:GroceryItemAttributes",
    "identity": {
      "brand": "FarmFresh",
      "originCountry": "IN"
    },
    "physical": {
      "weight": {
        "@type": "schema:QuantitativeValue",
        "value": 1,
        "unitText": "KG"
      }
    },
    "nutrition": [
      { "nutrient": "Energy", "value": { "@type": "schema:QuantitativeValue", "value": 364, "unitText": "KCAL" } },
      { "nutrient": "Protein", "value": { "@type": "schema:QuantitativeValue", "value": 13, "unitText": "G" } }
    ]
  }
}
```

The `@context` URI MUST be resolvable at runtime by any participant that needs to validate or process the extension semantics. Implementations MUST NOT use a `@context` URI that resolves to a draft-branch or non-registry artifact in production payloads.

#### Validation sequence

Production implementations MUST apply the following validation sequence when processing a Beckn message that contains `Attributes` containers:

```text
Step 1: Validate the message envelope and payload shape against beckn.yaml (structural validation).
Step 2: For each Attributes container, resolve @context and @type.
Step 3: Validate the Attributes container content against the resolved schema.json (structural extension validation).
Step 4: Expand the Attributes container using the resolved context.jsonld (semantic validation).
Step 5: Execute domain logic with validated structural + semantic data.
```

Step 1 is REQUIRED. Steps 2 and 3 are REQUIRED for any implementation that claims to support a specific domain schema. Step 4 (semantic expansion) SHOULD be applied for cross-network semantic consistency and MUST be applied when the receiving participant belongs to a different network or NFO context than the sender.

An implementation that skips Step 1 and proceeds directly to domain logic based on `Attributes` content is non-conformant and creates an unsafe processing path.

#### Version pinning in production

Production implementations MUST pin to a specific schema version for all `@context` URIs they consume. Floating references (for example, references to a `latest` alias or a registry API that always returns the most recent version) are prohibited in production payloads because they make the semantic contract of a message dependent on the state of an external service at read time.

Version pinning means:

- The `@context` URI in every payload carries an explicit version segment (for example, `/v1.2.0/`).
- The validator and semantic processor in the implementation are tested against that specific version.
- An upgrade to a new schema version is a deliberate implementation change, not an automatic consequence of a registry update.

When a schema version is deprecated, implementations have the full notice period (minimum ninety days for MAJOR deprecations) to update their version pin before the deprecated version is removed from active indexing.

#### Schema trust and security

A `@context` URI in a Beckn payload is a claim by the sender about the semantic interpretation of the extension data. A malicious or misconfigured sender can point `@context` at an attacker-controlled URI that redefines property meanings in ways that manipulate receiver behavior.

To mitigate this risk:

- Implementations MUST maintain an allowlist of trusted `@context` URI prefixes. Any payload whose `Attributes` container contains a `@context` URI not on the allowlist MUST be rejected or processed with the extension data treated as opaque.
- Implementations MUST NOT resolve `@context` URIs over unencrypted HTTP in production. All `@context` resolution MUST use HTTPS with certificate validation.
- Implementations SHOULD cache resolved context documents with content-addressing (for example, by hash of the document body) rather than trusting that the URI will return the same document on every fetch.
- Schema pack publishers MUST NOT modify the content of a published version directory. If the content at a published URI changes without a version increment, all consumers that cached the original version are silently using a different semantic contract.

#### Worked example — UAE retail network

This example illustrates how the JSON-LD layering pattern enables a CN and a PN with **different internal data models** to interoperate over a Beckn network, even when the network introduces a **region-specific concept** that does not exist in the canonical Beckn vocabulary. Every payload shown is strictly conformant with [`api/v2.0.0/beckn.yaml`](../api/v2.0.0/beckn.yaml) and references a real schema published in [github.com/beckn/schemas](https://github.com/beckn/schemas).

##### Setup

Consider a Beckn-conformant retail network operating in the United Arab Emirates, **`Souq Connect`**. The network has two active participants:

- **CN — `ShopGulf`**, a consumer-side shopping app. Internal data model uses `lowerCamelCase` English terms: `brand`, `originCountry`, `regulatoryCategory`, `weightKg`.
- **PN — `MerchantHub`**, a merchant catalog service. Internal data model uses different `snake_case` English terms reflecting its legacy schema: `brand_name`, `product_origin`, `classification`, `weight_kg`.

Both CN and PN exchange `Resource` objects whose semantic shape is the **canonical [`GroceryItem` schema](https://github.com/beckn/schemas/tree/main/schema/GroceryItem/v2.0)** published in `beckn/schemas`. That schema defines the `groc:GroceryItemAttributes` type together with sub-fields such as `identity`, `physical`, and `nutrition`. (The name `GroceryItemAttributes` is a legacy offending schema per [NOT RECOMMENDED — generic suffixes](#not-recommended--generic-suffixes-such-as-attributes-item-offer-resource); it is used here because it is the type currently published in `beckn/schemas` and any worked example must reference real artifacts.)

`Souq Connect` introduces one region-specific concept that does not exist anywhere in the canonical `GroceryItem` vocabulary: **`HalalCertified`** — the regional regulatory category for products certified as Halal by an approved certification body. The network publishes a **single JSON-LD context document** at `https://souqconnect.ae/v2/context.jsonld` that:

1. Internally references the canonical `GroceryItem` context published in `beckn/schemas`, so every canonical term is reachable from this one URL.
2. Adds the network's own term aliases (mapping both CN and PN local terms) onto canonical IRIs.
3. Declares `souqconnect:HalalCertified` as `rdfs:subClassOf` `beckn:productCategory` in a companion `vocab.jsonld` document on the same host.

The URLs of both `context.jsonld` and `vocab.jsonld` are registered under the `souqconnect` namespace on [dedi.global](https://dedi.global), so any counterparty can resolve and trust them via the trust layer.

No new Beckn schema is forked. No NFO-scoped schema is published. The network publishes one context document and one vocabulary document — and that is the single URL that appears on the wire as `@context`.

##### Architectural layers

```mermaid
flowchart TB
    subgraph Global[Layer 1 — Canonical Beckn schema]
        G["beckn/schemas/GroceryItem/v2.0<br/>identity, physical, nutrition, ...<br/>plus beckn.yaml core: Resource, Catalog, ..."]
    end
    subgraph Region[Layer 2 — Souq Connect network context]
        R["souqconnect.ae/v2/context.jsonld<br/>imports GroceryItem context<br/>brand, brand_name → schema:brand<br/>originCountry, product_origin → groc:originCountry<br/>souqconnect:HalalCertified<br/>rdfs:subClassOf beckn:productCategory"]
    end
    subgraph CN_local[Layer 3a — CN internal model]
        CN["ShopGulf<br/>brand, originCountry, regulatoryCategory, weightKg"]
    end
    subgraph BPP_local[Layer 3b — PN internal model]
        PN["MerchantHub<br/>brand_name, product_origin, classification, weight_kg"]
    end
    R --> G
    CN --> R
    PN --> R
```

Layer 1 is maintained as an open-source project in `beckn/schemas` with CWG oversight. Layer 2 is maintained by Souq Connect on its own infrastructure. Layers 3a and 3b are owned by each participant. No layer requires code changes when an adjacent layer evolves — provided the JSON-LD linkages remain valid.

##### Wire payload — `/discover` request

When `ShopGulf` searches for premium Halal-certified basmati rice, the CN sends the following payload to the network's DS on `/discover`. The structure conforms strictly to the `/discover` request body in `beckn.yaml`: a `Context` envelope and a `DiscoverAction` message:

```json
{
  "context": {
    "action": "discover",
    "version": "2.0.0",
    "bapId": "shopgulf.ae",
    "bapUri": "https://api.shopgulf.ae/beckn",
    "transactionId": "f4b9b8f0-2a3c-4f1e-9c4f-0e6a8b9b8f0a",
    "messageId": "1c2a3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
    "networkId": "souqconnect.ae/retail",
    "timestamp": "2026-05-12T08:15:00Z",
    "ttl": "PT30S",
    "schemaContext": [
      "https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld",
      "https://souqconnect.ae/v2/context.jsonld"
    ]
  },
  "message": {
    "intent": {
      "textSearch": "premium basmati rice",
      "filters": {
        "type": "jsonpath",
        "expression": "$.resources[?(@.resourceAttributes['@type']=='groc:GroceryItemAttributes' && @.resourceAttributes.identity.regulatoryCategory=='souqconnect:HalalCertified')]"
      }
    }
  }
}
```

Notes on this payload:

1. `context.action` is `discover` and `context.version` is the `2.0.0` const — both REQUIRED by the `Context` schema in `beckn.yaml`.
2. `context.schemaContext` is the **envelope-level** array of context URLs (the field name in `beckn.yaml` is `schemaContext`, NOT `@context`). It declares the JSON-LD contexts in scope for this transaction. It is distinct from the JSON-LD `@context` keyword that appears inside `Attributes` containers.
3. `message` is a `DiscoverAction` composed of an `Intent` — exactly per `beckn.yaml`. `Intent.textSearch` carries the free-text query in the consumer's language; `Intent.filters` is a JSONPath filter (RFC 9535) evaluated by the DS against its indexed catalog store.

##### Wire payload — `/on_discover` callback

After locating matching catalog entries, the DS calls `/on_discover` on the CN's registered URI, carrying an `OnDiscoverAction` with one or more `Catalog` objects:

```json
{
  "context": {
    "action": "on_discover",
    "version": "2.0.0",
    "bapId": "shopgulf.ae",
    "bapUri": "https://api.shopgulf.ae/beckn",
    "bppId": "merchanthub.ae",
    "bppUri": "https://api.merchanthub.ae/beckn",
    "transactionId": "f4b9b8f0-2a3c-4f1e-9c4f-0e6a8b9b8f0a",
    "messageId": "1c2a3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
    "networkId": "souqconnect.ae/retail",
    "timestamp": "2026-05-12T08:15:01Z",
    "schemaContext": [
      "https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld",
      "https://souqconnect.ae/v2/context.jsonld"
    ]
  },
  "message": {
    "catalogs": [
      {
        "id": "cat-mh-001",
        "descriptor": { "name": "MerchantHub — Gulf Foods Trading" },
        "isActive": true,
        "provider": {
          "id": "merchanthub-gulf-foods",
          "descriptor": { "name": "Gulf Foods Trading" }
        },
        "resources": [
          {
            "id": "mh-rice-basmati-5kg-001",
            "descriptor": { "name": "Premium Basmati Rice 5kg" },
            "resourceAttributes": {
              "@context": "https://souqconnect.ae/v2/context.jsonld",
              "@type": "groc:GroceryItemAttributes",
              "identity": {
                "brand": "Gulf Foods Select",
                "originCountry": "AE",
                "regulatoryCategory": "souqconnect:HalalCertified"
              },
              "physical": {
                "weight": {
                  "@type": "schema:QuantitativeValue",
                  "value": 5,
                  "unitText": "KGM"
                }
              }
            }
          }
        ]
      }
    ]
  }
}
```

Notes:

1. The envelope conforms to `Context` per `beckn.yaml`; the `message` is an `OnDiscoverAction` composed of one `Catalog` containing one `Provider` and one `Resource` — strictly per the v2.0.0 schema.
2. `resources[0].resourceAttributes` is the `Attributes` extension container defined in `beckn.yaml`. **`@context` is a single string URL** pointing to the Souq Connect network's context document. That document internally references the canonical `GroceryItem` context, so all `groc:` and `schema:` terms resolve transitively from the one URL.
3. `@type` is the canonical IRI from the `GroceryItem` schema (`groc:GroceryItemAttributes`), exactly as declared in `https://github.com/beckn/schemas/tree/main/schema/GroceryItem/v2.0/context.jsonld`.
4. `regulatoryCategory` carries the regional value `souqconnect:HalalCertified`. Because the Souq Connect vocabulary declares this IRI as `rdfs:subClassOf` `beckn:productCategory`, any participant resolving the single `@context` URL can interpret the term — even without prior knowledge of UAE Halal certification.

##### Why `@context` is a single string

The `Attributes.@context` property is constrained by `beckn.yaml` to `type: string`. Every Beckn 2.0 payload therefore carries exactly **one** `@context` URL per `Attributes` container. This is an intentional design choice:

- It keeps wire payloads compact and the resolution chain deterministic.
- It eliminates ambiguity over context-merging order when multiple contexts would otherwise be present.
- It places the responsibility for composing vocabularies in the **published context document** itself, where it can be reviewed, cached, and version-pinned — not on the wire, where each sender would otherwise be free to assemble a different stack.

NFOs that need to layer regional vocabulary on top of the canonical Beckn schemas MUST publish a **single combined context document** that internally references whatever other contexts it requires. The wire format always carries just that one URL.

##### Sequence diagram — end-to-end translation

```mermaid
sequenceDiagram
    autonumber
    participant App as ShopGulf<br/>(CN internal model)
    participant BAPLD as CN JSON-LD<br/>Processor
    participant DS as Souq Connect<br/>Discovery Service
    participant BPPLD as PN JSON-LD<br/>Processor
    participant Cat as MerchantHub<br/>(PN internal model)

    Note over App,Cat: /discover request (CN → DS) and /on_discover callback (DS → CN) per beckn.yaml
    App->>BAPLD: { brand: "Gulf Foods Select",<br/>originCountry: "AE",<br/>regulatoryCategory: "HalalCertified",<br/>search: "premium basmati rice" }
    Note over BAPLD: 1. Expand using ShopGulf local context<br/>brand → schema:brand<br/>originCountry → groc:originCountry<br/>regulatoryCategory → beckn:regulatoryCategory<br/>HalalCertified → souqconnect:HalalCertified
    Note over BAPLD: 2. Compose /discover envelope<br/>(Context + DiscoverAction)<br/>set resourceAttributes.@context to single URL<br/>https://souqconnect.ae/v2/context.jsonld
    BAPLD->>DS: POST /discover { context, message: { intent: { textSearch, filters } } }
    DS-->>BAPLD: 200 Ack
    Note over DS: DS evaluates the JSONPath filter<br/>against its indexed catalog store
    DS->>BAPLD: POST /on_discover { context, message: { catalogs: [...] } }
    Note over BAPLD: 3. Expand on_discover payload using<br/>the single @context URL on the wire
    Note over BAPLD: 4. Compact into ShopGulf local context<br/>schema:brand → brand<br/>groc:originCountry → originCountry<br/>beckn:regulatoryCategory → regulatoryCategory
    BAPLD->>App: { brand: "Gulf Foods Select", originCountry: "AE",<br/>regulatoryCategory: "HalalCertified", weightKg: 5 }

    Note over BPPLD,Cat: PN publication path — Resource is self-hosted by the PN, crawled and indexed by DS
    Cat->>BPPLD: { brand_name: "Gulf Foods Select",<br/>product_origin: "AE",<br/>classification: "HalalCertified", weight_kg: 5 }
    Note over BPPLD: A. Expand using MerchantHub local context<br/>brand_name → schema:brand<br/>product_origin → groc:originCountry<br/>classification → beckn:regulatoryCategory
    Note over BPPLD: B. Compose Resource per beckn.yaml<br/>set resourceAttributes.@context to single URL<br/>https://souqconnect.ae/v2/context.jsonld
    BPPLD->>BPPLD: Host a signed CatalogFile carrying the Resource above
    DS->>BPPLD: GET the CatalogFile, verify signature and digest, index the Resource
```

Steps 1–2 happen inside `ShopGulf`'s perimeter (outbound `/discover`). Steps 3–4 happen inside `ShopGulf`'s perimeter (inbound `/on_discover`). Steps A–B happen inside `MerchantHub`'s perimeter (self-hosted catalog publication, crawled and verified independently by DS). The wire format — with single-string `@context` URLs inside every `Attributes` container — is the only shared contract.

##### Pseudocode — edge processing

The Souq Connect network context is the **single URL on the wire**. Each side loads it once and uses it for both expansion and compaction at its own boundary. The CN and PN each load only their own local context plus the network context — never the canonical Beckn context directly, because the network context already chains it.

**CN outbound (`ShopGulf` composes a `/discover` request):**

```python
NETWORK_CTX_URL = "https://souqconnect.ae/v2/context.jsonld"
# This network context internally imports
# https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld

def compose_discover_request(internal_query: dict, ids: dict) -> dict:
    # internal_query uses ShopGulf's local vocabulary:
    # { "brand": "Gulf Foods Select", "originCountry": "AE",
    #   "regulatoryCategory": "HalalCertified", "search": "premium basmati rice" }

    bap_local_ctx = load("https://shopgulf.ae/context.jsonld")
    network_ctx   = load(NETWORK_CTX_URL)

    # 1. Expand local payload to canonical IRI form.
    expanded = jsonld.expand(internal_query, context=bap_local_ctx)

    # 2. Compact into the network's published vocabulary for wire serialization.
    wire_attrs = jsonld.compact(expanded, context=network_ctx)
    # wire_attrs now uses canonical Beckn / GroceryItem terms.

    # 3. Assemble the /discover envelope strictly per beckn.yaml.
    return {
        "context": {
            "action": "discover",
            "version": "2.0.0",
            "bapId": ids["bapId"],
            "bapUri": ids["bapUri"],
            "transactionId": ids["transactionId"],
            "messageId": ids["messageId"],
            "networkId": "souqconnect.ae/retail",
            "timestamp": now_rfc3339(),
            "ttl": "PT30S",
            "schemaContext": [
                "https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld",
                NETWORK_CTX_URL,
            ],
        },
        "message": {
            "intent": {
                "textSearch": internal_query["search"],
                "filters": {
                    "type": "jsonpath",
                    "expression": jsonpath_from(wire_attrs),
                },
            },
        },
    }
```

**CN inbound (`ShopGulf` handles `/on_discover`):**

```python
def handle_on_discover(envelope: dict) -> list[dict]:
    bap_local_ctx = load("https://shopgulf.ae/context.jsonld")
    network_ctx   = load(NETWORK_CTX_URL)
    out = []
    for catalog in envelope["message"]["catalogs"]:
        for resource in catalog["resources"]:
            attrs = resource["resourceAttributes"]
            assert isinstance(attrs["@context"], str), \
                "Beckn 2.0: @context inside Attributes MUST be a single string"

            # 1. Expand using the single network context URL on the wire.
            expanded = jsonld.expand(attrs, context=network_ctx)

            # 2. Compact into ShopGulf's local vocabulary.
            local_attrs = jsonld.compact(expanded, context=bap_local_ctx)
            out.append({"id": resource["id"], **local_attrs})
    return out
```

**PN outbound (`MerchantHub` prepares a `Resource` for self-hosted publication, crawled by DS):**

```python
def publish_resource(internal_item: dict) -> dict:
    # internal_item uses MerchantHub's local vocabulary:
    # { "sku": "mh-rice-basmati-5kg-001", "name": "Premium Basmati Rice 5kg",
    #   "brand_name": "Gulf Foods Select", "product_origin": "AE",
    #   "classification": "HalalCertified", "weight_kg": 5 }

    bpp_local_ctx = load("https://merchanthub.ae/context.jsonld")
    network_ctx   = load(NETWORK_CTX_URL)

    # 1. Expand to canonical IRI form using PN local context.
    expanded = jsonld.expand(internal_item, context=bpp_local_ctx)

    # 2. Compact into the network's published vocabulary.
    wire_attrs = jsonld.compact(expanded, context=network_ctx)

    # 3. Build a Resource per beckn.yaml with @context as a single string.
    return {
        "id": internal_item["sku"],
        "descriptor": {"name": internal_item["name"]},
        "resourceAttributes": {
            "@context": NETWORK_CTX_URL,
            "@type": "groc:GroceryItemAttributes",
            **wire_attrs,
        },
    }
```

Neither side needs to know the other's internal field names. If `ShopGulf` renames `brand` to `branding` tomorrow, the wire format does not change and `MerchantHub` is unaffected. If `MerchantHub` migrates from `snake_case` to `lowerCamelCase` internal field names, `ShopGulf` is unaffected. The wire format is a stable contract owned by the canonical `GroceryItem` schema in `beckn/schemas` and the Souq Connect network context — not by either participant.

##### The Souq Connect network context document

The single URL `https://souqconnect.ae/v2/context.jsonld` that appears on the wire resolves to a document that internally references the canonical `GroceryItem` context published in `beckn/schemas` and overlays Souq Connect's term aliases on top. The composition is performed in the published document — not on the wire:

```json
{
  "@context": [
    "https://raw.githubusercontent.com/beckn/schemas/main/schema/GroceryItem/v2.0/context.jsonld",
    {
      "@version": 1.1,
      "@protected": true,
      "souqconnect": "https://souqconnect.ae/v2/vocab#",
      "brand":      "schema:brand",
      "brand_name": "schema:brand",
      "originCountry":  "groc:originCountry",
      "product_origin": "groc:originCountry",
      "regulatoryCategory": "beckn:regulatoryCategory",
      "classification":     "beckn:regulatoryCategory",
      "weightKg":  "schema:weight",
      "weight_kg": "schema:weight"
    }
  ]
}
```

> Important: the array form above is permitted **inside a published JSON-LD 1.1 context document** — it composes the canonical Beckn-published context with the network's local overlay at the published URL. The wire-format `@context` inside an `Attributes` container is still a single string URL that points to this composed document; both endpoints see a single URL on the wire even though the document at that URL internally composes two contexts.

All term aliases collapse to the same canonical Beckn / `GroceryItem` IRI under expansion. A CN and a PN may each prefer a different alias internally; once expanded they are indistinguishable, and once compacted to the network context, all become the canonical term on the wire.

##### The Souq Connect vocabulary document

`HalalCertified` is not just an alias for an existing concept — it is a new value that the UAE regulatory context defines. The network's `vocab.jsonld` (referenced from the context document above) declares it explicitly:

```json
{
  "@context": {
    "rdfs":  "http://www.w3.org/2000/01/rdf-schema#",
    "skos":  "http://www.w3.org/2004/02/skos/core#",
    "beckn": "https://schema.beckn.io/LinkedData/v2.1/context.jsonld",
    "souqconnect": "https://souqconnect.ae/v2/vocab#"
  },
  "@graph": [
    {
      "@id": "souqconnect:HalalCertified",
      "@type": "rdfs:Class",
      "rdfs:subClassOf": { "@id": "beckn:productCategory" },
      "rdfs:label": "HalalCertified",
      "rdfs:comment": "UAE regulatory category for products certified Halal by an approved certification body.",
      "skos:broader": { "@id": "beckn:productCategory" }
    }
  ]
}
```

A PN outside the UAE that receives a payload referencing `souqconnect:HalalCertified` and does not understand the term can still safely treat it as a `beckn:productCategory` by following the `subClassOf` linkage. It is not forced to know what `HalalCertified` means in UAE regulation in order to interpret the message semantically.

##### Roundtrip stability

The JSON-LD pipeline is stable under repeated expansion and compaction. For a multi-turn `discover → on_discover → select → on_select → init → ... → confirm → on_confirm` exchange, the transformation at every hop is the same — and `@context` on the wire is always a single URL:

```text
local_BAP   → [expand CN_local_ctx]     → expanded
            → [compact network_ctx]      → wire (single-string @context)

wire        → [expand network_ctx]       → expanded
            → [compact BPP_local_ctx]    → local_BPP

local_BPP   → [expand BPP_local_ctx]     → expanded
            → [compact network_ctx]      → wire (single-string @context)

wire        → [expand network_ctx]       → expanded
            → [compact CN_local_ctx]    → local_BAP
```

At every hop the expanded form (the canonical IRI representation) is identical regardless of which side produced the message. The canonical Beckn schemas in `beckn/schemas`, the Souq Connect network context, the CN internal model, and the PN internal model evolve independently. JSON-LD makes them interoperable without code changes at any layer.

This is the architectural property that makes NFO-scoped schemas unnecessary in nearly every case where contributors think they need one.

#### Worked example — Composing a combo product

This example illustrates the **Composition over Extension** principle in practice. A retail provider on Souq Connect wants to publish a single bundled offer:

1. A primary item — a Robot Vacuum Cleaner (an `Electronics` Resource).
2. A free 1-year manufacturer warranty on the vacuum (a `Warranty` Resource).
3. A companion item — a Robot-Vacuum-compatible cleaning fluid (a `HomeCare` Resource).

The temptation, on first contact with this requirement, is to author a new schema in `beckn/schemas` called `ElectronicsWithWarrantyAndHomeCare`. **This is poor design and MUST be rejected.** A schema of that name:

- Forces every catalog consumer to learn an NFO-specific bundle type that is not reusable for any other product combination.
- Triggers a combinatorial explosion as soon as the next bundle is proposed: `ElectronicsWithWarranty`, `ElectronicsWithExtendedWarrantyAndHomeCare`, `GroceryWithWarrantyAndHomeCare`, and so on.
- Conflates the **products** (which have their own canonical schemas) with the **relationship between them** (which is not a product type at all).
- Violates [Composable evolution](#core-design-principles), [Principle 2: Unification over Standardization](#principle-2-unification-over-standardization), and [Composition over Extension](#core-design-principles) simultaneously.

##### The correct approach — express the bundle using `beckn.yaml` primitives

The bundle is expressed without authoring any new combined schema. Each product keeps its own canonical type from `beckn/schemas`. The relationship between them is carried by the existing `Offer`, `AddOn`, and `Resource`-reference primitives in `beckn.yaml`. Specifically:

| Concern | Primitive used | Defined in |
|---|---|---|
| The three products themselves | Three independent `Resource` objects | `Catalog.resources[]` in `beckn.yaml` |
| The primary item of the bundle | `Offer.resourceIds` | `beckn.yaml` |
| The free warranty and the companion item | `Offer.addOns[]` (each item is an `AddOn`, `oneOf [Resource, Offer]`) | `beckn.yaml` |
| The bundle price | `Offer.considerations[]` (a `Consideration` with `considerationAttributes`) | `beckn.yaml` |
| "This warranty covers that vacuum" | A simple `coveredResourceId` field inside the Warranty Resource's `resourceAttributes` | The published `Warranty` schema |
| "This cleaning fluid is compatible with that vacuum" | A simple `compatibleWith` ID reference inside the HomeCare Resource's `resourceAttributes` | The published `HomeCare` schema |

No schema named `ElectronicsWithWarrantyAndHomeCare` exists. The Electronics, Warranty, and HomeCare schemas remain independently meaningful and reusable across the ecosystem. The combo lives entirely in the Offer.

##### Wire payload — `/on_discover` callback carrying the combo offer

Every field below is strictly conformant with `api/v2.0.0/beckn.yaml`. The example assumes three published domain schemas in `beckn/schemas` — `Electronics`, `Warranty`, and `HomeCare` — authored in the same form as the existing [`GroceryItem`](https://github.com/beckn/schemas/tree/main/schema/GroceryItem/v2.0) and [`HomeAndKitchenItem`](https://github.com/beckn/schemas/tree/main/schema/HomeAndKitchenItem/v2.0) packs. Where any of those schemas does not yet exist, a contribution upstream is the correct path forward.

```json
{
  "context": {
    "action": "on_discover",
    "version": "2.0.0",
    "bapId": "shopgulf.ae",
    "bapUri": "https://api.shopgulf.ae/beckn",
    "bppId": "merchanthub.ae",
    "bppUri": "https://api.merchanthub.ae/beckn",
    "transactionId": "a8c1c2d3-9e4f-4f6a-9c4f-1e6a8b9b8f0a",
    "messageId": "b9d2e3f4-7a8c-4b9d-9e0f-2f3a4b5c6d7e",
    "networkId": "souqconnect.ae/retail",
    "timestamp": "2026-05-12T10:00:00Z",
    "schemaContext": [
      "https://raw.githubusercontent.com/beckn/schemas/main/schema/Electronics/v1.0/context.jsonld",
      "https://raw.githubusercontent.com/beckn/schemas/main/schema/Warranty/v1.0/context.jsonld",
      "https://raw.githubusercontent.com/beckn/schemas/main/schema/HomeCare/v1.0/context.jsonld",
      "https://souqconnect.ae/v2/context.jsonld"
    ]
  },
  "message": {
    "catalogs": [
      {
        "id": "cat-gulf-foods-bundles-001",
        "descriptor": { "name": "Gulf Foods Trading — Robot Vacuum Bundles" },
        "isActive": true,
        "provider": {
          "id": "merchanthub-gulf-foods",
          "descriptor": { "name": "Gulf Foods Trading" }
        },
        "resources": [
          {
            "id": "res-rvc-autoclean-x5",
            "descriptor": { "name": "AutoClean Pro X5 Robot Vacuum Cleaner" },
            "resourceAttributes": {
              "@context": "https://souqconnect.ae/v2/context.jsonld",
              "@type": "electronics:ElectronicsItemAttributes",
              "identity": {
                "brand": "AutoClean",
                "originCountry": "AE"
              },
              "powerRating": {
                "@type": "schema:QuantitativeValue",
                "value": 55,
                "unitText": "WATT"
              }
            }
          },
          {
            "id": "res-warranty-rvc-1y",
            "descriptor": { "name": "Manufacturer Warranty — 1 Year" },
            "resourceAttributes": {
              "@context": "https://souqconnect.ae/v2/context.jsonld",
              "@type": "warranty:WarrantyAttributes",
              "warrantyType": "MANUFACTURER",
              "duration": "P1Y",
              "coveredResourceId": "res-rvc-autoclean-x5",
              "terms": "Covers manufacturing defects only."
            }
          },
          {
            "id": "res-cleaner-rvc-500ml",
            "descriptor": { "name": "RVC Cleaning Fluid 500 ml" },
            "resourceAttributes": {
              "@context": "https://souqconnect.ae/v2/context.jsonld",
              "@type": "homecare:HomeCareItemAttributes",
              "identity": {
                "brand": "CleanPro",
                "originCountry": "AE"
              },
              "physical": {
                "volume": {
                  "@type": "schema:QuantitativeValue",
                  "value": 500,
                  "unitText": "MLT"
                }
              },
              "compatibleWith": ["res-rvc-autoclean-x5"]
            }
          }
        ],
        "offers": [
          {
            "id": "offer-rvc-combo-001",
            "descriptor": { "name": "AutoClean Pro X5 Combo — Free 1-Year Warranty + Cleaning Fluid" },
            "provider": { "id": "merchanthub-gulf-foods", "descriptor": { "name": "Gulf Foods Trading" } },
            "resourceIds": ["res-rvc-autoclean-x5"],
            "addOns": [
              {
                "id": "res-warranty-rvc-1y",
                "descriptor": { "name": "Manufacturer Warranty — 1 Year" },
                "resourceAttributes": {
                  "@context": "https://souqconnect.ae/v2/context.jsonld",
                  "@type": "warranty:WarrantyAttributes",
                  "warrantyType": "MANUFACTURER",
                  "duration": "P1Y",
                  "coveredResourceId": "res-rvc-autoclean-x5",
                  "terms": "Included free with the combo offer."
                }
              },
              {
                "id": "res-cleaner-rvc-500ml",
                "descriptor": { "name": "RVC Cleaning Fluid 500 ml" }
              }
            ],
            "considerations": [
              {
                "id": "cons-combo-001",
                "status": { "code": "PROPOSED" },
                "considerationAttributes": {
                  "@context": "https://souqconnect.ae/v2/context.jsonld",
                  "@type": "retail:PriceConsideration",
                  "totalPrice": {
                    "@type": "schema:MonetaryAmount",
                    "value": 1200,
                    "currency": "AED"
                  }
                }
              }
            ],
            "validity": {
              "startDate": "2026-05-12",
              "endDate": "2026-06-30"
            }
          }
        ]
      }
    ]
  }
}
```

Notes on the design:

1. **No new bundle schema.** The Electronics Resource is typed `electronics:ElectronicsItemAttributes`. The Warranty is typed `warranty:WarrantyAttributes`. The HomeCare item is typed `homecare:HomeCareItemAttributes`. Each is independently meaningful. The same Warranty Resource could appear in a different Offer for a different Electronics product without forking the schema.
2. **The Offer is the binding artifact.** `Offer.resourceIds` identifies the primary product. `Offer.addOns` lists the supplementary Resources, each of which is an `AddOn` per `beckn.yaml` — which is itself a `oneOf [Resource, Offer]`. The relationship between primary and add-on is structural (which array the resource appears in), not a new semantic type.
3. **The bundle price lives in `Offer.considerations`.** Bundle pricing belongs in `Consideration.considerationAttributes`, where domain-specific price schemas already apply. There is no need for a new schema to model "bundle pricing" — it is just a `Consideration` like any other.
4. **Inter-resource relationships are ID references.** `Warranty.coveredResourceId` and `HomeCare.compatibleWith[]` are simple `Resource.id` references defined in the relevant published schema. A consumer that does not understand them can still process each Resource by its own canonical type.
5. **A consumer that does not understand the combo at all** — e.g., an older CN that only renders flat catalogs — can still display every Resource correctly because each Resource is independently typed and self-describing. The combo is *additional* semantics in the Offer, not a precondition for processing the Resources.

##### When a `ComboProduct` relationship schema IS justified

The pattern above covers the overwhelming majority of bundle scenarios using primitives already in `beckn.yaml`. A new, focused `ComboProduct` **relationship** schema in `beckn/schemas` becomes justified only when the network needs richer bundle semantics that the existing primitives cannot express, such as:

- **Tiered bundles** in which different subsets of member Resources unlock different price tiers and the relationship rule must be machine-readable.
- **Substitutable bundles** in which alternative Resources may replace specific add-ons under stated conditions.
- **Dependency graphs** in which the inclusion of one add-on requires the inclusion of another.

A `ComboProduct` schema authored under those conditions MUST follow the principle to the letter: it describes the **relationship**, never the member products. A reasonable minimal shape would be:

```text
ComboProduct (a Resource extension, carried in resourceAttributes)

  comboType:           enum [ KIT, STARTER_PACK, TIERED_BUNDLE,
                              SUBSTITUTABLE_BUNDLE, DEPENDENT_BUNDLE ]
  primaryResourceId:   Resource.id
  memberResourceIds:   Resource.id[]
  substitutionRules:   SubstitutionRule[]    # optional, machine-readable
  dependencyEdges:     DependencyEdge[]      # optional, directed
```

What `ComboProduct` MUST NOT do:

- It MUST NOT enumerate the attributes (price, brand, warranty terms, etc.) of the resources it relates. Those remain on the member Resources, typed by their own canonical schemas.
- It MUST NOT carry domain-specific (Electronics, Warranty, HomeCare) properties. It is domain-neutral by design.
- It MUST NOT exist in the same namespace as a schema whose name conjoins concept names (`ElectronicsWithWarranty`).

A consumer that does not understand `ComboProduct` falls back gracefully to processing each member Resource via its own canonical type, exactly as in the primitive-only example above. `ComboProduct` adds metadata; it never replaces the canonical typing of its members.

##### Summary — anti-patterns and indicators

**Reject during review:**

- Any new schema name that contains the word `With`, `And`, or `Plus` joining two concept names.
- Any new schema that imports the property set of two unrelated existing schemas under a single new type.
- Any new schema authored to express "X is offered together with Y" — the composition belongs in an `Offer`, not in a new schema.
- Any new schema that duplicates fields already available on `Offer.considerations`, `Offer.addOns`, `Offer.resourceIds`, or `Resource.resourceAttributes`.

**Indicators that a new relationship schema is justified:**

- The relationship between resources cannot be expressed as a simple ID reference on an existing Resource type.
- The relationship carries its own metadata (a bundle tier, a substitution rule, a dependency direction) that cannot be placed in `Offer.offerAttributes` without making the Offer schema heavier for unrelated use cases.
- The relationship is reusable across multiple resource-type combinations — i.e., it would benefit Electronics+Warranty, Grocery+Coupon, and Mobility+Insurance equally.

When in doubt, **composition over extension**.

---

### Conformance requirements

| ID | Requirement | Level |
|---|---|---|
| CON-012-01 | Before proposing a new schema, contributors MUST search the Beckn Schema Registry for existing schemas that address the use case. | MUST |
| CON-012-02 | Every schema pack published to a shared venue MUST include `attributes.yaml`, `schema.json`, `context.jsonld`, `vocab.jsonld`, and `README.md`. | MUST |
| CON-012-03 | Schema versions MUST follow Semantic Versioning. | MUST |
| CON-012-04 | Published schema version directories MUST NOT be modified in place. Corrections require a new version. | MUST |
| CON-012-05 | Breaking changes MUST increment the MAJOR version and carry a minimum ninety-day deprecation notice period. | MUST |
| CON-012-06 | Extensions MUST NOT alter the meaning of any inherited core field. | MUST NOT |
| CON-012-07 | Schema PRs MUST follow the Discussion → Issue → PR to `draft` → PR to `release` → PR to `main` flow. PRs MUST NOT be raised directly to `main`. | MUST |
| CON-012-08 | Production implementations MUST validate message structure against `beckn.yaml` before processing `Attributes` content. | MUST |
| CON-012-09 | Production implementations MUST pin to an explicit schema version in all `@context` URIs. | MUST |
| CON-012-10 | Production implementations MUST maintain a `@context` URI allowlist and reject payloads whose extension context is not trusted. | MUST |
| CON-012-11 | Standalone NFO-scoped schemas are NOT RECOMMENDED. NFOs SHOULD contribute extensions upstream to `beckn/schemas` or `beckn/DEG` rather than fork the vocabulary. | SHOULD NOT |
| CON-012-12 | Network-specific `context.jsonld` and `vocab.jsonld` artifacts MUST NOT redefine any property or class already defined in the domain-agnostic vocabulary. | MUST NOT |
| CON-012-13 | Network-specific vocabulary terms MUST link back to the most specific superset concept in the domain-agnostic vocabulary using `rdfs:subClassOf`, `skos:broader`, or an equivalent JSON-LD construct. | MUST |
| CON-012-14 | All messages exchanged on a Beckn network MUST use the domain-agnostic vocabulary on the wire. Network-specific terminology MUST be applied only at CN and PN boundaries via JSON-LD expansion and compaction. | MUST |
| CON-012-15 | NFO-hosted experimental artifacts MUST NOT use `schema.beckn.io` or any `beckn.org` domain as their `@context` URI prefix, and MUST be retired once the corresponding upstream contribution is merged. | MUST NOT |
| CON-012-16 | `@context` resolution in production MUST use HTTPS with certificate validation. | MUST |
| CON-012-17 | Implementations SHOULD apply semantic expansion (JSON-LD processing) for cross-network message exchanges. | SHOULD |
| CON-012-18 | Shared schemas in `beckn/schemas` and `beckn/DEG` MUST NOT make any attribute mandatory by default. Mandatoriness MUST be expressed through network policy or manufacturer policy-as-code, not through the shared schema. | MUST NOT |
| CON-012-19 | NFOs SHOULD be added as external collaborators to `beckn/schemas` for the schemas relevant to networks they operate. Maintainers (including NFO collaborators) MAY merge PRs that conform to the design principles without CWG sign-off. | SHOULD |
| CON-012-20 | Schema PRs MUST conform to the design principles documented in [Design principles for schema authors](#design-principles-for-schema-authors). PRs that violate these principles MUST be rejected regardless of who reviews them. | MUST |
| CON-012-21 | The `@context` property of every `Attributes` container MUST be a single string URL, as constrained by the `Attributes` schema in `api/v2.0.0/beckn.yaml`. Implementations MUST NOT serialize `@context` as an array inside `Attributes` containers on the wire. | MUST |
| CON-012-22 | NFOs that need to layer multiple JSON-LD vocabularies MUST publish a single combined context document and reference it from the wire as a single URL. Composition of multiple contexts MUST occur in the published document, not on the wire. | MUST |
| CON-012-23 | All example payloads in any document referencing this RFC MUST be strictly conformant with `api/v2.0.0/beckn.yaml` and MUST reference schemas published in `github.com/beckn/schemas` (or `github.com/beckn/DEG` for energy schemas). Fabricated schemas, properties, or endpoints MUST NOT be used in normative examples. | MUST |
| CON-012-24 | Schema authors MUST NOT introduce schema names that conjoin existing concept names (e.g., names containing `With`, `And`, or `Plus` joining two concept tokens such as `ElectronicsWithWarrantyAndHomeCare`). Bundles, kits, and combo offers MUST be expressed using the composition primitives already defined in `api/v2.0.0/beckn.yaml` (`Offer.resourceIds`, `Offer.addOns`, `AddOn`, `Offer.considerations`, and `Resource.id` references on `resourceAttributes`). | MUST NOT |
| CON-012-25 | Where existing composition primitives are genuinely insufficient, a new schema MAY be authored only as a domain-neutral **relationship schema** that describes the relationship between member Resources. Such a relationship schema MUST NOT enumerate the attributes of the Resources it relates. | MUST NOT |
| CON-012-26 | Schemas MUST be designed for AI agents per [Principle 3: Agent-First Design](#principle-3-agent-first-design): descriptions MUST read as standalone semantic prose, term names MUST align with industry vocabulary, and every domain or network-specific term in `vocab.jsonld` MUST carry an explicit `rdfs:subClassOf`, `skos:broader`, `owl:sameAs`, or equivalent relation that links it to a superset concept reachable from the canonical Beckn vocabulary. Schema authoring SHOULD use AI as the primary instrument for naming, description, and semantic mapping per [Authoring with AI](#authoring-with-ai); the human author's role is curatorial. | MUST / SHOULD |
| CON-012-27 | Schema authors SHOULD prefer **dense `Descriptor` content** (rich `longDesc` prose plus `mediaFile[]` and `docs[]` references) over deeply-nested structured trees in `Attributes`. Structured fields in `Attributes` SHOULD be limited to values that participate in arithmetic, in deterministic filtering, or in cross-resource reference. Restrictive enums in `schema.json` SHOULD be replaced by JSON-LD vocabulary terms with `rdfs:subClassOf` or `skos:broader` linkages in `vocab.jsonld` so that the semantic graph remains open. See [Anti-pattern: Overdesigning schemas in an AI-first world](#anti-pattern-overdesigning-schemas-in-an-ai-first-world). | SHOULD |
| CON-012-28 | Schema authors SHOULD treat schema design as **context engineering at the protocol layer** per [Context Engineering](#context-engineering): the publisher-side configuration of `Descriptor` content, `Attributes` shape, `mediaFile[]` / `docs[]` references, and `vocab.jsonld` linkages MUST be evaluated for how well they support the **write / select / compress / isolate** patterns downstream agents apply. Where an entity's semantics can be fully expressed inside `Descriptor` (prose, media, documents, JSON-LD `@type`), a new schema extension of `Resource`, `Contract`, or `Offer` SHOULD NOT be authored. | SHOULD |

---

## Conclusion

This RFC defines the full lifecycle for Beckn schema artifacts from motivation through publication, extension, versioning, and production use. The schema extension mechanism is the primary means by which Beckn Protocol accommodates domain diversity without modifying the core transport layer. Its value depends entirely on schemas being created for the right reasons, published through the right process, governed by the right authorities, and consumed with the right validation guarantees. Schemas that bypass this lifecycle — whether through premature publication, informal extension, or unvalidated consumption — erode the semantic interoperability that the mechanism was designed to provide.

---

## Acknowledgements

This document reflects the governance model and schema design guidance developed by the Beckn Protocol Core Working Group and community contributors.

---

## References

### Beckn Protocol and governance

- [NFH-002 Keyword Definitions](./Keyword_Definitions.md)
- [NFH-003 The Beckn Protocol Stack](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/The_Beckn_Protocol_Stack.md) (drafted on `draft` branch, undergoing review)
- [NFH-004 Core Data Schema](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Core_Data_Schema.md) (drafted on `draft` branch, undergoing review)
- [NFH-005 Linked Data Schema](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Linked_Data_Schema.md) (drafted on `draft` branch, undergoing review)
- [NFH-009 Specification Design Guide](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Design_Guide.md) (drafted on `draft` branch, undergoing review)
- [NFH-010 RFC Authoring Guide](./RFC_Authoring_Guide.md)
- [GOVERNANCE.md](../GOVERNANCE.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [Beckn Schema Registry](https://schema.beckn.io)
- [beckn/schemas repository](https://github.com/beckn/schemas)
- [beckn/DEG repository](https://github.com/beckn/DEG)

### Context engineering — contemporary industry guidance

These external sources informed the framing in the [Context Engineering](#context-engineering) subsection. They are listed for reader reference only and do not constitute an endorsement.

- Anthropic, *Effective context engineering for AI agents* — [anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- LangChain, *Context engineering for agents* — [langchain.com/blog/context-engineering-for-agents](https://www.langchain.com/blog/context-engineering-for-agents)
- DAIR.AI, *Context engineering guide* — [promptingguide.ai/guides/context-engineering-guide](https://www.promptingguide.ai/guides/context-engineering-guide)
