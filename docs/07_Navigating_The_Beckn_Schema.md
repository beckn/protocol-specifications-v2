# RFC-007: Navigating the Beckn Schema

# 1. Document Details

- **Status:** Draft.
- **Authors:** Beckn Protocol contributors.
- **Created:** 2026-04-08.
- **Updated:** 2026-04-08.
- **Version history:** No commits found on `main` for `docs/07_Navigating_The_Beckn_Schema.md`.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/07_Navigating_The_Beckn_Schema.md)
- **Implementation report:** To be published.
- **Stress test report:** To be published.
- **Conformance impact:** Informative with normative implementation guidance.
- **Security/privacy implications:** Clarifies schema validation responsibilities for safe processing.
- **Replaces / Relates to:** Replaces non-RFC-form content in `07_Navigating_The_Beckn_Schema.md`.
- **Feedback:** Issues Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-007%22), Discussions Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-007%22), Pull Requests Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-007%22).
- **Errata:** To be published.

# 2. Abstract

This RFC defines how implementers should navigate Beckn schema assets across OpenAPI contracts, core schema objects, JSON-LD extension containers, and registry-published versioned artifacts to preserve structural and semantic interoperability.

# 3. Table of Contents

- [Introduction](#4-introduction)
- [Specification](#5-specification)
- [Conclusion](#6-conclusion)
- [Acknowledgements](#7-acknowledgements)
- [References](#8-references)

# 4. Introduction

Beckn implementations consume both transport contracts and semantic schema artifacts. Without a common navigation model, independent implementations can diverge on contract precedence, extension handling, version discovery, and semantic interpretation. This document defines a consistent way to read and validate these assets so implementations remain structurally and semantically interoperable.

For this document, the canonical contract is `api/v2.0.0/beckn.yaml`, which is the primary OpenAPI artifact for envelope and operation constraints. Core schema objects are shared entities such as `Context`, `Ack`, `Contract`, `Catalog`, `Intent`, and `Support`, and they require structural validation before business execution. `Attributes` containers are designated extension points for domain-specific semantics and MUST NOT be used to change the meaning of inherited core fields. Structural validation refers to JSON Schema or OpenAPI conformance checks, while semantic validation refers to JSON-LD processing through `@context` and `@type` so that meaning is preserved across participants.

The guidance in this RFC follows four principles: contract fidelity, so `beckn.yaml` remains authoritative for transport shape; semantic composability, so extensions are carried through linked-data containers; dual validation, so structural and semantic checks complement each other; and version continuity, so schema versions evolve without changing canonical concept meaning.

# 5. Specification

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in Click [here](./00_Keyword_Definitions.md).

## 5.1 Canonical contract interpretation

Implementations MUST treat `api/v2.0.0/beckn.yaml` as the primary contract for envelope and operation payload constraints.

## 5.2 Core schema handling

Core schema objects referenced from OpenAPI, including `Context`, `Ack`, `Contract`, `Catalog`, `Intent`, `Support`, and related entities, MUST be validated for structural conformance before business execution.

## 5.3 `Attributes` extensibility model

- Properties typed as `Attributes` are designated extension containers.
- Implementations SHOULD place domain-specific payload extensions inside these containers.
- Extensions MUST NOT alter the meaning of inherited core fields.

## 5.4 Dual validation requirement

Schema processing consists of:

1. structural validation through JSON Schema or OpenAPI constraints
2. semantic validation through JSON-LD context and type resolution

Structural validation MUST be enforced. Semantic validation SHOULD be enforced for cross-network semantic consistency.

## 5.5 Registry artifact model

Implementations MAY consume schema assets from recognized repositories indexed through the Beckn schema registry at Click [here](https://schema.beckn.io).

Commonly referenced source repositories include:

- Click [here](https://github.com/beckn/schemas/tree/main/schema/)
- Click [here](https://github.com/beckn/DEG/tree/main/specification/schema/)

## 5.6 Versioned schema pack expectations

Schema version directories SHOULD include:

- `attributes.yaml`
- `schema.json`
- `context.jsonld`
- `vocab.jsonld`
- `README.md`
- optional auxiliary assets such as `renderer.json`, `profile.json`, and `examples/`

Optional artifacts MUST NOT replace required structural and semantic contract files.

## 5.7 Semantic stability and migration

Schema versions MAY evolve structure and detail, but MUST preserve canonical concept meaning across versions. The current RFC restructuring is a documentation migration only and does not alter protocol wire behavior.

## 5.8 Implementation sequence and example

Implementations SHOULD follow this processing sequence:

```text
Step 1: Validate envelope and payload shape against OpenAPI/schema contracts
Step 2: Resolve @context and @type for Attributes containers
Step 3: Execute domain logic with validated structural + semantic data
```

## 5.9 Conformance requirements

| ID | Requirement | Level |
|---|---|---|
| CON-007-01 | Implementations MUST validate request/response structures against canonical schema contracts. | MUST |
| CON-007-02 | Implementations SHOULD process JSON-LD semantics for `Attributes` extension containers. | SHOULD |
| CON-007-03 | Schema version evolution MUST preserve canonical term meaning. | MUST |

## 5.10 Security and trust considerations

Improper schema interpretation can enable unsafe processing paths. Structural validation and trusted schema-source usage are required to mitigate malformed payload and semantic confusion risks. Open implementation questions remain around whether schema-source trust policies should be standardized for network certification and whether minimum semantic-validation requirements should become mandatory for all production deployments.

# 6. Conclusion

This RFC establishes a common navigation model for Beckn schema assets by defining contract precedence, extension handling, dual validation, registry discovery, and version continuity expectations. This draft also records the current Draft-01 restructuring completed on 2026-04-08 as an RFC-template migration that preserves existing technical behavior while carrying forward the outstanding trust and semantic-validation questions for future standardization work.

# 7. Acknowledgements

This document reflects the work of Beckn Protocol contributors and related community participants who developed the underlying schema-navigation guidance and RFC restructuring.

# 8. References

- Keyword definitions: Click [here](./00_Keyword_Definitions.md)
- Specification authoring style guide: Click [here](./05_Specification_Authoring_Style_Guide.md)
- Canonical OpenAPI contract: `api/v2.0.0/beckn.yaml`
- Beckn schema registry: Click [here](https://schema.beckn.io)
