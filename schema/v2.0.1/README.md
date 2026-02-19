# Beckn Protocol Schema — v2.0.1

**Status**: LTS (Long Term Support)

---

## Overview

This directory contains the **core schema** for Beckn Protocol v2.0.1 — the minimal, stable set of semantic definitions that underpin the protocol envelope.

| File | Purpose |
|------|---------|
| [`vocab.jsonld`](./vocab.jsonld) | OWL class definitions for Beckn core protocol types |
| [`context.jsonld`](./context.jsonld) | JSON-LD context mapping Beckn type names to their IRIs |

---

## Design Philosophy

These files are **intentionally minimal by design**.

Beckn Protocol v2 follows the same design principle as foundational internet protocols like HTTP: define a small, stable base that changes rarely, and allow the ecosystem to evolve rapidly on top of it. The schema in this directory defines only the core protocol envelope types — the minimal vocabulary needed to understand a Beckn message at the transport layer.

This approach means:
- **This repository changes rarely** — adding a new type here requires the same level of deliberation as a change to the HTTP spec.
- **The ecosystem evolves in other repositories** — detailed type definitions, payload schemas, action semantics, and domain-specific attributes live elsewhere.
- **Implementers can depend on this spec for the long term** — LTS status means breaking changes will not be introduced without a new major version.

---

## What's in scope here

The types defined in `vocab.jsonld` and mapped in `context.jsonld` are limited to the **protocol envelope layer**:

| Type | Role |
|------|------|
| `Action` | Identifies the specific Beckn protocol operation being performed |
| `Signature` | Beckn Signature used for authenticating requests and callbacks |
| `RequestAction` | A forward action payload originated by a BAP |
| `RequestActionQuery` | A forward action payload encoded as a URL query parameter (GET Query Mode) |
| `CallbackAction` | A callback action payload originated by a BPP or CPS |
| `Ack` | Synchronous acknowledgement confirming receipt and signature validation |
| `Nack` | Negative acknowledgement indicating the request could not be accepted |
| `NackBadRequest` | Nack for malformed or invalid requests (HTTP 400) |
| `NackUnauthorized` | Nack for invalid or missing authentication (HTTP 401) |
| `NpInternalError` | Server-side error on a network participant's platform (HTTP 500) |
| `NetworkParticipant` | A participant in a Beckn-enabled network (BAP, BPP, CPS, CDS, Registry) |

---

## What's NOT in scope here

Detailed type definitions, payload shapes, and action semantics are maintained in separate repositories to allow independent evolution:

| Content | Repository |
|---------|-----------|
| Full OWL/JSON-LD definitions for `RequestAction`, `CallbackAction`, `Ack`, `Nack`, `Action`, `Signature`, `NetworkParticipant`, etc. | [beckn/core_schema](https://github.com/beckn/core_schema) |
| Domain-specific attribute packs (mobility, retail, health, climate, etc.) | Per-vertical repositories |
| API endpoint definitions and action semantics | [api/v2.0.1/beckn.yaml](../../api/v2.0.1/beckn.yaml) + [beckn/core_schema](https://github.com/beckn/core_schema) |

---

## Namespace

The Beckn core namespace is:

```
https://schema.beckn.io#
```

Prefix: `beckn:`

All types defined here are identified by IRIs of the form `beckn:{TypeName}`, e.g.:
- `beckn:Action` → `https://schema.beckn.io#Action`
- `beckn:Ack` → `https://schema.beckn.io#Ack`

---

## Usage

### JSON-LD context

To use the Beckn core context in a JSON-LD document:

```json
{
  "@context": [
    "https://schema.beckn.io/schema/v2.0.1/context.jsonld"
  ],
  "@type": "RequestAction",
  ...
}
```

### OWL vocabulary

The `vocab.jsonld` file can be used with RDF/OWL tooling to reason over Beckn core types, validate semantic constraints, or integrate with graph databases and linked data ecosystems.

---

## Related

- [Beckn Protocol v2 — Main README](../../README.md)
- [Beckn Protocol API v2.0.1](../../api/v2.0.1/README.md)
- [Beckn core transaction schema](https://github.com/beckn/core_schema)
- [Beckn schema registry](https://schema.beckn.io)
- [DeDi protocol](https://dedi.global)
