# Beckn Protocol Version 2.0 - Long Term Support (LTS)

This repository contains the reference specification for Beckn Protocol Version 2 — defining the Beckn transport contract, action-specific OpenAPI endpoints, and governance artifacts needed to implement interoperable Beckn network participants.

The current v2.0.0 line reflects a developer-oriented, action-specific API surface in [`api/v2.0.0/beckn.yaml`](api/v2.0.0/beckn.yaml), with release-level contributor recognition in [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md).

This repository is intentionally kept **minimal and stable by design** — analogous to how HTTP defines a small, stable message envelope that supports a much broader ecosystem. Domain-level transaction schemas and type systems evolve outside this repository; this repository owns the stable protocol transport contract and its release-grade documentation.

> [!IMPORTANT]
> **v2.0.0-rc1 has reached End of Support.** The frozen snapshot of the specification as it existed during the RC1 phase is preserved on the [`core-2.0.0-rc1-eos`](https://github.com/beckn/protocol-specifications-v2/tree/core-2.0.0-rc1-eos) branch. Implementers who need the RC1 baseline should use that branch explicitly.

---

## Version History

| Version | Status | Key Changes |
|---------|--------|-------------|
| **v2.0.0** | **LTS (Long Term Support)** | Action-specific named endpoints in [`beckn.yaml`](api/v2.0.0/beckn.yaml), inline transport schemas, discovery/transaction/fulfillment/post-fulfillment coverage, and catalog publishing/extension APIs |
| v2.0.0-rc1 | **End of Support (EoS)** | Frozen on [`core-2.0.0-rc1-eos`](https://github.com/beckn/protocol-specifications-v2/tree/core-2.0.0-rc1-eos) branch — no further updates |
| v1.x | End of Support | Earlier Beckn protocol line with older discovery and registry patterns |

---

## Repository Structure

```text
protocol-specifications-v2/
├── ACKNOWLEDGEMENTS.md
├── api/
│   └── v2.0.0/
│       ├── beckn.yaml
│       └── README.md
├── docs/
│   └── *.md   (NFH-001 through NFH-013 RFC documents)
├── GOVERNANCE.md
├── LICENSE
└── README.md
```

### Key artifacts

- [`api/v2.0.0/beckn.yaml`](api/v2.0.0/beckn.yaml) — authoritative OpenAPI 3.1.1 specification for Beckn Protocol v2.0.0.
- [`api/v2.0.0/README.md`](api/v2.0.0/README.md) — API package overview, endpoint families, and operational notes.
- [`docs/`](docs/) — normative RFC documents (NFH-001 through NFH-013) covering architecture, protocol stack, API endpoints, authentication, error handling, design guides, and schema governance. See [`docs/README.md`](docs/README.md) for the suggested reading order.
- [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md) — contributor recognition for this release line.

---

## Design Principles

### Stable transport, evolving payloads

The schemas defined in [`beckn.yaml`](api/v2.0.0/beckn.yaml) are **transport schemas**. They define request/response framing, callback patterns, authentication expectations, acknowledgment behavior, and protocol-level constraints. They do **not** attempt to fully own domain semantics.

This separation allows the transport layer to remain stable while transaction payloads, vertical extensions, and implementation patterns continue to evolve over time.

### One named path per Beckn action

The v2.0.0 LTS line uses one named endpoint per Beckn action rather than a single universal endpoint. This makes the protocol easier to read, document, validate, and implement.

Examples include:
- [`/discover`](api/v2.0.0/beckn.yaml)
- [`/on_discover`](api/v2.0.0/beckn.yaml)
- [`/select`](api/v2.0.0/beckn.yaml)
- [`/on_select`](api/v2.0.0/beckn.yaml)
- [`/init`](api/v2.0.0/beckn.yaml)
- [`/confirm`](api/v2.0.0/beckn.yaml)
- [`/status`](api/v2.0.0/beckn.yaml)
- [`/track`](api/v2.0.0/beckn.yaml)
- [`/update`](api/v2.0.0/beckn.yaml)
- [`/cancel`](api/v2.0.0/beckn.yaml)
- [`/rate`](api/v2.0.0/beckn.yaml)
- [`/support`](api/v2.0.0/beckn.yaml)

### Asynchronous by default

Beckn remains fundamentally asynchronous. Forward actions typically receive an immediate acknowledgment, while business results flow through paired callback endpoints such as `discover → on_discover` and `confirm → on_confirm`.

### Endpoints are not actor-exclusive

Endpoints are **not** bound to a particular actor. Any action — the contracting lifecycle, `status`/`on_status`, `update`/`on_update`, `cancel`/`on_cancel`, `invoice`/`on_invoice`, `dispute`/`on_dispute`, and the rest — MAY be initiated by **either** node (CN or PN). Accordingly, **both nodes MUST implement the complete set of endpoints** — every action endpoint and its `on_*` callback. The action/callback pairing expresses correlation, not which actor hosts which endpoint.

### Release-quality specification matters

The repository treats the API specification and governance artifacts as part of the release contract. Changes to transport semantics, conformance expectations, and participation rules are documented directly in the versioned API package and top-level governance files.

---

## API Surface in v2.0.0 LTS

The OpenAPI definition in [`api/v2.0.0/beckn.yaml`](api/v2.0.0/beckn.yaml) currently covers the following endpoint families:

### Discovery
- `POST /discover`
- `POST /on_discover`

### Contracting / Ordering
- `POST /select`
- `POST /on_select`
- `POST /init`
- `POST /on_init`
- `POST /confirm`
- `POST /on_confirm`

### Fulfillment
- `POST /status`
- `POST /on_status`
- `POST /track`
- `POST /on_track`
- `POST /update`
- `POST /on_update`
- `POST /cancel`
- `POST /on_cancel`

### Post-Fulfillment
- `POST /rate`
- `POST /on_rate`
- `POST /support`
- `POST /on_support`

### Fabric API - Cataloging Service
- `POST /catalog/publish`
- `POST /catalog/on_publish`
- `POST /catalog/push`
- `POST /catalog/subscription`
- `POST /catalog/pull`
- `POST /catalog/on_pull`
- `POST /catalog/search`

For a concise package-level summary, see [`api/v2.0.0/README.md`](api/v2.0.0/README.md).

---

## Security and Protocol Semantics

- All protocol requests are expected to carry Beckn HTTP Signatures via the `Authorization` header as defined in [`api/v2.0.0/beckn.yaml`](api/v2.0.0/beckn.yaml).
- `Ack` responses confirm receipt at the transport layer; the responding actor signs the response payload and returns the signature in the `Signature` response header for the caller to verify. Business completion happens asynchronously through callback flows where applicable.
- `context.action` must match the semantics of the endpoint being invoked.
- `context.try` supports sandbox-style operation for applicable flows: `update` and `cancel` only.
- Error handling is standardized through response schemas such as `NackBadRequest`, `NackUnauthorized`, and `ServerError`.

For signing details and protocol semantics, see [`api/v2.0.0/beckn.yaml`](api/v2.0.0/beckn.yaml) and [`api/v2.0.0/README.md`](api/v2.0.0/README.md).

---

## How to Use This Repository

Use this repository as the reference baseline for:

- implementing Beckn v2.0.0-compatible participants and platform components,
- understanding the current action-specific Beckn API contract,
- reviewing callback semantics, transport acknowledgements, and security expectations,
- working with catalog publishing and catalog extension APIs,
- and onboarding implementers through the versioned API package and governance references.

When working at the API and transport level, start with [`api/v2.0.0/beckn.yaml`](api/v2.0.0/beckn.yaml).
When working at the specification and design level, start with [`docs/README.md`](docs/README.md).
When working at the process and policy level, start with [`GOVERNANCE.md`](GOVERNANCE.md).

---

## Related Release Artifacts

- [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md)
- [`api/v2.0.0/README.md`](api/v2.0.0/README.md)
- [`docs/README.md`](docs/README.md)
- [`GOVERNANCE.md`](GOVERNANCE.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)

---

## Related Resources

| Resource | Link |
|----------|------|
| Beckn Protocol v1 specification | https://github.com/beckn/protocol-specifications |
| Beckn schema registry | https://schema.beckn.io |
| DeDi protocol | https://dedi.global |
| Beckn website | https://beckn.io |

---

## Issues and Discussions

Visit the repository Issues and Discussions boards on GitHub for proposals, clarifications, release feedback, and implementation questions.
