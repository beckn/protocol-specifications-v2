# Discovery Architecture

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.0)

---

## 1. Overview

Discovery in Beckn v2 is **catalog-first and index-based**. BPPs push catalog updates asynchronously to a Publishing Service (PS), which normalizes and forwards them to a Discovery Service (DS). BAPs query the DS index for discovery — no real-time multicast to BPPs occurs.

This replaces the legacy pre-v2 legacy gateway layer (legacy gateway) multicast model entirely.

---

## 2. Historical Context: legacy pre-v2 legacy gateway layer

In legacy pre-v2, a legacy gateway layer (legacy gateway) sat between BAPs and BPPs:

1. BAP sends `discover` to legacy gateway.
2. legacy gateway looks up the registry for all BPPs matching the domain.
3. legacy gateway multicasts `discover` to all (or policy-filtered) BPPs simultaneously.
4. BPPs respond asynchronously with `on_discover` callbacks to the BAP.

**Limitations:**
- Discovery latency scaled with the number of BPPs.
- BPPs could not pre-compute or cache responses.
- Every BAP discover triggered live network fan-out.
- No clear separation between catalog management and query execution.

The concept of a "Search Provider" — an intermediate that pre-indexes BPP catalogs — was explored in legacy pre-v2 (see the original BECKN-011 draft). PS + DS in v2 is the full realization of that concept.

---

## 3. Publishing Service (PS)

### 3.1 Role

The PS is the catalog ingestion and normalization layer. It accepts catalog push publications from BPPs and prepares them for indexing.

### 3.2 PS Responsibilities

- Accept `RequestContainer` messages with a `publish` action from BPPs.
- Validate and normalize the catalog payload against `core_schema` and applicable domain schema packs.
- Deduplicate and merge incremental updates using stable item identifiers and timestamps.
- Forward normalized `Item` / `Offer` / `Provider` / `Catalog` JSON-LD graphs to one or more DS instances.
- Acknowledge successful publication with `Ack` (HTTP 200).

### 3.3 BPP Publication Flow

```
BPP                           PS
 │                              │
 │── POST /catalog/publish ──────►│
 │◄── 200 Ack ─────────────────│
 │                              │
 │                              │── normalize & validate
 │                              │── forward to DS
 │                              │
```

### 3.4 Publication Payload

A BPP sends a `RequestContainer` where `context.action = "publish"` and `message` contains the catalog payload as a JSON-LD graph conforming to `core_schema`:

```json
{
  "context": {
    "action": "publish",
    "bppId": "bpp.example.com",
    ...
  },
  "message": {
    "@context": ["https://schema.beckn.io/core/v2/context.jsonld", "..."],
    "@type": "Catalog",
    "provider": { ... },
    "items": [ { ... }, { ... } ],
    "offers": [ { ... } ]
  }
}
```

### 3.5 Incremental Updates

BPPs SHOULD send incremental updates (changed/new/deleted items) rather than full catalog snapshots. A publication containing only deleted items MUST include a marker (e.g., `"status": "DISABLED"`) to allow PS/DS to remove those items from the index.

---

## 4. Discovery Service (DS)

### 4.1 Role

The DS is the discovery query engine. It maintains a continuously updated index of catalog data received from PS and answers discovery queries from BAPs.

### 4.2 DS Responsibilities

- Maintain a read-optimized index of `Catalog` / `Item` / `Offer` graphs.
- Accept `RequestContainer` messages with a `discover` action from BAPs.
- Execute discovery queries with network-configurable ranking, filtering, and relevance scoring.
- Return matching catalog subsets to BAPs as `CallbackContainer` responses.
- Support both asynchronous (`on_discover` callback) and synchronous response modes per network policy.

### 4.3 BAP Discovery Flow

```
BAP                           DS
 │                              │
 │── GET /discover ──────►│
 │◄── 200 Ack ─────────────────│  (immediate receipt)
 │                              │
 │                              │── query index
 │                              │
 │◄── POST /on_discover ─│  (async callback with results)
 │── 200 Ack ──────────────────►│
 │                              │
```

### 4.4 Discovery Query

```json
{
  "context": {
    "action": "discover",
    "bapId": "bap.example.com",
    "bapUri": "https://bap.example.com",
    ...
  },
  "message": {
    "@type": "Intent",
    "item": {
      "@type": "Item",
      "name": "fresh vegetables"
    },
    "fulfillment": {
      "location": { "gps": "12.9716,77.5946" }
    }
  }
}
```

---

## 5. PS–DS Relationship

A network may deploy:
- **One PS, one DS**: simplest topology for small networks.
- **Multiple PS → one DS**: multiple ingestion points feeding a single index.
- **One PS → multiple DS**: single ingestion, multiple geographically distributed query engines.
- **Multiple PS → multiple DS**: fully distributed, high-availability topology.

A BPP chooses which PS instance(s) to publish to. Network policy governs which PS instances are authoritative for a given domain or region.

---

## 6. Comparison with legacy pre-v2

| Aspect | legacy pre-v2 legacy gateway | v2.0.x PS + DS |
|---|---|---|
| Catalog update trigger | On BAP `discover` (pull) | BPP push (continuous, async) |
| Discovery execution | Real-time multicast to all BPPs | Index query on DS |
| Latency | Depends on slowest BPP | Sub-second index lookup |
| Scalability | Fan-out grows with BPP count | Decoupled; index scales independently |
| BPP availability dependency | BPP must be online for discovery | BPP can be offline; index is always available |

---

## 7. Further Reading

- [10_Cataloging_Service.md](./10_Cataloging_Service.md) — normative PS spec (RFC)
- [11_Discovery_Service.md](./11_Discovery_Service.md) — normative DS spec (RFC)
- [06_Universal_Value_Exchange_Fabric_Infrastructure.md](./06_Universal_Value_Exchange_Fabric_Infrastructure.md) — overall network topology
