# Registry and Identity

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.0)

---

## 1. Overview

The Beckn v2 Network Registry is the identity and trust anchor of a Beckn network. It stores participant records — including signing keys, endpoint URLs, capabilities, and network membership — and exposes them for resolution by all network participants.

In v2, the registry is required to comply with the **[Decentralized Directory (DeDi) protocol](https://dedi.global)**, replacing the bespoke Beckn `lookup`/`subscribe` API of legacy pre-v2.

---

## 2. DeDi Protocol

[DeDi (Decentralized Directory)](https://dedi.global) is an open standard for publishing and querying machine-readable public directories over standard HTTPS. Key properties:

- **Publicly accessible**: any party can query the directory without credentials.
- **Machine-readable**: all entries are structured, typed records.
- **Verifiable**: records carry digital signatures from the publishing authority.
- **Multi-network composable**: a BAP or BPP can register once in a DeDi-compliant directory and be discoverable across multiple Beckn networks and other DeDi-participating ecosystems.

---

## 3. Participant Records

Each Beckn Network Participant (BAP, BPP, PS, DS) has a record in the DeDi registry containing:

| Field | Description |
|---|---|
| `subscriberId` | The participant's unique identifier (typically its FQDN) |
| `subscriberUrl` | The HTTPS endpoint URL implementing `/discover, /on_discover, /select, /on_select, and related action endpoints` |
| `role` | Participant role: `BAP`, `BPP`, `PS`, `DS` |
| `domain` | Supported interaction domain(s) |
| `signingPublicKey` | Ed25519 public key used to verify Beckn Signatures |
| `encryptionPublicKey` | (Optional) Public key for message encryption |
| `keyId` | Unique ID for this key entry (used in `Authorization` header) |
| `validFrom` | ISO 8601 timestamp — key validity start |
| `validUntil` | ISO 8601 timestamp — key validity end |
| `networkId` | The Beckn network this participant belongs to |
| `status` | `SUBSCRIBED`, `INITIATED`, `UNDER_SUBSCRIPTION`, `UNSUBSCRIBED`, `SUSPENDED` |

---

## 4. Registry Operations

### 4.1 Subscribe (Registration)

A new participant registers by submitting a `subscribe` request to the registry, providing its participant record and signing it with a key the registry can verify (via the DeDi trust chain).

Upon successful registration, the registry issues a `subscriberId` and stores the participant record.

### 4.2 Lookup (Key Resolution)

Any participant can resolve another participant's record:

```
GET /dedi/lookup?subscriberId={id}&keyId={keyId}
→ { subscriberId, subscriberUrl, signingPublicKey, validFrom, validUntil, ... }
```

Participants SHOULD cache lookup results for the duration of the key's validity period to reduce registry load.

### 4.3 Key Update / Rotation

A participant updates its signing key by submitting a new key record to the registry. The old key MUST remain valid (and present in the registry) until all in-flight requests signed with it have expired.

### 4.4 Unsubscribe

A participant removes itself from the network by submitting an `unsubscribe` request. The registry marks the record as `UNSUBSCRIBED`. Historical records SHOULD be retained for audit purposes.

---

## 5. Key Resolution in Authentication Flow

The key resolution step is a mandatory part of the request verification flow:

```
1. Receive request with Authorization header
2. Parse keyId → { subscriberId, keyId, algorithm }
3. lookup(subscriberId, keyId) → { signingPublicKey }
4. Verify Ed25519 signature using signingPublicKey
5. Accept or reject request
```

See [13_Authentication_and_Security.md](./13_Authentication_and_Security.md) for the full verification flow.

---

## 6. Comparison with legacy pre-v2 Registry

| Aspect | legacy pre-v2 Registry | v2.0.x DeDi Registry |
|---|---|---|
| API standard | Bespoke Beckn `lookup`/`subscribe` | DeDi-compliant standard APIs |
| Interoperability | Beckn-only | Cross-ecosystem (any DeDi participant) |
| Record format | Beckn-specific JSON schema | DeDi directory entry format |
| Public queryability | Network-specific | Publicly accessible by design |
| Multiple key support | Limited | Full `keyId`-based multi-key support |
| Trust chain | Beckn-specific | DeDi trust verification chain |

---

## 7. Further Reading

- [08_DeDi_Registry_Integration.md](./08_DeDi_Registry_Integration.md) — normative DeDi registry spec (RFC)
- [13_Authentication_and_Security.md](./13_Authentication_and_Security.md) — how keys are used for signing and verification
- [DeDi protocol](https://dedi.global)
