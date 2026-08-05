# ONIX Catalog Crawler Plugin — Requirements

**Status:** Draft for implementation
**Audience:** beckn-onix plugin developer
**Related:** [decentralized_catalog_design.md](decentralized_catalog_design.md), [Decentralized Catalog.md](Decentralized%20Catalog.md)

---

## 1. Purpose

Every Discovery Service (DS) that wants to consume self-hosted, DeDi-published catalogs has to implement the same fetch → verify → cache pipeline described in [decentralized_catalog_design.md §6](decentralized_catalog_design.md). None of that logic is DS-specific — it's the same three-level walk for every provider, on every DS. This plugin makes that walk a **built-in ONIX capability**, so a DS operator running on beckn-onix configures one plugin and gets crawling for free, rather than re-implementing signature verification, digest comparison, and freshness checks themselves.

**One-line goal:** given a `subscriber_id`, fetch and verify all three artifact levels (manifest → index → catalog) and cache the result, in either a full or incremental pass.

## 2. Background — the three-level chain

A provider publishes three artifacts (validated against a live local reference setup — see §10):

| Level | Location | Format | Example (reference fixture) |
|---|---|---|---|
| 1. Manifest | fixed: `{domain}/.well-known/dedi.json` | DeDi manifest (`type: dedi-manifest`), **signed** | `angular-absently-gab.ngrok-free.dev/.well-known/dedi.json` |
| 2. Index | anywhere; `manifest.files[].url` | DeDi file (`type: dedi-file`), `records[].details` = catalog pointers, **signed** | hosted on Google Drive |
| 3. Catalog | anywhere; `index.records[].details.parts[].url` | plain Beckn `Catalog` JSON, no DeDi envelope, **not signed** | hosted on Google Drive |

Only the manifest's location is fixed (RFC 8615). The index and catalog files can live on any host, including two different hosts from each other — the crawler must not assume co-location.

## 3. Scope

**In scope:**
- Resolving a `subscriber_id` to a domain and fetching its manifest.
- Fetching and verifying the index file(s) the manifest references.
- Fetching and verifying each catalog `parts[]` entry the index references.
- Verifying manifest and index signatures per the algorithm in §7 (this plugin **verifies**, it does not sign or manage private keys).
- Digest-based change detection, full vs. incremental crawl modes.
- Per-catalog version-regression (rollback) detection.
- Caching all three levels with appropriate TTLs.

**Out of scope (this plugin does not do):**
- **Signing or private-key management** — a provider's own signing process is out of scope entirely; this plugin only ever handles *public* keys, read from `keys[]`/`publisher.key`. Reuse existing `artifactverifier`/`manifestloader`/`keymanager` plugins for the underlying primitive.
- Defining a new externally-facing HTTP endpoint. This plugin is invoked in-process (see §8); whether to expose an admin/on-demand HTTP trigger is a separate, later decision (§11).
- NetworkId enumeration ("which subscribers exist") — that's an existing registry lookup, consumed as an input, not built here.
- Anything about how a provider publishes. This is DS-side only.

## 4. Terminology

- **Subscriber** — a Provider Node, identified by `subscriber_id` (its domain/`bppId`).
- **Manifest** — the DeDi manifest at `/.well-known/dedi.json`; the trust anchor (`keys[]`) and the pointer to the index (`files[]`).
- **Index** — the DeDi file whose `records[].details` are catalog *pointers*, not catalog content: `catalogId`, `version`, `status`, `visibility`, `schemaTypes`, `parts[]`.
- **Catalog** — the plain Beckn `Catalog` JSON a `parts[]` entry points to.
- **Full crawl** — re-fetch and re-verify every artifact regardless of cached digest.
- **Incremental crawl** — skip re-fetching an artifact whose digest matches what's already cached; still re-fetch the manifest and index (cheap) every cycle to detect what changed.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR1 | Given `subscriber_id`, resolve it to a base domain via the existing registry lookup plugin (`dediregistry` or equivalent) — this plugin does not implement resolution itself. |
| FR2 | Fetch `{domain}/.well-known/dedi.json`. Verify its signature per §7 step 1. |
| FR3 | Parse `files[]`; for each entry whose `registry` matches the catalog-index convention, fetch the referenced index file. |
| FR4 | Verify each index's signature per §7 step 2 (integrity against its embedded `publisher.key`, then authenticity against the manifest's `keys[]`, already fetched in FR2). |
| FR5 | Parse each verified index's `records[].details`: `catalogId`, `version`, `status`, `visibility`, `schemaTypes`, `parts[]`. |
| FR6 | For each `parts[]` entry, fetch the catalog file and verify it by digest match only (§7 step 3) — catalog files carry no signature of their own, by design. |
| FR7 | Verify freshness (`now ≤ next_update`) and state (`registry.state`/catalog `status == live/ACTIVE`) for every fetched artifact. |
| FR8 | Cache all three levels (see §9 for schema), keyed by `subscriber_id`. |
| FR9 | **Full mode**: ignore all cached digests; fetch and re-verify everything. |
| FR10 | **Incremental mode** (default): compare each artifact's digest against the cached value; skip re-fetching the catalog body when unchanged. The manifest and index are always re-fetched (they're small and this is how changes are detected at all), but downstream catalog fetches are skipped when their digest hasn't moved. |
| FR11 | Track the last-seen `details.version` per `catalogId`. If an incoming `version` is lower than the cached one, flag it as a rollback — do not index the new content, keep serving the last good cached copy, and surface it as a non-fatal error on the result. |
| FR12 | Return one structured result per `CrawlSubscriber` call: manifest verification outcome, one entry per catalog (content + verification outcome + `changed` flag), and a list of non-fatal per-catalog errors. A single bad catalog must not fail the whole subscriber's crawl. |
| FR13 | Invocable in-process via a Go method call (`Crawler.CrawlSubscriber`), by both a self-scheduled ticker loop and, potentially, another plugin/module in the same ONIX instance. No assumption of an external HTTP caller. |
| FR14 | Enforce a crawl budget: max artifact size, per-fetch timeout, reject private/loopback-address URLs (SSRF guard), bounded retries. |
| FR15 | All tunables (poll interval, size caps, timeouts, mode default) are configured the standard beckn-onix way — via the plugin's `Config.Config map[string]string`, declared in `config/<profile>/plugin.yaml`. |

## 6. Non-functional requirements

- **Reuse, don't reinvent.** Signature/digest verification goes through `pkg/security/artifactverifier`; HTTP fetching follows the existing `manifestloader`/`dediregistry` conventions (size-limited reads, `hashicorp/go-retryablehttp` for retries); caching goes through the existing `definition.Cache` interface (Redis-backed).
- **Idempotency.** Running a crawl twice with no upstream changes must be a no-op on the cache and produce the same result (modulo `crawled_at`).
- **Partial-failure tolerance.** One malformed/unreachable catalog degrades that one entry, not the subscriber's whole result.
- **Observability.** Emit the same structured logging/telemetry conventions as other plugins (see `pkg/telemetry`); at minimum log per-subscriber crawl duration, cache hit/miss counts, and verification failures.

## 7. Signing & verification algorithm

Only two of the three artifacts carry a signature — the **manifest** and the **index**. The catalog file has none, by design (§2): its integrity is inherited entirely from the index's `parts[].digest`. `artifactverifier` (or equivalent) is invoked exactly twice per subscriber crawl — once for the manifest, once per index — never for a catalog file.

### 7.1 Key format

- Algorithm: **Ed25519** (JWK `kty: "OKP"`, `crv: "Ed25519"`).
- Public key embedded as JWK `x` = base64url (no padding) of the raw 32-byte public key.
- `kid` — reuse the subscriber's existing Beckn registry `keyId` as-is rather than inventing a separate DeDi-specific identifier (see worked example, §7.5).
- The same keypair may sign both the manifest and every index it lists. Nothing requires distinct keys per artifact — only that whichever key signed an index is *also* present in the manifest's `keys[]` (that presence check is the actual authenticity gate, §7.4).

### 7.2 Canonicalization

JCS (RFC 8785) over the document with the `proof` block removed: sorted object keys, compact separators, UTF-8, no insignificant whitespace.

**Implementer caveat:** our reference documents contain only strings/booleans/integers, so a plain canonical JSON serializer (sort keys + compact separators) is sufficient. If a future index ever carries a non-integer number inside `details`, full RFC 8785 number-to-string formatting becomes load-bearing and a generic serializer is no longer safe — note that the `Catalog` object itself already has such fields (e.g. `rating.ratingValue: 4.1`), but that's never a problem today since catalogs are never signed.

### 7.3 Detached JWS format

- Header: `{"alg":"EdDSA","b64":false,"crit":["b64"]}` (RFC 7797 "unencoded payload"), base64url-encoded, no padding.
- Signing input: `header_b64 + "." + canonical_bytes` — the canonical JSON bytes are used **raw**, not base64url-encoded, because `b64:false`.
- Signature: `Ed25519(signing_input)`, base64url-encoded, no padding.
- Compact detached form: `header_b64 + ".." + signature_b64` — the empty middle segment is what makes it *detached*: the payload isn't carried in the string itself, so a verifier must independently canonicalize whatever document it received to reconstruct the signing input before checking the signature.

### 7.4 Verification algorithm (receiver side)

Two distinct checks, using two different key sources — this is the part worth being precise about, since it's easy to conflate "signature valid" with "key trusted":

1. **Manifest — self-verification.** The manifest is signed by a key it itself lists in `keys[]`. Verify: `proof.verification_method` matches some `kid` in `keys[]` → take that key's `x` → verify `proof.jws` against `JCS(manifest - proof)`. There is no *external* key for this step — authenticity for the manifest comes from TLS + the fixed well-known path ([publishing-dedi-files.md §6.1](/private/tmp/publishing-dedi-files.md)), not from a further signature chain.
2. **Index — two sub-steps, different key sources:**
   a. **Integrity (offline).** Verify `proof.jws` against the key embedded in the index's own `publisher.key` — no network fetch needed for this alone.
   b. **Authenticity (uses the manifest, already fetched in step 1).** Confirm `publisher.key.kid` is present in the manifest's `keys[]`. If (a) passes but this fails, treat the index as **integrity-valid but not authenticated** — reject it for indexing purposes ([publishing-dedi-files.md §7.3](/private/tmp/publishing-dedi-files.md) step 3).
3. **Catalog — no signature check at all.** Its only check is the digest match against the index's `parts[].digest` (already covered by FR6, not by `artifactverifier`).

### 7.5 Worked example (reference fixture, now signed)

The reference fixture in §10 was signed and independently re-verified using this exact algorithm, against a real Ed25519 keypair:

- `kid`: `76EU7ofwRCF1aobQkShARrf1PAUsNpHqWUJoynPu9w45YFKmzqaPmy`
- Public key (JWK `x`): `CqVy97DW45bcZPPrWIYGe2ldl9C93NFeVciiAEYsvR0`
- Both the manifest and the index are signed with this same key; the index's `publisher.key.kid` matches the entry in the manifest's `keys[]` — step 7.4(2)(b) holds.
- Verification was run independently of the signing code (a separate script, not just "the signer says it's fine") and confirmed: manifest self-signature valid, index integrity valid, index authenticity confirmed.

## 8. Interface contract

New plugin class, following the existing `pkg/plugin/definition/*.go` pattern (interface + provider):

```go
package definition

type CrawlMode string

const (
    CrawlModeIncremental CrawlMode = "incremental" // default
    CrawlModeFull        CrawlMode = "full"
)

type CrawlRequest struct {
    SubscriberID string
    NetworkID    string    // for standing check + visibility filtering
    Mode         CrawlMode // defaults to CrawlModeIncremental if empty
}

type ManifestResult struct {
    URL        string
    Digest     string
    Verified   bool
    VerifiedAt time.Time
}

type PartRef struct {
    URL          string
    Digest       string
    LastModified time.Time
}

type VerificationOutcome struct {
    DigestMatch    bool
    SchemaValid    bool
    VersionOK      bool // false only when a rollback was detected (FR11)
    SignatureValid bool // per §7.4: true only if both index-integrity AND manifest-authenticity checks pass. Always false for catalogs — they have no signature to check (§7).
}

type CatalogResult struct {
    CatalogID    string
    Version      int
    Status       string // e.g. ACTIVE | RETIRED
    Visibility   string // "public" | networks-scoped
    SchemaTypes  []string
    Source       PartRef
    Changed      bool // false = skipped in incremental mode, cache hit
    Verification VerificationOutcome
    Catalog      json.RawMessage // omitted when Changed == false, unless full mode
}

type CrawlError struct {
    CatalogID string
    Stage     string // "index_fetch" | "index_verify" | "part_fetch" | "part_verify"
    Reason    string
    Fatal     bool
}

type CrawlResult struct {
    SubscriberID string
    CrawledAt    time.Time
    Mode         CrawlMode
    Manifest     ManifestResult
    Catalogs     []CatalogResult
    Errors       []CrawlError
}

type Crawler interface {
    CrawlSubscriber(ctx context.Context, req CrawlRequest) (CrawlResult, error)
}

type CrawlerProvider interface {
    New(ctx context.Context, config map[string]string) (Crawler, func() error, error)
}
```

## 9. Cache schema

Backed by the existing `definition.Cache` (Redis). Key pattern:

```
onix:crawler:v1:{subscriberID}:manifest
onix:crawler:v1:{subscriberID}:index:{registryName}
onix:crawler:v1:{subscriberID}:catalog:{catalogID}
```

Each value stores: `{ digest, version (catalog entries only), content, verifiedAt, nextUpdate }`.

**TTL rule:** an entry's cache TTL must never exceed its own `next_update` — an expired-but-still-cached entry must be treated as stale on read, matching the spec's own freshness rule ([publishing-dedi-files.md §9](/private/tmp/publishing-dedi-files.md)).

## 10. Reference test fixture

A live setup already exercises this exact chain and can be used to validate the implementation without standing up new infrastructure:

- Manifest: `https://angular-absently-gab.ngrok-free.dev/.well-known/dedi.json` — **signed**, verifies against its own `keys[]`.
- Index: hosted on Google Drive (URL inside the manifest's `files[0].url`) — **signed** with the same key; verifies both offline (against embedded `publisher.key`) and for authenticity (key present in manifest's `keys[]`).
- Catalog: hosted on Google Drive (URL inside the index's `parts[0].url`) — **not signed**; verified by digest match only.

This fixture specifically exercises:
- **Cross-host hosting** — manifest, index, and catalog are on three different hosts (ngrok / Google Drive / Google Drive), proving the crawler must not assume co-location.
- **Digest verification** — real SHA-256 digests that must match at each level.
- **Real signature verification** — both the manifest and the index are signed with a real Ed25519 keypair (§7.5) and independently re-verified; `VerificationOutcome.SignatureValid` is expected to come back `true` for both. (An earlier version of this fixture used a placeholder `proof.jws`, which correctly produced `SignatureValid: false` without aborting the crawl — useful if the implementer wants to also exercise the rejection path deliberately.)
- **A non-`application/json` content-type and missing CORS headers** from Google Drive's download endpoint — the crawler must verify by digest/signature, not trust `Content-Type`.

## 11. Explicitly deferred / open questions

- Whether to expose an on-demand HTTP trigger or query surface for this plugin (vs. purely ticker-driven) — no endpoint is defined by any spec today; this is a build decision, not a protocol requirement.
- Whole-index rollback detection vs. per-catalog only (`details.version` is currently the only place this lives — see the versioning discussion in this design's history).
- The `visibleTo`/`schemaType` manifest-level alias convention ([decentralized_catalog_design.md §4.4](decentralized_catalog_design.md)) — fetch-then-filter is the required baseline; this plugin should not assume the alias convention exists.
- Delta-file support for large catalogs ([decentralized_catalog_design.md §7.1](decentralized_catalog_design.md)) — full-file fetch is the only guaranteed path for the phases below; delta support is a later optimization.
- Push-triggered early re-crawl (webhook/pub-sub, §7.2 Patterns B/C of the design doc) — this plugin only implements pull (Pattern A), which the design states MUST remain viable on its own.
- Key rotation / multiple concurrent keys in `keys[]` — the verification algorithm (§7.4) already supports it (any `kid` match in `keys[]` is sufficient), but this hasn't been exercised against the reference fixture yet (only one key exists there).

## 12. Phased implementation plan

| Phase | Delivers | Explicitly excludes |
|---|---|---|
| **Phase 1 — MVP** | `CrawlSubscriber` callable in-process, **full mode only**, single index per subscriber, real signature verification per §7 (reusing `manifestloader`/`artifactverifier`), writes through to cache. Validate against the reference fixture (§10) — both the signed and, optionally, an unsigned variant to exercise the rejection path. | Incremental mode, version-regression detection, scheduling, crawl-budget enforcement. |
| **Phase 2 — Incremental + safety** | Digest-based skip logic (FR10), crawl budget (FR14): size caps, timeouts, SSRF guard, bounded retries. | Version-regression detection, self-scheduling. |
| **Phase 3 — Rollback protection** | Per-`catalogId` version tracking and regression detection (FR11), structured non-fatal `CrawlError` reporting (FR12). | Multi-subscriber batch crawling, scheduling. |
| **Phase 4 — Scheduling** | Self-triggered ticker loop (matching the `opapolicychecker`/`schemav2validator` idiom) at a configurable interval; batch crawl across subscribers enumerated from the networkId registry. | On-demand HTTP trigger. |
| **Phase 5 — Deferred / optional** | On-demand internal trigger endpoint, webhook-based early recrawl, delta-file fetch support, multi-key rotation testing. | — |

Each phase should be independently mergeable and independently testable against the reference fixture in §10 (adding a second dummy catalog/subscriber as needed once Phase 3+ requires exercising multiple `catalogId`s).
