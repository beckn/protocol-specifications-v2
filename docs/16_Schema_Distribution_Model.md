# Schema Distribution Model

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.0)

---

## 1. Overview

Beckn v2 distributes schema definitions across three tiers, each governed and evolved independently. This separation keeps the core protocol small and stable while allowing the schema ecosystem above it to grow freely.

---

## 2. The Three Tiers

### Tier 1 — Transport Envelope (This Repository)

**Repository:** `beckn/protocol-specifications-v2`  
**File:** `api/v2.0.0/beckn.yaml`

This tier defines the **transport contract only**: the universal API endpoint, the message envelope structure, the authentication contract, and the non-repudiation schemas. It carries no domain semantics.

Schemas defined here:

| Schema | Purpose |
|---|---|
| `Context` | Mandatory transaction context (IDs, timestamps, domain, action) |
| `RequestContainer` | Envelope for forward actions |
| `CallbackContainer` | Envelope for async callbacks |
| `Message` | Open container for domain payload (`additionalProperties: true`) |
| `Signature` | HTTP Signature credential |
| `CounterSignature` | Signed receipt in Ack response |
| `InReplyTo` | Cryptographic request–response binding |
| `LineageEntry` | Cross-transaction causal attribution |
| `Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, `ServerError` | Transport response types |

**Stability:** These schemas change extremely rarely. A change here is a major protocol version bump.

### Tier 2 — Core Transaction Schema

**Repository:** [`beckn/core_schema`](https://github.com/beckn/core_schema)

This tier defines **domain-agnostic transaction schemas** — the entities and actions that appear inside the `Message` payload. All schemas are JSON-LD with `@context` and `@type` annotations and are aligned with [schema.org](https://schema.org).

Schemas defined here (representative, not exhaustive):

| Schema | Purpose |
|---|---|
| `RequestAction` | Base type for all forward action payloads |
| `CallbackAction` | Base type for all callback action payloads |
| `DiscoverAction`, `SearchAction`, `SelectAction`, `InitAction`, `ConfirmAction`, ... | Specific action types |
| `Catalog`, `Provider`, `Item`, `Offer` | Lifecycle entities |
| `Order`, `Contract`, `Fulfillment` | Transaction entities |
| `Intent` | Discovery query structure |
| `NetworkParticipant` | Registry participant entity |

**Stability:** This tier evolves continuously. New fields, new action types, and new entity types are added here without affecting the transport envelope.

### Tier 3 — Domain Schema Packs

**Repositories:** Per-vertical repositories (e.g., `beckn/mobility-schema`, `beckn/retail-schema`)

Domain schema packs extend `core_schema` entities with sector-specific attributes using additional JSON-LD `@context` documents and typed attribute overlays.

Example: a `mobility-schema` pack adds ride-specific attributes to `Item` (vehicle type, route, fare class) and `Fulfillment` (driver details, GPS tracking) — without modifying the core `Item` or `Fulfillment` definitions.

**Stability:** Domain packs evolve independently. Multiple packs can be composed on a single entity (e.g., `mobility` + `carbon-accounting` on the same `Item`).

---

## 3. Schema Composability

### Design-Time Composability

At design time, a network defines:
- Which `core_schema` entities are mandatory.
- Which domain schema packs are required, optional, or prohibited.
- The JSON-LD `@context` documents to be used by participants.

This produces the network's **schema profile**, published as a Network Profile document (see [26_Network_Policy_Profiles.md](./26_Network_Policy_Profiles.md)).

### Run-Time Composability

At run time:
- Participants inspect `@context` and `@type` on received `Message` payloads to determine which schema they understand.
- Unknown schema can be safely ignored or passed through — backward compatibility is preserved.
- A single `Item` can carry attributes from multiple domain packs simultaneously.

---

## 4. The `Message` Object

The `Message` schema in `beckn.yaml` is intentionally defined as an open container:

```yaml
Message:
  type: object
  additionalProperties: true
```

This is deliberate. The transport envelope does not constrain the payload content. Domain semantics live entirely in Tier 2 and Tier 3 — the transport envelope is agnostic to them.

Implementations MUST NOT add domain-specific constraints to the `Message` schema in this repository.

---

## 5. External `$ref` Pattern

Tier 2 and Tier 3 schemas are referenced from `beckn.yaml` via external `$ref` URIs:

```yaml
message:
  $ref: "https://schema.beckn.io/core/v2/schemas/Message.json"
```

This allows schema resolution to be performed at run time against a version-pinned URI, keeping `beckn.yaml` free of domain schema content.

---

## 6. No `schema/` Directory — By Design

This repository intentionally contains **no `schema/` directory**. All transaction-level schemas are defined in `core_schema`. If a `schema/` folder appears anywhere in this repository, it is an error and should be removed.

---

## 7. Further Reading

- [17_JSONld_Context_and_Schema_Alignment.md](./17_JSONld_Context_and_Schema_Alignment.md) — JSON-LD context design rules
- [18_Schema_Pack_Contract.md](./18_Schema_Pack_Contract.md) — how domain schema packs are authored and versioned
- [`beckn/core_schema`](https://github.com/beckn/core_schema)
- [schema.beckn.io](https://schema.beckn.io)
---

## 8. Evolution Direction: Structural → Semantic Interoperability

Beckn schema evolution has moved from a **structural interoperability** focus (shape-level compatibility only) to a **semantic interoperability** focus (shared meaning across contexts, vocabularies, and ontological relations).

Implications:
- Compatibility is not just field-level shape matching.
- Vocabulary continuity and meaning preservation are first-class requirements.
- Schema evolution decisions should optimize cross-network machine interpretability.

### 8.1 Contributor-first pattern before proposing new schema

Before creating a new schema or schema version, schema authors MUST:
1. Search [schema.beckn.io](https://schema.beckn.io) for existing use-case-specific schemas.
2. Prefer extending an existing use-case schema where feasible.
3. Contribute improvements back to the existing use-case schema when appropriate.

PWG periodically reviews emerging patterns from use-case schemas and abstracts stable patterns into domain-agnostic/core constructs.

### 8.2 Meaning preservation in extensions

Extensions MUST be additive and MUST NOT change the semantic meaning of inherited terms.

A schema extension may refine, specialize, or add constraints, but must not redefine what an existing class/property means.

### 8.3 Mandatory semantic artifacts

All schema packs MUST include both:
- `context.jsonld`
- `vocab.jsonld`

Both artifacts MUST conform to the rules in [05_Specification_Authoring_Style_Guide.md](./05_Specification_Authoring_Style_Guide.md).

### 8.4 Version-to-version vocabulary continuity

For any schema version `vN+1` relative to `vN`:
- `vN+1` MUST carry forward `vN` vocabulary and context terms unless deprecated.
- `vN+1` SHOULD be semantically richer than `vN`.
- Deprecated terms MUST remain mapped with explicit deprecation semantics.
- New vocabulary in `vN+1` MUST include at least one ontological relationship to prior-version vocabulary (e.g., subclass, equivalentClass, subPropertyOf, or explicit replacement linkage).
