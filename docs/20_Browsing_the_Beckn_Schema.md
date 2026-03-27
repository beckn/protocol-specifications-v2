# Browsing the Beckn Schema

## A simple guide to understanding the organization of schemas used in Beckn Protocol APIs and their usage

# The `beckn.yaml` document and its structure

The beckn.yaml is the MOST IMPORTANT technical specification document for anyone using Beckn Protocol. It is an Open API 3.1.1 API specification document that contains all the API endpoints.

The request and response payloads along with their headers and security schemes point to a few locally referenced schemas like Context, Message, Ack, Error, Intent, Catalog, Contract, Support, TrackingInfo, Resource, Offer, Settlement, Commitment, Consideration, Performance, SupportInfo, etc, that travel inside the HTTP request body. Let’s call these schemas as First-class schemas (sometimes also known as “core schemas”, “container schemas”, “envelope schemas”, and “root schemas”). These schemas ARE ALWAYS published inside the beckn.yaml.

### NOTE:

Each of these core schemas have properties that are permanent and immutable until the protocol version itself changes.

# The composable `Attributes` schema

Alongside these immutable properties, there are some properties that are of type “Attributes”. The `Attributes` schema is a special composable JSON-LD container schema with two properties – @context and @type, both of which are required fields with `additionalProperties` set to `true`, indicating that it allows for custom properties to be composed, inserted, and validated at runtime i.e. during Beckn API calls.

Any payload with a property of type `Attributes` ALWAYS contains a linked-data (JSON-LD) object that can be semantically validated using the existing @context and @type fields irrespective of their shape and routed into the consuming application’s relevant business logic.

The protocol recommends that any beckn-enabled application (BAP, BPP) SHOULD embed domain-specific data inside these JSON LD containers when communicating with one another. The processing of this JSON-LD object SHOULD be done via a JSON-LD processor which uses the @context URLs and @type properties to identify and navigate the vocabulary graph, and ultimately map it to its internal vocabulary and data model.

### Note:

It is however to be noted that a semantic validation doesn’t eliminate the need for structural validation. Both validations are required to ensure strict interoperability between NPs, however the order of execution, and the preference of using one or both validations is left to the implementation guidelines being used by the application provider.

# The Beckn Schema Registry

In addition to the API specification, Beckn also comes with a hosted library of useful structured schemas with canonical IRIs, shape validation logic, property-IRI mappings, rendering templates, and a detailed vocabulary with semantic linkages to well known global general purpose vocabularies like schema.org, and other domain-specific vocabularies

Each schema in the schema registry is also individually versioned allowing them to evolve independently in shape, composition, validation logic, description, semantics, and other significant aspects.

All these schemas and their respective versions are neatly arranged and managed on one or more public GitHub repositories.

Yes, you heard me right – “one or more” GitHub repositories.

You see, the complete Beckn Schema Registry contains both domain-agnostic and domain-specific schemas sourced from *multiple* GitHub repositories. While some bundles may contain both domain-agnostic and domain-specific schemas, other bundles may contain only domain-specific schemas. As of today, Beckn Protocol recognizes and maintains schemas across *only two* repositories. There could be more in the future. Some may even be maintained outside the Beckn organisation’s influence but recognized as a significant resource to be referenced and catalogued.

The first schema bundle is published at [https://github.com/beckn/schemas/tree/main/schema/](https://github.com/beckn/schemas/tree/main/schema/)\*. This schema contains both domain-agnostic and domain-specific schemas. The current domains that the schemas in this repository cover are – retail (grocery, food and beverages), logistics, mobility, and skilling.

The second schema bundle is available at [https://github.com/beckn/DEG/tree/main/specification/schema/](https://github.com/beckn/DEG/tree/main/specification/schema/)\*. This bundle only contain energy sector specific schemas, specifically EV Charging, P2P energy trading, and Demand Response / Flexibility.

The two repositories namely schemas and DEG act as the source of truth and more importantly the persistence layer for all CRUD operations for Beckn schemas and their respective versions.

## How the Beckn Schema Registry is organized

Each schema maintained across the above two repositories has its own individual schema directory. The name of the directory is ALWAYS the same name as the canonical name of the schema.

### Schema Root README.md (REQUIRED)

Each schema directory has a detailed README.md that contains information covering all its existing versions.

### Schema version subdirectories

Each schema directory MAY contain one or more subdirectories containing various versions. Each version folder contains multiple files, each with its own purpose, content format, and file extensions like .yaml, .json, .jsonld, .md. Let us take a brief look at the important ones.

### File 1: attributes.yaml (REQUIRED)

This file contains the structural (payload) validation rules  for the respective schema.

### File 2: context.jsonld (REQUIRED)

Contains schema name, first-class field names (keys), enumerations, and defaults, of each schema version are mapped to the standard beckn canonical IRIs via a file called context.jsonld

### File 3: vocab.jsonld (REQUIRED)

Contains the knowledge graph (ontology) of that schema version with semantic linkages to other vocabularies like schema.org, owl, xsd, rdf, rdfs, foaf, etc.

### File 4: renderer.json (RECOMMENDED)

Contains templates to render each schema version on specific user interfaces like Web, Android, iOS, etc.

### File 5: README.md (REQUIRED)

Contains detailed documentation on the schema version’s history, description, property table, developer URLs, issue links, errata, semantics, usage, inheritance, examples and much more.

### File 6: IMPLEMENTATION\_REPORT.md (PLANNED)

Will contain reports on the implementation and usage of that schema version.

### File 7: CONTRIBUTORS.md (PLANNED)

Contains contributors and the necessary acknowledgement given to its authors

There are several more files but they are out of scope of this content.

### Examples folder

In addition to these files, sometimes there is also an `examples` folder that may contain subfolders for different use case contexts containing one or more json documents.

This folder structure is a REQUIRED pattern for any schema library Beckn recognizes.

#### NOTE:

While the structure and description of each schema version may evolve, the underlying semantics and meaning of the schemas will ALWAYS remain the same. For example, a `Driver` schema may evolve to have more attributes and better structure in newer versions but a `Driver` schema will NEVER evolve into a `Bus` schema. A driver will always remain a driver whether the schema design is crude or global standard / state-of-the-art.

# The `schema.beckn.io` website

Finally, the entire schema of Beckn (sometimes called the schema registry, schema database, schema library, schema website) has been catalogued and is accessible at [https://schema.beckn.io](https://schema.beckn.io). The schema website is fully available to the public. Each schema has a dedicated landing webpage available at [https://schema.beckn.io/{SchemaName}](https://schema.beckn.io/{SchemaName}) where {SchemaName} represents the canonical name given to  each schema. The landing page contains human/agent-readable content along with developer URLs, examples, current status, and property-type-description tables.

The developer URLs section contains a table of versioned URL paths pointing to the schema’s version folder. The endpoints of each url are the same files that were described earlier namely attributes.yaml, context.jsonld, vocab.jsonld, renderer.json, profile.json, etc.   