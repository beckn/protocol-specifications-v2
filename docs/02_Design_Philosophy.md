# Beckn Architecture Design Philosophy and Principles

**Status:** Draft RFC  
**Author:** Ravi Prakash  
**Date:** 2026-03-03  
**Repository:** `beckn/protocol-specifications-v2`

---

## 1. Purpose

This document captures the design philosophy and derived principles that govern the Beckn Protocol architecture. Every architectural decision — which repo owns what, how schemas relate to the API spec, how the schema registry federates — must be traceable to this document. When a future decision conflicts with something here, this document is updated first, and the change is reasoned through, not made ad hoc.

---

## 2. Design Philosophy

Four philosophies guide all decisions. These have a longer half-life than any specific design principle. When principles conflict, refer back to the philosophy.

### 2.1 Minimalism

Every component does exactly one thing. No duplication across layers. No schema that knows about HTTP. No protocol spec that knows about business actions. When something can be expressed in one place, it is expressed in one place.

### 2.2 Future-readiness

Design for actors and use cases that don't exist yet. The current actors on the Beckn fabric are BAP, BPP, Registry, and Catalog Discovery/Publishing Services. Tomorrow there will be Issue and Grievance Management Services, Reconciliation and Settlement Services, Reputation Management Services, Credentialing Services, Observability and Insight Engines, Transaction Ledgers, and potentially AI Agents that eliminate the need for BAP/BPP altogether. The protocol must accommodate all of them without structural change.

HTTP did not know, when it was specified, that it would carry e-commerce transactions, social media feeds, payment flows, or AI agent calls. It has undergone only three major versions since publication. That is the standard we hold ourselves to.

### 2.3 Pragmatism

The design must be implementable today. Abstract ideals that cannot be shipped are not useful to the network. Every architectural decision must have a concrete, working implementation path. When a theoretically superior design cannot be realised with current tooling and team capacity, we choose the pragmatic approximation and document the gap as a future RFC.

### 2.4 Optimal Ignorance

Each layer knows only what it must to do its job. The protocol transport layer does not know what actions exist. The schema registry does not know about HTTP. Domain schema owners do not know about core schema internals. This principle limits coupling and enables independent evolution.

---

## 3. Derived Design Principles

These principles follow from the philosophy and are more specific. They may evolve across major versions of the protocol.

### 3.1 Protocol Stability (Long Half-Life)

The `protocol-specifications-v2` repository — and specifically `beckn.yaml` — must remain stable for a very long time. Stability here means: adding a new actor to the Beckn network, defining a new action, or onboarding a new domain should not require a commit to `protocol-specifications-v2`.

`beckn.yaml` defines pure transport: the universal HTTP endpoint pattern, authentication, ACK/NACK response shapes, and signature verification. It references the schema layer at exactly two points. Everything else evolves independently.

### 3.2 Independent Evolution

New actors, new actions, and new domains are added to the `schemas` repository (formerly `core_schema`) without touching `protocol-specifications-v2`. The schema registry is designed to absorb change. The protocol spec is designed to resist it.

### 3.3 One-Way Dependency

`protocol-specifications-v2` depends on `schemas`. `schemas` does not depend on `protocol-specifications-v2`. This is a strict one-way relationship. No schema in `schemas` may reference anything in `protocol-specifications-v2`.

### 3.4 Three-Import Principle

A Beckn implementer building a conformant API interface (e.g., ONIX or any Beckn-speaking client or server) requires exactly three imports:

1. `beckn.yaml` — the API specification
2. `context.jsonld` — the JSON-LD context mapping Beckn terms to IRIs
3. `vocab.jsonld` — the ontological vocabulary defining classes and properties

Everything else — all JSON Schema validation schemas, all action schemas, all data model schemas — is resolved automatically via `$ref` at compile time or runtime. No manual schema imports are required.

### 3.5 Federated Schema Registry

`schema.beckn.io` is a namespace router, not a monolithic schema store. Domain schema owners may host their schemas in their own repositories and register a domain prefix in the `schema.beckn.io` namespace routing manifest. External schemas are ingested through `schema-admin.beckn.io` (a staging and validation pipeline) before being published to `schema.beckn.io`.

This means:
- Core schemas: `https://schema.beckn.io/{SchemaName}/v2.0` — served from `beckn/schemas`
- Domain schemas: `https://schema.beckn.io/{domain}/{SchemaName}/v2.0` — served from the domain owner's repo (e.g. `beckn/DEG` for energy domain schemas)

No domain owner is forced to migrate their schemas into `beckn/schemas`. Migration is opt-in.

---

## 4. Architecture

### 4.1 Two-Tier Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Tier 1: protocol-specifications-v2  (transport — long half-life) │
│                                                                   │
│  beckn.yaml                                                       │
│  ├── HTTP endpoint: /discover, /on_discover, /select, /on_select, and related action endpoints (GET + POST)          │
│  ├── Authentication: Signature / CounterSignature                 │
│  ├── Responses: Ack, AckNoCallback, Nack, ServerError            │
│  ├── Transport binding: InReplyTo, LineageEntry                  │
│  └── $ref (2 points only):                                       │
│       ├── path param → https://schema.beckn.io/BecknEndpoint/v2.0│
│       └── request body → https://schema.beckn.io/BecknAction/v2.0│
└──────────────────────────────────┬──────────────────────────────┘
                                   │ one-way $ref
┌──────────────────────────────────▼──────────────────────────────┐
│  Tier 2: schemas (formerly core_schema)  (schema registry)       │
│                                                                   │
│  BecknEndpoint   — known endpoints + open extension pattern      │
│  Context         — transaction context (action → BecknEndpoint)  │
│  Message         — open payload container                        │
│  BecknAction     — Context + Message + if/then dispatch per action│
│                                                                   │
│  [Data model schemas: Catalog, Item, Provider, Fulfillment, ...] │
│  [Action schemas: DiscoverAction, SelectAction, ...]             │
│  [Domain schemas: /mobility/*, /logistics/*, /deg/*, ...]        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 `BecknAction` — The Unified Action Envelope

`BecknAction` is the schema that `beckn.yaml`'s request body resolves to. It:

- Requires a `context` (conforming to `Context`) and a `message` (open object)
- Uses a series of `if/then` pairs in `allOf` to conditionally constrain `message` based on `context.action`
- Covers all known action pairs (`beckn/discover` → `Intent` in message, `beckn/on_discover` → `Catalog[]` in message, etc.)
- Remains open for extension: unknown endpoint values pass through with an unconstrained `message`

This replaces the former `RequestAction` + `CallbackAction` split, which was both structurally broken and conceptually wrong (the protocol layer should not distinguish request from callback — that distinction is encoded in the action value).

### 4.3 `BecknEndpoint` — The Evolving Endpoint Enumeration

`BecknEndpoint` lives in `schemas`, not in `beckn.yaml`. It enumerates all known Beckn endpoints using a hybrid pattern:

- `oneOf` with `const` for each known endpoint (provides validation, documentation, tooling autocomplete)
- A catch-all `pattern` branch (`'^beckn\/[a-z_]+(?:\/[a-z_]+)*$'`) for extension endpoints from new actors

Adding a new actor's endpoints requires a commit to `schemas/BecknEndpoint`. It never requires a commit to `beckn.yaml`.

### 4.4 Federated Registry and Staging Pipeline

```
External domain repo (e.g. beckn/DEG)
        │
        │  (push / webhook)
        ▼
schema-admin.beckn.io
  ├── Schema validation (JSON Schema Draft 2020-12 conformance)
  ├── Vocabulary compatibility check (terms must be in vocab.jsonld or declared new)
  ├── Design principles adherence check
  └── Marshalling to expected folder structure
        │
        │  (publish — one-way, no bidirectional sync)
        ▼
schema.beckn.io
  (namespace router: serves /deg/* from beckn/DEG, /* from beckn/schemas, etc.)
```

### 4.5 Repo Structure (Target State)

| Repository | Role | Half-life |
|---|---|---|
| `beckn/protocol-specifications-v2` | Transport layer — `beckn.yaml` | Very long |
| `beckn/schemas` (renamed from `core_schema`) | Schema registry — all Beckn schemas | Medium |
| `beckn/DEG` | Energy domain schemas — external, registered in manifest | Medium |
| `beckn/mobility` | Mobility domain schemas — migration optional | Medium |
| `beckn/logistics` | Logistics domain schemas — migration optional | Medium |
| `beckn-one/schema.beckn.io` | Namespace router + website | Long |
| `beckn-one/schema-admin.beckn.io` | Staging and validation pipeline | Medium |

---

## 5. Known Deviations and Bugs (Current State)

The following deviations from the design principles exist in the current codebase and are being actively fixed:

| Location | Deviation | Fix |
|---|---|---|
| `core_schema/schema/RequestAction` | `oneOf` nested inside `properties` — invalid JSON Schema | Superseded by `BecknAction` |
| `core_schema/schema/CallbackAction` | Same structural bug | Superseded by `BecknAction` |
| `beckn.yaml` components | `Context`, `BecknEndpoint`, `Message` defined inline | Move to `schemas` via `$ref` |
| `core_schema/schema/Context` | References non-existent `Action/v2.0` schema | Fix to `$ref BecknEndpoint/v2.0` |
| `core_schema/schema/Context` | Duplicated between `core_schema` and `beckn.yaml` with divergent content | Consolidate in `schemas`, remove from `beckn.yaml` |
| `core_schema` action schemas | Not referenced by `beckn.yaml` — orphaned | Absorbed into `BecknAction` dispatch |

These are tracked in Issues #8 and related sub-issues in `beckn/core_schema`.

---

## 6. Future RFCs

The following design decisions are deferred, requiring dedicated RFC documents before implementation:

| RFC | Description |
|---|---|
| #16 | Enable polymorphic `@context` and `@type` — support arrays for domain extensibility |
| TBD | SDK generation from `beckn.yaml` + `schemas` — tooling specification |
| TBD | Versioning contract — how `beckn.yaml` stays stable across schema version bumps |
| TBD | Beckn example generation framework — specification for the retail use case generator |

---

## 7. Reference

- `beckn/core_schema` Issue #1 — Original schema review by @anandp504
- `beckn/core_schema` Issue #8 — Action schema architectural redesign
- `beckn/protocol-specifications-v2` RFC Issue — This document's tracking issue
- `beckn-one/schema.beckn.io` — Folder structure investigation issue
