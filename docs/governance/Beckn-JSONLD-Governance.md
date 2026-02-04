# Beckn JSON-LD Governance Rules

**Request for Comments – DRAFT**

---

## About this Document

### Status of this Memo

This document defines **normative governance rules** for the use of JSON-LD within Beckn Protocol V2.x.
Distribution of this memo is unlimited.

---

### Latest Published Version

Not yet published. This document is under active review and iteration.

---

### Latest Editor’s Draft

The editorial source of truth for this document resides in the Beckn Protocol V2 repository.

---

### Editors

* Beckn Protocol Core Maintainers

---

### Feedback

Feedback should be provided via GitHub issues or pull requests against the protocol-specifications-v2 repository.

---

## 1. Background and Motivation

Beckn Protocol V2 adopts JSON-LD to enable **global semantic interoperability** while preserving strict, machine-verifiable contracts.
This requires a disciplined separation between **runtime JSON processing** and **design-time semantic modeling**.

Historically, ecosystems that blur this boundary suffer from semantic drift, breaking changes hidden as “minor edits,” and brittle AI or agent behavior—risks that are unacceptable in federated, auditable networks like Beckn.

---

## 2. Scope of This Document

This RFC governs **only two JSON-LD artifacts** used in Beckn:

* `context.jsonld`
* `vocab.jsonld`

It explicitly does **not** define:

* API schemas
* JSON Schema validation rules
* Domain-specific extension vocabularies (except where governance applies)

---

## 3. Terminology

This section establishes precise meanings for commonly used terms to avoid ambiguity.

* **Runtime**: JSON-LD expansion/compaction during message exchange
* **Design-time**: Semantic modeling, ontology alignment, and review
* **Canonical**: The authoritative Beckn-defined semantic identity

---

## 4. Prime Directive (Non-Negotiable)

Every JSON-LD file in Beckn has **exactly one responsibility**.

| File             | Single Responsibility                           |
| ---------------- | ----------------------------------------------- |
| `context.jsonld` | Runtime term resolution and value normalization |
| `vocab.jsonld`   | Semantic truth: concepts, relations, alignment  |

**Any change that violates this separation is invalid, regardless of intent or correctness.**

---

## 5. Artifact-Specific Governance Rules

### 5.1 `context.jsonld`

This file exists solely to answer:
**“At runtime, what IRI does this JSON key or value resolve to?”**

It must remain deterministic, minimal, and completely free of semantic or ontological claims.

---

#### ✅ Allowed Content

The following examples are correct because they **only perform term mapping and value typing**, which are required for deterministic JSON-LD expansion.

```json
{
  "@context": {
    "@protected": true,
    "beckn": "https://becknprotocol.io/schema/",
    "isActive": {
      "@id": "beckn:isActive",
      "@type": "xsd:boolean"
    }
  }
}
```

**Why this is correct**

* Maps JSON keys to stable IRIs
* Explicitly types values to avoid ambiguity
* Introduces no semantic meaning or constraints

---

#### ❌ Forbidden Content

The following examples are invalid because they **introduce semantic or ontological constructs into a runtime artifact**.

```json
{
  "@graph": [
    {
      "@id": "beckn:Order",
      "owl:equivalentClass": "schema:Order"
    }
  ]
}
```

```json
{
  "orderStatus": {
    "schema:hasEnumerationMember": []
  }
}
```

**What is wrong**

* Declares semantic identity (`owl:equivalentClass`)
* Embeds ontology (`@graph`, enumerations) in a runtime context
* Collapses runtime resolution with semantic truth

**Potential consequences in applications**

* Silent semantic changes across network participants
* Context edits become breaking changes without versioning
* LLMs and agents infer incorrect equivalence
* Auditing and dispute resolution become unreliable

---

### 5.2 `vocab.jsonld`

This file defines **what concepts exist**, how they relate, and how they align with global vocabularies.
It is the **only authoritative source of semantic truth** in Beckn.

---

#### ✅ Allowed Content

The following examples are valid because they **declare meaning without enforcing structure or validation**.

```json
{
  "@id": "beckn:Order",
  "@type": "rdfs:Class",
  "rdfs:subClassOf": "schema:Order"
}
```

```json
{
  "@id": "beckn:isActive",
  "@type": "rdf:Property",
  "schema:domainIncludes": "beckn:Item",
  "schema:rangeIncludes": "schema:Boolean"
}
```

**Why this is correct**

* Declares classes and properties explicitly
* Uses schema.org for alignment, not enforcement
* Leaves validation to protocol schemas

---

#### ❌ Forbidden Content

The following examples are invalid because they **mix validation or runtime concerns into a semantic vocabulary**.

```json
{
  "@id": "beckn:Order",
  "type": "object",
  "required": ["id"]
}
```

```json
{
  "@id": "beckn:orderStatus",
  "@context": {}
}
```

**What is wrong**

* Introduces JSON Schema concepts into vocab
* Embeds runtime context logic in semantic definitions
* Confuses meaning with structure

**Potential consequences in applications**

* Tooling misinterprets vocab as a validation schema
* Conflicting enforcement across implementations
* Domain extensions become brittle and unsafe
* False assumptions about protocol guarantees

---

## 6. Prefix and Namespace Governance

Namespaces establish **global semantic identity** and must never be redefined or hijacked.

---

### ✅ Allowed

These examples are correct because they reference **globally authoritative namespaces**.

```json
{
  "schema": "https://schema.org/",
  "beckn": "https://becknprotocol.io/schema/"
}
```

**Why this is correct**

* Preserves global dereferenceability
* Ensures all participants resolve identical IRIs

---

### ❌ Forbidden

These examples are invalid because they **fork or override global namespaces**.

```json
{
  "schema": "https://example.com/schema/"
}
```

```json
{
  "beckn": "https://my-network.example/beckn/"
}
```

**What is wrong**

* Breaks global meaning of well-known prefixes
* Introduces private semantics under public names

**Potential consequences in applications**

* Cross-network interoperability collapses
* Semantic mappings become non-portable
* Agents hallucinate equivalence
* Federation-level reasoning fails

---

## 7. Mapping to schema.org (Global-first)

Beckn is **schema.org–aligned**, but never schema.org–dependent.

This section governs how alignment is declared without collapsing identities.

---

### Canonical Mapping Rules

| Concept Type | Preferred Strategy                         |
| ------------ | ------------------------------------------ |
| Class        | `rdfs:subClassOf schema:*`                 |
| Property     | Reuse schema.org if exact                  |
| Enum value   | Beckn canonical + optional `schema:sameAs` |

---

### ❌ Forbidden

```json
{
  "@id": "beckn:Order",
  "owl:equivalentClass": "schema:Order"
}
```

```json
{
  "@id": "beckn:priceCurrency"
}
```

**What is wrong**

* Asserts semantic identity instead of alignment
* Duplicates existing global concepts

**Potential consequences in applications**

* Beckn semantics become externally mutable
* Versioning guarantees are violated
* Agents cannot distinguish protocol vs global meaning

---

## 8. Typing Discipline

Typing rules differ sharply between runtime and design-time artifacts.

---

### 8.1 Typing in `context.jsonld`

Typing here exists **only to disambiguate runtime values**.

#### ✅ Allowed

```json
{
  "provider": {
    "@id": "beckn:provider",
    "@type": "@id"
  }
}
```

**Why this is correct**

* Makes IRI intent explicit
* Avoids literal vs reference ambiguity

---

#### ❌ Forbidden

```json
{
  "provider": {
    "@id": "beckn:provider"
  }
}
```

**What is wrong**

* Leaves value interpretation ambiguous

**Potential consequences**

* Inconsistent expansion across processors
* Agents mis-handle references vs literals

---

### 8.2 Typing in `vocab.jsonld`

Typing here is **descriptive, not enforceable**.

* Prefer `schema:rangeIncludes`
* Use `rdfs:range` only when unavoidable

---

## 9. Enumeration Governance (Critical Section)

Enumerations are one of the highest-risk areas for semantic drift.

---

### Canonical Pattern

```json
{
  "@id": "beckn:OrderStatus",
  "@type": "schema:Enumeration",
  "schema:hasEnumerationMember": [
    { "@id": "beckn:OrderCancelled" }
  ]
}
```

---

### ❌ Forbidden

```json
{
  "schema:hasEnumerationMember": [
    { "@id": "schema:OrderCancelled" }
  ]
}
```

**What is wrong**

* Makes schema.org values canonical
* Transfers semantic authority outside Beckn

**Potential consequences in applications**

* Enum meaning changes without Beckn versioning
* Domain extensions break unexpectedly
* Post-facto audits become unreliable

---

## 10. Domain and Range Discipline

Over-constraining domain or range harms extensibility.

---

### ✅ Preferred

```json
{
  "schema:domainIncludes": ["beckn:Order", "beckn:Item"],
  "schema:rangeIncludes": "schema:Boolean"
}
```

---

### ❌ Forbidden

```json
{
  "rdfs:domain": "beckn:Order"
}
```

**What is wrong**

* Imposes closed-world assumptions

**Potential consequences**

* Extensions become invalid by default
* Cross-domain reuse is blocked

---

## 11. Identity and Equivalence Rules

Identity claims have **irreversible consequences** in federated systems.

---

### Allowed

* `rdfs:subClassOf`
* `rdfs:seeAlso`
* `schema:sameAs` (only when exact)

---

### ❌ Forbidden

```json
"owl:equivalentClass"
"owl:equivalentProperty"
```

**Potential consequences**

* Semantic lock-in
* Network-wide breaking changes
* Impossible rollback

---

## 12. Extension and Federation Rules

Extensions may **add meaning**, never rewrite it.

---

### ❌ Forbidden

```json
{
  "orderStatus": {
    "@id": "mobility:tripStatus"
  }
}
```

```json
{
  "CANCELLED": "mobility:TripCancelled"
}
```

**Potential consequences**

* Canonical meaning is lost
* Cross-network reasoning fails

---

## 13. Backward Compatibility

Semantic contracts are long-lived and auditable.

---

### ❌ Forbidden

```json
"beckn:OrderCancelled" → "beckn:OrderCanceled"
```

**Potential consequences**

* Historical payloads become ambiguous
* Legal and audit trails break

---

## 14. Guidance for LLMs and Tooling

This section defines **expected refusal behavior** for automated systems.

LLMs and tools **must refuse** to:

* Add OWL axioms to `context.jsonld`
* Replace Beckn IRIs with schema.org IRIs
* Treat contexts as ontologies

**Syntactic validity does not imply semantic correctness.**

---