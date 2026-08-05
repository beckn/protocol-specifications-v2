# How it works (v2)

**Status:** Discussion draft. Catalog access is public-only, with no restricted path, ever. See `Decentralized Catalog_fileSpec_v2.md` for file-format mechanics.

---

Publishers host their catalogs as plain files on their own storage, behind any CDN they like. A small catalog index file lists every catalog, carrying **a self-signed entry for each catalog**. (The catalog index is the publisher's own file on its storage; it is distinct from the DeDi manifest at the well-known path, which stays stable.) DeDi tells the network who exists and where their catalog index lives. Crawlers fetch the catalog index, check every file against its signature, and **pull only the files that changed** since their last visit. **There is no central catalog server anywhere in the content path, and no server of any kind is required for publishing — catalogs are public, so there is nothing to gate.**

**Identity is the domain.** This is a restructure of today's identifiers: `bapId` and `bppId`, `networkId`, the older `subscriberId`, all of them collapse into one identifier, `nodeId`, whose value is a domain name. A publisher is its domain, a network is its operator's domain, uniqueness comes from DNS, and nobody allocates identifiers. Subdomains are independent publishers in their own right, with one caveat worth stating: a subdomain inherits its parent zone's control, so whoever operates the apex can reassign it. A participant that wants identity fully in its own hands uses a domain it owns; subdomains under the fabric's zone are a convenience, natural in hosted mode.

# Who does what

## Publisher

- Hosts its catalog files and the catalog index on its own storage; registers its domain once.
- **Never runs a server.** Catalogs are public, unconditionally — there is no restricted catalog, so there is no download gate to operate, ever. This is stronger than "no server for public catalogs, one for restricted ones": there is no restricted case at all.
- Never calls a publish API (of Catalog Service).
- Assumption: A DeDi entry describing details of the network participant (node) verified against a domain it controls. For DeDi onboarding, the network participant may use the DeDi web interface or a manifest at the fixed well-known path (`/.well-known/dedi.index.json`).
- Hosting is the publisher's own responsibility: any static host it controls, from an object store to a CDN to a third-party static-site host. The fabric does not host catalog files. Whatever the host, the publisher signs its own files, so hosting is a deployment choice and never a transfer of identity.
  * A publisher that does not want to host itself has an alternative, called hosted mode: onboard through DeDi by verifying its domain, creating a namespace, and keeping a record there that points to a catalog index kept in storage operated on its behalf. The publisher still signs its own files; hosting is a deployment choice, never a transfer of identity.

## DeDi

- DeDi is the registry, and in the target state the only one. Learns of publishers from a public discovery list, crawls each domain's manifest, verifies it, and holds the resulting records.
- A publisher's manifest lists the DeDi file holding its Beckn Subscriber Schema record, and that record carries one or more `catalog_index_url` entries. **That record is the pointer into the catalog chain.** The catalog index is not a DeDi file, and DeDi never ingests either: **DeDi holds the pointer, not the data.**
- Never hosts catalog content. Never sits in the download path — there is no download path to sit in front of, since nothing is gated.
- Assumptions: reverse lookup with filters, and authentic keys per publisher. The reverse lookup is an ask on DeDi; until it exists, a registry service can fill the gap (see the two discovery shapes under Discovery).

## Discovery Crawler (ONIX).

- Runs in ONIX, as one edge module (ONIX Plugin) together with the Discovery Service; a working prototype exists.
- Finds publishers through the Registry, fetches each catalog index, pulls only the changed files, and hands the verified catalogs to the Discovery Service over an internal `/push` call. The Discovery Service serves consumers through the existing `/discover` API. Scheduling and on-demand re-sync are covered under the Migration Guide's Service changes.
- Never trusts unverified file content. Never receives pushed content.
- Assumptions: it verifies the digest and signature of every file it ingests — both the catalog file's own self-signature and the index entry's self-signature — and keeps its own store of what it has crawled. It understands how to work with incremental changes and full or incremental changes are pushed to Discovery's own search indexes.
- **MASTER catalogs:** Today's model has network-wide template catalogs that other catalogs extend, with master-wins merge, resolved centrally at publish. Discover service will now resolve the referenced Master catalogs in Regular catalogs.
- **ID collisions:** Catalogs, resources, and offers now arrive directly from publishers, so the Discovery Service needs a stated rule for colliding ids. The design leans on **domain-prefixed** ids (`catalogId` and resource ids carry the publisher's domain), which prevents collisions across publishers; the open part is enforcement: what a crawler does when a publisher's file declares ids outside its own domain, and how collisions within one publisher's files are reported back.

## Network operator (NFO)

- An operator running more than one network (production and sandbox, or several markets) constructs its network ids as per below:
  * `<domain>/<registryName>`**:** as in `ion.nfh.global/production`. Keeps every existing network id valid exactly as it is.
- **The membership registry.** It is the same registry participants are onboarded into today. The operator signs it under its own domain. Joining or leaving a network is one edit to this registry, by the operator. No new artifact is introduced.
  * This is the operator's registry of `beckn-subscriber-reference` records, used exactly as that schema already exists today: each record references a node's own subscriber record. Presence of a record is membership; nothing else is stored on it — see below for why.
- **Membership is binary, and it governs indexing under a network's banner — never visibility.** Catalog access is uniform and public; nothing about membership ever restricts who can fetch a catalog's bytes. What membership governs is narrower: whether a network-scoped Discovery Service will index and serve a given publisher's catalogs under that network's name at all.
  * A publisher can name networks in its own files (per-catalog `networkIds` in its index). That is only a declaration, and a relevance hint for Discovery services — never a gate.
  * Where the declaration and the membership registry disagree on whether the publisher belongs to the network at all, membership wins: a network-scoped Discovery Service indexes only publishers with a membership record, regardless of what a publisher declared about itself. This changes *what gets indexed under a network's banner*, never *who can download a file*.
- **Fine-grained scope — approving retail but not mobility from the same publisher — is a policy question, not a registry field.** The existing `beckn-subscriber-reference` schema carries no status, approved-scope, or validity-window fields, and none are added — that would itself be the new artifact this design avoids. Scope enforcement is left to the network's own rego/OPA policy (already named elsewhere in this document as where catalog-content enforcement runs), evaluated by the Discovery Service against a catalog's declared `schemaTypes`. Where that policy bundle lives and how a Discovery Service discovers it is not yet decided.
- **Two readers rely on this registry.**
  * A network-scoped Discovery Service, to decide whether a publisher is a member at all before indexing under that network's banner.
  * Anyone, to validate a network claim.
- **A network is real only when its membership registry exists.** Whoever publishes that registry under their domain is the operator. Three things follow:
  * Public catalogs need no operator at all. Publishing, discovery, and verification work end to end with no NFO anywhere. Example: a publisher with only public catalogs never touches a membership registry, and every crawler can take its catalogs. (All catalogs are public in this design, so this is simply the default case, not a special one.)
  * A publisher can be its own operator. It publishes a membership registry under its own domain and uses its own domain as the networkId. Example: open-economy wants a market network to index its catalogs under a specific banner, so it lists itself in a registry at `open-economy.nfh.global`. The cost is real: it now does the operator's job of keeping that list current.
- Everything else the operator does today (subnet policy, onboarding its participants) is unchanged by this design.

## Consumer app

- Calls `/discover` exactly as today; nothing changes for it.
- A consumer that chooses to crawl for itself becomes a crawler, with the same duties.

# Publishing

A publisher does three things once, and one thing on every update.

Once, at onboarding: put the catalog files and the catalog index on any static storage; and its small pointer file on the domain; add the domain to the public discovery list. DeDi crawls the manifest from there and the publisher becomes discoverable.

On every update: save the changed files and sign each one, sign the fresh catalog index entry, update the catalog index. **DeDi is not touched and no API is called.** Keeping the domain root untouched too: that the manifest lists only the stable pointer file, and all publish churn stays in the catalog index and the catalog files (tracked in File Specifications).

## ![][image1]

*Publishing Flow for a Provider*

## Whose index is it? Providers, platforms, and the NFO

The rule is **indexes belong to the node, never to the provider**. A node may keep more than one index: the node manifest lists them, so a node can separate retail from mobility, or a public index from a network-only one, and each churns on its own. What is not allowed is a per-provider index inside a platform. The arrangements:

- A provider that is its own node (its own domain) hosts its own manifest and index. DeDi's record points there; nobody aggregates it.
- A platform that onboards many providers is **one node**, however many indexes it keeps; each catalog inside names its provider, since the catalog schema already carries a provider object. The platform signs with its key. This is today's provider-platform model, translated to files.
- A provider run as a subdomain node (`provider-x.platform.com`) has its own manifest, index, and keys; one host's storage can serve many small nodes side by side.
- **The NFO is never in the catalog path.** Pointing crawlers at indexes is DeDi's job through records. The NFO's artifacts stay the network registry, the network manifest, and membership. An organization that both runs a network and hosts providers wears two hats, and the files stay separate per hat.

# Discovery

A crawler works in four steps: find catalog publishers, fetch each catalog index, fetch the changed files and verify each against its own signature, then hand the verified catalogs to the Discovery Service over its `/push` endpoint. `/push` accepts the catalog data or a file path to it, consolidating the old `/on_pull` callback into `/push`. **The Discovery Service and the crawler are one edge module**, running in ONIX; the diagrams draw two lanes only to show the handoff, and the push is an internal call. The crawler exposes an on-demand trigger for a specific publisher (the same API listed under Service changes in the Migration Guide) for immediate re-crawling needs outside from the scheduled pass. Consumers query the Discovery Service through `/discover`; **they never wait on a crawl**.

The first step, finding publishers and the indexes relevant to you, has two shapes. In both, DeDi is the source of the records; the question is only whether a separate registry service runs beside it. Without one, the crawler asks DeDi directly; with one, the service pre-computes the answer. Both are presented below with their trade-offs.

## With a registry service

The registry service is a cache of DeDi's records with a reverse lookup on top: from each publisher's record and manifest it learns the catalog index URI and, where declared, the networks that index is scoped to. **It never reads a catalog index itself.** A crawler makes a single call and receives the index URIs relevant to it: public ones plus those scoped to its networks. **Publishing is unchanged**; the publisher does nothing extra.
![][image2]
*Provider Flow with Registry Service*

![][image3]
*Discovery Flow with Registry Service*

**Pros:** one call replaces the enumeration sweep, and its cost is paid once and shared by all crawlers; new publishers surface as soon as their DeDi records do; network filtering is answered by the service instead of re-implemented by every crawler; and since every catalog is public regardless, the registry service can freely list every index with no authentication concern at fetch time.

**Cons:** it is a running service that someone operates and prices; there is a small staleness window against DeDi's records (small in practice, since records and manifests change rarely); and its filters are per index, not per catalog, so catalog-level relevance is still decided by the crawler after it fetches the index.

Two properties hold regardless. **Neither registry is ever an authority**: every file a crawler ingests is verified at its source against its own signature, so DeDi and the registry service alike can only answer where things are, never what they say; a crawler that already knows the publisher domains could function with no registry at all, just less efficiently. And if DeDi itself grows the reverse lookup, **the registry service folds into DeDi**, and the two shapes converge exactly: both answer with index pointers filtered at the index level, and catalog-level filtering stays with the crawler in every case.

# Incremental updates

Each catalog in the index carries a **baseline** (the latest full file) and a list of **change files**, one per publish, each holding just the added or updated items and the ids of removed ones. All are immutable files, and every one, baseline and change file alike, self-signs its own content. The index entry for the catalog additionally self-signs the whole set of file references together — see File Specifications. **A crawler remembers the last version it applied:**

- A little behind: fetch only the change files after its version.
- New, or far behind: fetch the baseline, then the change files after it.
- Changes add up to a large share of the baseline: fetch the baseline instead, it is cheaper.

Version numbers are plain monotonic integers, a deliberate choice over timestamps — see File Specifications for the reasoning.

![][image4]
*Incremental Updates*

When the change list grows long, or on a simple schedule, the publisher runs a **compaction**: it folds everything into a fresh baseline and starts the change list again. Compaction can also happen at the change level: several small change files squashed into one covering the same version range, which is just another change file, since every change file names the versions it spans. That gives a middle option when the list is long but the total delta is still small. Either way, **crawlers need no special handling for compaction**; their rule is already complete: if the changes they need are listed, take them; otherwise take the baseline. A crawler on any older version, however far behind, simply jumps to the new baseline and continues from there. See [Change Files in File Specification](?tab=t.gx10opdpldz9#heading=h.cknu8nksrwtq) for more details

References, inspiration from other projects:

- Debian apt `Pdiffs`: per-version diff files beside the full package index, with the same fallback to the full file when accumulated diffs grow too large. See the [Debian repository format](https://wiki.debian.org/DebianRepository/Format#indices_difference_files_.28diffs.29) and the [apt index diff proposal](https://lists.debian.org/debian-devel/2005/09/msg00494.html).
- OpenStreetMap: the planet's edit stream as numbered diff files with periodic baselines, served as plain files over HTTP. See [Planet.osm diffs](https://wiki.openstreetmap.org/wiki/Planet.osm/diffs).

# Catalog visibility

Catalogs are public, always. There is no restricted catalog, no download gate, and no per-catalog authentication method — any party can fetch any catalog file it has a URL for, exactly like any other public web resource. **This is a design decision, not a limitation still being worked out:** the catalog design will never support restricted catalogs.

A catalog may still name the networks it is meant for (per-catalog `networkIds` in the index). That's a **relevance declaration** for Discovery services, not an access control: it tells a network-scoped Discovery service which catalogs to bother indexing under that network's banner, but naming no network doesn't hide a catalog from anyone who fetches it directly, and naming one doesn't restrict it either. Where a publisher's declared `networkIds` and a network's membership registry disagree on whether the publisher belongs to that network at all, the membership registry wins for what gets indexed and served under that network — a binary membership decision, never a visibility one, and fine-grained scope beyond that is a policy question (see Network operator, above), not something this registry decides.

## The rules that hold it together

1. **Verify before trust, at two independent levels.** Every catalog file signs itself, so its content is verifiable on its own, wherever a copy travels. Every catalog's entry in the index also signs itself as one unit — its identity, status, network/schema declarations, and every baseline/change-file reference together — so no file reference can be added, dropped, or swapped without breaking that entry's signature. Neither level depends on the other; a crawler that only has one still gets a real guarantee. The index as a whole is still not signed by default; what that does and does not protect is spelled out in File Specifications.
2. **Immutable files.** Baselines and change files never change once published, so CDNs cache them forever and polling stays cheap for the publisher.
3. **Digests signal change; freshness bounds belief.** An unchanged file has an unchanged digest, so digests, not timestamps, drive what gets re-fetched. Timestamps still matter for one thing: `next_update`, carried once at the index level, caps how long any copy, including a rolled-back one, may be believed.
4. **One authoritative publisher per catalog.** No multi-writer merging exists or is needed.
5. **Pull only.** Crawlers fetch on their own schedule. A change signal may invite them sooner, but content always comes from the source and is always verified.

## What this changes in Beckn terms

- `/discover` and the transaction leg are untouched.
- Catalog access is uniformly public. There is no restricted-catalog path, and no new authentication surface anywhere beyond what already secures the transaction leg — no signed-request scheme, no download gate, no per-catalog auth negotiation.
- The central Cataloging Service and the catalog publish, push, pull, and subscription APIs are retired: **publishing becomes saving files, and distribution becomes crawling**.
- Publish-time validation moves to the edge: the crawler (ONIX) validates before `/push`, or the Discovery Service validates on `/push`. Failures reach the publisher through the feedback log, and the validator tool runs the same checks before publishing. This is also where a network's rego policies on catalog content can run, replacing the central enforcement point.
- **One field on the subscriber schema, `catalog_index_url` (or a list of them), and nothing else.** The catalog schema is untouched, and the catalog design introduces no registry of its own.
- Identifiers are restructured: today's identity fields (`bapId` and `bppId` on the wire, `networkId`, and the older `subscriberId`) become a single `nodeId` whose value is a domain. This is a cross-cutting change, not a rename; registry lookups and network filters key on those fields today, and the impact is tracked in File Specifications.
- Anyone may still run an aggregator as optional infrastructure; it is simply no longer mandatory.

## Publisher tooling

- Every step of the publishing flow (producing catalog files, maintaining the index, signing files and index entries, cutting change files, compaction) is deterministic, which makes it fully automatable.
- We ship tooling alongside the spec, standalone or possibly as ONIX plugins, that owns the flow end to end: generate and validate the files, sign them, maintain versions and change files, run compaction on schedule.
- A publisher connects the tool to its own catalog source and publishes from day one; with pre-built connectors for common platforms, **integration is configuration, not code**.
- The Provider Adapter draft explores this direction in detail.

### Open items to be accounted for

- **API-based catalogs:** Some publishers will serve catalog data from an API rather than files. Whether the index may point at API endpoints, and under what rules a crawler consumes them, is open.
- **Pagination:** Very large catalogs and very long indexes need a paging or sharding convention (the baseline already splits into parts; the convention needs pinning).
- **The change signal / relay service:** Referenced as the optional accelerator that invites crawlers sooner than their schedule. Not yet designed: what carries the signal, who runs the relay, and how it is priced are open. One rule is already fixed: a signal only triggers a crawl; content always comes from the source, verified.
- **The feedback log:** Referenced throughout as how a publisher learns what a crawler rejected and why, but not yet designed: where it lives, per-crawler or aggregated, its format, and its retention are all open.
- **Multiple indexes per node:** whether the node manifest (the DeDi manifest itself) lists multiple catalog-index entries directly, or the Subscriber record carries a list of index URLs, is open — see File Specifications.

## Where the details live

The File Specifications tab specifies every file format, the DeDi integration, and the verification rules an implementer builds against. The Migration Guide tab covers how today's catalogs move to this model.
