# RFC-006: Beckn API Endpoints (v2.0.0)

# 1. Document Details

- **Status:** Draft.
- **Authors:** Beckn Protocol contributors.
- **Created:** 2026-04-10.
- **Updated:** 2026-04-10.
- **Version history:** No commits found on `main` for `docs/06_Beckn_API_Endpoints.md`.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/06_Beckn_API_Endpoints.md).
- **Implementation report:** To be published by the implementation working group.
- **Stress test report:** To be published by the testing and certification working group.
- **Conformance impact:** Normative endpoint interpretation guidance for v2.0.0.
- **Security/privacy implications:** Reinforces signature and counter-signature requirements on endpoint interactions.
- **Replaces / Relates to:** Replaces non-RFC-form content in `06_Beckn_API_Endpoints.md`; the source contract remains `api/v2.0.0/beckn.yaml`.
- **Feedback:** Issues Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-006%22), Discussions Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-006%22), Pull Requests Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-006%22).
- **Errata:** To be published.

# 2. Abstract

This RFC explains the Beckn v2.0.0 endpoint surface, covering action and callback lifecycle semantics, common envelopes, endpoint grouping, and implementation constraints derived from the canonical OpenAPI contract.

# 3. Table of Contents

- [Introduction](#4-introduction)
- [Specification](#5-specification)
- [Conclusion](#6-conclusion)
- [Acknowledgements](#7-acknowledgements)
- [References](#8-references)

# 4. Introduction

Beckn v2 defines a broad action surface across discovery, transaction, fulfillment, post-fulfillment, and catalog infrastructure. Without a normalized interpretation guide, implementations can diverge on action semantics, callback behavior, envelope handling, and transport trust expectations even when they use the same OpenAPI contract. This document consolidates lifecycle and endpoint behavior so implementations remain interoperable while preserving the canonical contract in `api/v2.0.0/beckn.yaml`.

Within this document, the canonical OpenAPI contract is `api/v2.0.0/beckn.yaml`, action and callback pairing refers to a forward action endpoint and its corresponding `on_*` asynchronous callback endpoint, an envelope is the standard transport container carrying `context` and `message`, the ACK/NACK model refers to the immediate acknowledgement response families (`Ack`, `AckNoCallback`, `Nack*`, and `ServerError`), counter-signature refers to the signed receipt used to strengthen non-repudiation, and catalog infrastructure endpoints cover publish, subscription, pull, and master resource search flows.

Implementations are expected to preserve three design foundations throughout this endpoint surface: the OpenAPI contract remains the source of endpoint and payload truth, forward actions and `on_*` callbacks remain semantically paired, and the async-first interaction model with request signatures and acknowledgement counter-signatures remains intact wherever the contract defines it.

# 5. Specification

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in `00_Keyword_Definitions.md` (Click [here](./00_Keyword_Definitions.md)).

## 5.1 API fundamentals

- OpenAPI version: `3.1.1`
- Spec version: `2.0.0`
- Base server: subscriber-specific HTTPS origin represented by the `subscriberUrl` server variable in the canonical contract.
- Canonical contract: `api/v2.0.0/beckn.yaml`
- Authentication: every protected endpoint MUST validate Beckn HTTP Signature (`Authorization`).
- Interoperability model: implementations MUST treat the OpenAPI contract as the canonical endpoint and payload definition, and SHOULD preserve action/callback pairing semantics for lifecycle interoperability.

## 5.2 Common envelope semantics and acknowledgements

Most request operations use `context` and `message` envelopes.

Standard response families are:

- `Ack`
- `AckNoCallback` (`409`)
- `NackBadRequest` (`400`)
- `NackUnauthorized` (`401`)
- `ServerError` (`500`)

Successful acknowledgements SHOULD include signed receipt semantics through counter-signature, and implementations SHOULD verify response counter-signatures where provided.

Illustrative request envelope:

```json
{
  "context": {
    "version": "2.0.0",
    "action": "select",
    "transactionId": "txn-123",
    "messageId": "msg-456",
    "timestamp": "2026-04-10T00:00:00Z"
  },
  "message": {}
}
```

## 5.3 Lifecycle mapping

Core lifecycle:

```text
discover -> on_discover
select -> on_select -> init -> on_init -> confirm -> on_confirm
-> [status / on_status]* -> [update / on_update]* -> [cancel / on_cancel]?
-> [track / on_track]* -> rate / on_rate -> support / on_support
```

This lifecycle expresses the intended action symmetry between forward actions and asynchronous callbacks and should be preserved unless the canonical contract defines operation-specific behavior otherwise.

## 5.4 Endpoint groups

### 5.4.1 Discovery

- `POST /discover`
- `POST /on_discover`

### 5.4.2 Transaction

- `POST /select`, `POST /on_select`
- `POST /init`, `POST /on_init`
- `POST /confirm`, `POST /on_confirm`

### 5.4.3 Fulfillment

- `POST /status`, `POST /on_status`
- `POST /track`, `POST /on_track`
- `POST /update`, `POST /on_update`
- `POST /cancel`, `POST /on_cancel`

### 5.4.4 Post-fulfillment

- `POST /rate`, `POST /on_rate`
- `POST /support`, `POST /on_support`

### 5.4.5 Catalog infrastructure

- `POST /catalog/publish`, `POST /catalog/on_publish`
- `POST /catalog/subscription`, `GET /catalog/subscriptions`
- `GET|DELETE /catalog/subscription/{subscriptionId}`
- `POST /catalog/pull`, `GET /catalog/pull/result/{requestId}/{filename}`

### 5.4.6 Master resource search

- `POST /catalog/master/search`
- `GET /catalog/master/schemaTypes`
- `GET /catalog/master/{masterItemId}`

Endpoint grouping shorthand:

```text
Discovery: /discover, /on_discover
Transaction: /select,/on_select,/init,/on_init,/confirm,/on_confirm
Fulfillment: /status,/on_status,/track,/on_track,/update,/on_update,/cancel,/on_cancel
Post-fulfillment: /rate,/on_rate,/support,/on_support
```

## 5.5 Operation behavior and conformance requirements

- `context.try` semantics are used for preview and commit behavior in selected flows, including `update`, `cancel`, `rate`, and `support`.
- Catalog publishing actions may support alias forms such as `catalog/publish` and `catalog_publish` where defined in OpenAPI.
- Catalog pull is asynchronous and returns an immediate acknowledgement with request tracking metadata.
- Implementations MUST treat `api/v2.0.0/beckn.yaml` as the canonical endpoint and payload contract.
- Implementations MUST enforce request signature validation and SHOULD verify response counter-signatures where provided.
- Catalog infrastructure endpoints MUST follow operation-specific constraints defined in OpenAPI, including parameter and response semantics.

## 5.6 Security and compatibility considerations

Endpoint misuse, weak signature validation, or misinterpreted callback behavior can create spoofing and state inconsistency risks. Implementations SHOULD enforce strict request authentication, response integrity checks, and message correlation controls.

This RFC-format restructuring preserves the existing v2.0.0 endpoint interpretation intent. Compatibility questions that remain relevant to future revisions include whether alias action forms should be deprecated over a defined compatibility window and whether endpoint conformance profiles should be published as machine-readable test suites.

# 6. Conclusion

This document normalizes the Beckn v2.0.0 endpoint surface into a single RFC-style interpretation guide while preserving the canonical OpenAPI contract, endpoint groupings, lifecycle semantics, and transport security expectations. The current draft reflects the migration of the endpoint guide into RFC structure as Draft-01 dated 2026-04-10.

# 7. Acknowledgements

This document reflects the work of Beckn Protocol contributors and the implementation, testing, and certification working groups that support endpoint interoperability, conformance, and operational guidance.

# 8. References

- Keyword definitions: Click [here](./00_Keyword_Definitions.md)
- Canonical OpenAPI contract: `api/v2.0.0/beckn.yaml` (Click [here](../api/v2.0.0/beckn.yaml))
