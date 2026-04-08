# Beckn Protocol Communication
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./22_Communication_Protocol_RFC.md

## 1.3 Implementation report
- To be published by implementation working group.

## 1.4 Stress Test Report
- To be published by testing and certification working group.

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Beckn Protocol contributors.

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-023%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-023%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-023%22

## 1.8 Errata
- To be published.

<!-- TOC START -->
## Table of Contents

  - [CWG Working Draft - 2026-03-27](#cwg-working-draft-2026-03-27)
- [1. Document Details](#1-document-details)
  - [1.1 Version History](#11-version-history)
  - [1.2 Latest editor's draft](#12-latest-editors-draft)
  - [1.3 Implementation report](#13-implementation-report)
  - [1.4 Stress Test Report](#14-stress-test-report)
  - [1.5 Editors](#15-editors)
  - [1.6 Authors](#16-authors)
  - [1.7 Feedback](#17-feedback)
    - [1.7.1 Issues](#171-issues)
    - [1.7.2 Discussions](#172-discussions)
    - [1.7.3 Pull Requests](#173-pull-requests)
  - [1.8 Errata](#18-errata)
- [2. Context](#2-context)
  - [Abstract](#abstract)
  - [1. Context](#1-context)
  - [2. Core Communication Properties](#2-core-communication-properties)
    - [2.1 Server-to-Server](#21-server-to-server)
    - [2.2 Asynchronous](#22-asynchronous)
    - [2.3 Digitally Signed](#23-digitally-signed)
  - [3. Communication Flows](#3-communication-flows)
    - [3.1 Discovery: BAP → DS](#31-discovery-bap-ds)
    - [3.2 Catalog Publication: BPP → PS](#32-catalog-publication-bpp-ps)
    - [3.3 Transaction: BAP ↔ BPP](#33-transaction-bap-bpp)
    - [3.4 Status Updates (Multiple Callbacks)](#34-status-updates-multiple-callbacks)
  - [4. Callback Naming Convention](#4-callback-naming-convention)
  - [5. Comparison with legacy pre-v2](#5-comparison-with-legacy-pre-v2)
  - [6. Conformance Requirements](#6-conformance-requirements)
  - [7. References](#7-references)
  - [8. Changelog](#8-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):** Ravi Prakash (Beckn Foundation)  
**Created:** 2021-12-10  
**Updated:** 2026-02-01  
**Conformance impact:** Major (replaces legacy gateway-based communication model with PS/DS model)  
**Security/privacy implications:** All communication is server-to-server and digitally signed. No client-side exposure of protocol messages.  
**Replaces / Relates to:** Adapted and updated from BECKN-003 (legacy pre-v2). Replaces legacy gateway multicast section with PS/DS flows.

---

## Abstract

This RFC defines the communication model for Beckn Protocol v2. All network communication is server-to-server and asynchronous. Requests are acknowledged immediately with an `Ack`, and actual responses arrive later as callback API calls. Discovery is routed through the DS (not legacy gateway multicast). Post-discovery transactions are routed directly between BAP and BPP.

---

## 1. Context

Beckn-enabled networks have multiple entities communicating with each other via standard protocol APIs. The communication model defines who talks to whom, in what sequence, and with what guarantees.

---

## 2. Core Communication Properties

### 2.1 Server-to-Server

All Beckn protocol communication is between server processes. Client applications (mobile apps, web browsers) interact with the BAP's own backend — they are not directly involved in any protocol message exchange.

### 2.2 Asynchronous

All API calls are asynchronous. The immediate response in a session is an `Ack` — receipt confirmation only. The actual response arrives in a separate session as a callback.

### 2.3 Digitally Signed

Every message is digitally signed by the sender. See [14_Signing_Beckn_APIs_in_HTTP.md](./14_Signing_Beckn_APIs_in_HTTP.md).

---

## 3. Communication Flows

### 3.1 Discovery: BAP → DS

```
BAP                           DS
 │── GET /discover ────►│
 │◄── 200 Ack ────────────────│
 │                             │── query index
 │◄── POST /on_discover ─│
 │── 200 Ack ────────────────►│
```

1. BAP sends a signed `RequestContainer` (action: `discover`) to DS.
2. DS immediately responds with `Ack`.
3. DS executes the query against its index.
4. DS sends results as a `CallbackContainer` (action: `on_discover`) to BAP.
5. BAP responds with `Ack`.

### 3.2 Catalog Publication: BPP → PS

```
BPP                           PS
 │── POST /catalog/publish ─────►│
 │◄── 200 Ack ─────────────────│
 │                              │── normalize & forward to DS
```

1. BPP sends a signed `RequestContainer` (action: `publish`) to PS.
2. PS immediately responds with `Ack`.
3. PS normalizes and forwards the catalog graph to DS asynchronously.
4. No callback to BPP is required for standard publications.

### 3.3 Transaction: BAP ↔ BPP

Post-discovery, BAP communicates directly with BPP for all transaction actions.

```
BAP                            BPP
 │── POST /select ──────►│
 │◄── 200 Ack ─────────────────│
 │◄── POST /on_select ───│
 │── 200 Ack ────────────────►│
```

The same pattern applies for: `init`/`on_init`, `confirm`/`on_confirm`, `status`/`on_status`, `cancel`/`on_cancel`, `update`/`on_update`, `rate`/`on_rate`.

### 3.4 Status Updates (Multiple Callbacks)

For `status` / `on_status`, a BPP MAY send multiple `on_status` callbacks after the initial request. The BPP does not wait for the BAP to poll — it pushes updates asynchronously as the fulfillment state changes.

```
BAP                            BPP
 │── POST /status ──────►│
 │◄── 200 Ack ─────────────────│
 │◄── POST /on_status ───│  (first status update)
 │── 200 Ack ────────────────►│
 │◄── POST /on_status ───│  (second status update, later)
 │── 200 Ack ────────────────►│
```

---

## 4. Callback Naming Convention

The callback action name is always the request action name prefixed with `on_`:

| Request | Callback |
|---|---|
| `discover` | `on_discover` |
| `select` | `on_select` |
| `init` | `on_init` |
| `confirm` | `on_confirm` |
| `status` | `on_status` |
| `cancel` | `on_cancel` |
| `update` | `on_update` |
| `rate` | `on_rate` |
| `publish` | _(no standard callback)_ |

---

## 5. Comparison with legacy pre-v2

| Aspect | legacy pre-v2 | v2.0.x |
|---|---|---|
| Discovery routing | BAP → legacy gateway → BPPs (multicast) | BAP → DS (index) |
| legacy gateway gateway | Required for discovery | Removed |
| legacy gateway signature header | `legacy-gateway-signature header` | Removed |
| Catalog updates | Pull (triggered by `discover`) | Push (BPP → PS, continuous) |
| Transaction routing | BAP → legacy gateway → BPP | BAP → BPP (direct) |

---

## 6. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-015-01 | All API calls MUST be server-to-server | MUST |
| CON-015-02 | All API calls MUST be asynchronous (immediate `Ack`, later callback) | MUST |
| CON-015-03 | Discovery queries MUST be sent to DS, not directly to BPPs | MUST |
| CON-015-04 | BPPs MUST publish catalogs to PS | MUST |
| CON-015-05 | Transaction actions MUST be sent directly from BAP to BPP | MUST |
| CON-015-06 | BPPs MAY send multiple `on_status` callbacks for a single `status` request | MAY |

---

## 7. References

- [21_Communication_Protocol.md](./21_Communication_Protocol.md)
- [09_Discovery_Architecture.md](./09_Discovery_Architecture.md)
- [14_Signing_Beckn_APIs_in_HTTP.md](./14_Signing_Beckn_APIs_in_HTTP.md)

---

## 8. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2021-12-10 | Ravi Prakash | Initial draft (BECKN-003 legacy pre-v2) |
| Draft-02 | 2026-02-01 | — | v2 update: removed legacy gateway multicast, replaced with PS/DS flows |
