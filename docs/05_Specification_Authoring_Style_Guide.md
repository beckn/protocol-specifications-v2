# RFC-005: Specification Authoring Style Guide

# 1. Document Details

- **Status:** Draft.
- **Authors:** Beckn Protocol contributors.
- **Created:** 2026-04-10.
- **Updated:** 2026-04-10.
- **Version history:** No commits found on `main` for `docs/05_Specification_Authoring_Style_Guide.md`.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/05_Specification_Authoring_Style_Guide.md).
- **Implementation report:** Not applicable (authoring and governance guidance RFC).
- **Stress test report:** Not applicable.
- **Conformance impact:** Normative for authoring quality and interoperability hygiene.
- **Security/privacy implications:** Reduces semantic ambiguity that can cause unsafe processing or misinterpretation.
- **Replaces / Relates to:** Replaces non-RFC-form content in `05_Specification_Authoring_Style_Guide.md`.
- **Feedback:** Issues Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-005%22), Discussions Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-005%22), Pull Requests Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-005%22).
- **Errata:** To be published.

# 2. Abstract

This RFC defines authoring rules for Beckn API contracts, schema packs, JSON-LD artifacts, and supporting documentation so that naming, semantics, validation, and backward-compatible evolution remain consistent across repositories and teams.

# 3. Table of Contents

- [Introduction](#4-introduction)
- [Specification](#5-specification)
- [Conclusion](#6-conclusion)
- [Acknowledgements](#7-acknowledgements)
- [References](#8-references)

# 4. Introduction

Beckn specifications are authored across multiple repositories and teams, and small inconsistencies in naming, schema semantics, endpoint tokenization, and documentation-example alignment can accumulate into interoperability debt. This guide establishes a common authoring baseline so artifacts evolve predictably, remain validation-aligned, and reduce the risk of unsafe parsing or inconsistent policy enforcement.

The following terms are used throughout this RFC:

- **Machine contract:** Authoritative artifacts such as `attributes.yaml` and `schema.json` that define enforceable structure.
- **Semantic artifacts:** `context.jsonld` and `vocab.jsonld` files that define linked-data meaning and term mapping.
- **Schema pack:** A versioned bundle of required and optional schema, context, vocab, and documentation assets.
- **Cross-artifact consistency:** The requirement that contracts, semantic files, examples, and prose stay aligned.
- **Backward-compatible evolution:** An additive, mapped, deprecated-first change strategy for renames or replacements.
- **Canonical naming:** Governed, consistent naming for types, properties, enums, and endpoint actions.

This RFC follows four core principles:

- **Contract-first consistency:** Machine contracts take precedence over prose.
- **Semantic clarity:** Names and IRIs SHOULD preserve stable meaning.
- **Composable evolution:** New terms SHOULD extend, not duplicate or redefine existing semantics.
- **Backward-safe change:** Renames and removals MUST carry migration and ontology mapping.

# 5. Specification

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in Click [here](./00_Keyword_Definitions.md).

## 5.1 Scope and audience

This RFC applies to:

- Core protocol maintainers
- Schema authors publishing L2 packs
- Domain, regional, and network profile authors

## 5.2 Artifact model and precedence

Expected schema pack structure:

- Required: `attributes.yaml`, `schema.json`, `context.jsonld`, `vocab.jsonld`, `README.md`
- Optional: `renderer.json`, `profile.json`, `examples/**`

When artifacts conflict, precedence MUST be:

1. `attributes.yaml` and `schema.json`
2. `context.jsonld`
3. `vocab.jsonld`
4. examples
5. docs and `README.md`

## 5.3 Naming and casing conventions

- Types and classes MUST use `TitleCase`.
- Properties MUST use `lowerCamelCase`.
- Enum values MUST use `SCREAMING_SNAKE_CASE`.
- New `snake_case` schema properties MUST NOT be introduced.
- Reserved or ambiguous property names such as `type` MUST be avoided, except for JSON-LD `@type`.

## 5.4 Endpoint and action naming

- Endpoints SHOULD use lowercase path tokens.
- Multi-word endpoint tokens SHOULD use `snake_case`.
- For action `/<...>/<action>`, the callback SHOULD be `/<...>/on_<action>`.
- Canonical `context.action` derivation MUST remain deterministic and documented.
- Legacy endpoint exceptions MUST be explicitly documented and MUST NOT become new precedent.

## 5.5 JSON-LD conventions

- Composition and extension objects MUST include `@context` and `@type`.
- Every schema term MUST map to an IRI.
- `context.jsonld` and `vocab.jsonld` MUST remain aligned with schema contracts.
- Renamed terms SHOULD include explicit ontology relations and migration mapping.

## 5.6 Schema authoring and validation gates

Each schema bundle MUST pass:

- OpenAPI validation for `attributes.yaml`
- JSON Schema validation for `schema.json`
- JSON-LD validation for `context.jsonld` and `vocab.jsonld`

Core schemas SHOULD default to `additionalProperties: false`; extension containers SHOULD remain open and carry explicit semantic metadata.

## 5.7 Change management and compatibility

Breaking changes include:

- renaming properties, types, or enums
- adding required fields
- changing term meaning without introducing new terms

The preferred migration path is:

1. Add the new term while retaining the old term.
2. Mark the old term as deprecated.
3. Publish migration notes and semantic mapping.
4. Remove the old term only in a planned major release.

This RFC itself is a structural migration of the style guide into RFC order and does not change the underlying authoring intent.

## 5.8 Cross-artifact checklist

Before merge, authors SHOULD verify:

- canonical naming and casing consistency
- action and callback pairing with deterministic action derivation
- alignment across `attributes.yaml`, `schema.json`, `context.jsonld`, and `vocab.jsonld`
- examples validate against canonical contracts
- migration notes exist for renames and deprecations
- attribution and upstream traceability exist for derived specifications

## 5.9 Examples and normalization patterns

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

## 5.10 Conformance requirements

| ID | Requirement | Level |
|---|---|---|
| CON-005-01 | New schema properties MUST use `lowerCamelCase` and MUST NOT introduce `snake_case`. | MUST |
| CON-005-02 | Enum values MUST use `SCREAMING_SNAKE_CASE` for canonical representation. | MUST |
| CON-005-03 | Authors MUST keep `attributes.yaml`, `schema.json`, `context.jsonld`, and `vocab.jsonld` semantically aligned. | MUST |
| CON-005-04 | Breaking renames and removals MUST include deprecation and migration guidance. | MUST |
| CON-005-05 | Examples and documentation SHOULD validate against canonical machine contracts. | SHOULD |

## 5.11 Security and interoperability considerations

Ambiguous naming, schema and documentation drift, and untracked semantic changes can cause unsafe parsing and inconsistent policy enforcement. Strict cross-artifact validation, deterministic action naming, and explicit semantic mapping reduce these risks.

# 6. Conclusion

This RFC consolidates the style guide into a single ordered structure while preserving the original normative guidance for naming, artifact precedence, validation, compatibility, and semantic alignment. Draft-01 records this RFC-form restructuring, and future governance work may standardize JSON-LD extension patterns and automated pull-request gates for minimum cross-artifact checks.

# 7. Acknowledgements

This document reflects input from Beckn Protocol contributors maintaining protocol contracts, schema packs, semantic artifacts, and governance processes.

# 8. References

- **Keyword definitions:** Click [here](./00_Keyword_Definitions.md)
- **Schema.org style guide:** Click [here](https://schema.org/docs/styleguide.html)
- **Related pull request 67:** Click [here](https://github.com/beckn/protocol-specifications-v2/pull/67)
- **Related pull request 68:** Click [here](https://github.com/beckn/protocol-specifications-v2/pull/68)
