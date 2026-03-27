# Introduction to Beckn Protocol Version 2

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.1)

---

## 1. What is Beckn Protocol?

Beckn Protocol is an open, interoperable communication protocol that enables any two platforms — a buyer-side application and a seller-side platform — to perform digitally signed, asynchronous commerce transactions over standard HTTPS, without either party needing a prior commercial relationship or a shared intermediary.

Beckn is designed to be:

- **Domain-agnostic**: the same protocol handles mobility, retail, logistics, health, education, and any other sector.
- **Decentralized**: no single platform owns the network; participants discover each other via an open registry.
- **Minimal by design**: the core specification defines only what is strictly necessary for two parties to transact. Everything else — domain semantics, business rules, catalog structures — is layered on top.

The best analogy is HTTP: HTTP defines a small, stable message envelope that underpins the entire web. Beckn defines a small, stable transaction envelope that can underpin any open commerce network.

---

## 2. What is New in Version 2?

Beckn Protocol v2 is a ground-up rearchitecture motivated by four goals:

### 2.1 Global Semantic Interoperability

v1.x used ad-hoc JSON fields with no machine-readable connection to global vocabularies. v2 aligns all core entities with [JSON-LD](https://www.w3.org/TR/json-ld11/) and [schema.org](https://schema.org), so that Beckn data can be consumed by any JSON-LD-aware tool — RDF libraries, graph databases, knowledge graph platforms — without custom adapters.

### 2.2 Catalog-First Discovery

v1.x discovery relied on a Beckn Gateway (BG) that multicast `search` requests to all registered BPPs in real time. v2 replaces this with:

- A **Catalog Publishing Service (CPS)** that accepts asynchronous catalog push updates from BPPs and normalizes them.
- A **Catalog Discovery Service (CDS)** that answers BAP queries from a continuously updated index — without any real-time multicast.

This makes discovery faster, more scalable, and independent of any specific BAP request.

### 2.3 Decentralized Registry

v1.x registries exposed bespoke Beckn `lookup`/`subscribe` APIs. v2 requires the registry to be compliant with the **[Decentralized Directory (DeDi) protocol](https://dedi.global)** — a globally interoperable, machine-readable public directory standard. This allows Beckn registries to participate in a shared trust layer across ecosystems.

### 2.4 Composable Schema Architecture

v2 introduces a three-tier schema model:

| Tier | Repository | Role |
|---|---|---|
| Transport envelope | This repo (`beckn.yaml`) | Minimal, stable, version-locked |
| Core transaction schema | `beckn/core_schema` | Domain-agnostic, evolvable |
| Domain schema packs | Per-vertical repositories | Use-case specific, independently governed |

New industries onboard by creating domain schema packs — not by modifying the core protocol.

---

## 3. Relationship to v1.x

v2 is a **new protocol line**, not an in-place upgrade. v1.x networks continue to operate independently. The recommended migration path is:

1. Run v1 and v2 in parallel during a transition period.
2. Migrate registry participant records to DeDi-compliant format.
3. Convert v1 catalog models to v2 `Item` + `Offer` JSON-LD graphs.
4. Deprecate v1 infrastructure once v2 equivalents are stable.

See [5_Versioning_and_Compatibility.md](./5_Versioning_and_Compatibility.md) for the full migration guide.

---

## 4. Design Philosophy

### The HTTP Analogy

Just as HTTP defines `GET`, `POST`, headers, and status codes — and says nothing about what a webpage contains — Beckn v2 defines a universal endpoint, a transport envelope, and an authentication contract, and says nothing about what a catalog or an order contains. That is the job of `core_schema` and domain schema packs.

### Optimal Ignorance

A feature that is not required for interoperability should not be standardized in the core. The core specification should be the last place a new capability is added, not the first.

### Stability by Design

The base protocol specification (this repository) is intended to change extremely rarely — like HTTP itself. All innovation happens in the schema layer above it.

---

## 5. Repository Map

| Repository | Purpose |
|---|---|
| [`beckn/protocol-specifications-v2`](https://github.com/beckn/protocol-specifications-v2) | **This repo** — transport envelope, universal API, authentication contract |
| [`beckn/core_schema`](https://github.com/beckn/core_schema) | Domain-agnostic transaction schemas: `Catalog`, `Item`, `Offer`, `Order`, action types, etc. |
| `beckn/<domain>-schema` | Per-vertical domain schema packs |
| [DeDi](https://dedi.global) | Decentralized Directory protocol for network registries |
| [schema.beckn.io](https://schema.beckn.io) | Beckn schema registry and JSON-LD context hosting |

---

## 6. How to Use This Documentation

| Goal | Start Here |
|---|---|
| Understand the overall system | [4_Network_Architecture.md](./4_Network_Architecture.md) |
| Implement the API endpoint | [7_Communication_Protocol.md](./7_Communication_Protocol.md) |
| Implement request signing | [9_Authentication_and_Security.md](./9_Authentication_and_Security.md) and [10_Signing_Beckn_APIs_in_HTTP.md](./10_Signing_Beckn_APIs_in_HTTP.md) |
| Build a CPS or CDS | [14_Discovery_Architecture.md](./14_Discovery_Architecture.md) |
| Build a DeDi-compliant registry | [12_Registry_and_Identity.md](./12_Registry_and_Identity.md) |
| Design a domain schema pack | [6_Schema_Distribution_Model.md](./6_Schema_Distribution_Model.md) and [21_Schema_Pack_Contract.md](./21_Schema_Pack_Contract.md) |
| Understand conformance | [24_Conformance_and_Testing.md](./24_Conformance_and_Testing.md) |

---

## 7. Related Resources

| Resource | Link |
|---|---|
| Beckn Protocol v1 specification | https://github.com/beckn/protocol-specifications |
| Beckn core transaction schema | https://github.com/beckn/core_schema |
| Beckn schema registry | https://schema.beckn.io |
| DeDi protocol | https://dedi.global |
| Beckn website | https://beckn.io |
