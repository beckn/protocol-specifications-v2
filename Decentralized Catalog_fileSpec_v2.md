# File Specifications (v2)

---

**Status:** Discussion draft. Companion to `Decentralized Catalog-HowItWorks.md`.

---

A publisher's surface is four files in two layers. The DeDi layer is two files that follow DeDi's published format exactly and rarely change; the Beckn layer is where all the publish churn lives:

1. The **manifest** at `/.well-known/dedi.index.json`, written once at onboarding.
2. The **Subscriber record** — the publisher's existing DeDi file for its Beckn identity, carrying one new field, `catalog_index_url` (or `catalog_index_urls`, see below). Not a new registry — see "The pointer" below. DeDi layer.
3. The **catalog index**, a plain Beckn file listing the catalogs, updated on every publish. **It is not a DeDi file and DeDi never ingests it.**
4. The **catalog files**: baselines (plain Beckn catalog JSON, schema unchanged) and change files — each now self-signed (see "Catalog files and change files").

One thing to say plainly about this shape: the two DeDi files buy conformance and discoverability, not extra security. The chain's security is the signed entries inside the catalog index and the self-signatures inside the catalog files themselves.


---

# The manifest

DeDi's manifest format, used exactly as published: keys as JWKs, a files list naming each DeDi file the domain offers (with a digest on every entry, as DeDi requires), freshness fields, and a proof block (JCS canonicalization per RFC 8785, detached JWS per RFC 7515). No Beckn extensions are needed. It changes only when keys rotate, hosting moves, or a use case is added; the publish pipeline never writes it.

```json
{
  "dedi_version": "0.1",
  "type": "dedi-manifest",
  "domain": "open-economy.nfh.global",
  "keys": [
    { "kid": "key-1", "kty": "OKP", "crv": "Ed25519", "x": "..." }
  ],
  "updated_at": "2026-01-05T00:00:00Z",
  "next_update": "2026-08-05T00:00:00Z",
  "files": [
    {
      "registry": "beckn-subscriber",
      "url": "https://open-economy.nfh.global/dedi/beckn-subscriber.dedi.json",
      "schema": "https://schema.beckn.org/dedi/Beckn_subscriber.json",
      "digest": "sha-256:4a8b..."
    }
  ],
  "proof": { "verification_method": "key-1", "canonicalization": "JCS", "jws": "..." }
}
```

Notes:

- The file's entry points at the **Subscriber record**, not at the catalog index. The Subscriber record rarely changes, so its digest here is stable and **publish churn never touches the domain root**.
- `next_update` on the manifest bounds how long its keys may be cached (DeDi's revocation bound).
- `registry: "beckn-subscriber"` and the schema URL above are illustrative — the actual registry name DeDi already uses to host Subscriber records as files is a coordination point with whoever owns `Beckn_subscriber.json` in the DeDi repo, not something this document can assert unilaterally.

---

# The pointer

The pointer is **one new field on the existing `Beckn_subscriber` schema**, the record every Beckn participant already needs for its identity. No second schema, no second registry.

```json
{
  "dedi_version": "0.1",
  "type": "dedi-file",
  "source_url": "https://open-economy.nfh.global/dedi/beckn-subscriber.dedi.json",
  "next_update": "2027-01-24T00:00:00Z",
  "publisher": {
    "domain": "open-economy.nfh.global",
    "key": { "kid": "key-1", "kty": "OKP", "crv": "Ed25519", "x": "..." }
  },
  "namespace": "open-economy.nfh.global",
  "registry": {
    "name": "beckn-subscriber",
    "schema": "https://schema.beckn.org/dedi/Beckn_subscriber.json",
    "state": "live",
    "updated_at": "2026-07-24T00:00:00Z"
  },
  "records": [
    {
      "record_name": "open-economy.nfh.global",
      "details": {
        "subscriber_id": "open-economy.nfh.global",
        "url": "https://open-economy.nfh.global",
        "type": "BPP",
        "domain": "retail",
        "countries": ["IDN"],
        "signing_public_key": "...",
        "catalog_index_urls": [
          { "url": "https://cdn.open-economy.nfh.global/beckn/catalog-index.json" }
        ]
      }
    }
  ],
  "proof": { "verification_method": "key-1", "canonicalization": "JCS", "jws": "..." }
}
```

Rules:

- `catalog_index_urls` is a **list**, not a single URL. `Decentralized Catalog-HowItWorks.md` states a node may keep more than one index (e.g. separating retail from mobility, or a fast-moving catalog from a slow one), and a single-URL field can't represent that.
- No `restricted` flag anywhere — catalogs are public-only (see "Catalog access is public"), so there's nothing for the pointer to declare about access.
- The record changes only when an index URL is added, removed, or moved — rare and publisher-controlled. It does not change on publish, and it does not change when networks are joined or left.
- **Key rotation order.** Rotation is add-then-remove: add the new key to the manifest, re-sign the Subscriber record with it, update its digest in the manifest, then remove the old key in a later manifest update, keeping both keys valid through at least one `next_update` window. A crawler that hits a digest mismatch re-fetches the manifest once before treating it as a failure, which covers the swap window.
- **Freshness derives from the manifest.** The manifest signs the Subscriber record's digest, so a record past its own `next_update` means re-fetch and re-verify against the manifest, not invalid. A publisher cannot silently drop out of discovery because a file written once at onboarding expired.

---

# Catalog access is public

Catalogs are public, unconditionally. There is no restricted catalog, no download gate, and no per-catalog authentication method — any party with a catalog file's URL can fetch it, the same as any other public web resource. There is no signed-request anywhere in this design.

`networkIds` on a catalog entry (below) still exists, but as a **Discovery-service relevance filter**, not an access control: it tells a network-scoped Discovery service which catalogs to bother indexing for that network. Declining to name a network doesn't hide a catalog from anyone who fetches it directly, and naming one doesn't restrict it either. Where a publisher's declared `networkIds` and a network's membership registry disagree on whether the publisher belongs to that network at all, the membership registry wins for what a network-scoped Discovery service indexes and serves under that network's banner — that's a binary membership decision (the existing `beckn-subscriber-reference` record for this node either exists in the operator's registry, or it doesn't; no separate status/scope/validity fields), never a visibility one. Finer-grained scope enforcement (e.g. "retail approved, mobility not"), if a network wants it, is a policy question — see HowItWorks' rego/OPA reference — not a registry lookup.

---

# The catalog index

A plain Beckn file; DeDi never reads it. It lists the catalogs, each self-signing its own entry as one unit. The index as a whole is not required to be signed; trust rides on the per-entry signatures.

```json
{
  "nodeId": "open-economy.nfh.global",
  "next_update": "2026-07-24T09:00:00Z",
  "catalogs": [
    {
      "catalogId": "open-economy.nfh.global/electronics-2026",
      "entryVersion": 7,
      "catalogType": "REGULAR",
      "status": "ACTIVE",
      "networkIds": ["ion.nfh.global"],
      "schemaTypes": ["https://schema.beckn.org/retail/schema/1.1.0/context.jsonld"],
      "baseline": {
        "version": 40,
        "url": "https://cdn.open-economy.nfh.global/beckn/electronics-2026.v40.json",
        "size": 1848320,
        "digest": "sha-256:9f2c..."
      },
      "changes": [
        { "version": 41, "url": "https://cdn.open-economy.nfh.global/beckn/electronics-2026.v41.changes.json", "size": 18240, "digest": "sha-256:5b1a..." },
        { "version": 42, "url": "https://cdn.open-economy.nfh.global/beckn/electronics-2026.v42.changes.json", "size": 9212, "digest": "sha-256:7e3d..." }
      ],
      "signature": { "keyId": "key-1", "value": "..." }
    },
    {
      "catalogId": "open-economy.nfh.global/electronics-2025",
      "entryVersion": 13,
      "status": "RETIRED",
      "retiredAt": "2026-01-31T00:00:00Z",
      "signature": { "keyId": "key-1", "value": "..." }
    },
    {"..": ".."}
  ]
}
```

Rules:

- **Each catalog entry signs itself.** `signature.value` is Ed25519 over the JCS canonicalization of the catalog entry with the `signature` field itself removed — `catalogId`, `entryVersion`, `catalogType`, `status`, `networkIds`, `schemaTypes`, and every `baseline`/`changes[]` file reference, together, as one unit. A file reference cannot be added, dropped, or swapped without breaking the whole entry's signature.
- **`entryVersion` bumps on any change to the entry — content or metadata.** It's the crawler's first, cheap check: unchanged since the last crawl means skip this entry entirely, guaranteed nothing about it moved; changed means look closer. It is deliberately independent of `baseline.version`/`changes[].version` — see § Versioning for why the two don't collapse into one.
- **There is no whole-index version field.** Whether the index has changed at all is answered by ordinary conditional HTTP (`ETag`/`If-Modified-Since` — see § Crawler verification rules, step 4). Rollback is caught per catalog instead, by comparing `entryVersion` and the content-lineage versions against the crawler's own stored cursor for that `catalogId` — see § Versioning for why that's a strictly better check than a document-level counter would have been.
- **`version` is monotonic.** `entryVersion` and each catalog's `baseline`/`changes[]` versions are all plain integers. See "Version numbering: integers, not timestamps" below for the reasoning; this document takes a position rather than leaving it as an open question.
- **`size` is required** on every file entry; it is what makes the fetch-baseline-instead cutover rule computable before downloading anything.
- A catalog entry may carry a suggested crawl frequency (`crawlHint`, like a sitemap's `changefreq`): a hint crawlers may honor for fast-moving catalogs, with the crawler always in control of its own schedule and budget.
- **A retired catalog stays as a tombstone** (status `RETIRED` with `retiredAt`, no files, still self-signed), so crawlers learn it is gone; a missing record is indistinguishable from a broken host.
- **`next_update`** bounds how long any copy of the index may be believed; a crawler past it re-fetches before relying.
- The index MAY additionally carry a whole-file signature, for publishers who want membership and ordering within a served copy covered as well.
- The per-entry `signature` object may equally be encoded as a detached JWS to match DeDi's proof encoding; the final encoding is a schema decision, not a semantic one.
- Keys declare their algorithm, and both Ed25519 and ES256 are accepted; ES256 matches the fabric's shipped signing guidance (OPA verifies it natively), Ed25519 matches DeDi's examples. Examples in this document use Ed25519.

## Version numbering: integers, not timestamps

**Recommendation: monotonic integers.** Stated as a position, not an open question, because the reasoning is one-sided:

- Single-writer-per-catalog is already an established invariant of this design ("no multi-writer merging exists or is needed"), which makes an integer counter trivially safe — no coordination, no collision risk, ever.
- The two systems this design explicitly draws from — Debian apt's `Pdiffs` and OpenStreetMap's Planet diffs — both use sequence numbers, not timestamps, for exactly this problem.
- A timestamp-as-version would duplicate information the design already carries elsewhere (`next_update` for staleness, the manifest's own `updated_at`), for no new capability.
- It would introduce a real new failure mode for no offsetting benefit: clock skew or a corrected system clock can make a legitimate republish look like a rollback, or tie with a prior version — neither is possible with a counter. The "a crawler that sees version go backwards flags it" rule stays unambiguous only if version is monotonic by construction.

Nothing above prevents a publisher from also carrying human-readable timestamps elsewhere (the index's `next_update`, or inside a catalog file's own content) — this is specifically about what the *ordering cursor* should be.

## What is protected, and what is not

**Protected, now at two independent levels:**

- **File bytes** — any change breaks the digest.
- **File authenticity, independent of the index** — every catalog file (baseline and change file alike) now self-signs its own content (see "Catalog files and change files"). A relocated or cached copy is verifiable on its own, without the index alongside it.
- **The catalog entry as a whole** — `catalogId`, `entryVersion`, `catalogType`, `status`, `networkIds`, `schemaTypes`, and every file reference are signed together, including the tombstone status and network declarations.
- **Binding** — a signature is valid for exactly one catalog's exact set of declared metadata and file references.

**Not protected, because the index as a whole is unsigned by default:**

- **Absence** — a stale or hostile host can still serve an old index that omits a newer catalog entry entirely, or omits a new change file. Content that's present and self-signed is verifiable; content that's silently missing is not detectable without the optional whole-index signature.
- **Cross-catalog ordering and membership** — which catalog entries appear in the index, and in what order, relative to each other.

Bounds on the residual exposure: `next_update` forces refresh on a short cadence, the monotonic `entryVersion` and content-lineage versions expose rollback to any crawler with history, and an optional whole-file signature closes the remaining gap entirely for publishers who want it. The residual risk is accepted for discovery data: much of what is stale is caught at transaction time, where the authoritative leg validates again.

---

# Catalog files and change files

Two named schemas, `CatalogFile` and `CatalogChangeFile` — not an ad hoc wrapper. Each composes the existing core schemas (`Catalog`, `Resource`, `Offer`) by `$ref` rather than duplicating them, so they track `beckn.yaml` automatically as it evolves; the file-format-specific concerns (right now, just `signature`) live entirely in sibling properties that evolve independently of the core schemas. **Open, not yet decided:** where `CatalogFile`/`CatalogChangeFile` themselves get published and versioned — the same category of question as the schema-publication-venue item raised for the catalog index's own schema, and not something this document can settle alone.

## `CatalogFile` (baseline)

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["catalogId", "version", "next_update", "catalog", "signature"],
  "properties": {
    "catalogId": { "type": "string" },
    "version": { "type": "integer" },
    "next_update": { "type": "string", "format": "date-time" },
    "catalog": { "$ref": "<Catalog's own schema location in beckn.yaml>" },
    "signature": {
      "type": "object",
      "additionalProperties": false,
      "required": ["keyId", "canonicalization", "value"],
      "properties": {
        "keyId": { "type": "string" },
        "canonicalization": { "type": "string", "enum": ["JCS"] },
        "value": { "type": "string" }
      }
    }
  }
}
```

An actual baseline file, conforming to it:

```json
{
  "catalogId": "open-economy.nfh.global/electronics-2026",
  "version": 40,
  "next_update": "2026-07-30T09:00:00Z",
  "catalog": {
    "id": "open-economy.nfh.global/electronics-2026",
    "descriptor": { "name": "Open Economy Electronics" },
    "provider": {
      "id": "open-economy.nfh.global/provider",
      "descriptor": { "name": "Open Economy" }
    },
    "resources": [
      {
        "id": "open-economy.nfh.global/item-laptop-xps-15",
        "descriptor": { "name": "Dell XPS 15" },
        "resourceAttributes": {
          "@context": "https://schema.beckn.org/retail/schema/1.1.0/context.jsonld",
          "@type": "ElectronicsItem",
          "brand": "Dell",
          "inStock": true
        }
      }
    ],
    "offers": [],
    "validity": { "startDate": "2026-01-01", "endDate": "2026-12-31" },
    "isActive": true
  },
  "signature": {
    "keyId": "key-1",
    "canonicalization": "JCS",
    "value": "3nF8k2v9QwZ...=="
  }
}
```

- **Avoiding circular signing:** the signing input is the JCS canonicalization of this document with the `signature` field itself removed — the same non-circularity convention DeDi already uses for its own `proof` block, applied here without requiring the file to be a DeDi file at all.
- The wrap does not reopen `Catalog` for changes, and does not weaken wire compliance: `beckn.yaml`'s `Catalog` schema governs the wire format (`/discover`/`/on_discover`), not this hosting file. A crawler unwraps `.catalog` back to a bare object before anything reaches the Discovery Service's index or the wire; the envelope only ever exists at rest.
- **`catalogId`, `version`, and `next_update` sit as siblings of `catalog`, never inside it** — so they cost nothing against `Catalog`'s own closed schema, and they're covered by the file's self-signature the same way `catalog` is, since signing input is the whole document minus `signature`. See § Versioning for what this buys and how it relates to the same fields on the index entry.
- Two other requirements on how it's produced: **canonical serialization** (stable key order and formatting on every publish, so digests change only when content changes), and **immutable, versioned URLs** (a new version is a new file at a new URL; nothing is overwritten in place).

## `CatalogChangeFile`

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["catalogId", "fromVersion", "toVersion", "next_update", "resources", "offers", "signature"],
  "properties": {
    "catalogId": { "type": "string" },
    "fromVersion": { "type": "integer" },
    "toVersion": { "type": "integer" },
    "next_update": { "type": "string", "format": "date-time" },
    "resources": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "upserts": { "type": "array", "items": { "$ref": "<Resource's own schema location in beckn.yaml>" } },
        "removals": { "type": "array", "items": { "type": "string" } }
      }
    },
    "offers": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "upserts": { "type": "array", "items": { "$ref": "<Offer's own schema location in beckn.yaml>" } },
        "removals": { "type": "array", "items": { "type": "string" } }
      }
    },
    "catalog": { "type": "object", "description": "partial catalog-level attribute changes (name, validity window)" },
    "signature": { "$ref": "#/CatalogFile/properties/signature" }
  }
}
```

An actual change file, conforming to it:

```json
{
  "catalogId": "open-economy.nfh.global/electronics-2026",
  "fromVersion": 41,
  "toVersion": 42,
  "next_update": "2026-07-30T09:00:00Z",
  "resources": {
    "upserts": [
      {
        "id": "open-economy.nfh.global/item-laptop-xps-15",
        "descriptor": { "name": "Dell XPS 15" },
        "resourceAttributes": {
          "@context": "https://schema.beckn.org/retail/schema/1.1.0/context.jsonld",
          "@type": "ElectronicsItem",
          "brand": "Dell",
          "inStock": true
        }
      }
    ],
    "removals": ["open-economy.nfh.global/item-laptop-xps-13"]
  },
  "offers": { "upserts": [], "removals": [] },
  "catalog": {},
  "signature": {
    "keyId": "key-1",
    "canonicalization": "JCS",
    "value": "9pQ2h7XmRk...=="
  }
}
```

- Upserts are complete, schema-valid `Resource`/`Offer` objects; the receiver replaces by id. Removals are ids. The optional `catalog` object carries catalog-level attribute changes (name, validity window).
- **Compaction:** when the change list exceeds a threshold (by count or by combined size relative to the baseline) or on a schedule, the publisher emits a fresh baseline at a new URL, points the index at it, and resets the change list. Old files remain for a grace period covering the slowest expected crawler, then are deleted.
- **Cutover rule** for crawlers: if the combined `size` of pending change files exceeds a set fraction of the baseline `size`, fetch the baseline instead.

Why sign at the file level *and* the index-entry level: they answer different questions. A file's own signature proves "this content genuinely came from this publisher, unmodified," and travels with the file wherever it goes. An index entry's signature proves "this version/URL is the one the publisher currently endorses as current." Neither depends on the other; a crawler that only has one still gets a real guarantee.

**Validation on both sides:** the same `CatalogFile`/`CatalogChangeFile` schemas are what publisher-side pre-publish tooling and crawler-side ingest validation both check against — one schema pair, not two divergent implementations. Resolving the nested `$ref` is native to standard JSON Schema validators; no bespoke validation engine is required.

---

# Versioning

Three independent layers, each with its own scope. Worth keeping distinct rather than conflating, since they answer different questions.

**There is deliberately no index-file-level version.** "Has the index changed at all" is answered by ordinary conditional HTTP (`ETag`/`If-Modified-Since`, § Crawler verification rules step 4) at no extra cost. A whole-document version counter would add nothing on top of that: the index as a whole isn't signed (§ The catalog index), so an unsigned document-level field couldn't actually back a rollback check — a hostile host could set it to whatever it wanted regardless of what it was really serving underneath. Rollback detection belongs, and is handled, one layer down, where the signed data actually is.

**Catalog-entry level — has-anything-changed.** Each catalog entry carries `entryVersion`, bumped on *any* change to the entry — content or metadata (`networkIds`, `schemaTypes`, `catalogType`, `status`, all live here too, and can change independent of the underlying resources/offers). It's the crawler's cheap first check: unchanged since last crawl means skip the entry entirely.

**Catalog-entry level — what's-current.** Independent of `entryVersion`, each catalog entry also carries `baseline.version` and `changes[].version` — the crawler's per-catalog cursor for deciding which change files it still needs (§ Crawler verification rules, step 6). These three counters (`entryVersion`, `baseline.version`, `changes[].version`) don't collapse into one: `entryVersion` bumps on every edit, but `baseline`/`changes[]` versions bump only when a corresponding file is actually published. Forcing a metadata-only edit to also bump `baseline.version` would send a crawler looking for a new baseline or change file that doesn't exist — either a no-op file has to be published to satisfy it, or version numbers get gaps that don't correspond to real files, breaking the "fetch changes after my cursor" contiguity the whole incremental scheme depends on. Keeping them separate is what lets a metadata edit stay as cheap as it should be: one re-signed entry, no file republished.

**Catalog-file level.** `CatalogFile` and `CatalogChangeFile` (§ Catalog files and change files) carry `catalogId`, a version marker (`version` for a baseline; `fromVersion`/`toVersion` for a change file), and `next_update` inside the file itself, not only in the index entry that points at it. This gives a crawler two equally valid paths: read the index first and fetch files by cursor as usual, or fetch a catalog file directly — from a known URL, an out-of-band reference, or a storage listing — and verify it entirely on its own, since it now carries enough to check its own identity, version, freshness, and signature without the index at hand.

Rules:

- **The file's own fields are covered by its own signature.** Signing input is the whole document minus `signature`, so `catalogId`/`version` (or `fromVersion`/`toVersion`)/`next_update` are part of what's signed automatically — no separate binding step needed.
- **A mismatch between the index entry's declared `catalogId`/version and the file's own internal `catalogId`/version is treated exactly like a digest mismatch: reject, don't index, log it.** Neither side is authoritative over the other; a disagreement means something is wrong, not a tiebreak.
- **`next_update` inside the file and `next_update` on the index are not required to agree, and that's fine.** They will often carry the same value in practice, since a publisher typically regenerates both together — but they're independent freshness leases for the two access paths above: a crawler that fetched via the index honors the index's `next_update`; a crawler that fetched the file directly honors the file's own. This is not a mismatch case the way `catalogId`/version is; there's no single right answer to reconcile against.
- None of this touches `Catalog`'s own closed schema. `catalogId`, `version`, and `next_update` sit as siblings of `catalog` on `CatalogFile`, never inside it — see § Catalog files and change files.

---

# Master and regular catalog resolution

- A REGULAR catalog's resources may extend a MASTER catalog's via `resourceDirectives[].extends.masterResourceId` — unchanged from today's `publishDirectives`, carried inside the catalog file's own content, not the index.
- Resolution moves from centralized publish-time merge (today's Cataloging Service) to Discovery-Service-side resolution, at index time: a REGULAR resource carrying `extends.masterResourceId` inherits attributes from the named MASTER resource, with the REGULAR resource's own fields taking precedence — the same merge semantics as today, just resolved later and locally.
- `catalogType` in the index entry lets a crawler order its work (index MASTER catalogs within a pass before resolving REGULAR ones that reference them) without fetching every file first.
- **Open:** what a Discovery Service does when a referenced MASTER catalog hasn't been crawled yet, or belongs to a publisher outside this Discovery Service's crawl set — serve the REGULAR resource unresolved, defer it, or drop it. Not yet decided.

---

# Crawler verification rules

In order, per publisher, per pass:

1. Resolve the node and its `catalog_index_urls` (registry service today, DeDi reverse lookup in the target state).
2. Fetch the manifest if not cached or past its `next_update`. Keys follow DeDi's trust model: **the manifest at the domain's well-known path, served under the domain's TLS, is the authority for the publisher's keys** (the same anchor as `did:web`), and every registry copy is a cache of it. A key not present in the current manifest is invalid, and so is everything signed with it; removal from the manifest is revocation. The accepted tradeoff is DeDi's own: a full compromise of the web host can swap keys and files together, and the mitigation is external monitors that watch manifests for unexpected key changes. *Note that the transaction leg still resolves keys from the Subscriber record; converging the two resolution paths is an open choice in the Migration Guide.*
3. Verify the Subscriber record against the digest the manifest signs for it. On a mismatch, re-fetch the manifest once before treating it as a failure (this covers a key rotation or a record update in progress).
4. Fetch the catalog index, conditionally: a `HEAD` check or `If-Modified-Since`/`ETag` first, so an unchanged index costs nothing — this is what stands in for a whole-document version check, and it costs nothing extra since a fresh copy has to be fetched and parsed anyway. On a fresh copy, check `next_update` and check the index's `nodeId` matches the node being crawled.
5. For each catalog entry: verify the entry's own signature (§ The catalog index) against the registered key; check `entryVersion` and the content-lineage versions (`baseline.version`/`changes[].version`) have not regressed against the stored per-catalog cursor — this is where rollback is actually caught, not at the whole-index level; check `catalogId`'s domain prefix matches the node being crawled — see "Open: id-collision enforcement" below. When crawling on behalf of a network, confirm the publisher has a reference record in that network's membership registry (binary — present or not) before indexing under that network's banner. Finer-grained scope enforcement, if a network wants it, is a policy question evaluated separately, not a field this registry lookup checks; every catalog remains fetchable regardless.
6. Fetch only what the cursor requires (change files, or baseline by the cutover rule). Verify every fetched file's bytes against its digest, **and verify the file's own embedded signature** (§ Catalog files and change files) against the registered key, before use.
7. Schema-validate; resolve MASTER/REGULAR references (§ Master and regular catalog resolution); apply upserts and removals by id; advance the cursor. Catalogs failing any check are not indexed, and the reason is written to a feedback log the publisher can read.
8. Standing checks: registration standing of the node, staleness window for re-verification, fetch bounds, refusal of private-address URLs.

**Open: id-collision enforcement.** Ids are domain-prefixed by convention (`{domain}/{slug}`) precisely to avoid collisions across publishers, and every example in this document follows it. What's not yet decided, per `Decentralized Catalog-HowItWorks.md`: what a crawler does when a publisher's file declares an id outside its own domain (reject the catalog, reject just that id, or flag and continue), and how a collision *within* one publisher's own files gets reported back to it.

The ONIX crawler module implements exactly this contract. One alignment note for it: the current prototype's `receiverId` becomes `nodeId`.

---

# `nodeId` impact map

- Transaction leg context fields (`bapId`, `bppId`) stay on the wire for compatibility, per the v2 spec's own note; the collapse to `nodeId` applies to the catalog leg now and to the transaction leg as a future migration.
- The Catalog schema's `bppId` and `bppUri` fields are superseded: the publishing node is the domain whose index listed the catalog, so the fields become `nodeId` or are dropped as derivable.
- `networkId` values become domains. Subnet registry lookups and network filters that key on today's free-form network names migrate with it.
- `subscriberId` maps to `nodeId` case by case, not as a blind rename. One subscriber on its own domain: a rename. Several subscribers of one organization under one domain: they collapse into one `nodeId`, and the migration decides which keys carry forward. The migration table records each mapping explicitly.
- Catalog-file and index-entry self-signing (this document) are new, catalog-specific constructs, independent of the `Signature` schema, and not used on the transaction leg. There is no restricted-download path, so the `Signature` schema needs no extension for one.

---

# Vocabulary map: today's terms in this design

Nothing below is lost; it changes name and home. Implementers migrating from CATALG or DISCOVR can read this as the equivalence table.

| Today (CATALG / DISCOVR) | In this design |
| :---- | :---- |
| `catalog/publish` with ACK/NACK | Saving files; validation at the edge, results in the feedback log |
| `publishDirectives.visibleTo` | Per-catalog `networkIds` in the index — a Discovery-service relevance filter, not an access gate |
| `publishDirectives.updateMode: MERGE` | A change file (id-keyed upserts and removals) |
| `publishDirectives.updateMode: FULL` | A fresh baseline |
| `catalog/pull`, mode FULL | The baseline |
| `catalog/pull`, mode DELTA | Change files after the crawler's cursor |
| `downloadManifest` (sha256, sizeBytes) | `digest` and `size` in the self-signed index entry |
| Subscription filters (`networkIds`, `schemaTypes`) | Crawler-side filtering on the index; `networkIds` also answerable by the registry service |
| Subscription CRUD APIs (`catalog/subscription`) | No longer needed; a crawler's scope is its own configuration |
| `catalog/search` | Will be removed; a Discovery Service may still offer search over its own store |
| `catalog/push` | Crawler pull, with the optional change signal as accelerator |
| `/on_pull` callback | Consolidated into the Discovery Service's `/push` (data or file path) |
| `subscriberId` | `nodeId`, a domain |
| Restricted catalogs / download gate | **Removed.** Catalog design is public-only; no per-catalog authentication exists |
| Offer-only catalogs, query-time attachment | Unchanged, lives behind `/discover` as today |
