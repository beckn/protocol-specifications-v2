# RFC-005: Specification Design Guide

## Status of this document

This document is a Working Draft of the Beckn Protocol Specification, published by the Networks for Humanity Foundation. It is subject to change without notice. Feedback may be submitted via the issue tracker linked in the Document Details section.

## Copyright Notice

Copyright © 2026 Networks for Humanity Foundation. All rights reserved.

## Document Details

- **Publication Status:** Draft.
- **Authors:** 
  - Ravi Prakash V, Networks for Humanity Foundation 
- **Created:** 2026-04-10.
- **Updated:** 2026-04-10.
- **Version history:** Draft-01 (2026-04-10): Initial publication as RFC-005. Restructured from `05_Specification_Authoring_Style_Guide.md` into RFC form.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/release-v2.0.0-lts/docs/Design_Guide.md).
- **Implementation report:** Not applicable (authoring and governance guidance RFC).
- **Stress test report:** Not applicable.
- **Conformance impact:** Normative for authoring quality and interoperability hygiene.
- **Security/privacy implications:** Reduces semantic ambiguity that can cause unsafe processing or misinterpretation.
- **Replaces / Relates to:** Replaces non-RFC-form content in `05_Specification_Authoring_Style_Guide.md`.
- **Feedback:** Issues Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-005%22), Discussions Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-005%22), Pull Requests Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-005%22).
- **Errata:** To be published.

## Abstract

This RFC defines authoring rules for Beckn API Specifications, Fabric-aware schema, JSON-LD artifacts, and supporting documentation so that naming, semantics, validation, and backward-compatible evolution remain consistent across repositories and teams.

## Table of Contents

- [Introduction](#introduction)
- [Definitions](#defintions)
- [Scope and Audience](#scope-and-audience)
- [Core Principles](#core-principles)
- [Designing API Endpoints](#designing-api-endpoints-required)
  - [Naming Convention](#naming-convention)
  - [Writing Descriptions](#writing-descriptions)
- [Designing Schema](#designing-schema-required)
  - [Naming the Schema](#naming-the-schema)
  - [Describing a Schema](#describing-a-schema)
  - [Managing Exceptions and Offending Schemas](#managing-exceptions-and-offending-schemas)
- [Schema Organization Rules](#schema-organization-rules-required)
  - [Schema Source Directory](#schema-source-directory)
  - [Schema Directory Structure](#schema-directory-structure)
- [JSON-LD Conventions](#json-ld-conventions)
- [Schema Authoring and Validation Gates](#schema-authoring-and-validation-gates)
- [Change Management and Compatibility](#change-management-and-compatibility)
- [Cross-Artifact Checklist](#cross-artifact-checklist)
- [Examples and Normalization Patterns](#examples-and-normalization-patterns)
- [Conformance Requirements](#conformance-requirements)
- [Security and Interoperability Considerations](#security-and-interoperability-considerations)
- [Conclusion](#conclusion)
- [Acknowledgements](#acknowledgements)
- [References](#references)

## Introduction

Beckn Protocol specifications are authored across multiple repositories, and small inconsistencies in naming, schema semantics, endpoint tokenization, and documentation-example alignment can accumulate into interoperability debt. This guide establishes a common authoring baseline so artifacts evolve predictably, remain validation-aligned, and reduce the risk of unsafe parsing or inconsistent policy enforcement.

## Definitions

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in the [Keyword Definitions](./Keyword_Definitions.md) document.

From hereon, all references of "fabric" will refer to the Universal Value-exchange Fabric hosted by the Networks for Humanity Foundation, unless explicitly mentioned otherwise. 

- **Machine contract:** Authoritative artifacts such as `attributes.yaml` and `schema.json` that define enforceable structure.
- **Semantic artifacts:** `context.jsonld` and `vocab.jsonld` files that define linked-data meaning and term mapping.
- **Schema pack:** A versioned bundle of required and optional schema, context, vocab, and documentation assets.
- **Cross-artifact consistency:** The requirement that contracts, semantic files, examples, and prose stay aligned.
- **Backward-compatible evolution:** An additive, mapped, deprecated-first change strategy for renames or replacements.
- **Canonical naming:** Governed, consistent naming for types, properties, enums, and endpoint actions.

## Scope and audience

This RFC applies to architects and maintainers of:

- Beckn Protocol APIs
- Fabric APIs
- Fabric-aware schema 
- Domain, regional, and network-specific schema

## Core principles

### Naming
Global protocol design should be inclusive and empathetic to the regional and linguistic diversity of the implementing ecosystem. Therefore, complicated multi-word, ambiguous keywords will create confusion and recall overhead in the minds of the implementer, especially when they are not fluent in english. The simplicity of the keywords, `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` used for HTTP method names are a example of the inclusivity and developer empathy embedded in their design. 

The naming conventions of Fabric keywords should use such inclusive and empathetic design patterns to allow smooth adoption across the globe. 

The following design principles SHOULD be considered by any architect coining the name of any keyword (i.e. endpoint, schema, property, or enumeration). 

1. **Semantic clarity:** The name of any keyword SHOULD convey its semantics purely by its structure.
2. **Least token/word count:** The number of tokens used in any keyword SHOULD be minimized as much as possible.
3. **Least number of syllables:** Any keyword when verbally expressed SHOULD involve the least number of syllables.
4. **High retention and recall:** Keywords SHOULD be easy to remember and recall.

### Schema evolution

When designing schema terms and IRIs, the following principles SHOULD be applied:

1. **Semantic stability:** Names and IRIs SHOULD preserve stable meaning across versions.
2. **Composable evolution:** New terms SHOULD extend, not duplicate or redefine, existing semantics.
3. **Backward-safe change:** Renames and removals MUST carry migration and ontology mapping.

## Designing API Endpoints (REQUIRED)

### Naming Convention
Naming protocol endpoints is an extremely crucial step in long-term protocol stability. The design challenge is to convey maximum meaning using the least amount of tokens/words with the least number of syllables while creating high recall value.

An example for such an endpoint name in Beckn is `track`. It uses only one syllable, conveys its purpose unambiguously, and has high recall.

For an action name, the ideal number of syllables is *one* but the recommended limit is *two*, although exceptions MAY be considered and accepted by the protocol working group, albeit begrudgingly. 

> Exception: The `discover` endpoint is an example of a three syllable action, which is an exception to the least syllables rule. 

#### For stateless APIs
- The last path parameter of the request endpoint MUST be a **verb** describing the action requested by the caller. The `discover`, `select`, `init` (short for initialize), `confirm`, `update`, `cancel`, `track`, `rate`, `support` are all verbs.
- The last path parameter of the callback endpoint MUST be the verb used in the request endpoint preceeded by an `on_`. For example, the callback endpoint for `discover` endpoint MUST be `on_discover`. 
  
> NOTE: The ONLY exception to the verb rule is the `status` endpoint, which has been preserved as a legacy endpoint name due to its meaning being consistent across the globe. An endpoint with the name `/status` typically means *"get the status"*, hence the deviation from the "verb-like" naming. However, all future endpoints MUST ALWAYS be in a verb form. 

#### For stateful APIs
- For stateful, Fabric service APIs like cataloging, registry, etc, the endpoint naming MUST follow the format `resource/action` for request, and `resource/on_action` for the callback endpoint. For example, if the resource being managed on the fabric is a **catalog**, and the action being performed on that resource is **publish**, then the endpoints MUST be `catalog/publish` and `catalog/on_publish`. 

- Legacy endpoint exceptions MUST be explicitly documented and MUST NOT become new precedent.

#### Casing rules 
- Endpoints MUST use `snake_case` path tokens.

### Writing descriptions
An endpoint description MUST precisely state what the endpoint does in terms of the fabric-aware value-exchange model. It MUST NOT use informal language or leave any aspect of the endpoint's behaviour implicit or assumed.

Each endpoint description MUST include the following:

**1. Action statement.** A single sentence beginning with a verb that states what the caller requests and what the implementer performs. Both actor names MUST be stated explicitly. For example: *"The BAP invokes this endpoint to request the BPP to confirm a previously initialized order contract."*

**2. Preconditions.** Any state or prior API call that must have occurred before this endpoint may be invoked MUST be stated. For example: *"This endpoint MUST only be invoked after a successful `on_init` response has been received by the BAP."*

**3. Fabric context.** Where the endpoint interacts with or depends on a Fabric service (such as the Discovery Service, Registry, or catalog infrastructure), the relationship MUST be stated and the relevant Fabric component MUST be named. If a canonical document describes that component, a hyperlink to that document MUST be embedded inline within the description text.

**4. Message envelope.** The description MUST state the required envelope fields and their significance for this endpoint. All properties of the `context` and `message` objects that carry endpoint-specific semantics MUST be individually described.

**5. Response semantics.** Every response family (`Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, `ServerError`) that the implementer may return MUST be described. The description MUST state what each response means in the context of this specific endpoint's behaviour — it MUST NOT merely restate the HTTP status code.

**6. Callback relationship.** For request endpoints that have an `on_*` callback counterpart, the description MUST state when and by whom the callback is triggered, what it carries, and how the caller MUST interpret it.

**Tone and grammar.** Descriptions MUST be written in formal technical prose. The passive voice SHOULD be used only when the active actor is genuinely indeterminate. Descriptions MUST NOT contain colloquial phrasing, unexplained abbreviations, or normative requirements expressed in informal language. Every normative statement MUST use the keywords `MUST`, `SHOULD`, or `MAY` as defined in [Keyword Definitions](./Keyword_Definitions.md).

**Conformance to the fabric-first narrative.** Endpoint descriptions MUST reflect the fabric-first positioning of the Beckn Protocol. Endpoints that operate through Fabric services — such as catalog publishing, catalog-driven discovery, and registry lookup — MUST be described in terms of the Fabric infrastructure, not solely in terms of peer-to-peer exchange. The role of the NFH Fabric as the central coordination layer MUST be acknowledged wherever it is relevant to the endpoint's behaviour.

### Examples

#### ✓ Preferred — `/confirm`

> The BAP invokes this endpoint to request the BPP to confirm a previously initialized order contract. This endpoint MUST only be invoked after a successful `on_init` response has been received by the BAP, establishing an active initialized transaction identified by `context.transactionId`. The BPP MUST validate the signature on the request as described in [Authentication and Trust](./Authentication_and_Trust.md) before processing. Upon successful validation and processing, the BPP MUST return an `Ack` synchronously and subsequently invoke the `/on_confirm` callback on the BAP's registered callback URI, carrying the confirmed `Contract` object in the `message` field. If signature validation fails, the BPP MUST return a `NackUnauthorized` response and MUST NOT invoke the callback. If the request body is structurally invalid or the `transactionId` does not correspond to an active initialized transaction, the BPP MUST return a `NackBadRequest` response. For the role of a confirmed contract within the NFH Fabric's value-exchange lifecycle, refer to [Value Exchange Lifecycle](./Value_Exchange_Lifecycle.md).

Both actor names are present, the precondition is explicit, every response family is described with business semantics, the callback relationship is fully stated, and two canonical documents are linked inline.

#### ✗ Avoid — `/confirm`

**Variant A — Too brief**

> "Confirms the order."

No actors named, no precondition, no response semantics, no callback described. A reader cannot implement this endpoint from this description alone.

---

**Variant B — Casual and assumption-laden**

> "Call this when you want to confirm an order. Returns 200 OK on success, otherwise returns an error."

Second-person voice is informal and ambiguous about which actor is the caller. The description restates the HTTP status code instead of describing business-level response semantics. It assumes the reader knows what "an error" means in this context and makes no mention of the callback, preconditions, or fabric context.

---

**Variant C — Structurally correct but semantically empty**

> "This endpoint is used for order confirmation. The BPP processes the request and sends a response back to the BAP."

Names the actors but conveys nothing about preconditions, signature validation, which response families apply, what the callback carries, or how this fits into the fabric-first lifecycle.

## Designing Schema (REQUIRED)

### Naming the schema
Naming a schema is a practiced skill for a protocol architect. It requires thorough industry research, strong communication skills, and developer empathy. Like endpoints, the design challenge is to convey maximum semantics with the least amount of tokens or words using the least number of syllables, while creating high recall value. 

Schema authors MUST assume that the schema user (typically a developer) will NOT read and understand the canonical description of the schema in detail. The name of the schema should be extremely intuitive and self describing. Schema authors are strongly advised to include a language refinement step in their design process. In today's AI-powered world, a simple prompt like this should work. 

> Prompt: "Generate an intuitive name for (describe concept). Widely adopted, industry-defined name for this concept take precedence over coining your own. Multi-word names are allowed"

#### Naming Rules
Schemas MUST always be nouns or the noun forms of verbs (especially when describing the state of an action).

Domain-agnostic schema names should be abstract but meaningful and unambiguous. Any schema user reading the name of the schema should get a fairly good idea of its meaning without referring to its canonical description.

Multi-word, industry-agnostic names like `FulfillmentAgent` or `PaymentMethod` are allowed. However, it is RECOMMENDED to restrict the components of a multi-word schema to **two**. Anything more than two is strongly discouraged until there is no other way to convey its meaning.

Extremely long, verbose schemas are also discouraged. 

Authors coining domain or industry-specific schema names MUST use the most widely adopted, industry standard terms instead of coining their own. For example, a business offering EV charging services should be called a `ChargingPointOperator` instead of something like `ChargingServiceProvider` which although seems clear, is NOT the industry standard term. 

When naming a schema that describes an action, it is REQUIRED to append a word `Action` as a suffix to the schema. For example, when describing an act of payment, the preferred name is `PaymentAction` instead of just `Payment` which creates a doubt in the mind of the user if the term is describing the act of payment or the state of payment.

#### Casing rules 
- Types and classes MUST use `TitleCase`.
- Properties MUST use `lowerCamelCase`.
- Enum values MUST use `SCREAMING_SNAKE_CASE`.
- Reserved or ambiguous property names such as `type` SHOULD be avoided, except for JSON-LD `@type`.

### Describing a schema

A schema description MUST precisely state what real-world concept, entity, or state the schema represents. It MUST NOT describe the schema in terms of its structural composition (e.g., *"an object containing X and Y"*) but exclusively in terms of its semantic meaning within the value-exchange model.

**Describing the schema itself.** The top-level description of a schema MUST include:

**1. Concept statement.** A single sentence identifying the real-world concept the schema models. The sentence MUST be unambiguous — a reader with no prior context MUST be able to identify the concept from the description alone, without reading the property definitions.

**2. Scope and lifecycle position.** The description MUST state in which part of the value-exchange lifecycle this schema appears, and which actors produce or consume it.

**3. Fabric context.** Where the schema models a resource managed by or exchanged through a Fabric service, that relationship MUST be named, and a hyperlink to the relevant canonical document MUST be embedded inline in the description. The same document IRI MUST also appear as a `seeAlso` triple in the schema's `vocab.jsonld` file.

**4. Relationship to other schemas.** If the schema extends, composes, or constrains another schema, that relationship MUST be stated explicitly.

**Describing properties.** Every property of a schema MUST have a description. Property descriptions MUST:

- State what the property represents, not merely restate its name.
- State whether the value is assigned by the caller, the implementer, or a Fabric service.
- State any constraints on the value that are not already captured by the JSON Schema type declaration (e.g., business-rule constraints, lifecycle invariants, or ordering requirements).
- For properties whose value is drawn from an enumeration, describe what each enumeration value means in the context of this specific schema.
- For properties that reference another schema by type, state the semantics of that reference rather than merely naming the referenced type.

**Tone and grammar.** Schema and property descriptions MUST be written in formal technical prose. They MUST NOT be written as imperative instructions or in the first or second person. Normative constraints on values MUST use `MUST`, `SHOULD`, or `MAY` as defined in [Keyword Definitions](./Keyword_Definitions.md). Descriptions MUST NOT assume domain-specific knowledge on the part of the reader unless that knowledge is defined elsewhere in this specification, in which case a hyperlink to that definition MUST be embedded inline.

**Conformance to the fabric-first narrative.** Schema descriptions MUST reflect the fabric-first positioning of the Beckn Protocol. Schemas that model Fabric-managed resources — such as catalogs, contracts, or registry entries — MUST be described in terms of their role within the NFH Fabric, not merely as data transfer objects.

### Examples

#### ✓ Preferred — `Contract` schema

**Schema-level description:**

> A `Contract` represents the formally agreed state of a value-exchange transaction between a BAP and a BPP, governed by the NFH Fabric. It is produced by the BPP and transmitted to the BAP in the `on_confirm` callback response. It constitutes the authoritative, cryptographically anchored record of the negotiated terms, fulfillment obligations, and payment conditions for a transaction. Once confirmed, a `Contract` serves as the reference object for all subsequent lifecycle operations including `status`, `update`, `cancel`, and `track`. For the full lifecycle in which a `Contract` transitions through states, refer to [Value Exchange Lifecycle](./Value_Exchange_Lifecycle.md).

**Property — `id`:**

> A globally unique identifier for this contract instance, assigned by the BPP at the time of confirmation and carried in all subsequent `status`, `update`, `cancel`, and `track` requests to identify the transaction. This value MUST remain stable for the entire lifetime of the contract and MUST NOT be reassigned or reused across distinct transactions.

**Property — `state`:**

> The current lifecycle state of the contract as maintained by the BPP. The value MUST be one of the enumeration values defined in `ContractState`. `ACTIVE` indicates the contract is in force and fulfillment is ongoing. `CANCELLED` indicates the contract has been terminated prior to fulfillment completion, and MUST only appear after a successful `on_cancel` exchange. `COMPLETED` indicates all fulfillment and payment obligations have been met.

The concept statement names the real-world entity, both actors, and the fabric role. Both property descriptions state who assigns the value, when, and what constraints apply. The `state` property covers every enumeration value with business semantics.

#### ✗ Avoid — `Contract` schema

**Variant A — Structural, not semantic**

Schema-level: `"An object that contains order details including items, fulfillment, and payment."`

Property `id`: `"The ID of the contract."`

Lists structural contents instead of stating what the concept represents. The property description for `id` is a pure restatement of the property name with no information about who assigns it, when, or what constraints apply to it.

---

**Variant B — Domain assumption without definition**

Schema-level: `"Represents a confirmed booking or purchase on the platform."`

Uses the word "platform" without definition, implying a single-platform context that contradicts the decentralised, multi-network nature of the Beckn Protocol. "Booking or purchase" introduces domain-specific assumptions not supported by the schema's actual scope. No lifecycle position, no actors, no fabric context.

---

**Variant C — Imperative tone**

Schema-level: `"Use this schema to send confirmed order data from BPP to BAP."`

Property `state`: `"Set this to the current state of the order."`

Written in the imperative ("Use this", "Set this"), which is the voice of a tutorial, not a specification. The property description for `state` gives no indication of what valid values are, who sets them, or what each value signifies.

### Managing Exceptions and Offending Schemas
Sometimes due to timeline constraints, and implementer demand, some schema names tend to violate the above rules. Such schemas are called **offending schemas**. While such practices are not recommended, the protocol does allow for their temporary existence. Schema authors are REQUIRED to eventually deprecate these names and provide clean machine-readable migration paths using `owl` syntax describing the deprecation of the offending schema name to the compliant schema name. This is also an opportunity for external contributors to flag such offending schemas as issues and keep such deviations in check. 

## Schema Organization Rules (REQUIRED)
Every schema defined in the scope of the fabric MUST conform to the following organizational pattern. 

### Schema Source Directory
All schemas defined in a specific context must be grouped inside a single directory. While the name of the directory is irrelevant, it is RECOMMENDED to have an intuitive name like `schema`, `schemas`, or `models`. A typical schema catalog directory looks like this.

```text
schemas/ 
├── ExampleSchemaOne/ 
│   └── v2.0/
│   │   ├── ...
│   │   └── ...
│   └── v2.1/
│   │   ├── ...
│   │   └── ...
│   └── v2.1.1/
│       ├── ...
│       └── ...
│
├── ExampleSchemaTwo/
│   ├── v1.0/
│   │   ├── ...
│   │   └── ...
│   ├── v2.0/
│   │   ├── ...
│   │   └── ...
│   └── v3.1/
│       ├── ...
│       └── ...
├── context.jsonld (Master context for all schemas)
├── vocab.jsonld (Master vocabulary for all schemas)
└── README.md
```

### Schema Directory Structure
Every schema MUST reside in a schema directory whose name is the same as the schema with matching case. For example, a schema called `Catalog` MUST be defined in a directory called `Catalog`

```text
├── Catalog/
│   └── v1.0/
│   │   ├── attributes.yaml
│   │   ├── schema.json
│   │   ├── context.jsonld
│   │   ├── vocab.jsonld
│   │   ├── profile.json
│   │   ├── renderer.json
│   │   └── README.md
│   ├── v2.0/
│   │   ├── attributes.yaml
│   │   ├── schema.json
│   │   ├── context.jsonld
│   │   ├── vocab.jsonld
│   │   ├── profile.json
│   │   ├── renderer.json
│   │   └── README.md
│   ├── v3.1/
│   │   ├── ...
│   │   └── ...
│   └── README.md (Canonical, version-agnostic description)
├── .../
```

Expected schema pack structure:

- Required: `attributes.yaml`, `schema.json`, `context.jsonld`, `vocab.jsonld`, `README.md`
- Optional: `renderer.json`, `profile.json`, `examples/**`

## JSON-LD conventions

- Composition and extension objects MUST include `@context` and `@type`.
- Every schema term MUST map to an IRI.
- `context.jsonld` and `vocab.jsonld` MUST remain aligned with schema contracts.
- Renamed terms SHOULD include explicit ontology relations and migration mapping.

## Schema authoring and validation gates

Each schema bundle MUST pass:

- OpenAPI validation for `attributes.yaml`
- JSON Schema validation for `schema.json`
- JSON-LD validation for `context.jsonld` and `vocab.jsonld`

Core schemas SHOULD default to `additionalProperties: false`; extension containers SHOULD remain open and carry explicit semantic metadata.

### Artifact precedence

When artifacts conflict, the following precedence MUST be applied:

1. `attributes.yaml`
2. `schema.json`
3. `context.jsonld`
4. `vocab.jsonld`
5. `examples`
6. `docs`
7. `README.md`

## Change management and compatibility

Breaking changes include:

- renaming properties, types, or enums
- adding required fields
- changing term meaning without introducing new terms

The preferred migration path is:

1. Add the new term while retaining the old term.
2. Mark the old term as deprecated.
3. Publish migration notes and semantic mapping.
4. Remove the old term only in a planned major release.

## Cross-artifact checklist

Before merge, authors SHOULD verify:

- canonical naming and casing consistency
- action and callback pairing with deterministic action derivation
- alignment across `attributes.yaml`, `schema.json`, `context.jsonld`, and `vocab.jsonld`
- examples validate against canonical contracts
- migration notes exist for renames and deprecations
- attribution and upstream traceability exist for derived specifications

## Examples and normalization patterns

Example naming normalization:

```text
transaction_id -> transactionId
expires_at -> expiresAt
http/get -> HTTP_GET
filters.type -> filters.expressionType
```

Example action and callback pairing:

```text
/select -> /on_select
/catalog/publish -> /catalog/on_publish
```

## Conformance requirements

| ID | Requirement | Level |
|---|---|---|
| CON-005-01 | New schema properties MUST use `lowerCamelCase` and MUST NOT introduce `snake_case`. | MUST |
| CON-005-02 | Enum values MUST use `SCREAMING_SNAKE_CASE` for canonical representation. | MUST |
| CON-005-03 | Authors MUST keep `attributes.yaml`, `schema.json`, `context.jsonld`, and `vocab.jsonld` semantically aligned. | MUST |
| CON-005-04 | Breaking renames and removals MUST include deprecation and migration guidance. | MUST |
| CON-005-05 | Examples and documentation SHOULD validate against canonical machine contracts. | SHOULD |
| CON-005-06 | Endpoint descriptions MUST explicitly name both the caller and the implementer actor. | MUST |
| CON-005-07 | Endpoint descriptions MUST describe every applicable response family using business semantics, not HTTP status codes. | MUST |
| CON-005-08 | Schema descriptions MUST be written as concept statements and MUST NOT describe structural composition. | MUST |
| CON-005-09 | Every property of a schema MUST have a description stating what it represents and who assigns its value. | MUST |
| CON-005-10 | All endpoint and schema descriptions MUST be written in formal technical prose using normative keywords as defined in [Keyword Definitions](./Keyword_Definitions.md). | MUST |

## Security and interoperability considerations

Ambiguous naming, schema and documentation drift, and untracked semantic changes can cause unsafe parsing and inconsistent policy enforcement. Strict cross-artifact validation, deterministic action naming, and explicit semantic mapping reduce these risks.

# Conclusion

This RFC consolidates the style guide into a single ordered structure while preserving the original normative guidance for naming, artifact precedence, validation, compatibility, and semantic alignment. Draft-01 records this RFC-form restructuring, and future governance work may standardize JSON-LD extension patterns and automated pull-request gates for minimum cross-artifact checks.

# Acknowledgements

This document reflects input from Beckn Protocol contributors maintaining protocol contracts, schema packs, semantic artifacts, and governance processes.

# References

- **Keyword definitions:** [Keyword Definitions](./Keyword_Definitions.md)
- **Schema.org style guide:** Click [here](https://schema.org/docs/styleguide.html)
- **Related pull request 67:** Click [here](https://github.com/beckn/protocol-specifications-v2/pull/67)
- **Related pull request 68:** Click [here](https://github.com/beckn/protocol-specifications-v2/pull/68)

