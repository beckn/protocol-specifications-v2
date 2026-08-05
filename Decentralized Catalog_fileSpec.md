# File Specifications

---

A publisher's surface is four files in two layers. The DeDi layer is two files that follow DeDi's published format exactly and rarely change; the Beckn layer is where all the publish churn lives:

1. The **manifest** at `/.well-known/dedi.index.json`, written once at onboarding.  
2. The **pointer file** (`beckn-catalog-index.dedi.json`), a normal DeDi file with a single record: the location of the catalog index. DeDi layer.  
3. The **catalog index**, a plain Beckn file listing the catalogs, updated on every publish. **It is not a DeDi file and DeDi never ingests it.**  
4. The **catalog files**: baselines (plain Beckn catalog JSON, schema unchanged) and change files.

One thing to say plainly about this shape: the two DeDi files buy conformance and discoverability, not extra security. The chain's security is the signed entries inside the catalog index, exactly as it was when the surface was described.

Example domain throughout: `open-economy.nfh.global`, with ION (Indonesian Open Network, `ion.nfh.global`) as a restricted network.

# The manifest

DeDi's manifest format, used exactly as published: keys as JWKs, a files list naming each DeDi file the domain offers (with a digest on every entry, as DeDi requires), freshness fields, and a proof block (JCS canonicalization per RFC 8785, detached JWS per RFC 7515). No Beckn extensions are needed. It changes only when keys rotate, hosting moves, or a use case is added; the publish pipeline never writes it.

```json
{
  "dedi_version": "0.1",
  "type": "dedi-manifest",
  "domain": "open-economy.nfh.global",
  "keys": [
    {
      "kid": "key-1",
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "..."
    }
  ],
  "updated_at": "2026-01-05T00:00:00Z",
  "next_update": "2026-08-05T00:00:00Z",
  "files": [
    {
      "registry": "beckn-catalogs",
      "url": "https://open-economy.nfh.global/dedi/beckn-catalog-index.dedi.json",
      "schema": "https://schema.beckn.org/dedi/beckn-catalog-pointer.json",
      "digest": "sha-256:4a8b..."
    }
  ],
  "proof": {
    "verification_method": "key-1",
    "canonicalization": "JCS",
    "jws": "..."
  }
}
```

Notes:

- The file's entry points at the pointer file, not at the catalog index. The pointer file rarely changes, so its digest here is stable and **publish churn never touches the domain root**.  
- `next_update` on the manifest bounds how long its keys may be cached (DeDi's revocation bound).

# The pointer file

A normal DeDi file, conformant in every field, holding one record: where the catalog index lives. DeDi ingests this record like any other, which is what makes every publisher's catalog-index location queryable through DeDi's own APIs.

```json
{
  "dedi_version": "0.1",
  "type": "dedi-file",
  "source_url": "https://open-economy.nfh.global/dedi/beckn-catalog-index.dedi.json",
  "next_update": "2027-01-24T00:00:00Z",
  "publisher": {
    "domain": "open-economy.nfh.global",
    "key": { "kid": "key-1", "kty": "OKP", "crv": "Ed25519", "x": "..." }
  },
  "namespace": "open-economy.nfh.global",
  "registry": {
    "name": "beckn-catalogs",
    "schema": "https://schema.beckn.org/dedi/beckn-catalog-pointer.json",
    "state": "live",
    "updated_at": "2026-07-24T00:00:00Z"
  },
  "records": [
    {
      "record_name": "catalog-index",
      "details": {
        "url": "https://cdn.open-economy.nfh.global/beckn/catalog-index.json",
        "restricted": false
      }
    }
  ],
  "proof": {
    "verification_method": "key-1",
    "canonicalization": "JCS",
    "jws": "..."
  }
}
```

Rules:

- The record's details carry the index URL, a `restricted` flag, and, when the index is restricted, its `authMethods`; nothing more. **Network scoping does not live here.** Which networks may see a restricted index is answered by each operator's membership registry, the single authority; repeating the network list in the pointer would create a second copy that drifts (a publisher that leaves a network would have to remember to edit its pointer, re-sign it, and re-sign its manifest, and silent mismatch would be the normal failure).  
- The pointer changes only when the index URL moves or the restricted flag flips, which is rare and publisher-controlled. It does not change on publish, and it does not change when networks are joined or left.  
- **Key rotation order.** Rotation is add-then-remove: add the new key to the manifest, re-sign the pointer with it, update the pointer digest in the manifest, then remove the old key in a later manifest update, keeping both keys valid through at least one `next_update` window. A crawler that hits a pointer digest mismatch re-fetches the manifest once before treating it as a failure, which covers the swap window.  
- **Freshness derives from the manifest.** The manifest signs the pointer's digest, so a pointer past its own `next_update` means re-fetch and re-verify against the manifest, not invalid. A publisher cannot silently drop out of discovery because a file written once at onboarding expired.

# The catalog index

A plain Beckn file; DeDi never reads it. It lists the catalogs, each carrying identity, status, visibility, and the file list with signed entries. The index as a whole is not required to be signed; trust rides on the per-entry signatures

```json
{
  "participantId": "open-economy.nfh.global",
  "version": 42,
  "next_update": "2026-07-24T09:00:00Z",
  "catalogs": [
    {
      "catalogId": "open-economy.nfh.global/electronics-2026",
      "catalogType": "REGULAR",
      "status": "ACTIVE",
      "schemaTypes": ["https://schema.beckn.org/retail/schema/1.1.0/context.jsonld"],
      "baseline": {
        "version": 40,
        "url": "https://cdn.open-economy.nfh.global/beckn/electronics-2026.v40.json",
        "size": 1848320,
        "digest": "sha-256:9f2c...",
        "signature": {
          "keyId": "key-1",
          "value": "...",
          "validUntil": "2026-07-30T09:00:00Z"
        }
      },
      "changes": [
        {
          "version": 41,
          "url": "https://cdn.open-economy.nfh.global/beckn/electronics-2026.v41.changes.json",
          "size": 18240,
          "digest": "sha-256:5b1a...",
          "signature": {
            "keyId": "key-1",
            "value": "...",
            "validUntil": "2026-07-30T09:00:00Z"
          }
        },
        {
          "version": 42,
          "url": "https://cdn.open-economy.nfh.global/beckn/electronics-2026.v42.changes.json",
          "size": 9212,
          "digest": "sha-256:7e3d...",
          "signature": {
            "keyId": "key-1",
            "value": "...",
            "validUntil": "2026-07-30T09:00:00Z"
          }
        },
        {"version": 43}
      ]
    },
    {
      "catalogId": "open-economy.nfh.global/ion-exclusive-2026",
      "catalogType": "REGULAR",
      "status": "ACTIVE",
      "networkIds": ["ion.nfh.global"],
      "authMethods": [
        {
          "method": "signed-challenge",
          "algorithm": "Ed25519",
          "header": "Authorization",
          "signedHeaders": ["(created)", "(expires)", "(request-target)", "host", "digest"],
          "freshnessSeconds": 60
        }
      ],
      "schemaTypes": ["https://schema.beckn.org/retail/schema/1.1.0/context.jsonld"],
      "baseline": {
        "version": 12,
        "url": "https://cdn.open-economy.nfh.global/beckn/ion-exclusive-2026.v12.json",
        "size": 202400,
        "digest": "sha-256:1c9a...",
        "signature": {
          "keyId": "key-1",
          "value": "...",
          "validUntil": "2026-07-30T09:00:00Z"
        }
      },
      "changes": []
    },
    {
      "catalogId": "open-economy.nfh.global/electronics-2025",
      "status": "RETIRED",
      "retiredAt": "2026-01-31T00:00:00Z"
    },
    {..}
  ]
}
```

Rules:

- **The signed entry is a tuple, not a bare hash.** `signature.value` is Ed25519 over the JCS canonicalization of `{ catalogId, version, url, size, digest, validUntil }`. This binds each signature to one file in one role: it cannot be replayed for a different file, a different version, or past its validity window.  
- **`version` is monotonic**, both the index `version` (the crawler's cursor) and each catalog's file versions. A crawler that sees either go backwards flags it.  
- **`size` is required** on every file entry; it is what makes the fetch-baseline-instead cutover rule computable before downloading anything.  
- A catalog entry may carry a suggested crawl frequency (`crawlHint`, like a sitemap's `changefreq`): a hint crawlers may honor for fast-moving catalogs, with the crawler always in control of its own schedule and budget.   
- **A retired catalog stays as a tombstone** (status RETIRED with retiredAt, no files), so crawlers learn it is gone; a missing record is indistinguishable from a broken host.  
- **`next_update`** bounds how long any copy of the index may be believed; a crawler past it re-fetches before relying.  
- The index MAY additionally carry a whole-file signature, for publishers who want membership and ordering within a served copy covered as well.  
- The per-entry `signature` object may equally be encoded as a detached JWS to match DeDi's proof encoding; the final encoding is a schema decision, not a semantic one.  
- Keys declare their algorithm, and both Ed25519 and ES256 are accepted; ES256 matches the fabric's shipped signing guidance (OPA verifies it natively), Ed25519 matches DeDi's examples. Examples in this document use Ed25519.

# What is protected, and what is not

**Protected by the signed entries:**

- File bytes: any change breaks the digest.  
- File authenticity: the signature verifies against the publisher's registered key.  
- Binding: a signature is valid for exactly one catalog, version, URL, size and digest.  
- Lifetime: `validUntil` caps how long an entry may be presented.

**Not protected, because the index as a whole is unsigned:**

- Absence: a stale or hostile host can serve an old index that omits newer catalogs or change files.  
- Ordering and membership: which records appear, and with which change lists.  
- Tombstones and visibility flags: RETIRED status, `networkIds`, and `authMethods` are plain fields.

Because `authMethods` is a plain field, a crawler treats it as capability negotiation only: it never honors a freshness window longer than its own configured maximum, and never switches to a weaker method (such as signed URLs) unless its own configuration permits it. A tampered auth block can inconvenience a crawler; it cannot widen the crawler's exposure.

Bounds on the exposure: `next_update` forces refresh on a short cadence, the monotonic `version` exposes rollback to any crawler with history, and an optional whole-file signature closes the gap entirely for publishers who want it. A brand-new crawler has no version history, so its protection is `next_update` and, where the publisher opts in, the whole-file signature. The residual risk is accepted for discovery data: much of what is stale is caught at transaction time, where the authoritative leg validates again.

# Catalog files and change files

The **baseline** is the plain Beckn catalog JSON, exactly the schema used today; nothing in this design changes it. Two requirements on how it is produced:

- **Canonical serialization**: stable key order and formatting on every publish, so digests change only when content changes.  
- **Immutable, versioned URLs**: a new version is a new file at a new URL; nothing is overwritten in place.

The **change file** carries what changed between two consecutive versions, keyed by id, never by position:

```json
{
  "catalogId": "open-economy.nfh.global/electronics-2026",
  "fromVersion": 41,
  "toVersion": 42,
  "resources": {
    "upserts": [
      { "id": "open-economy.nfh.global/item-laptop-xps-15", "descriptor": { "name": "Dell XPS 15" }, "resourceAttributes": { } }
    ],
    "removals": ["open-economy.nfh.global/item-laptop-xps-13"]
  },
  "offers": { "upserts": [], "removals": [] },
  "catalog": { }
}
```

- Upserts are complete, schema-valid objects; the receiver replaces by id. Removals are ids. The optional `catalog` object carries catalog-level attribute changes (name, validity window).  
- **Compaction**: when the change list exceeds a threshold (by count or by combined size relative to the baseline) or on a schedule, the publisher emits a fresh baseline at a new URL, points the index at it, and resets the change list. Old files remain for a grace period covering the slowest expected crawler, then are deleted.  
- **Cutover rule** for crawlers: if the combined `size` of pending change files exceeds a set fraction of the baseline `size`, fetch the baseline instead.

# Crawler verification rules

In order, per publisher, per pass:

1. Resolve the participant and its index URL (registry service today, DeDi reverse lookup in the target state).  
2. Fetch the manifest if not cached or past its `next_update`. Keys follow DeDi's trust model: **the manifest at the domain's well-known path, served under the domain's TLS, is the authority for the publisher's keys** (the same anchor as did:web), and every registry copy is a cache of it. A key not present in the current manifest is invalid, and so is everything signed with it; removal from the manifest is revocation. The accepted tradeoff is DeDi's own: a full compromise of the web host can swap keys and files together, and the mitigation is external monitors that watch manifests for unexpected key changes. *Note that the transaction leg still resolves keys from the subscriber record; converging the two resolution paths is an open choice in the Migration Guide.*  
3. Verify the pointer file against the digest, the manifest signs for it. On a mismatch, re-fetch the manifest once before treating it as a failure (this covers a key rotation or pointer update in progress).  
4. Fetch the catalog index, conditionally: a `HEAD` check or `If-Modified-Since` / `ETag` first, so an unchanged index costs nothing. On a fresh copy, check `next_update`, check the index `version` has not regressed, check the index's `participantId` matches the participant being crawled.  
5. For each record: verify each file entry's signature tuple against the registered key; check `validUntil`; note per-catalog versions against the stored cursor. When crawling on behalf of a network, keep only the catalogs whose declared schema types fall within the scopes the operator's membership registry approves for this publisher; this binds declared metadata, and a mis-declared catalog is caught downstream by content validation at the edge.  
6. Fetch only what the cursor requires (change files, or baseline by the cutover rule). Verify every fetched file's bytes against its digest before use.  
7. Schema-validate, apply upserts and removals by id, advance the cursor. Catalogs failing any check are not indexed, and the reason is written to a feedback log the publisher can read.  
8. Standing checks: registration standing of the participant, staleness window for re-verification, fetch bounds, caps on auth freshness windows, refusal of private-address URLs.

The ONIX crawler module implements exactly this contract. One alignment note for it: the current prototype's `receiverId` becomes `participantId`.

# Auth methods for restricted downloads

The `authMethods` entry is self-describing; a crawler reads it and knows what to build:

```json
{
  "method": "signed-request",
  "header": "Authorization",
  "signedHeaders": ["(created)", "(expires)", "(request-target)", "host", "digest"],
  "freshnessSeconds": 60
}
```

**signed-request**, the first method. It is the standard Beckn HTTP Signature, used as the signature standard itself binds a request to its URL, with no custom fields:

1. The crawler signs the download request with its network-registered key. The signing string is the base `(created) (expires) digest` (digest of the empty body, for a GET) plus the standard's own request binding: `(request-target)` and `host`, which every existing verifier of the underlying signature scheme already implements. Nothing new is invented; a signature for one URL cannot be presented for another because the URL is inside the signing string.  
2. Identity rides in the signature's standard `keyId` (`{participantId}|{unique_key_id}|{algorithm}`), so no separate requester field is needed. During migration a legacy `subscriber_id` in the first position maps to its `participantId` through the migration table.  
3. The download gate rebuilds the signing string from the request it received: scheme and host lowercased, no default port, the path exactly as received, and for the header method the query string excluded. It resolves the key by `unique_key_id`, **takes the verification algorithm from that registered key, never from the request**, verifies, checks `(created)` within `freshnessSeconds`, and checks the requester's membership (and, for scoped networks, approved scopes) in a permitted network's registry.  
4. Serve or deny. Verification itself needs no stored state; what a gate logs is its own business.

Replay is bounded first by keeping `freshnessSeconds` short: tens of seconds is ample for a machine-to-machine fetch, and 60 is the default. Clients sign each attempt freshly and never reuse a signature across retries or range requests. A gate with shared state MAY additionally keep a short-lived cache of served signatures and reject repeats; if it does, the cache must live at least as long as the freshness window plus clock skew, be bounded, and fail closed under eviction pressure. This cache is RECOMMENDED where the gate is a single service and of limited value on a distributed CDN edge, where each location caches separately; there, the short window does the work.

One accepted disclosure: the pointer record of a restricted index is itself public, so the existence of a private index is visible; only the contents are protected.

Additional methods extend the list without changing the shape; a **signed-url** variant (the same signature carried as query parameters) is the intended fallback for clients that cannot set headers. Signed URLs land in access logs and referrers, so their exposure is bounded only by `freshnessSeconds`; restricted responses must be non-cacheable, and the header method is preferred wherever possible. A restricted index declares the same `authMethods` in its pointer record's details, beside the `restricted` flag; fetching the index then works exactly like fetching a restricted catalog file. Download gate reference implementations (CDN edge functions, an ONIX plugin) are tooling deliverables, not protocol.

# participantId impact map

- Transaction leg context fields (`bapId`, `bppId`) stay on the wire for compatibility, per the v2 spec's own note; the collapse to `participantId` applies to the catalog leg now and to the transaction leg as a future migration.  
- The Catalog schema's `bppId` and `bppUri` fields are superseded: the publishing participant is the domain whose index listed the catalog, so the fields become `participantId` or are dropped as derivable.  
- `networkId` values become domains. Subnet registry lookups and network filters that key on today's free-form network names migrate with it.  
- `subscriberId` maps to `participantId` case by case, not as a blind rename. One subscriber on its own domain: a rename. Several subscribers of one organization under one domain: they collapse into one participantId, and the migration decides which keys carry forward and how per-subscriber approvals are re-recorded as approved scopes in the membership registry. The migration table records each mapping explicitly.  
- The Signature schema needs no new signed lines for restricted downloads. The download path uses the signature standard's own request binding (`(request-target)` and `host` in the signed headers) plus the standard `keyId` for identity; the change is a documented profile of the existing scheme, not an extension to it.

# Vocabulary map: today's terms in this design

Nothing below is lost; it changes name and home. Implementers migrating from CATALG or DISCOVR can read this as the equivalence table.

| Today (CATALG / DISCOVR) | In this design |
| :---- | :---- |
| `catalog/publish` with ACK/NACK | Saving files; validation at the edge, results in the feedback log |
| `publishDirectives.visibleTo` | Per-catalog `networkIds` in the index |
| `publishDirectives.updateMode: MERGE` | A change file (id-keyed upserts and removals) |
| `publishDirectives.updateMode: FULL` | A fresh baseline |
| `catalog/pull`, mode FULL | The baseline |
| `catalog/pull`, mode DELTA | Change files after the crawler's cursor |
| `downloadManifest` (sha256, sizeBytes) | `digest` and `size` in the signed index entry |
| Subscription filters (`networkIds`, `schemaTypes`) | Crawler-side filtering on the index; `networkIds` also answerable by the registry service |
| Subscription CRUD APIs (`catalog/subscription`) | No longer needed; a crawler's scope is its own configuration |
| `catalog/search` | Will be removed; a Discovery Service may still offer search over its own store |
| `catalog/push` | Crawler pull, with the optional change signal as accelerator |
| `/on_pull` callback | Consolidated into the Discovery Service's `/push` (data or file path) |
| `subscriberId` | `participantId`, a domain |
| Offer-only catalogs, query-time attachment | Unchanged, lives behind `/discover` as today |

|  
