# Domain Schema Pack Contract
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./17_Schema_Pack_Contract.md

## 1.3 Implementation report
- To be published by implementation working group.

## 1.4 Stress Test Report
- To be published by testing and certification working group.

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Beckn Protocol contributors.

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls

## 1.8 Errata
- To be published.

<!-- TOC START -->
## Table of Contents

  - [CWG Working Draft - 2026-03-27](#cwg-working-draft-2026-03-27)
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
  - [2. What is a Domain Schema Pack?](#2-what-is-a-domain-schema-pack)
  - [3. Pack Structure](#3-pack-structure)
  - [4. Context Document Rules](#4-context-document-rules)
  - [5. Attribute Definitions](#5-attribute-definitions)
  - [6. Versioning](#6-versioning)
  - [7. Composition Rules](#7-composition-rules)
  - [8. Publication Requirements](#8-publication-requirements)
  - [9. Conformance Requirements](#9-conformance-requirements)
  - [10. References](#10-references)
  - [11. Changelog](#11-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Informative for core; normative for domain schema pack authors  
**Security/privacy implications:** Domain schema packs extend core entities. Extensions MUST NOT redefine core field semantics or introduce fields that could be confused with core transport fields.  
**Replaces / Relates to:** New in v2. Establishes the governance contract for domain schema pack authorship and versioning.

---

## Abstract

This RFC defines the contract that domain schema pack authors MUST follow when creating, versioning, and publishing sector-specific schema extensions for Beckn Protocol v2. A domain schema pack is a set of JSON-LD context documents and typed attribute overlays that extend `core_schema` entities with sector-specific vocabulary, without modifying the core transport or core transaction schema.

---

## 1. Context

Beckn v2 supports any industry domain by design. New sectors are onboarded by creating domain schema packs — not by modifying the core protocol. The schema pack contract ensures that all domain packs are authored consistently, versioned predictably, and composed safely.

---

## 2. What is a Domain Schema Pack?

A domain schema pack is a versioned collection of:

1. **JSON-LD context document** — maps domain-specific terms to global vocabulary (schema.org + domain namespaces).
2. **Attribute definitions** — typed properties that extend `core_schema` entities.
3. **Examples** — runtime JSON-LD examples for key use cases.
4. **Validation rules** — JSON Schema or SHACL constraints for domain-specific mandatory fields.
5. **Changelog** — version history with conformance impact classification.

---

## 3. Pack Structure

```
{domain}-schema/
├── context.jsonld           ← JSON-LD context document
├── attributes/
│   ├── Item.jsonld          ← Item attribute extensions
│   ├── Fulfillment.jsonld   ← Fulfillment attribute extensions
│   └── ...
├── examples/
│   ├── discover.json
│   ├── confirm.json
│   └── ...
├── validation/
│   └── schema.json          ← JSON Schema validation rules
├── README.md
└── CHANGELOG.md
```

---

## 4. Context Document Rules

The domain context document MUST:
- Declare the `beckn:` and `schema:` namespaces.
- Define a domain-specific namespace (e.g., `mobility:`, `retail:`).
- Map all domain attributes to either schema.org terms or the domain namespace.
- NOT redefine any term already defined in the Beckn core context.
- Be published at a versioned URI: `https://schema.beckn.io/{domain}/v{N}/context.jsonld`

```json
{
  "@context": {
    "beckn": "https://schema.beckn.io/vocab#",
    "schema": "https://schema.org/",
    "mobility": "https://schema.beckn.io/mobility/v1/vocab#",
    "vehicleType": "mobility:vehicleType",
    "routeId": "mobility:routeId",
    "fareClass": "mobility:fareClass",
    "seatsAvailable": "schema:availableAtOrFrom"
  }
}
```

---

## 5. Attribute Definitions

Domain attribute definitions MUST specify:

| Field | Description |
|---|---|
| `term` | The attribute name (camelCase) |
| `namespace` | The namespace URI |
| `type` | The JSON-LD type (`@id`, `@value`, `xsd:string`, etc.) |
| `appliesTo` | Which `core_schema` entity this attribute extends |
| `required` | Whether this attribute is required in the domain context |
| `description` | Human-readable description |

---

## 6. Versioning

Domain schema packs follow SemVer independently of the core protocol:

| Increment | Trigger |
|---|---|
| PATCH | Clarifications, editorial fixes |
| MINOR | New optional attributes, new entity extensions |
| MAJOR | Removal of attributes, semantic changes to existing terms, breaking namespace changes |

A domain pack MUST declare the minimum `core_schema` version it is compatible with:

```json
{
  "packId": "https://schema.beckn.io/mobility/v1/context.jsonld",
  "version": "1.2.0",
  "coreSchemaVersion": ">=2.0.0",
  "protocolVersion": ">=2.0.1"
}
```

---

## 7. Composition Rules

Multiple domain packs MAY be composed on a single entity:

```json
{
  "@context": [
    "https://schema.org/",
    "https://schema.beckn.io/core/v2/context.jsonld",
    "https://schema.beckn.io/mobility/v1/context.jsonld",
    "https://schema.beckn.io/carbon/v1/context.jsonld"
  ],
  "@type": ["Item", "TaxiService"],
  "vehicleType": "sedan",
  "carbonFootprint": { "@type": "carbon:Footprint", "value": 0.12, "unit": "kgCO2e" }
}
```

Composition MUST NOT produce conflicting term definitions. If two packs define the same term differently, the pack author MUST resolve the conflict by aliasing.

---

## 8. Publication Requirements

Domain schema pack authors MUST:
1. Publish the pack in a public GitHub repository under the `beckn/` organization or a registered domain organization.
2. Publish the context document at a stable, versioned HTTPS URI.
3. Register the pack in the Beckn schema registry at `schema.beckn.io`.
4. Include a `CHANGELOG.md` with conformance impact for each version.

---

## 9. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-023-01 | Domain context MUST NOT redefine Beckn core terms | MUST |
| CON-023-02 | Domain context MUST be published at a versioned URI | MUST |
| CON-023-03 | Domain pack MUST declare compatible `core_schema` and protocol versions | MUST |
| CON-023-04 | Domain pack MUST include at least one runtime example | MUST |
| CON-023-05 | Domain pack MUST use SemVer | MUST |
| CON-023-06 | Composition of multiple packs MUST NOT produce conflicting term definitions | MUST |

---

## 10. References

- [15_Schema_Distribution_Model.md](./15_Schema_Distribution_Model.md)
- [16_JSONld_Context_and_Schema_Alignment.md](./16_JSONld_Context_and_Schema_Alignment.md)
- [`beckn/core_schema`](https://github.com/beckn/core_schema)
- [schema.beckn.io](https://schema.beckn.io)

---

## 11. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
