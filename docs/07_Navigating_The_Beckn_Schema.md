# RFC-007: Navigating the Beckn Schema
## CWG Working Draft - 2026-04-08

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-04-08 | Migrated schema navigation guide to RFC template format |

## 1.2 Latest editor's draft
- ./07_Navigating_The_Beckn_Schema.md

## 1.3 Implementation report
- To be published.

## 1.4 Stress Test Report
- To be published.

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Beckn Protocol contributors.

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-007%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-007%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-007%22

## 1.8 Errata
- To be published.

# 2. Context

**Status:** Draft  
**Author(s):** Beckn Protocol contributors  
**Created:** 2026-04-08  
**Updated:** 2026-04-08  
**Conformance impact:** Informative with normative implementation guidance  
**Security/privacy implications:** Clarifies schema validation responsibilities for safe processing  
**Replaces / Relates to:** Replaces non-RFC-form content in `07_Navigating_The_Beckn_Schema.md`.

---

## Abstract

This RFC defines how implementers should navigate Beckn schema assets across OpenAPI references, core schema objects, JSON-LD extensibility containers, and registry-published versioned artifacts.

---

## 1. Context

Beckn implementations consume a combination of transport contracts and semantic schema artifacts. Consistent navigation of these layers is required for interoperable validation and processing.

---

## 2. Problem

Without a formal schema-navigation model, implementations can diverge on artifact precedence, extension handling, and semantic interpretation.

---

## 3. Motivation

This RFC provides a common method for reading and validating schema assets so independent implementations preserve structural and semantic compatibility.

---

## 4. Design Principles

- **Contract fidelity:** `beckn.yaml` remains the source contract for transport payload shape.
- **Semantic composability:** Extension points support domain evolution through linked-data containers.
- **Dual validation:** Structural and semantic checks are complementary, not interchangeable.
- **Version continuity:** Schema versions MUST preserve canonical meaning across releases.

---

## 5. Specification (Normative)

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in [00_Keyword_Definitions.md](./00_Keyword_Definitions.md).

### 5.1 Canonical contract interpretation

Implementations MUST treat `api/v2.0.0/beckn.yaml` as the primary contract for envelope and operation payload constraints.

### 5.2 Core schema handling

Core schema objects referenced from OpenAPI (for example `Context`, `Ack`, `Contract`, `Catalog`, `Intent`, `Support`, and related entities) MUST be validated for structural conformance before business execution.

### 5.3 `Attributes` extensibility model

- Properties typed as `Attributes` are designated extension containers.
- Implementations SHOULD place domain-specific payload extensions inside these containers.
- Extensions MUST NOT alter the meaning of inherited core fields.

### 5.4 Dual validation requirement

Schema processing consists of:

1. structural validation (JSON Schema / OpenAPI constraints)
2. semantic validation (JSON-LD context and type resolution)

Structural validation MUST be enforced. Semantic validation SHOULD be enforced for cross-network semantic consistency.

### 5.5 Registry artifact model

Implementations MAY consume schema assets from recognized repositories indexed through `https://schema.beckn.io`.

Commonly referenced source repositories include:

- `https://github.com/beckn/schemas/tree/main/schema/`
- `https://github.com/beckn/DEG/tree/main/specification/schema/`

### 5.6 Versioned schema pack expectations

Schema version directories SHOULD include:

- `attributes.yaml`
- `schema.json`
- `context.jsonld`
- `vocab.jsonld`
- `README.md`
- optional auxiliary assets (`renderer.json`, `profile.json`, `examples/`)

Optional artifacts MUST NOT replace required structural and semantic contract files.

### 5.7 Semantic stability

Schema versions MAY evolve structure and detail, but MUST preserve canonical concept meaning across versions.

---

## 6. Examples

### Example 1 - Validation sequence

```text
Step 1: Validate envelope and payload shape against OpenAPI/schema contracts
Step 2: Resolve @context and @type for Attributes containers
Step 3: Execute domain logic with validated structural + semantic data
```

---

## 7. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-007-01 | Implementations MUST validate request/response structures against canonical schema contracts. | MUST |
| CON-007-02 | Implementations SHOULD process JSON-LD semantics for `Attributes` extension containers. | SHOULD |
| CON-007-03 | Schema version evolution MUST preserve canonical term meaning. | MUST |

---

## 8. Security Considerations

Improper schema interpretation can enable unsafe processing paths. Structural validation and trusted schema-source usage are required to mitigate malformed payload and semantic confusion risks.

---

## 9. Migration Notes

This update is a structural migration to RFC template form. It does not alter protocol wire behavior.

---

## 10. Open Questions

1. Should schema-source trust policies be standardized for network certification?
2. Should semantic-validation minimum requirements be made mandatory for all production deployments?

---

## 11. References

- [00_Keyword_Definitions.md](./00_Keyword_Definitions.md)
- [05_Specification_Authoring_Style_Guide.md](./05_Specification_Authoring_Style_Guide.md)
- `api/v2.0.0/beckn.yaml`
- https://schema.beckn.io

---

## 12. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2026-04-08 | Beckn Protocol contributors | RFC-template migration for schema navigation guide |
