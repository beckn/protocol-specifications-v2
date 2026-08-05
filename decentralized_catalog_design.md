# Decentralized Catalog

## Design Discussion Draft

**Status:** Discussion draft **Purpose:** Explore replacing the centralized Cataloging Service (CS) with a model where each Provider Node (PN) self-hosts its catalog data, anchored to its dedi.global identity, and Discovery Services (DS) crawl/index it directly. For Working Group discussion, not a decision.  
---

## 1\. The model being replaced

Today (`api/v2.0.0/beckn.yaml`), the CS is a mandatory Fabric building block (§ "Required Infrastructure Building Blocks") that does four jobs:

| Endpoint | Job |
| :---- | :---- |
| `POST /catalog/publish` → `/catalog/on_publish` | PN pushes `Catalog` objects to the CS; CS validates, indexes, and reports per-catalog `ACCEPTED / REJECTED / PARTIAL` |
| `POST /catalog/subscription` | DS declares interest (`networkIds` \+ `schemaTypes`) |
| `POST /catalog/push` | CS pushes matching updates to subscribed DSes |
| `POST /catalog/search`, `POST /catalog/pull` → `/catalog/on_pull` | DS queries/bulk-retrieves the CS's index (sync search; async FULL/INCREMENTAL pull with `downloadManifest` for large payloads) |

`/discover` ↔ `/on_discover` (CN↔DS) sits on top of whatever the DS has indexed, and is **unaffected** by anything in this document — the CS is purely how the DS's index gets populated.

The `Catalog` object itself (`id`, `descriptor`, `provider`, `resources[]`/`offers[]`, `validity`) and the `publishDirectives` concept (`catalogType` MASTER/REGULAR, `updateMode` FULL/MERGE, `resourceDirectives[].extends.masterResourceId`, `variant`) are reused as-is below — this proposal changes *where these objects live and how they get to a DS*, not their shape.

---

## 2\. Why decentralize

- The CS is a single piece of mandatory shared infrastructure every PN must trust and depend on for a *fabric-wide* concern (catalog reach), which cuts against the fabric's stated principle that shared "Threads" should be a species of one *only* where unavoidable (identity, registry). Cataloging doesn't need a shared write path — only a shared way to *find* things.  
- Providers already run infrastructure (websites, CDNs, git repos). Forcing a second, protocol-specific write path (`/catalog/publish`) duplicates that.  
- It removes a chokepoint: CS downtime, policy, or rate limits currently gate every PN's visibility on every network it participates in.

The trade-off, addressed throughout §5–§8: a self-hosted model gives up the CS's synchronous validation feedback and its single trusted mirror, and must re-derive integrity/authenticity guarantees without a transport-level signature on every write.

### Key considerations

1. **The Fabric hosts no catalog data.** Catalogs always live at the edge — on infrastructure the PN itself controls — never inside a Fabric-operated service.  
2. **Catalog quality is the edge node's responsibility, not the Fabric's.**  
   - NFH (the Fabric) is not a validating authority.  
   - Edge nodes own the quality of what they publish or receive, aided by optional tooling (e.g. a schema validator, §5) rather than a mandatory check.  
   - Some channel for quality-control feedback to reach the publisher after the fact is needed — see the open question in §9 on whether a `catalog/on_index`\-style notice should be standardized.  
3. **Lifecycle: account for how updates reach the network.** Publishing is only half the problem — DSes also need a defined way to learn that a change happened. Worked through in the update & synchronization flow (§7).  
4. **Data integrity.** Catalog consumers must be able to rely on the integrity of a catalog and trust that it has not been tampered with, in transit or at rest.  
5. **Referential integrity.** Cross-references between catalogs must stay resolvable once catalogs are split across many independently-hosted files  
6. **Uniqueness.**   
7. **Schema extensibility must keep working unmodified.** The extension points the protocol already supports — domain-specific `resourceAttributes`/`offerAttributes` via the `Attributes` bag, and JSON-LD `@context`/`@type` — are unaffected by this design.   
8. **Population-scale support.** The design must hold up at the scale of a large production network — potentially thousands of PNs and catalogs, with millions of resources in aggregate — without every DS re-fetching and re-verifying everything on every crawl cycle. 

---

## 4\. New artifacts

### 

### 4.1 No Beckn-specific manifest — reuse the DeDi manifest

A signed `/.well-known/dedi.json`, served under the domain's TLS at a fixed path (RFC 8615), declaring the publisher's current key(s) and listing the registries (files) it offers. A Beckn PN publishing this way is simply a conformant DeDi publisher; its catalogs are additional `files[]` entries, not a second artifact.

```json
// /.well-known/dedi.json — DeDi's own manifest format, unmodified by Beckn
{
  "dedi_version": "0.1",
  "type": "dedi-manifest",
  "domain": "bpp.techmart.com",
  "keys": [
    { "kid": "key-001", "kty": "OKP", "crv": "Ed25519", "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo" }
  ],
  "updated_at": "2026-07-01T09:00:00Z",
  "next_update": "2026-07-15T10:00:00Z",
  "files": [
    { "registry": "CAT-TECHMART-2026",
      "url": "https://techmart.com/dedi/CAT-TECHMART-2026.dedi.json",
      "digest": "sha-256:9f2c1d4e7a8b0c3d5e6f70819293a4b5c6d7e8f90a1b2c3d4e5f60718293aebae",
      "schema": "https://schema.nfh.global/dedi/BecknCatalogRecord/1.0.0/schema.json" },
    { "registry": "CAT-TECHMART-OFFERS-2026",
      "url": "https://techmart.com/dedi/CAT-TECHMART-OFFERS-2026.dedi.json",
      "digest": "sha-256:5b1a2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f0",
      "schema": "https://schema.nfh.global/dedi/BecknCatalogRecord/1.0.0/schema.json" }
  ],
  "proof": { "verification_method": "key-001", "canonicalization": "JCS", "jws": "..." }
}
```

Consequence: **no new dedi-record attribute at all.** A DS that already knows a PN's domain (from `bppUri`/`subscriber_id`) fetches `https://{domain}/.well-known/dedi.json` directly — zero registry round-trips to *locate* anything. 

### 4.2 Granularity: one DeDi file per catalog

One Beckn `Catalog` \= one DeDi file \= one DeDi `registry`. Not one file per network, and not one record per resource/offer.

Rationale: DeDi already tracks change-detection (via the manifest's `digest`), freshness (`next_update`), and lifecycle (`registry.state`) at the whole-file level. A DS already treats a catalog as one thing to fetch, verify, and index in a single pass — matching that boundary to DeDi's own unit of change avoids inventing a second, competing notion of "atomic unit."

### 4.3 What goes inside the file

DeDi's own schemas (`dedi-file.schema.json`, `dedi-manifest.schema.json`) are closed — `additionalProperties: false` — at every level except `records[].details`, which is deliberately open, its shape declared only by the registry's own `schema`. That has one direct consequence here: **`publishDirectives` and `schemaTypes` cannot be added to the DeDi file's top level, or to its `registry` block** — there is no room for them there, and this design doesn't propose changing DeDi's own schema. They both have to live inside `details`.

Given that, and given the `Catalog` schema itself must not change (it's core, CWG-governed, and used unmodified across `/discover`↔`/on_discover`), the cleanest placement is a wrapper — `details = { catalog, schemaTypes, publishDirectives }` — that leaves `Catalog` untouched and reuses `publishDirectives` exactly as `beckn.yaml`'s `CatalogPublishAction` already defines it (`catalogId`, `visibleTo`, `catalogType`, `updateMode`, `resourceDirectives`), rather than inventing a renamed or reshaped equivalent:

```json
{
  "dedi_version": "0.1",
  "type": "dedi-file",
  "source_url": "https://techmart.com/dedi/CAT-TECHMART-2026.dedi.json",
  "next_update": "2026-07-15T10:00:00Z",

  "publisher": {
    "domain": "bpp.techmart.com",
    "key": { "kid": "key-001", "kty": "OKP", "crv": "Ed25519", "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo" }
  },
  "namespace": "bpp.techmart.com",

  "registry": {
    "name": "CAT-TECHMART-2026",
    "schema": "https://schema.nfh.global/dedi/BecknCatalogRecord/1.0.0/schema.json",
    "state": "live",
    "updated_at": "2026-07-01T00:00:00Z"
  },

  "records": [
    {
      "record_name": "CAT-TECHMART-2026",
      "details": {
        "catalog": {
          "id": "CAT-TECHMART-2026",
          "descriptor": { "name": "TechMart Product Catalog" },
          "provider": { "id": "provider-techmart-001", "descriptor": { "name": "TechMart Electronics" } },
          "resources": [ "...unchanged Resource objects..." ],
          "offers": [ "...unchanged Offer objects..." ],
          "validity": { "startDate": "2026-01-01", "endDate": "2026-12-31" },
          "isActive": true
        },
        "schemaTypes": ["https://schema.nfh.global/retail/schema/1.1.0/context.jsonld"],
        "publishDirectives": [
          {
            "catalogId": "CAT-TECHMART-2026",
            "visibleTo": ["retail-network", "hyperlocal-network"],
            "catalogType": "REGULAR",
            "updateMode": "MERGE",
            "resourceDirectives": [
              { "resourceId": "ITEM-LAPTOP-XPS-15-TECHMART", "extends": { "masterResourceId": "MASTER-LAPTOP-XPS-15" } }
            ]
          }
        ]
      }
    }
  ],

  "proof": { "verification_method": "key-001", "canonicalization": "JCS", "jws": "..." }
}
```

`publishDirectives` stays an **array**, exactly as `beckn.yaml` defines it — that schema was built to batch directives for many catalogs in one API call. Here, one DeDi file always carries exactly one catalog, so the array holds exactly one entry, matched by its own `catalogId`. Nothing about the schema itself changes; only its container does.

`schemaTypes` is **not** part of `beckn.yaml`'s `publishDirectives` (it comes from `CatalogSubscribeAction`/`CatalogSearchAction` instead), so it's kept as its own sibling under `details` rather than folded into `publishDirectives` — reusing that schema "as is" means not extending it with fields it was never defined to carry.

`registry.name` and `records[0].record_name` are both set to the `catalogId`. With one catalog per file there is exactly one record, so this is slightly redundant, but it costs nothing and keeps the record self-describing if it's ever extracted or relocated without its surrounding file.

### 4.4 The `visibleTo` / `schemaType` pre-fetch filtering trade-off

DeDi's manifest `files[]` entries carry a `schema` field explicitly meant to allow "discovery/filtering without fetching the file" — but that's the *structural* schema (here, always the same `BecknCatalogRecord` schema for every Beckn catalog file), not a Beckn *domain* schema type or a network scope. Neither `publishDirectives[].visibleTo` nor `schemaTypes` have anywhere to live at the manifest level, because `files[]` items are a closed schema too — only `registry`, `url`, `digest`, `schema`, `state`.

Practical consequence: **a DS cannot learn which network(s) or domain a catalog belongs to without fetching it.** Two ways to handle that:

- **Default — fetch-then-filter.** The DS fetches every catalog file listed in a PN's manifest that it hasn't already fetched (skipping unchanged ones via `digest`), reads `details.publishDirectives[0].visibleTo` and `details.schemaTypes`, and discards what it doesn't care about. Always correct, needs no new convention, costs one fetch per catalog per DS the first time it's seen — never again, since digest-based skip applies from then on.  
- **Optional accelerant — alias entries in the manifest.** A PN that wants pre-fetch filtering can list the same `url` \+ `digest` more than once under different `registry` names carrying a network prefix — e.g. `"retail-network:CAT-TECHMART-2026"` and `"hyperlocal-network:CAT-TECHMART-2026"`, both pointing at the identical file. A DS that only cares about one network can pattern-match the prefix and skip entries that don't match, at the cost of the PN maintaining one manifest line per network a multi-network catalog serves. This is a non-normative convention, in the same spirit as DeDi's own filename conventions ("aid glob matching... and nothing more") — never load-bearing for trust, purely a discovery shortcut.

**Recommendation:** fetch-then-filter as the required baseline; the aliasing trick as an optional, per-PN choice. Whether the alias convention is worth standardizing at all is flagged in §9.

### 4.5 Signing

Rather than reusing Beckn's HTTP `Signature` scheme (three-line canonical string, `keyId` string format) applied to bytes at rest, this design adopts DeDi's own signing convention directly — a Beckn PN publishing this way is a DeDi publisher and needs only one at-rest signing scheme, not two.

- **Canonicalization:** JCS (RFC 8785\) over the document with `proof` removed.  
- **Signature:** detached JWS (RFC 7515); `proof.verification_method` names the signing key's `kid`; algorithm matches the key (`EdDSA` for the Ed25519 keys the Registry already uses).  
- **Key material:** the same Ed25519 keys already registered for the PN's fabric identity, embedded as a public JWK in `publisher.key`, declared authoritative via the domain's `/.well-known/dedi.json` `keys[]` — the manifest is the trust anchor, `did:web`\-style (DeDi spec §6.1).

No new key material, no new registry concept, and no second signature format to maintain alongside whatever a PN already does for any other DeDi-published registry.

---

## 5\. Hosted Publish workflow (PN side)

1. **Prerequisite (unchanged):** PN has a namespace \+ registered Ed25519 key on the Registry.  
2. **Author** one or more `Catalog` JSON documents — same schema as today, no changes.  
3. **Host** them anywhere — own domain, GitHub, object storage. Prefer a location with immutable, addressable history (e.g. a GitHub commit SHA or a versioned object-store key) over a mutable "latest" path, so `updated_at`/`next_update` claims are independently auditable against host-side history.  
4. **Wrap each catalog as a DeDi file** (§4.3) — one file per catalog, `details = { catalog, schemaTypes, publishDirectives }`, `registry.state: "live"`.  
5. **Sign the file** — JCS canonicalization \+ detached JWS (§4.5).  
6. **List it in `/.well-known/dedi.json`** — add or update the corresponding `files[]` entry (`registry`, `url`, `digest`, `schema`), re-sign the manifest. There is no separate pointer-registration step: this is the PN's ordinary DeDi manifest, serving double duty for its identity keys and its catalogs.  
7. **On every content update:** edit the catalog file, bump `registry.updated_at`, recompute the manifest's `digest` for that entry, re-sign both. This *is* "publish" now — no API call.  
8. **Optional efficiency hint:** ping any DSes the PN already has a relationship with (a lightweight webhook) so they re-crawl sooner. This is a hint only — see §6, a DS MUST still fetch and verify from the source of truth; an unsolicited ping is never itself trusted.  
9. **Optional:** push a change notification to a queue/topic instead of (or in addition to) direct pings — see §7 for the full design, including how a DS discovers and subscribes to it.

### Quality control on publish

- **No synchronous gate replaces `/catalog/on_publish`** — there's no CS to reject a bad payload before it's "live." Recommended mitigation: a public, optional pre-publish validator (a hosted or CLI validator against the `BecknCatalogRecord` schema) a PN can run before publishing. Non-blocking, advisory.  
- **Freshness, not a version counter:** `next_update` bounds how long a copy may be trusted before re-fetch; `updated_at` advances only when content actually changes. A stale copy is detectable on its own terms — no monotonically-increasing version field to maintain or to guard against rollback.  
- **`registry.state: "inactive"`, not a bespoke tombstone field.** Retiring a catalog is expressed the same way DeDi expresses retiring any registry — one less piece of Beckn-specific vocabulary.  
- **Signing is the real quality gate:** an unsigned or invalidly-signed file fails DeDi's own verification step 2 (§6), which is the actual enforcement mechanism that stands in for CS validation today.

---

## 6\. Discovery workflow (DS side)

1. **Enumerate PNs** from each networkId registry the DS cares about (the same registry lookup already used to resolve `subscriber_url`) — this is the DS's crawl target list, replacing `POST /catalog/subscription` against a CS.  
2. **Fetch `https://{domain}/.well-known/dedi.json` directly** — no registry lookup is needed to locate it (§4.1). Compare each `files[].digest` against what's already indexed; fetch only entries that are new or changed.  
3. **Verify each fetched file end-to-end using DeDi's own 5-step procedure** (DeDi spec §7): (1) schema-check against `registry.schema`, (2) integrity — verify `proof.jws` against the file's embedded `publisher.key`, (3) authenticity — confirm that key is present in the manifest's `keys[]`, (4) freshness — `now ≤ next_update` for both file and manifest, (5) `registry.state == "live"`. Reject on any failure; do not index partial or unverified content.  
4. **Schema-validate `details.catalog`** against the `Catalog` schema specifically — a Beckn-specific check layered on top of DeDi's generic step 1, since `registry.schema` (`BecknCatalogRecord`) validates the wrapper shape but a DS still needs `id`/`descriptor`/`provider` and the resources/offers `anyOf` enforced on the nested `Catalog` object itself.  
5. **Check networkId standing:** confirm the PN's networkId registration isn't revoked (reusing the existing `subscriber_reference` revocation check from `Authentication_and_Trust.md` §CON-004-20) before trusting anything it publishes. DeDi's own verification has no notion of Beckn networkId membership — this check is Beckn-specific and stays.  
6. **Incremental re-crawl:** digest comparison (step 2\) plus, for large catalogs, the delta-file pattern (§7.1) — this absorbs the FULL/INCREMENTAL distinction `CatalogPullAction` used to express as an API parameter.  
7. **Track freshness independently:** record `lastVerifiedAt` (the DS's own last successful fetch) alongside the file's self-declared `next_update`. The two answer different questions — `next_update` is the publisher's own freshness *promise*, not proof the host is actually reachable; a DS that hasn't managed to re-verify within its own staleness window should drop or flag a catalog even if `next_update` hasn't technically lapsed.  
8. **Enforce a crawl budget:** per-host size caps and minimum re-crawl intervals, so one large or misbehaving host can't starve the DS's crawl loop or look like an amplification target.

### Quality control on discovery

Steps 3–5 above *are* the quality control layer — DeDi's own verification (identity binding, signature, freshness, registry state) plus Beckn's own additions (Catalog-schema validation, networkId standing) together substitute for the single synchronous "CS accepts or rejects" gate that exists today. The difference is that enforcement now happens independently at every DS rather than once, centrally — which means a malicious or malformed catalog can never be trusted by a conforming DS, but also means there's no single shared verdict; two DSes could, in principle, disagree if one has stricter validation than the other. That's an accepted trade-off of decentralization, not a gap to close.

---

## 7\. Update & synchronization flow (PN → DS)

The discovery workflow (§6) establishes how a DS fetches and verifies a PN's catalogs at all. This section covers the harder question layered on top of that baseline: once an update exists, how does it actually reach every DS that needs it — for one provider and one DS, and for the realistic case of many providers and many DSes?

### 7.1 What gets transferred: full file vs. incremental delta

- Every catalog file is now covered by the manifest's `digest` (§4.1) and its own `next_update`/`registry.updated_at` (§4.3). The minimum viable sync strategy needs no extra artifact: compare `digest` against what was last indexed, re-fetch and re-verify on change (§6, step 6). This MUST always work — it is the fallback of last resort under every pattern below.  
- For catalogs large enough that re-downloading the whole file on every change is wasteful (a MASTER catalog with thousands of resources, one price changing), the PN MAY additionally publish a delta document alongside the full file — e.g. `catalog-delta-<fromDigest>-<toDigest>.json` — listing only the `added`/`updated`/`removed` resource or offer IDs since a prior version. DeDi's own spec explicitly defers "sharding a very large registry across multiple files" as future work (§5.1 of the DeDi spec); a delta-file convention sits in exactly that gap without waiting on DeDi to define it, and should be revisited if/when DeDi standardizes sharding.  
- A DS already holding the prior `digest` fetches and applies the delta; one that doesn't (first crawl, or too many versions behind) falls back to the full file. Deltas are a pure optimization — a PN that never publishes them just gets re-crawled in full every time, which is correct, only less efficient. **Recommendation:** support both, delta-publishing OPTIONAL per catalog, full-file fetch always available as the guaranteed fallback.

  *How many deltas a PN should keep around* is a retention trade-off with no free answer. Too few (e.g. only the single most recent delta) means any DS that misses one cycle — a crawl outage, a slow re-poll — immediately falls back to a full fetch, which erases most of the benefit for exactly the DSes that need it most. Too many, kept indefinitely, turns the delta chain itself into an unbounded artifact the PN has to keep generating, signing, and hosting alongside the full file. A workable default is a bounded window — keep deltas back to the last K versions or a fixed time horizon (e.g. matching a typical DS re-crawl interval, a few days to a couple of weeks) — with the oldest delta still available exposed as its own field (an "earliest applicable `fromDigest`") so a DS can tell *up front* whether its last-seen digest still has a chain to the present, rather than requesting a delta and discovering only on a 404 that it has to fall back. Making the fallback boundary self-describing this way keeps it a deliberate check rather than a guess.

### 7.2 How a DS learns that something changed: three patterns to evaluate

Pure polling doesn't stay cheap once there are many providers and many DSes: every DS independently re-polling every PN's manifest is an N(providers) × M(DSes) relationship, with latency bounded by whatever interval each DS happens to poll at. Three candidate patterns, in increasing order of shared infrastructure and decreasing per-relationship overhead:

- **A — Pull-only (baseline).** Each DS polls each PN's `/.well-known/dedi.json` on its own cadence and compares `files[].digest` (§6, steps 1–2). Zero new infrastructure, and MUST remain viable regardless of what else is layered on — it is the correctness backstop if B or C are unavailable. DeDi's own public discovery list (its spec §8 — a bare list of publisher domains, asserting nothing) is available as an additional bootstrap signal for finding candidate domains, alongside — not instead of — the networkId registry, which remains the source of truth for which domains are legitimate, active Beckn PNs. Cost: bandwidth and latency scale with N×M.

  *Why digest and not just the manifest's own version/counter fields:* a single monotonic counter (index-level or manifest-level) only tells a crawler that *something* under that manifest was resaved — not which of potentially many listed files actually changed, and not whether the bytes differ at all (a re-sign after key rotation, or a reformat with no content change, still bumps a counter). `digest` is per-file and content-addressed, so it answers the question a crawler actually needs answered — "is this specific file worth re-fetching" — at the right granularity. A version/counter still earns its keep at the manifest level as the anti-rollback signal (§4.3, §5): a version going backwards is itself evidence of tampering or a bad rollback, independent of any single file's content. The two aren't redundant — version protects against regression, digest drives the actual fetch decision — but digest, not version, is what should gate a re-fetch.

- **B — Per-PN push channel.** The PN's `/.well-known/dedi.json` advertises an `updateChannelUrl` the PN itself runs — a webhook-subscribe endpoint, a WebSub/Atom-style feed, or an SSE stream. A DS discovers it and subscribes directly to that one PN. The notification carries no catalog content, only `{domain, registry, digest, updated_at}` — a pure "go re-fetch" signal; per §5 step 8 and §6's verification steps, the DS MUST still fetch and verify the DeDi file itself — an unsolicited notification is never trusted on its own, only used to trigger an earlier re-crawl. Cost: O(providers) channels to run, but each is still a 1-to-M fan-out the PN itself has to serve.  
- **C — Shared notification bus per networkId.** A broker — optionally run by the NFO that already manages that networkId's registry, or by independent community infra; not a mandated Fabric Thread — exposes one topic per `networkId`. PNs publish the same lightweight change-event to the topic instead of, or alongside, their own channel; a DS subscribes once per `networkId` \+ `schemaType` combination it cares about, collapsing the N×M relationship into N publishers \+ M subscribers against one shared topic. This is structurally the direct descendant of today's `CatalogSubscribeAction` (`networkIds` \+ `schemaTypes`) — the same subscription shape, just re-targeted at a pub/sub topic instead of a CS. Cost: reintroduces one piece of shared, *optional* infrastructure per network; if that broker is unavailable, Pattern A is what keeps the system eventually correct, just slower.

  *A caution on both B and C, from experience rather than theory:* push/broker-based "go re-fetch" notification has a track record of underdelivering on its promise once it meets real edges — subscriber endpoints go down silently, retry/backoff policy diverges per implementation with no shared spec for it, and at-least-once delivery means duplicate or out-of-order signals are the normal case, not the exception, so a DS still has to de-dupe and tolerate missed or late notifications regardless. A broker (C) additionally reintroduces exactly the kind of mandatory-feeling shared infrastructure this design set out to get away from, plus an open operational question this doc doesn't answer — who runs it, to what uptime, and what a DS does the day it's down. None of that makes B/C worthless, but it argues for treating them strictly as a latency shortcut a DS is free to ignore, never as something any correctness or completeness guarantee is conditioned on — Pattern A has to be fully sufficient on its own, not just "sufficient in theory."

**Where this leaves the design:** A is the required floor and is sufficient on its own. Whether B, C, or both should be defined normatively — and if C, who is expected to operate the broker and with what technology (a plain pub/sub topic vs. a durable queue with replay for a DS that was offline) — is exactly the infra evaluation flagged in §9. Nothing above depends on that choice being settled first.

---

## 8\. What happens to each existing endpoint

| Endpoint | Status |
| :---- | :---- |
| `POST /catalog/publish` / `/catalog/on_publish` | **Removed.** Superseded by self-hosting \+ a signed DeDi file (§5). |
| `POST /catalog/subscription` | **Removed as a fabric API.** Becomes internal DS crawler config, driven by networkId registry enumeration (and, optionally, the pub/sub subscription in §7.2 Pattern C). |
| `POST /catalog/push` | **Removed as a CS API.** DS pulls (crawls) by default (§6); optionally accelerated by the push patterns in §7.2. |
| `POST /catalog/search` | **Removed as mandatory fabric infra.** A DS MAY still expose an equivalent search API to its own downstream consumers — that was always a DS/CS implementation detail, not a required cross-fabric contract. |
| `POST /catalog/pull` / `/catalog/on_pull` | **Removed as a CS API.** Its FULL/INCREMENTAL semantics and `downloadManifest` shape are directly reused inside the DeDi-file crawl loop (§6, steps 2/6) and the delta-file pattern (§7.1). |
| `POST /discover` / `/on_discover` | **Unchanged.** This is the only interface a CN ever sees; everything above is entirely below it. |

CS itself isn't banned — nothing stops a party from still running CS-like aggregator infrastructure that crawls every PN and offers smaller DSes a convenience pull/search API on top. It just stops being a *mandatory* Fabric Thread and becomes optional, common-good infrastructure any DS can choose to lean on or bypass — the same optionality the spec already grants DS itself ("DS MAY be implemented as an independent SaaS... or by the CNs themselves").

---

## 9\. Open questions

1. **Catalog file access model** — DeDi's model assumes public data by design ("the data is public by definition and no credentials are involved" — DeDi spec §5.2, on CORS); it does not address confidentiality. Signing proves authenticity, not access — it does nothing to restrict who can *download* a catalog file sitting at a public URL. Two options remain open:  
   - **A. Public feed.** Catalog files are openly readable by anyone, exactly as DeDi's own model assumes. No new server component; actual transactions still require registered identity \+ signature as today. Trade-off: non-participants (scrapers, competitors) can read published catalogs freely.  
   - **B. Restricted to verified participants.** Only entities that can prove fabric identity can fetch the bytes at all, via a verifying proxy, short-lived pre-signed URLs, or a private repo with per-DS tokens. Preserves today's `AuthorizationHeader`\-gated confidentiality on `/catalog/search`/`/catalog/pull`, but reintroduces a server-side component and a per-DS provisioning step the PN must run, and sits *outside* the DeDi model entirely.  
2. **Schema publication venue** — a canonical `BecknCatalogRecord` schema needs to be published somewhere DeDi files can reference by URL. DeDi's own `schemas/` directory already carries `Beckn_subscriber`/`Beckn_subscriber_reference` — the natural sibling location — but this is a coordination point with the DeDi Working Group, not something this document can settle unilaterally.  
3. **The `visibleTo`/`schemaType` alias convention (§4.4)** — worth standardizing, or leave every DS to fetch-then-filter?  
4. **Two parallel drafts** — this document and [DeDi PR \#2](https://github.com/nfh-trust-labs/DeDi/pull/2) are both still in review. Worth flagging to both working groups so this design doesn't get built against a DeDi shape that shifts before their PR lands.  
5. **Publish-time feedback** — is an optional, best-effort `catalog/on_index` webhook (DS → PN, courtesy only, since 0..N DSes may crawl a given PN) worth standardizing, or is a pre-publish validator tool sufficient?  
6. **Multi-DS consistency** — different DSes may apply different strictness or crawl on different schedules, so the same PN can appear "discoverable" on one DS and not another at a given moment. Is any convergence guarantee needed, or is this an accepted property of decentralization?  
7. **Sybil/spam resistance** — networkId registry membership \+ revocation checks are the only gate on who gets crawled at all; is that sufficient, or does self-hosting need an additional reputation signal now that there's no CS acceptance step to filter low-quality submissions?  
8. **Deletion/right-to-be-forgotten** — `registry.state: inactive` (§5) handles graceful retirement; what's the expected behavior for a DS that already indexed data before a PN goes permanently offline without ever setting it?  
9. **CDN/caching correctness** — caching layers in front of a PN's host are fine for bandwidth, but a DS must never treat cache freshness as a substitute for signature/digest re-verification. DeDi's own Cache-Control guidance (SHOULD NOT outlive `next_update`) covers this at the protocol level; worth citing directly rather than restating.  
10. Should we recommend using git as a protocol to host files, to leverage capabilities like versioning, diff etc.  
11. Optional — queue that a provider chooses to send all update notifications to, with the subscribe URL made available via the PN's manifest, for any DS to subscribe to those notifications — see §7.2 (Patterns B and C) for candidate shapes; still open which (if either) should be normative, and who operates a shared broker if Pattern C is chosen.  
12. Would a PN want to not allow a certain DS in spite of that DS being part of a valid networkId?
