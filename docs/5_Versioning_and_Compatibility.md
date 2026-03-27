# Versioning and Compatibility

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.1)

---

## 1. Versioning Scheme

Beckn Protocol uses **Semantic Versioning (SemVer)** in the form `MAJOR.MINOR.PATCH`.

| Component | Meaning |
|---|---|
| **PATCH** | Clarifications, editorial fixes, non-breaking tightening of normative text with explicit rationale. No conformance impact on existing implementations. |
| **MINOR** | Backward-compatible additions — new optional fields, new endpoint modes, new response schemas that do not break existing conformant implementations. |
| **MAJOR** | Breaking changes: removals, semantic shifts, changes to mandatory fields, changes to the signing algorithm, or changes to the endpoint contract. |

A MAJOR version bump is a new protocol line. Existing implementations do not need to upgrade to remain conformant with the prior major version.

---

## 2. Version History

| Version | Status | Key Changes |
|---|---|---|
| **v2.0.1** | **LTS (Long Term Support)** | Universal `/beckn/{becknEndpoint}` endpoint (GET + POST), GET Body Mode and Query Mode, transport schemas inlined in `beckn.yaml`, non-repudiation types (`CounterSignature`, `InReplyTo`, `LineageEntry`) |
| v2.0.0-rc1 | **End of Support (EoS)** | Frozen on `core-2.0.0-eos` branch — no further updates |
| v2.0.0 | Superseded | Initial v2 architecture — JSON-LD alignment, CDS/CPS and DeDi protocol based Registry |
| v1.x | End of Support | Original Beckn protocol — OpenAPI/JSON Schema, Beckn Gateway, bespoke registry |

---

## 3. LTS Policy

A version designated **Long Term Support (LTS)** receives:
- Security fixes for a defined support window.
- Critical bug fixes via PATCH releases.
- No new features (new features go into the next MINOR or MAJOR release).

The current LTS version is **v2.0.1**. Implementors SHOULD target the current LTS version for new implementations.

---

## 4. End of Support (EoS)

A version that has reached **End of Support** receives no further updates of any kind. The frozen specification is preserved on a dedicated git branch for reference.

Implementors MUST NOT build new networks on an EoS version.

---

## 5. Deprecation Policy

When a feature, field, or behavior is deprecated:

1. A deprecation notice MUST be published in the release notes of the version where it is deprecated.
2. The deprecated feature MUST specify:
   - The replacement (or "no replacement" with rationale).
   - The migration path.
   - The earliest MAJOR version where it may be removed.
3. Removal can only happen in a MAJOR version.

Implementations MAY continue to support deprecated features for backward compatibility but SHOULD migrate to replacements before the target removal version.

---

## 6. Compatibility Rules

### Backward Compatibility (MINOR releases)

A MINOR release MUST NOT:
- Remove or rename any mandatory field in the transport envelope.
- Change the meaning of any existing response code.
- Change the signing algorithm or signing string construction.

A MINOR release MAY:
- Add new optional fields to existing schemas.
- Add new endpoint modes (as v2.0.1 did with GET Query Mode).
- Add new response schemas for new response codes.
- Add new normative requirements that are additive (i.e., conformant v2.0.0 implementations are also conformant with v2.0.1 unless they trigger new error conditions).

### Core–Domain–Network Compatibility

- Domain schema packs and Network Profiles are independently versioned.
- Domain schema pack updates do not require a core protocol version bump.
- Networks SHOULD pin their participants to a specific core version and specific domain pack versions.

---

## 7. Migration from v1.x to v2

v2 is a **new protocol line**, not an in-place upgrade. The recommended migration approach:

### Phase 1 — Parallel Operation

- Keep existing v1.x infrastructure running for production traffic.
- Deploy v2 infrastructure (CPS, CDS, DeDi Registry) for pilot traffic.
- Register v2 participants in the DeDi registry in parallel with v1 registry entries.

### Phase 2 — Catalog Migration

- Convert v1 item models to v2 `Item` + `Offer` JSON-LD graphs with appropriate domain schema pack compositions.
- Deploy CPS; begin BPP → CPS catalog publication.
- Validate CDS index quality against v1 catalog.

### Phase 3 — Traffic Migration

- Onboard BAPs to use the CDS for discovery (replacing BG multicast calls).
- Migrate BAP → BPP transaction flows to the v2 universal endpoint.
- Remove v1 BG dependency.

### Phase 4 — v1 Decommission

- Decommission v1 Beckn Gateway.
- Archive v1 registry entries.
- Complete migration of all participants to v2 DeDi registry.

---

## 8. Context Version Field

The `context.version` field in every `RequestContainer` and `CallbackContainer` identifies the protocol version of the message. Receivers MUST validate this field and return `NackBadRequest` if the version is not supported.

```json
{
  "context": {
    "version": "2.0.1",
    ...
  }
}
```

---

## 9. Further Reading

- [GOVERNANCE.md](../GOVERNANCE.md) — versioning governance rules (SemVer, deprecation, removal)
- [8_Core_API_Envelope.md](./8_Core_API_Envelope.md) — normative transport contract
- [24_Conformance_and_Testing.md](./24_Conformance_and_Testing.md) — conformance rules per version
