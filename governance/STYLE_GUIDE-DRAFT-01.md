# Beckn Protocol V2.0 Spec Authoring Style Guide \[DRAFT\]

## For core protocol authors & maintainers, and for anyone publishing domain / network schema packs & API profiles

This style guide exists because small “paper-cut” inconsistencies (casing drift, ambiguous names like `type`, enum mismatches, endpoint tokenization oddities, docs referring to non-existent schemas, etc.) compound into big interoperability debt across Beckn’s **API**, **schemas**, **JSON-LD vocab/context**, **profiles**, and **documentation**.

It takes inspiration from Schema.org’s approach to naming and clarity—TitleCase types, lowerCamelCase properties, singular terms, avoid “type” unless you mean “class/type”—but adds the protocol-specific rigor Beckn needs: multi-artifact consistency, JSON-LD binding rules, extension pack discipline, and a practical “don’t break the world” evolution policy. ([Schema.org](https://schema.org/docs/styleguide.html))

---

# 1\. Scope and audiences

## 1.1 Who this is for

* **Core protocol maintainers**: editing `api/beckn.yaml` and `schema/core/v2/**`.  
* **Domain spec authors (Layer 2\)**: publishing sector-specific schema packs and optional profiles / IGs (Implementation Guides).  
* **Network spec authors (Layer 3\)**: extending domain packs with regional/network policy fields and network IGs.

## 1.2 What this covers

* API endpoint naming & action/callback pairing.  
* Schema naming (types/classes), property naming, enum conventions.  
* JSON-LD conventions (contexts, vocabularies, compact IRIs, bindings to schema.org).  
* Cross-artifact consistency rules (OpenAPI ↔ JSON-LD ↔ profiles ↔ README ↔ examples).  
* Editorial quality and documentation norms.  
* A practical change-management policy (how to evolve without turning everyone’s parsers into confetti).  
* Attribution & reuse expectations for domain/network layers.

---

# 2\. Beckn V2.0 modeling philosophy (the “why” behind the rules)

## 2.1 “Core \+ schema packs” is the design

Beckn v2 models core entities as **JSON-LD graphs** (`@context`, `@type`) and relies on a modular **core \+ pluggable schema packs** approach for domain and network needs. ([GitHub](https://github.com/beckn/protocol-specifications-new/tree/draft))

## 2.2 Extension happens via “Attributes” containers, not core bloat

Core entities expose explicit extension points (e.g., `...Attributes`) typed as an **Attributes** “JSON-LD aware bag” that requires `@context` and `@type`, and permits additional properties.

This gives forward compatibility: unknown schema can be passed through or ignored if a participant doesn’t understand it, without breaking base parsing. ([GitHub](https://github.com/beckn/protocol-specifications-new/tree/draft))

## 2.3 Three-layer ecosystem reality

In practice:

* **Layer 1 (Core)** changes slowest.  
* **Layer 2 (Domain)** changes faster and includes semantic bindings \+ IGs.  
* **Layer 3 (Network)** changes fastest due to go-to-market and policy pressure.

This guide is designed to keep those layers composable *without* incentivizing permanent forks and attribution loss.

---

# 3\. Normative keywords (kept minimal, but precise)

* **MUST** / **MUST NOT**: hard requirements for spec compatibility and tooling stability.  
* **SHOULD** / **SHOULD NOT**: strong defaults; deviating needs a documented reason.  
* **MAY**: optional patterns.

---

# 4\. Repository artifacts and “source of truth”

Beckn V2 specs typically ship as **bundles**. A “bundle” is only healthy if it stays internally consistent.

## 4.1 Core bundle

* `api/beckn.yaml` — normative API definition.  
* `schema/core/v2/attributes.yaml` — normative schemas.  
* `schema/core/v2/context.jsonld` — normative JSON-LD context.  
* `schema/core/v2/vocab.jsonld` — normative vocabulary (human+machine meaning).

## 4.2 Domain / Network schema pack bundle (expected structure)

A schema pack is expected to include, at minimum:

* `attributes.yaml`  
* `context.jsonld`  
* `vocab.jsonld`  
* `README.md` (human guidance)  
* `examples/**` (payloads that validate)  
* Optional: `profile.json` (capabilities/config for services like discovery profiles)

PRs \#67 and \#68 explicitly call out that name changes must be applied across **attributes.yaml, vocab.jsonld, context.jsonld, README.md, profile.json** to prevent drift. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 4.3 Canonical naming authority (when conflicts exist)

When artifacts disagree, the priority order is:

1. **`attributes.yaml`** schema names and property names (machine contracts).  
2. **`context.jsonld`** bindings (semantic meaning / interoperability).  
3. **`vocab.jsonld`** labels/definitions (human meaning).  
4. **Examples** (must validate against \#1).  
5. **README / docs** (must match everything else).

If \#4 or \#5 disagree with \#1: examples/docs are wrong until fixed.

---

# 5\. Naming conventions

Beckn naming rules deliberately align with Schema.org where possible:

* **Types/classes**: TitleCase (PascalCase) ([Schema.org](https://schema.org/docs/styleguide.html))  
* **Properties**: lowerCamelCase ([Schema.org](https://schema.org/docs/styleguide.html))  
* **Singular terms** even if the value is an array ([Schema.org](https://schema.org/docs/styleguide.html))  
* Avoid naming a **type** and a **property** the same thing ([Schema.org](https://schema.org/docs/styleguide.html))

Then Beckn adds protocol-specific rules for endpoints, JSON-LD compact IRIs, enums, and extension packs.

---

# 6\. API endpoint and action naming

## 6.1 Base endpoint shape

* All protocol endpoints MUST be rooted under: `/<root>/beckn/...` (exact server root varies by deployment; path after it is normative).  
* Endpoint path segments MUST be **lowercase**.  
* Multi-word tokens MUST use **snake\_case** (`browser_search`), not hyphenation (`browser-search`).

**Example (fixed):** `browser-search` → `browser_search` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 6.2 Action vs callback pairing

* For every action endpoint `/<...>/<action>`, the callback endpoint MUST be `/<...>/on_<action>`.  
* If an action name is compound (multi-segment), the *canonical action identifier* MUST be the segments joined with `_` for use in `context.action`.

This explicitly resolves the drift described in the context doc (path tokenization vs `context.action`).

**Rule: canonical action name**

* Strip the leading `/beckn/`  
* Join remaining path segments with `_`

Examples:

* `/beckn/select` → `select`  
* `/beckn/on_select` → `on_select`  
* `/beckn/discover/offer` → `discover_offer`  
* `/beckn/on_discover/offer` → `on_discover_offer`

## 6.3 Versioning MUST NOT live in endpoint path

Protocol versioning belongs in the message metadata (`context.version`, etc.), not in the URL path. The context file flags `/beckn/v2/...` as an inconsistency that creates taxonomy drift.

If you need a non-backward-compatible API surface, that is a **new protocol major version**, not a path fork.

## 6.4 Endpoint namespaces (allowed, but disciplined)

Namespaces like `/discover/...` are allowed when:

* They represent a durable conceptual grouping (e.g., discovery vs transaction).  
* They follow the same action/callback pairing rules.  
* They do not create ambiguous “is the action `publish` or `catalog_publish`?” situations.

## 6.5 Legacy exceptions

Some legacy shapes exist (e.g., noun-form `rating`), and MUST be explicitly documented as exceptions so they don’t become precedents.

---

# 7\. Schema pack names, folder names, and type names

## 7.1 Folder name ↔ root class name alignment

**Rule:** A schema pack folder name and its “primary” schema class name MUST match 1:1 for domain/network packs.

PR \#68 made this explicit by renaming EV Charging classes to match folders:

* `EvChargingService`: `ChargingService` → `EvChargingService`  
* `EvChargingOffer`: `ChargingOffer` → `EvChargingOffer`  
* `EvChargingSession`: `ChargingSession` → `EvChargingSession`  
* `EvChargingPointOperator`: `ChargingPointOperator` → `EvChargingPointOperator` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

**Rationale:** Domain objects are domain-specific and not meant to be reused across domains; alignment prevents collisions and confusion. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

## 7.2 Core types vs domain types

* **Core types MUST be domain-agnostic** (e.g., `Order`, `Item`, `Fulfillment`, `Invoice`, `Payment`).  
* **Domain types MUST be explicitly domain-scoped** (prefix, namespace, or pack naming) to avoid collisions over time.

## 7.3 When to use `*Action` types

If you model a concept as an **action/event** (often aligned with schema.org `Action`), use `*Action`:

* Use `TrackAction` when representing “the act of tracking” (event semantics).  
* Use `Tracking` (noun) when representing a persistent “tracking object/state”.

The context doc highlights confusion when both exist without clear rules.

**Decision test:**

* If it has an **agent**, **object/target**, and **time-bounded execution** → `*Action`.  
* If it’s a **thing with state** over time → noun.

---

# 8\. Property naming

## 8.1 Universal casing rule

* New properties MUST be **lowerCamelCase**. ([Schema.org](https://schema.org/docs/styleguide.html))  
* snake\_case is legacy and MUST NOT be introduced in new work.

PR \#67 and \#68 standardized many fields accordingly:

* `transaction_id` → `transactionId`  
* `ack_status` → `ackStatus`  
* `tl_method` → `tlMethod`  
* `expires_at` → `expiresAt`  
* `mime_type` → `mimeType`  
* `submission_id` → `submissionId` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

And in profile/API configs:

* `schema_context` → `schemaContext`  
* `network_id` → `networkId`  
* `catalog_id` → `catalogId`  
* `item_count` → `itemCount` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

## 8.2 Reserved/ambiguous names are forbidden

Avoid property names that are overloaded by JSON Schema/OpenAPI or unclear to humans.

**Forbidden unless explicitly required by an external standard:**

* `type` (except JSON-LD’s `@type`)

PR \#67 renamed a real example:

* `filters.type` → `filters.expressionType` (avoids JSON Schema reserved keyword) ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 8.3 Singular property names (even for arrays)

Property names MUST be singular. The array-ness is expressed by the schema type, not by pluralization. ([Schema.org](https://schema.org/docs/styleguide.html))

✅ `item`, `fulfillment`, `location` ✅ `item` can be `type: array` ❌ `itemsList`, `locationsArray`, `parents`

## 8.4 Prepositions go last

Use Schema.org’s guidance: prepositions come after the noun/verb concept. ([Schema.org](https://schema.org/docs/styleguide.html))

✅ `reservationFor` ❌ `forReservation`

## 8.5 Abbreviations and acronyms

**Default rule:** spell out abbreviations unless it becomes painfully verbose. ([Schema.org](https://schema.org/docs/styleguide.html))

**Beckn-specific additions:**

* Use consistent casing for repeated acronyms across the spec.  
* If an acronym is an industry-standard identifier, preserve it.

PR \#67 standardized a unit-casing example:

* `meteredEnergyKWh` → `meteredEnergyKWH` (to match `maxPowerKW`) ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

PR \#68 lists explicit “industry standard identifier” exceptions (kept as-is):

* `connectorType` enum values like `CCS2`, `Type2`, `CHAdeMO`, `GB_T` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

## 8.6 Dates and times

Use:

* `...At` for instants (`expiresAt`, `createdAt`)  
* `...On` for date-only semantics (`issueDate` / `issueOn` depending on type clarity)

Be consistent across packs.

## 8.7 Legacy exceptions (document; don’t copy)

PR \#68 explicitly kept certain **context object** fields in snake\_case as legacy from v1.x:

* `message_id`, `bap_id`, `bap_uri`, `bpp_id`, `bpp_uri` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

**Rule:** These are exceptions; new fields MUST NOT follow that pattern.

---

# 9\. Enum value conventions

## 9.1 Canonical enum style

Enum values MUST be **SCREAMING\_SNAKE\_CASE**:

* Uppercase ASCII letters, digits, and `_`  
* No hyphens, spaces, or mixed casing

PR \#67 and \#68 standardized many enums:

* `parkingType`: `OnStreet` → `ON_STREET`  
* `amenityFeature`: `WI-FI` → `WI_FI`  
* `vehicleType`: `2-WHEELER` → `2_WHEELER` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

API enums:

* `mode_hint`: `link_only` → `LINK_ONLY`, etc.  
* `quantifier`: `any` → `ANY`  
* `goals`: `visual-similarity` → `VISUAL_SIMILARITY` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

Core enum:

* `tlMethod`: `http/get` → `HTTP_GET`, etc. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

## 9.2 Grammar rules for enums

Enum members MUST be grammatically consistent within an enum:

* **Statuses** should be adjectives or past participles (`PENDING`, `ACTIVE`, `COMPLETED`, `STOPPED`), not raw verbs.

PR \#67 example:

* `sessionStatus`: `STOP` → `STOPPED` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 9.3 Stability and evolution

* Enum values are part of the public contract.  
* Adding values is usually backward compatible.  
* Renaming/removing values is breaking and requires a migration strategy (see §13).

---

# 10\. JSON-LD conventions (contexts, vocab, and compact IRIs)

## 10.1 Every serializable entity MUST be JSON-LD self-describing

Core and extension objects MUST include:

* `@context` (URI)  
* `@type` (compact or full IRI)

This is a core design principle used by the Attributes container.

## 10.2 Namespacing strategy

* Use `schema:` (schema.org) when semantics match schema.org.  
* Use `beckn:` when semantics are protocol-specific.

When mapping a field to schema.org, provide an explicit binding (e.g., using an extension such as `x-jsonld` in schema definitions). The core schema uses this pattern for mappings like `schema:priceSpecification`.

## 10.3 Context and vocab must not drift from schemas

For every term/type defined in `attributes.yaml`, ensure:

* `context.jsonld` defines how it maps to IRIs  
* `vocab.jsonld` contains human-readable labels/definitions aligned to that meaning  
* README references the correct canonical names

PR \#67 explicitly fixed a README mismatch:

* `ChargingProvider` → `ChargingPointOperator` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 10.4 Backward-compatibility mappings

When renaming a property or enum value:

* Provide a migration path in the JSON-LD context layer when feasible (e.g., aliasing old terms/values), and document it clearly. PR \#67 notes backward-compatibility mappings were added for enum value changes. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

---

# 11\. Schema authoring rules (OpenAPI/JSON Schema)

## 11.1 Structural correctness is non-negotiable

Broken indentation can accidentally introduce nonsense fields (e.g., an unintended property literally named `items`). The context doc calls out a real case where `items` was mis-indented. PR \#67 fixed that `amenityFeature` array structure. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

**Rule:** All schema bundles MUST pass:

* YAML syntax validation  
* OpenAPI validation  
* JSON Schema validation (at least for examples)

## 11.2 Closed core, open extensions

* Core entity schemas SHOULD default to `additionalProperties: false`.  
* Extension containers (`Attributes`) MUST allow `additionalProperties: true` and require `@context` and `@type`.

## 11.3 Required fields: be conservative

Adding a required field is a breaking change for producers.

**Rule:** Make fields required only when:

* The object is invalid/meaningless without it, AND  
* A safe default cannot exist, AND  
* You are willing to treat this as a compatibility commitment.

## 11.4 Prefer reuse over duplication

If semantics already exist in core or schema.org, reuse rather than inventing near-duplicates. Schema.org explicitly encourages reuse and warns that terms have specific semantic meaning beyond the name. ([Schema.org](https://schema.org/docs/styleguide.html))

---

# 12\. Examples and documentation quality gates

## 12.1 Examples MUST validate

Every example payload MUST match:

* property names (case-sensitive)  
* enum casing and values  
* schema structure

PR \#67 fixed real example mismatches:

* `Tracking.trackingStatus`: `"active"` → `"ACTIVE"`  
* `SupportInfo.channels`: `["web","phone","email"]` → `["WEB","PHONE","EMAIL"]`  
* `AcceptedPaymentMethod`: `["UPI","Card","Wallet"]` → `["UPI","CREDIT_CARD","WALLET"]` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 12.2 Documentation must name real things

README tables MUST reference canonical schema names, not “what we meant”.

PR \#67 fixed a mismatch (`ChargingProvider` → `ChargingPointOperator`). ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## 12.3 Editorial tone and consistency

* Use US English spelling. ([Schema.org](https://schema.org/docs/styleguide.html))  
* Expand acronyms on first use in READMEs/docs (unless globally obvious in the Beckn ecosystem).  
* Avoid internal jargon unless defined in a glossary.

---

# 13\. Change management and backward compatibility

## 13.1 What counts as breaking

Breaking changes include:

* Renaming a property (`transaction_id` → `transactionId`)  
* Renaming a type (`ChargingService` → `EvChargingService`)  
* Renaming enum values (`http/get` → `HTTP_GET`)  
* Changing required fields  
* Changing the meaning of an existing field

PR \#68 explicitly lists these as breaking categories. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

## 13.2 Preferred evolution path (practical and safe)

When you need change:

1. **Add new field / new enum value** (keep old).  
2. Mark old as **deprecated** in description/docs.  
3. Provide a **migration note** and (when feasible) a JSON-LD alias mapping.  
4. Remove only in a planned major release.

## 13.3 Don’t silently “semantic shift”

Never reuse an existing name with a new meaning. If meaning changes, create a new term and deprecate the old.

---

# 14\. Domain-specific schema & API spec rules (Layer 2\)

Domain packs exist because “core can’t model all nouns” and need sector vocabularies bound back to Beckn for validation/interoperability.

## 14.1 Domain packs MUST be additive to core

* Do NOT fork core semantics into new names when an extension pack suffices.  
* Use core’s `...Attributes` extension points to attach domain objects at runtime.

## 14.2 Semantic binding is mandatory (eventually)

A domain pack SHOULD provide JSON-LD mappings to:

* `beckn:` terms when it is protocol-specific  
* `schema:` terms when schema.org already captures the semantics

This is key for validators like Beckn ONIX to validate extended schema “comfortably” without breaking interoperability.

## 14.3 Domain pack naming

* Pack folder: TitleCase (e.g., `EvChargingService`)  
* Primary types: match folder name and be domain-scoped (see §7.1) ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))  
* Properties: lowerCamelCase; enums SCREAMING\_SNAKE\_CASE (see §8–§9)

## 14.4 Domain profiles and IGs

Implementation Guides are **recommendations**, not protocol law, but they must still:

* Use canonical schema names  
* Provide validating examples  
* Declare deviations/policies explicitly

---

# 15\. Network-specific schema & API spec rules (Layer 3\)

Networks often need regional identifiers (e.g., UPI IDs, FSSAI license numbers) and policy constraints.

## 15.1 Extension strategy

Network specs SHOULD extend **domain packs**, not core, unless:

* The field is universally applicable across domains, and  
* It is proven stable enough for core.

## 15.2 Network namespacing

Network-specific attributes MUST be namespaced to avoid collisions:

* Prefer network context URIs and network-specific `@type` values.  
* Avoid “generic” names like `licenseNumber` without context; be specific (`fssaiLicenseNumber`, etc.).

## 15.3 Fast-moving does not mean sloppy-moving

Even if go-to-market forces a network to ship quickly:

* Keep a clear mapping to domain/core semantics.  
* File upstream PRs/issues when possible.  
* Don’t create permanent forks without attribution and traceability.

---

# 16\. Attribution and reuse guidelines (Core → Domain → Network)

Because specs are reused, copied, and sometimes forked, governance must ensure attribution is preserved—especially when networks publish their own IGs and schema extensions.

## 16.1 Minimum attribution requirements (practical, not ceremonial)

Anyone publishing a domain or network spec derived from Beckn MUST:

* Preserve upstream license notices and copyright headers.  
* Include a visible “Based on Beckn Protocol v2.x” attribution in README.  
* Link to the upstream repository and the specific release/commit/tag used as the base.  
* Maintain a `CHANGES.md` (or equivalent section) listing what was modified from upstream.

## 16.2 Forking is allowed; silent copying is not

If you must fork to meet timelines:

* Make the fork explicit.  
* Keep attribution intact.  
* Track upstream merges so the fork doesn’t become a permanent parallel universe.

---

# 17\. Cross-artifact consistency checklist (for every PR)

Use this as a PR review gate:

## Naming & casing

- [ ] Types are TitleCase; properties lowerCamelCase; enums SCREAMING\_SNAKE\_CASE. ([Schema.org](https://schema.org/docs/styleguide.html))  
- [ ] No new snake\_case except documented legacy exceptions. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))  
- [ ] No ambiguous reserved names like `type` (unless JSON-LD `@type`). ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## API

- [ ] Endpoint tokens use lowercase \+ snake\_case; no hyphens. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))  
- [ ] Action/callback pairing is consistent (`on_` prefix).

## Schemas

- [ ] YAML structure validated (arrays have correctly nested `items`, etc.). ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))  
- [ ] Domain pack folder ↔ class name alignment holds. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

## JSON-LD and docs

- [ ] `attributes.yaml` changes mirrored in `context.jsonld`, `vocab.jsonld`, README, profile.json. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))  
- [ ] Examples validate against schemas; enum casing matches. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))

## Compatibility and governance

- [ ] Breaking changes are clearly labeled and include migration guidance. ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))  
- [ ] Domain/network extensions include attribution and traceability to upstream.

---

# 18\. Quick reference tables

## 18.1 Casing summary

| Thing | Format | Example |
| :---- | :---- | :---- |
| Schema type/class | TitleCase | `EvChargingService` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68)) |
| Property (general) | lowerCamelCase | `transactionId` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67)) |
| Enum values | SCREAMING\_SNAKE\_CASE | `HTTP_GET`, `LINK_ONLY` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68)) |
| JSON-LD keywords | JSON-LD standard | `@context`, `@type` |
| Endpoint tokens | lowercase \+ snake\_case | `browser_search` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67)) |

## 18.2 “Before → After” examples pulled from real cleanups

* Reserved ambiguity: `filters.type` → `filters.expressionType` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))  
* snake\_case → camelCase: `expires_at` → `expiresAt` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))  
* Enum normalization: `http/get` → `HTTP_GET` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))  
* Domain scoping: `ChargingSession` → `EvChargingSession` ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))

---

# 19\. Source materials used for this guide

* Beckn style-guide context (problem statements, inconsistency classes).  
* Attribution & layering context (core→domain→network, IG realities, attribution problem).  
* Beckn core schema reference (Attributes container pattern, JSON-LD requirements).  
* Schema.org naming guidance baseline (TitleCase / lowerCamelCase / singular / avoid “type”). ([Schema.org](https://schema.org/docs/styleguide.html))  
* Beckn PR \#67 (naming, enum, example fixes). ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/67))  
* Beckn PR \#68 (domain class alignment, remaining casing/enum standardization, legacy exceptions). ([GitHub](https://github.com/beckn/protocol-specifications-v2/pull/68))
