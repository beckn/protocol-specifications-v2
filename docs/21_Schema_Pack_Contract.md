# Domain Schema Pack Contract

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
│   ├── search.json
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

- [6_Schema_Distribution_Model.md](./6_Schema_Distribution_Model.md)
- [20_JSONld_Context_and_Schema_Alignment.md](./20_JSONld_Context_and_Schema_Alignment.md)
- [`beckn/core_schema`](https://github.com/beckn/core_schema)
- [schema.beckn.io](https://schema.beckn.io)

---

## 11. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
