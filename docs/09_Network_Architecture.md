# Network Architecture

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.0)

---

## 1. Overview

A Beckn v2 network is a set of independently operated platforms that communicate with each other using the Beckn Protocol transport envelope. Each platform implements a specific **actor role**. The network has no central broker: all communication is peer-to-peer, mediated only by a shared registry for identity and key resolution.

---

## 2. Actor Roles

### 2.1 Beckn Application Platform (BAP)

A BAP is a buyer-side platform. It represents the consumer's interface to the network. A BAP:

- Sends `RequestContainer` messages to DS (for discovery) and BPPs (for transactions).
- Implements a callback endpoint to receive `CallbackContainer` responses.
- Resolves BPP endpoints and signing keys via the DeDi-compliant Registry.

Examples: consumer apps, aggregator platforms, agent interfaces, IoT clients.

### 2.2 Beckn Provider Platform (BPP)

A BPP is a seller-side platform. It represents a provider's catalog, transaction engine, and fulfillment logic. A BPP:

- Publishes catalog updates to the PS.
- Receives `RequestContainer` messages from BAPs and responds via `CallbackContainer` callbacks.
- Registers itself in the DeDi-compliant Registry with its endpoint, signing keys, and capabilities.

Examples: e-commerce backends, mobility providers, logistics platforms, healthcare providers.

### 2.3 Publishing Service (PS)

A PS is the catalog ingestion layer. It:

- Accepts asynchronous catalog push publications from BPPs (as `RequestContainer` messages on the `publish` endpoint).
- Normalizes catalog data against the Beckn v2 `core_schema` and domain schema packs.
- Forwards indexed catalog graphs to one or more DS instances.

A network may operate multiple PS instances. A BPP may publish to more than one PS.

### 2.4 Discovery Service (DS)

A DS is the discovery query engine. It:

- Maintains a continuously updated index of `Catalog` / `Item` / `Offer` graphs received from PS.
- Answers discovery queries from BAPs (on the `discover` endpoint), returning matching catalog subsets.
- Does **not** multicast to BPPs; all discovery is served from its own index.

### 2.5 DeDi-Compliant Registry

The Registry is the identity and trust anchor of the network. It:

- Stores participant records (BAP, BPP, PS, DS) as [DeDi](https://dedi.global)-compliant directory entries.
- Exposes DeDi-standard APIs for participant registration (`subscribe`), key publication, and lookup (`lookup`).
- Allows any participant to resolve a `subscriberId` to its public signing key, endpoint URL, and capabilities.

In legacy pre-v2 this was a bespoke Beckn registry. In v2 it is a DeDi-compliant public directory.

---

## 3. Core → Domain → Network Layering

Beckn v2 adopts an explicit three-layer governance and schema model:

```
┌─────────────────────────────────────────────────────────┐
│  Network Layer                                          │
│  Network-specific constraints, regional policies,       │
│  mandatory schema pack lists, DS configuration         │
├─────────────────────────────────────────────────────────┤
│  Domain Layer                                           │
│  Domain schema packs, domain IGs, sector-specific       │
│  vocabulary bindings and conformance guidance           │
├─────────────────────────────────────────────────────────┤
│  Core Layer                                             │
│  Transport envelope (this repo), core_schema,           │
│  DeDi registry contract, PS/DS interface contracts    │
└─────────────────────────────────────────────────────────┘
```

**Key constraint:** Higher layers may be _stricter_ than lower layers. They MUST NOT contradict or redefine core semantics.

---

## 4. Component Interaction Model

### 4.1 Catalog Publication Flow (BPP → PS → DS)

```
BPP ──publish(catalog)──► PS ──normalize & index──► DS
```

1. BPP sends a `RequestContainer` with a `publish` action to PS.
2. PS normalizes the payload against `core_schema` and domain schema packs.
3. PS forwards `Item` / `Offer` / `Provider` graphs to DS for indexing.
4. This flow runs continuously and is decoupled from any BAP request.

### 4.2 Discovery Flow (BAP → DS)

```
BAP ──discover(query)──► DS ──catalog subset──► BAP
```

1. BAP sends a `RequestContainer` with a `discover` action to DS.
2. DS resolves, scores, and returns matching catalog data.
3. BAP receives results as a `CallbackContainer` (or synchronously, depending on network policy).

### 4.3 Transaction Flow (BAP → BPP)

```
BAP ──select/init/confirm/...──► BPP ──on_select/on_init/on_confirm/...──► BAP
```

Post-discovery, BAP communicates directly with BPP for all transactional actions (`select`, `init`, `confirm`, `status`, `cancel`, `update`, `rate`).

### 4.4 Registry Lookup Flow

```
BAP / BPP ──lookup(subscriberId)──► DeDi Registry ──{endpoint, publicKey}──► caller
```

Before sending a request, a participant resolves the recipient's endpoint and public key from the registry. Before accepting a request, a participant resolves the sender's public key to verify the Beckn Signature.

---

## 5. Network Topology Diagram

```
                    ┌─────────────────┐
                    │  DeDi Registry  │
                    └────────┬────────┘
                             │ lookup / subscribe
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌──────▼──────┐    ┌──────▼──────┐
    │    BAP    │     │     DS     │    │     BPP     │
    └─────┬─────┘     └──────▲──────┘    └──────┬──────┘
          │                  │                  │
          │ discover ────────┘        publish   │
          │                                     ▼
          │                             ┌───────────────┐
          │                             │      PS      │
          │                             └───────────────┘
          │
          │ select/init/confirm/...
          └──────────────────────────────────────► BPP
                                                  (direct)
```

---

## 6. Comparison with legacy pre-v2 Architecture

| Aspect | legacy pre-v2 | v2.0.x |
|---|---|---|
| Discovery | legacy gateway multicast `discover` to all BPPs | BAP queries DS index |
| Catalog updates | Pull on demand (discover triggers BPP response) | BPP pushes asynchronously to PS |
| Registry | Bespoke Beckn `lookup`/`subscribe` | DeDi-compliant public directory |
| Schema | OpenAPI/JSON Schema, ad-hoc fields | JSON-LD + schema.org, typed graphs |
| Endpoint model | Per-action endpoints (`/discover`, `/confirm`, etc.) | Universal `/discover, /on_discover, /select, /on_select, and related action endpoints` |

---

## 7. Further Reading

- [02_Communication_Protocol.md](./02_Communication_Protocol.md) — how messages flow between actors
- [12_Discovery_Architecture.md](./12_Discovery_Architecture.md) — PS and DS in depth
- [10_Registry_and_Identity.md](./10_Registry_and_Identity.md) — DeDi registry in depth
- [RFC-002: Core API Envelope](./03_Core_API_Envelope.md)
