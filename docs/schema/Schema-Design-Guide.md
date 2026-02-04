# A Robust, Forward-looking Schema Design Framework to Create Domain-specific Bindings for Beckn Protocol 2.0

## Request for Comments – Jan 19, 2026 - DRAFT

# About this Document

### Latest published version

To be published. This RFC is currently under community review and iteration.

### Latest editor's draft

* Google Docs (comment access required): [https://docs.google.com/document/d/17JJMherJ68ILYRqMqpnNdto1eENs24_d5ylin8uNkQ0/edit?usp=sharing](https://docs.google.com/document/d/17JJMherJ68ILYRqMqpnNdto1eENs24_d5ylin8uNkQ0/edit?usp=sharing)
* GitHub (editorial source of truth): To be added

Contributors are requested to review the Community Guidelines for Contributing before requesting access.

### Implementation report

Not available at the time of publishing this draft.

### Editors

* Ravi Prakash (Beckn Labs)
* Pramod Varma (Networks for Humanity)

### Authors

* Ravi Prakash (Beckn Labs)

### Feedback

#### Issues

To view open issues on this topic, [click here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue%20state%3Aopen%20label%3Aschema-design)

#### Discussions

To view discussions on this topic [click here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=is:open%20label:schema-design)

#### Pull Requests

To be tracked via GitHub Pull Requests.

### Errata

No errata recorded as of this draft.

# Acknowledgements

The author would like to thank the following contributors for their insights and reviews:

1. Abhishek Jain

# Context

## Beckn Protocol 2.0

Beckn Protocol 2.0 represents a structural evolution of the Beckn ecosystem, shifting from loosely coupled, interpretation-heavy payloads to a rigorously defined, schema-first transactional protocol. The core objective of Beckn v2.0 is to enable interoperable, verifiable, and automatable commerce across heterogeneous networks, platforms, and AI agents.

A central pillar of this evolution is the introduction of strict core schemas, explicit domain extensions, and a clear separation between protocol-level guarantees and domain-specific semantics. This allows Beckn to scale horizontally across industries such as mobility, commerce, energy, logistics, and finance without fragmenting the protocol itself.

## Adoption Landscape

As Beckn adoption increases across sectors, domain implementers bring with them pre-existing data standards, ontologies, and operational schemas (for example, GTFS in mobility or industry-specific catalog formats in commerce). Without a consistent methodology to bind these domain standards to Beckn, implementations risk semantic drift, incompatible payloads, and brittle integrations.

This RFC addresses that gap.

# Intended Outcome

A developer building a Beckn Protocol 2.0 endpoint for a domain-specific application (BAP or BPP) should be able to:

1. Install Beckn ONIX.
2. Install a domain binding plugin (for example, mobility-beckn or gtfs-beckn) on the ONIX adapter.
3. Map an existing domain schema to Beckn core and extension schemas using a predictable, repeatable process.
4. Validate payloads deterministically at runtime.
5. Achieve semantic interoperability with other Beckn participants without bespoke bilateral agreements.

# Problem

## Current State

Today, domain-specific Beckn implementations often rely on ad-hoc schema extensions, implicit assumptions, or undocumented field mappings. Different teams may model the same real-world concept in incompatible ways, even within the same domain.

Common symptoms include:

* Reuse of Beckn fields with domain-specific overloading.
* Proliferation of custom attributes without shared semantics.
* Ambiguous precedence between schema.org, Beckn core schemas, and domain vocabularies.
* Difficulty validating payload correctness beyond basic structural checks.

## Consequences

This approach leads to:

* Reduced interoperability across networks.
* Increased integration costs for new participants.
* Fragile agent behavior due to semantic ambiguity.
* Inability to reason over transactions programmatically at scale.

## Problem Statement

How do we enable domain experts and implementers to reuse existing domain standards while producing Beckn-compliant schemas that are unambiguous, verifiable, and interoperable across networks?

# Solution

## Design Principles

1. Human intent precedes machine enforcement.
2. Closed schemas are required for validation and contract enforcement.
3. Openness is achieved through semantic equivalence, not schema inheritance.
4. Beckn core schemas remain minimal and domain-agnostic.
5. Domain-specific semantics are isolated, versioned, and explicitly bound.

## Proposed Framework

The framework defines a staged schema derivation pipeline:

1. **Domain Standard**: Human-readable specifications such as PDFs, HTML documents, or markdown files that describe domain concepts and rules.
2. **Closed Domain Vocabulary**: A machine-readable but closed representation of domain terms, independent of JSON-LD or web semantics.
3. **Closed JSON-LD Schema**: A strict JSON-LD schema with a self-contained vocabulary, suitable for validation and runtime enforcement.
4. **Open Semantic Mapping Layer**: A derived schema that declares semantic equivalence to schema.org and/or Beckn schemas without relaxing validation rules.

This staged approach ensures clarity at each level while preventing premature coupling to external ontologies.

## Schema Precedence Rules

1. Beckn core schemas take precedence for protocol-level constructs.
2. Domain schemas define semantics within their declared scope.
3. schema.org is used as a semantic reference, not as a validation authority.
4. In the absence of a suitable mapping, new domain vocabulary entries must be explicitly defined and versioned.

## Concrete Example (Mobility / GTFS)

* Existing GTFS fields are first mapped to Beckn core entities where semantic equivalence exists.
* Fields without Beckn counterparts are mapped to schema.org terms if appropriate.
* Remaining unmapped fields are defined in a domain vocabulary file (for example, mobility/gtfs/vocab.json).
* Validation rules for these fields are enforced via the closed JSON-LD schema.

## Tooling Requirements

To operationalize this framework at scale, the following tooling is required:

* Schema binding repositories with clear versioning.
* Automated validators for closed JSON-LD schemas.
* Linting tools to detect ambiguous or conflicting mappings.
* Plugin-based adapters (for example, Beckn ONIX plugins) that load domain bindings dynamically.
* CI pipelines to enforce schema governance rules.

## Flow Diagram

Refer to the accompanying schema design methodology diagram that illustrates the staged derivation and semantic binding process.

# Conclusion

This RFC proposes a disciplined, forward-looking schema design framework that balances strict validation with semantic openness. By separating concerns across layers and enforcing clear precedence rules, Beckn Protocol 2.0 can support deep domain specialization without sacrificing interoperability or long-term evolvability.
