# Beckn Protocol v2 — Documentation

This folder contains the reference documentation and RFC series for Beckn Protocol Version 2.

The documents are ordered as a **progressive learning journey** — from the most general concepts through to the most advanced normative specifications. A reader who follows the documents in order will arrive at full comprehension of the protocol, its rationale, and its conformance requirements.

---

## How to Read This Documentation

Each document belongs to one of two types:

- **Reference documents** (marked *Narrative*) — informative, conceptual explanations. No prior implementation knowledge required.
- **RFCs** (marked *RFC*) — normative specifications. Each RFC follows the template in document 3 and uses the keyword definitions from document 2.

---

## Stage 1 — Before You Read Anything Else

> **Goal:** Equip the reader to understand all subsequent documents. These three documents are prerequisites for everything that follows.

| # | Document | Type | What you learn |
|---|---|---|---|
| 1 | [1_Introduction.md](./1_Introduction.md) | Narrative | What Beckn Protocol v2 is, how it differs from v1, the HTTP analogy, the repo map |
| 2 | [2_Keyword_Definitions.md](./2_Keyword_Definitions.md) | RFC | What MUST, SHOULD, MAY, REQUIRED mean — how to read normative text |
| 3 | [3_RFC_Template.md](./3_RFC_Template.md) | Template | The structure every RFC in this folder follows |

---

## Stage 2 — The Big Picture

> **Goal:** Understand the architecture, the schema model, and the versioning philosophy before touching any implementation detail.

| # | Document | Type | What you learn |
|---|---|---|---|
| 4 | [4_Network_Architecture.md](./4_Network_Architecture.md) | Narrative | The five actor roles (BAP, BPP, CPS, CDS, Registry), how they relate, Core→Domain→Network layering, network topology diagram |
| 5 | [5_Versioning_and_Compatibility.md](./5_Versioning_and_Compatibility.md) | Narrative | SemVer (PATCH/MINOR/MAJOR), LTS and EoS designations, deprecation policy, v1→v2 migration phases |
| 6 | [6_Schema_Distribution_Model.md](./6_Schema_Distribution_Model.md) | Narrative | The three-tier schema model: transport envelope (this repo) / core_schema / domain packs; why there is no `schema/` directory |

---

## Stage 3 — Core Protocol Mechanics

> **Goal:** Understand exactly how two participants communicate, how requests are signed, and what errors look like. This is the foundation every implementor needs.

| # | Document | Type | What you learn |
|---|---|---|---|
| 7 | [7_Communication_Protocol.md](./7_Communication_Protocol.md) | Narrative | Async server-to-server model; the universal `/beckn/{endpoint}`; GET Body Mode, GET Query Mode, POST; ACK/callback lifecycle; response codes |
| 8 | [8_Core_API_Envelope.md](./8_Core_API_Envelope.md) | RFC | Normative transport contract — mandatory `Context` fields, `RequestContainer`, `CallbackContainer`, response schemas |
| 9 | [9_Authentication_and_Security.md](./9_Authentication_and_Security.md) | Narrative | The Beckn Signature: Ed25519, BLAKE2b-512, signing string construction, key resolution via DeDi registry, key lifecycle |
| 10 | [10_Signing_Beckn_APIs_in_HTTP.md](./10_Signing_Beckn_APIs_in_HTTP.md) | RFC | Step-by-step signing algorithm with worked example and test vectors |
| 11 | [11_Error_Codes.md](./11_Error_Codes.md) | RFC | Transport-level error schemas (Nack types) and the full application-level error code registry (30xxx–60xxx) |

---

## Stage 4 — Identity and Discovery Infrastructure

> **Goal:** Understand the two pillars of network infrastructure — the registry (who participants are) and the catalog index (what they offer). These enable the protocol to function at network scale.

| # | Document | Type | What you learn |
|---|---|---|---|
| 12 | [12_Registry_and_Identity.md](./12_Registry_and_Identity.md) | Narrative | The DeDi-compliant registry: what it stores, how participants register and are looked up, comparison with v1.x |
| 13 | [13_DeDi_Registry_Integration.md](./13_DeDi_Registry_Integration.md) | RFC | Normative registry spec: participant record schema, subscribe/lookup/unsubscribe operations, key rotation rules |
| 14 | [14_Discovery_Architecture.md](./14_Discovery_Architecture.md) | Narrative | CPS + CDS replacing BG multicast: the catalog-first push/index model, BPP publication flow, BAP discovery flow |
| 15 | [15_Catalog_Publishing_Service.md](./15_Catalog_Publishing_Service.md) | RFC | Normative CPS spec: `publish` endpoint, validation, normalization, CPS→CDS forwarding, idempotency |
| 16 | [16_Catalog_Discovery_Service.md](./16_Catalog_Discovery_Service.md) | RFC | Normative CDS spec: `discover` endpoint, index maintenance, result delivery via `on_discover` callback |

---

## Stage 5 — Advanced Protocol Features

> **Goal:** Master the non-repudiation model, the full normative communication flows, and the self-contained URL mode. These build directly on Stage 3.

| # | Document | Type | What you learn |
|---|---|---|---|
| 17 | [17_Non_Repudiation_and_Lineage.md](./17_Non_Repudiation_and_Lineage.md) | RFC | `CounterSignature` (signed receipt in every Ack), `InReplyTo` (callback binding), `LineageEntry` (cross-transaction causal attribution) |
| 18 | [18_Communication_Protocol_RFC.md](./18_Communication_Protocol_RFC.md) | RFC | Full normative communication flows: discovery, catalog publication, all transaction actions, multi-callback status updates |
| 19 | [19_Get_Query_Mode.md](./19_Get_Query_Mode.md) | RFC | GET Query Mode — encoding payload + signature as URL parameters; QR code, deep link, IoT use cases; security constraints |

---

## Stage 6 — Schema Extension and Network Policy

> **Goal:** Learn how to extend the core protocol for a specific industry domain and how to configure a network-specific policy layer on top of core. These documents are for domain pack authors, network operators, and implementors building verticals.

| # | Document | Type | What you learn |
|---|---|---|---|
| 20 | [20_JSONld_Context_and_Schema_Alignment.md](./20_JSONld_Context_and_Schema_Alignment.md) | RFC | JSON-LD context design rules; mandatory schema.org mappings; `beckn:` namespace; controlled document loaders; context URI governance |
| 21 | [21_Schema_Pack_Contract.md](./21_Schema_Pack_Contract.md) | RFC | How to author, version, and publish a domain schema pack; pack structure; composition rules; publication requirements |
| 22 | [22_Network_Policy_Profiles.md](./22_Network_Policy_Profiles.md) | RFC | How networks publish a JSON-LD Network Profile; required schema packs; action subsets; geographic and temporal coverage; policy enforcement |
| 23 | [23_Payments_on_Beckn_Networks.md](./23_Payments_on_Beckn_Networks.md) | RFC | Payment contract model (out-of-band execution, in-band terms); `Payment` object; BAP collects vs BPP collects flows; `payto://` URI examples |

---

## Stage 7 — Conformance and Certification

> **Goal:** Understand what it means to be conformant with Beckn Protocol v2.0.1, and how to test and certify an implementation. These are the final destination documents — every conformance requirement in Stages 1–6 is consolidated here.

| # | Document | Type | What you learn |
|---|---|---|---|
| 24 | [24_Conformance_and_Testing.md](./24_Conformance_and_Testing.md) | Narrative | Conformance levels; per-role MUST requirements (BAP, BPP, CPS, CDS, Registry); schema validation, signature, flow, and negative test guidance |
| 25 | [25_Conformance_and_Certification.md](./25_Conformance_and_Certification.md) | RFC | Normative conformance rules per role; conformance test suite structure; certification process and criteria |

---

## Governance

All RFCs in this folder follow the lifecycle defined in [GOVERNANCE.md](../GOVERNANCE.md):

```
Proposal → Draft → Candidate → Released → Deprecated → Removed
```

Any normative change MUST include a conformance impact classification (Patch / Minor / Major / Informative) and explicit security/privacy implications as required by the Governance Model.

---

## Quick Reference by Role

| I am a... | Start here | Then read |
|---|---|---|
| **New to Beckn v2** | 1, 2, 4 | 5, 6, 7 |
| **BAP implementor** | 1, 2, 4, 7, 8, 9, 10 | 12, 13, 14, 17, 18, 19, 24 |
| **BPP implementor** | 1, 2, 4, 7, 8, 9, 10 | 12, 13, 15, 17, 18, 23, 24 |
| **CPS implementor** | 1, 2, 4, 7, 8, 9, 10 | 12, 13, 14, 15, 24 |
| **CDS implementor** | 1, 2, 4, 7, 8, 9, 10 | 12, 13, 14, 16, 24 |
| **Registry implementor** | 1, 2, 4, 9, 10 | 12, 13, 24, 25 |
| **Domain schema pack author** | 1, 2, 4, 6 | 20, 21, 22 |
| **Network operator** | 1, 2, 4, 5, 6 | 13, 22, 24, 25 |
