# Specification Authoring Style Guide

## For core protocol authors and maintainers, and for anyone publishing schema packs, API profiles, and regional extensions

This guide exists because small inconsistencies (casing drift, ambiguous names like `type`, enum mismatches, endpoint tokenization mismatches, docs referring to non-existent schemas) compound into interoperability debt across Beckn API contracts, schemas, JSON-LD artifacts, profiles, and documentation.

It aligns with Schema.org naming clarity where practical (TitleCase types, lowerCamelCase properties, and semantically clear names), while adding protocol-specific rigor for cross-artifact consistency, JSON-LD governance, extension discipline, and safe evolution.

---

# 1. Scope and audience

## 1.1 Who this is for

- **Core protocol maintainers** managing API and core schema contracts.
- **Schema authors** publishing reusable L2 schemas.
- **Domain and regional/network implementers** publishing profiles, examples, and policy overlays.

## 1.2 What this covers

- API endpoint naming and action/callback pairing.
- Schema type/property/enum naming.
- JSON-LD context/vocab conventions and IRI hygiene.
- Cross-artifact consistency rules (`attributes.yaml`, `schema.json`, `context.jsonld`, `vocab.jsonld`, README, examples, profiles).
- Schema distribution and governance across core and registries.
- Change management, compatibility policy, attribution, and extension discipline.

## 1.3 Normative keywords

Normative keyword definitions (`MUST`, `SHOULD`, `MAY`) are maintained by the RFC template. This guide uses those keywords with the same meanings.

---

# 2. Beckn V2 modeling philosophy

## 2.1 Core + composable schema design

Beckn v2 models entities as JSON-LD graphs (`@context`, `@type`) and uses composable schemas over monolithic core expansion.

## 2.2 Extension via explicit containers

Core entities expose extension points (for example, `...Attributes`) that carry JSON-LD semantics and permit controlled extensibility.

## 2.3 Layering baseline

Current baseline is two schema layers:

- **Layer 1 (L1)**: extremely minimal core/container schemas.
- **Layer 2 (L2)**: domain-agnostic and domain-specific schemas for value exchange, not all required in every use case.

L2 schemas are indexed/hosted via `schema.beckn.io`, sourcing verified registries including:

- `github.com/beckn/schemas`
- `github.com/beckn/DEG`

Network-specific policy enforcement is treated outside schema validation using policy rules (for example, IFTTT-style rules codified in Rego), not as a separate schema layer.

---

# 3. Repository artifacts and source of truth

## 3.1 Core artifacts (L1)

Core API plus minimal container schemas are defined in `api/beckn.yaml`.

Core artifacts SHOULD be published with canonical JSON-LD endpoints:

- `api/beckn.yaml`
- canonical `context.jsonld`
- canonical `vocab.jsonld`

## 3.2 Registry model

Schema distribution is registry-driven. Implementers should treat `schema.beckn.io` as the discovery/index surface for verified L2 schema sources.

## 3.3 Schema pack structure (expected)

A schema pack is expected to include:

1. A top-level canonical folder.
2. A top-level `README.md` as the landing page.
3. Versioned subfolders.

Within each version folder:

- `attributes.yaml` (OpenAPI document) - **REQUIRED**
- `schema.json` (JSON Schema) - **REQUIRED**
- `context.jsonld` (JSON-LD context) - **REQUIRED**
- `vocab.jsonld` (JSON-LD vocabulary) - **REQUIRED**
- `README.md` - **REQUIRED**
- `renderer.json` - **OPTIONAL**
- `profile.json` - **OPTIONAL**
- `examples/**` - **OPTIONAL but strongly recommended**

## 3.4 Canonical naming authority

When externally sourced schemas conflict with existing registry terms, Networks for Humanity Foundation (NFH) may designate canonical names.

Governance requirements:

- Rename decisions MUST be traceable.
- If the renamed schema has an external canonical URL, `vocab.jsonld` MUST declare an ontological relationship linking prior and new terms.
- Migration notes MUST be published alongside renames.

## 3.5 Conflict resolution priority

When artifacts disagree, priority order is:

1. `attributes.yaml` and `schema.json` machine contracts.
2. `context.jsonld` semantic bindings.
3. `vocab.jsonld` labels/definitions.
4. Examples (must validate against #1).
5. README/docs (must align with all above).

If examples/docs conflict with contracts, examples/docs are incorrect until fixed.

## 3.6 Semantic evolution baseline

Schema evolution is semantic-first:

- Authors MUST search `schema.beckn.io` before introducing new terms.
- Extension MUST be preferred over duplication.
- Extension MUST NOT alter inherited meaning.
- New schema versions MUST carry forward previous terms with deprecation markers where needed.
- New schema versions MUST introduce at least one explicit ontological relationship to predecessor vocabulary.

---

# 4. Naming conventions

## 4.1 Schema names and keywords

- Types/classes: **TitleCase**.
- Properties: **lowerCamelCase**.
- Enums: **SCREAMING_SNAKE_CASE**.
- Avoid type/property name collisions where possible.

## 4.2 IRI naming conventions

- Every schema term MUST map to an IRI.
- Keyword and IRI local names SHOULD match (for example, `billingInfo` -> `beckn:billingInfo`).
- Default `beckn:` prefix is expected to resolve via Beckn canonical context.
- Enum values SHOULD have scoped IRIs.
- Class/property/enum entries SHOULD be present in both:
  - version-specific `context.jsonld`
  - master/root context for registry-level discoverability

---

# 5. API endpoint and action naming

## 5.1 Base endpoint shape

- Protocol endpoints MUST be rooted under `/<root>/beckn/...`.
- Path segments MUST be lowercase.
- Multi-word tokens MUST use snake_case (no hyphens).

## 5.2 Action and callback pairing

- For every action endpoint `/<...>/<action>`, callback endpoint MUST be `/<...>/on_<action>`.
- Canonical action identifier for `context.action` is path segments joined with `_` after stripping `/beckn/`.

Examples:

- `/select` -> `select`
- `/on_select` -> `on_select`
- `/catalog/publish` -> `catalog_publish`
- `/catalog/on_publish` -> `catalog_on_publish`

## 5.3 Verb-form preference

Transaction and fabric action names SHOULD be verb forms whenever practical.

## 5.4 Fabric endpoint guidance

Management/fabric services may use service/action patterns (for example, `/catalog/publish`, `/catalog/on_publish`) when:

- Pairing rules remain consistent.
- Canonical `context.action` remains unambiguous.
- The endpoint is clearly management/fabric oriented, not misrepresented as generic P2P behavior.

## 5.5 Legacy endpoint exceptions

Legacy exceptions MUST be documented explicitly and MUST NOT become new naming precedent.

Current examples:

- changed: `rating`/`on_rating` -> `rate`/`on_rate`
- preserved due high adoption: `status`/`on_status`

Community-proposed API names may be normalized by central governance where required for consistency.

---

# 6. Schema pack names, folder names, and type names

## 6.1 Folder-to-primary-type alignment

For L2 packs, folder name and primary schema class name SHOULD align 1:1.

Example cleanup history:

- `ChargingService` -> `EvChargingService`
- `ChargingOffer` -> `EvChargingOffer`
- `ChargingSession` -> `EvChargingSession`
- `ChargingPointOperator` -> `EvChargingPointOperator`

## 6.2 Core types and naming stewardship

Domain namespacing should not be treated as the only collision-avoidance strategy. Governance may rename terms for global consistency, with migration traceability.

## 6.3 When to use `*Action` types

Use `*Action` for event/act semantics, noun types for persistent stateful entities.

Decision test:

- Agent + target/object + bounded execution -> `*Action`
- Persistent state over time -> noun type

---

# 7. Property naming

## 7.1 Casing baseline

- New schema properties MUST use lowerCamelCase.
- snake_case MUST NOT be introduced in schema property names.
- snake_case remains acceptable in endpoint path tokens.

Examples:

- `transaction_id` -> `transactionId`
- `ack_status` -> `ackStatus`
- `tl_method` -> `tlMethod`
- `expires_at` -> `expiresAt`

## 7.2 Reserved/ambiguous names

Avoid overloaded/reserved names unless externally mandated.

- `type` is forbidden as a schema property name (except JSON-LD `@type`).
- Prefer specific alternatives such as `expressionType`.

## 7.3 Singular vs plural property names

Both singular and plural property names are allowed when semantically appropriate.

Guidance:

- Prefer semantic clarity over rigid morphology.
- Do not append artificial suffixes (`List`, `Array`) to encode cardinality.
- Cardinality is defined by schema constraints, not naming hacks.

## 7.4 Prepositions and readability

Prefer readable, schema-style ordering (`reservationFor`, not `forReservation`).

## 7.5 Acronyms and industry codes

- Spell out abbreviations unless verbosity is harmful.
- Preserve true industry-standard identifiers where required.
- If industry forms are not SCREAMING_SNAKE_CASE, define Beckn-compatible SCREAMING_SNAKE_CASE aliases mapped to the same IRI with equivalence declared in `vocab.jsonld`.

## 7.6 Dates and times

- `...At` for instants (`expiresAt`, `createdAt`).
- `...On` for date-only semantics where that distinction is explicit.

## 7.7 Legacy snake_case handling

Legacy snake_case schema fields are no longer an accepted baseline. If found in active schemas, treat as defect and raise an issue with migration guidance.

## 7.8 Naming stewardship note

Contributed/external property names may be normalized by governance with:

- deprecation markers for prior names
- ontological links from old to new names
- migration notes

---

# 8. Enum value conventions

## 8.1 Canonical enum style

Enum values MUST use SCREAMING_SNAKE_CASE:

- uppercase ASCII letters, digits, `_`
- no spaces, hyphens, or mixed casing

Examples:

- `OnStreet` -> `ON_STREET`
- `WI-FI` -> `WI_FI`
- `2-WHEELER` -> `2_WHEELER`
- `http/get` -> `HTTP_GET`

## 8.2 Grammar consistency

Within one enum, preserve grammatical form consistency.

- status enums should use adjective/past participle forms (`PENDING`, `ACTIVE`, `STOPPED`), not mixed imperative verbs.

## 8.3 Evolution rules

- Adding enum values is usually backward compatible.
- Renaming/removing enum values is breaking and requires migration planning.
- Apply alias/equivalence mappings when transitioning legacy values.

---

# 9. JSON-LD conventions

## 9.1 JSON-LD self-description requirement

Composition/extension objects MUST include:

- `@context` (URI)
- `@type` (compact IRI or full IRI)

## 9.2 Namespacing strategy

- Use `schema:` when semantics are directly from Schema.org.
- Use `beckn:` for Beckn-specific semantics.

## 9.3 Mapping mechanism guidance

Schema-level mapping extensions (for example, `x-jsonld` usage in schema definitions) are under PWG review. Until finalized, avoid introducing new mapping patterns that are not yet stabilized.

## 9.4 Anti-drift requirement

For each term in `attributes.yaml` and `schema.json`:

- `context.jsonld` MUST define IRI binding.
- `vocab.jsonld` MUST define aligned human/machine meaning.
- README/examples MUST use canonical names.

## 9.5 Backward compatibility mapping

When renaming terms:

- provide migration mapping in context/vocab where feasible
- use explicit semantic links (OWL/ontology relations)
- document deprecation and replacement

---

# 10. Schema authoring and validation

## 10.1 Validation gates

Each schema bundle MUST pass:

- OpenAPI 3.1.1 validation for `attributes.yaml`
- JSON Schema validation for `schema.json`
- JSON-LD validation for `context.jsonld` and `vocab.jsonld`

## 10.2 Closed core, open extensions

- Core schemas SHOULD default to `additionalProperties: false`.
- Extension containers MUST permit `additionalProperties: true`.
- Extension containers MUST carry `@context` and `@type`.

## 10.3 Required fields

Adding required fields is breaking. Make fields required only when semantically mandatory and default-less.

## 10.4 Prefer reuse

Reuse existing semantics from core or Schema.org before adding near-duplicates.

---

# 11. Examples and documentation quality gates

## 11.1 Examples must validate

Examples MUST match:

- property names and case
- enum values and case
- object structure

## 11.2 Documentation must name canonical entities

Docs/README tables MUST reference real canonical schema/type/property names.

## 11.3 Editorial consistency

- Use US English spelling.
- Expand acronyms on first use when not globally obvious.
- Avoid undefined internal jargon.
- Avoid tautological naming such as `item.itemName`; prefer concise names such as `item.name` when semantics are unchanged.

## 11.4 Active evolution notice

Vocabulary/grammar refinements may continue in existing schemas. Evolution MUST be declared with ontology semantics (for example, OWL links) so implementers can map old terms to new terms safely.

---

# 12. Change management and backward compatibility

## 12.1 Breaking change categories

Breaking changes include:

- renaming properties
- renaming types
- renaming enum values
- changing required fields
- changing meaning without introducing new terms

## 12.2 Preferred migration path

1. Add new term/value while retaining old.
2. Mark old as deprecated.
3. Publish migration notes and semantic mapping.
4. Remove only in planned major release.

## 12.3 No silent semantic shifts

Do not reuse existing names for changed meaning. Introduce new names and deprecate old.

---

# 13. Domain/L2 schema rules

## 13.1 Additive extension principle

L2 schemas SHOULD extend composable core patterns and avoid semantic forks.

## 13.2 Semantic binding requirement

L2 packs SHOULD provide JSON-LD bindings (`beckn:` and/or `schema:` as applicable).

## 13.3 L2 naming and packaging

- pack folder and primary type should align
- properties use lowerCamelCase
- enums use SCREAMING_SNAKE_CASE
- examples and docs remain validation-aligned

## 13.4 Profiles and implementation guides

Profiles/IGs are recommendations, but MUST still use canonical names and validating examples.

---

# 14. Regional/network extension guidance

## 14.1 Extension boundaries

Regional/network implementers MAY extend L2 schemas and are encouraged to contribute reusable terms back to shared registries.

L1/core schema extensions SHOULD be avoided unless universally applicable and stable enough for major-version inclusion.

## 14.2 Namespace safety

- `beckn:` is reserved.
- Prefer network/region context URIs and specific type names.
- Avoid generic names without context (`licenseNumber`); prefer context-specific identifiers (`fssaiLicenseNumber`, etc.).

## 14.3 Policy layer separation

Fast-moving regional policy constraints should be enforced in policy engines (for example, Rego rules) rather than fragmenting schema semantics.

## 14.4 Conflict caution

If regional schemas are hosted independently with custom contexts, naming collisions may still occur in composed environments. Maintain explicit mapping and compatibility notes.

---

# 15. Attribution and reuse guidelines

Anyone publishing derived specifications MUST:

- preserve upstream notices
- include visible "Based on Beckn Protocol v2.x" attribution
- link to upstream baseline release/commit/tag
- maintain `CHANGES.md` (or equivalent) for divergence traceability

Forking is acceptable when explicit, attributable, and kept in sync with upstream evolution.

---

# 16. Cross-artifact consistency checklist (PR gate)

## Naming and casing

- [ ] Types are TitleCase; properties lowerCamelCase; enums SCREAMING_SNAKE_CASE.
- [ ] No new snake_case in schema property names.
- [ ] Endpoint tokens use lowercase snake_case.
- [ ] Ambiguous names like `type` are not used as schema properties.

## API

- [ ] Action/callback pairing follows `on_` convention.
- [ ] Canonical `context.action` derivation is deterministic.
- [ ] Legacy endpoint exceptions are documented.

## Schema and JSON-LD

- [ ] `attributes.yaml`, `schema.json`, `context.jsonld`, `vocab.jsonld` remain aligned.
- [ ] Version + master context entries are synchronized for new terms.
- [ ] Validation gates pass (OpenAPI, JSON Schema, JSON-LD).

## Documentation and examples

- [ ] Examples validate and use canonical names.
- [ ] README/docs reflect real schema contracts.
- [ ] Migration notes exist for any rename/deprecation.

## Governance and compatibility

- [ ] Breaking changes are explicitly labeled.
- [ ] Ontological relationships are declared for renamed terms.
- [ ] Attribution and upstream traceability are present.

---

# 17. Quick reference

## 17.1 Casing summary

| Thing | Format | Example |
| :--- | :--- | :--- |
| Schema class/type | TitleCase | `EvChargingService` |
| Property | lowerCamelCase | `transactionId` |
| Enum value | SCREAMING_SNAKE_CASE | `HTTP_GET` |
| JSON-LD keywords | JSON-LD standard | `@context`, `@type` |
| Endpoint tokens | lowercase snake_case | `browser_search` |

## 17.2 Before/after examples

- `filters.type` -> `filters.expressionType`
- `expires_at` -> `expiresAt`
- `http/get` -> `HTTP_GET`
- `ChargingSession` -> `EvChargingSession`

---

# 18. Source materials

- Beckn style guide context and inconsistency classes.
- Beckn schema distribution and registry practices.
- Beckn core schema references and JSON-LD patterns.
- Schema.org naming guidance: https://schema.org/docs/styleguide.html
- Beckn PR #67: https://github.com/beckn/protocol-specifications-v2/pull/67
- Beckn PR #68: https://github.com/beckn/protocol-specifications-v2/pull/68
