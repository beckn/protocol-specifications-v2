# Beckn Protocol Communication

**Status:** Draft  
**Author(s):** Ravi Prakash (Beckn Foundation)  
**Created:** 2021-12-10  
**Updated:** 2026-02-01  
**Conformance impact:** Major (replaces BG-based communication model with CPS/CDS model)  
**Security/privacy implications:** All communication is server-to-server and digitally signed. No client-side exposure of protocol messages.  
**Replaces / Relates to:** Adapted and updated from BECKN-003 (v1.x). Replaces BG multicast section with CPS/CDS flows.

---

## Abstract

This RFC defines the communication model for Beckn Protocol v2. All network communication is server-to-server and asynchronous. Requests are acknowledged immediately with an `Ack`, and actual responses arrive later as callback API calls. Discovery is routed through the CDS (not BG multicast). Post-discovery transactions are routed directly between BAP and BPP.

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

Every message is digitally signed by the sender. See [10_Signing_Beckn_APIs_in_HTTP.md](./10_Signing_Beckn_APIs_in_HTTP.md).

---

## 3. Communication Flows

### 3.1 Discovery: BAP → CDS

```
BAP                           CDS
 │── GET /beckn/discover ────►│
 │◄── 200 Ack ────────────────│
 │                             │── query index
 │◄── POST /beckn/on_discover ─│
 │── 200 Ack ────────────────►│
```

1. BAP sends a signed `RequestContainer` (action: `discover`) to CDS.
2. CDS immediately responds with `Ack`.
3. CDS executes the query against its index.
4. CDS sends results as a `CallbackContainer` (action: `on_discover`) to BAP.
5. BAP responds with `Ack`.

### 3.2 Catalog Publication: BPP → CPS

```
BPP                           CPS
 │── POST /beckn/publish ─────►│
 │◄── 200 Ack ─────────────────│
 │                              │── normalize & forward to CDS
```

1. BPP sends a signed `RequestContainer` (action: `publish`) to CPS.
2. CPS immediately responds with `Ack`.
3. CPS normalizes and forwards the catalog graph to CDS asynchronously.
4. No callback to BPP is required for standard publications.

### 3.3 Transaction: BAP ↔ BPP

Post-discovery, BAP communicates directly with BPP for all transaction actions.

```
BAP                            BPP
 │── POST /beckn/select ──────►│
 │◄── 200 Ack ─────────────────│
 │◄── POST /beckn/on_select ───│
 │── 200 Ack ────────────────►│
```

The same pattern applies for: `init`/`on_init`, `confirm`/`on_confirm`, `status`/`on_status`, `cancel`/`on_cancel`, `update`/`on_update`, `rating`/`on_rating`.

### 3.4 Status Updates (Multiple Callbacks)

For `status` / `on_status`, a BPP MAY send multiple `on_status` callbacks after the initial request. The BPP does not wait for the BAP to poll — it pushes updates asynchronously as the fulfillment state changes.

```
BAP                            BPP
 │── POST /beckn/status ──────►│
 │◄── 200 Ack ─────────────────│
 │◄── POST /beckn/on_status ───│  (first status update)
 │── 200 Ack ────────────────►│
 │◄── POST /beckn/on_status ───│  (second status update, later)
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
| `rating` | `on_rating` |
| `publish` | _(no standard callback)_ |

---

## 5. Comparison with v1.x

| Aspect | v1.x | v2.0.x |
|---|---|---|
| Discovery routing | BAP → BG → BPPs (multicast) | BAP → CDS (index) |
| BG gateway | Required for discovery | Removed |
| BG signature header | `X-Gateway-Authorization` | Removed |
| Catalog updates | Pull (triggered by `search`) | Push (BPP → CPS, continuous) |
| Transaction routing | BAP → BG → BPP | BAP → BPP (direct) |

---

## 6. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-015-01 | All API calls MUST be server-to-server | MUST |
| CON-015-02 | All API calls MUST be asynchronous (immediate `Ack`, later callback) | MUST |
| CON-015-03 | Discovery queries MUST be sent to CDS, not directly to BPPs | MUST |
| CON-015-04 | BPPs MUST publish catalogs to CPS | MUST |
| CON-015-05 | Transaction actions MUST be sent directly from BAP to BPP | MUST |
| CON-015-06 | BPPs MAY send multiple `on_status` callbacks for a single `status` request | MAY |

---

## 7. References

- [7_Communication_Protocol.md](./7_Communication_Protocol.md)
- [14_Discovery_Architecture.md](./14_Discovery_Architecture.md)
- [10_Signing_Beckn_APIs_in_HTTP.md](./10_Signing_Beckn_APIs_in_HTTP.md)

---

## 8. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2021-12-10 | Ravi Prakash | Initial draft (BECKN-003 v1.x) |
| Draft-02 | 2026-02-01 | — | v2 update: removed BG multicast, replaced with CPS/CDS flows |
