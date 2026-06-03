# Beckn API Endpoints

## Document Details

- **ID:** NFH-006
- **Status:** Draft.
- **Authors:**
  - [Ravi Prakash](https://github.com/ravi-prakash-v), [Networks for Humanity](https://networksforhumanity.org)
- **Created:** 2026-05-11
- **Updated:** 2026-05-11
- **Version history:** No commits found on `main` for `docs/06_Beckn_API_Endpoints.md`.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/06_Beckn_API_Endpoints.md).
- **Implementation report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Stress test report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Conformance impact:** Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main.
- **Security/privacy implications:** Reinforces signature requirements on endpoint interactions, including the synchronous `Signature` response header defined in [NFH-007 §5](./Authentication_and_Trust.md).
- **Replaces / Relates to:** Replaces non-RFC-form content in `06_Beckn_API_Endpoints.md`; the source contract remains `api/v2.0.0/beckn.yaml`.
- **Feedback:** Issues Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22NFH-006%22), Discussions Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22NFH-006%22), Pull Requests Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22NFH-006%22).
- **Errata:** To be published.

## Abstract

This RFC explains the Beckn v2.0.0 endpoint surface, covering action and callback lifecycle semantics, common envelopes, endpoint grouping, and implementation constraints derived from the canonical OpenAPI contract.

## Table of Contents

- [Beckn API Endpoints](#beckn-api-endpoints)
  - [Document Details](#document-details)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Specification](#specification)
    - [Definitions](#definitions)
    - [API fundamentals](#api-fundamentals)
    - [Common envelope semantics and acknowledgements](#common-envelope-semantics-and-acknowledgements)
    - [Lifecycle mapping](#lifecycle-mapping)
    - [Endpoint groups](#endpoint-groups)
      - [Discovery](#discovery)
      - [Transaction](#transaction)
      - [Fulfillment](#fulfillment)
      - [Post-fulfillment](#post-fulfillment)
      - [Catalog infrastructure](#catalog-infrastructure)
      - [Master resource search](#master-resource-search)
    - [Operation behavior and conformance requirements](#operation-behavior-and-conformance-requirements)
    - [Security and compatibility considerations](#security-and-compatibility-considerations)
  - [Conclusion](#conclusion)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)

## Introduction

Beckn v2 defines a broad action surface across discovery, transaction, fulfillment, post-fulfillment, and catalog infrastructure. Without a normalized interpretation guide, implementations can diverge on action semantics, callback behavior, envelope handling, and transport trust expectations even when they use the same OpenAPI contract. This document consolidates lifecycle and endpoint behavior so implementations remain interoperable while preserving the canonical contract in `api/v2.0.0/beckn.yaml`.

Within this document, the canonical OpenAPI contract is `api/v2.0.0/beckn.yaml`, action and callback pairing refers to a forward action endpoint and its corresponding `on_*` asynchronous callback endpoint, an envelope is the standard transport container carrying `context` and `message`, the ACK/NACK model refers to the immediate acknowledgement response families (`Ack`, `AckNoCallback`, `Nack*`, and `ServerError`), the synchronous response `Signature` header is the signed receipt the responding node returns to chain its receipt to the inbound request as defined in [NFH-007 §5](./Authentication_and_Trust.md), and catalog infrastructure endpoints cover publish, subscription, pull, and master resource search flows.

Implementations are expected to preserve three design foundations throughout this endpoint surface: the OpenAPI contract remains the source of endpoint and payload truth, forward actions and `on_*` callbacks remain semantically paired, and the async-first interaction model with request signatures and the synchronous `Signature` response header on every acknowledgement remains intact wherever the contract defines it.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described [here](./Keyword_Definitions.md). These definitions aim to ensure that the terms are understood precisely and consistently to avoid confusion in the interpretation of standards, specifications, and protocols.

### Definitions
To be added

### API fundamentals

- OpenAPI version: `3.1.1`
- Spec version: `2.0.0`
- Base server: subscriber-specific HTTPS origin represented by the `subscriberUrl` server variable in the canonical contract.
- Canonical contract: `api/v2.0.0/beckn.yaml`
- Authentication: every protected endpoint MUST validate Beckn HTTP Signature (`Authorization`).
- Interoperability model: implementations MUST treat the OpenAPI contract as the canonical endpoint and payload definition, and SHOULD preserve action/callback pairing semantics for lifecycle interoperability.

### Common envelope semantics and acknowledgements

Most request operations use `context` and `message` envelopes.

Standard response families are:

- `Ack`
- `AckNoCallback` (`202`)
- `NackBadRequest` (`400`)
- `NackUnauthorized` (`401`)
- `ServerError` (`500`)

Successful acknowledgements MUST carry a `Signature` response header as defined in [NFH-007 §5](./Authentication_and_Trust.md), and the sending node MUST verify it.

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

### Lifecycle mapping

Typical lifecycle:

```text
discover -> on_discover
select -> on_select -> init -> on_init -> confirm -> on_confirm
-> [status / on_status]* -> [update / on_update]* -> [cancel / on_cancel]?
-> [track / on_track]* -> rate / on_rate -> support / on_support
```

This lifecycle expresses the intended action symmetry between forward actions and asynchronous callbacks and should be preserved unless the canonical contract defines operation-specific behavior otherwise.

### Endpoints are not actor-exclusive

Protocol endpoints are **not** exclusive to a particular actor. Any value-exchange action — the contracting actions (`select` / `init` / `confirm`), `status` / `on_status`, `update` / `on_update`, `cancel` / `on_cancel`, the post-fulfillment actions, and the post-performance actions `invoice` / `on_invoice` ([NFH-015](./Invoicing_and_Settlements.md)) and `dispute` / `on_dispute` ([NFH-014](./Resolving_Disputes.md)) — MAY be initiated by **either** network participant (the CN or the PN).

Consequently, **both nodes MUST implement the complete endpoint surface — every action endpoint and its corresponding `on_*` callback.** A node MUST NOT assume that it will only ever receive a given call or only ever originate it. The action/callback pairing shown in the lifecycle above describes message *correlation*, not a fixed assignment of which actor hosts which endpoint.

### Endpoint groups

#### Discovery

- `POST /discover`
- `POST /on_discover`

#### Transaction

- `POST /select`, `POST /on_select`
- `POST /init`, `POST /on_init`
- `POST /confirm`, `POST /on_confirm`

#### Fulfillment

- `POST /status`, `POST /on_status`
- `POST /track`, `POST /on_track`
- `POST /update`, `POST /on_update`
- `POST /cancel`, `POST /on_cancel`

#### Post-fulfillment

- `POST /rate`, `POST /on_rate`
- `POST /support`, `POST /on_support`

#### Catalog infrastructure

- `POST /catalog/publish`, `POST /catalog/on_publish`
- `POST /catalog/push`
- `POST|GET|DELETE /catalog/subscription`
- `POST /catalog/pull`, `POST /catalog/on_pull`
- `POST /catalog/search`

#### Master resource search

*The following endpoints are planned for a future release and are not yet defined in the canonical OpenAPI contract (`api/v2.0.0/beckn.yaml`).*

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

### Operation behavior and conformance requirements

- `context.try` semantics are used for preview and commit behavior in selected flows, limited to `update` and `cancel`.
- Catalog publishing actions may support alias forms such as `catalog/publish` and `catalog_publish` where defined in OpenAPI.
- Catalog pull is asynchronous and returns an immediate acknowledgement with request tracking metadata.
- Both network participants (CN and PN) MUST implement the complete set of action and callback endpoints. Endpoints are not exclusive to a specific actor: any action MAY be initiated by either node, so a node MUST be able to both originate and receive every action and its `on_*` callback.
- Implementations MUST treat `api/v2.0.0/beckn.yaml` as the canonical endpoint and payload contract.
- Implementations MUST enforce request signature validation and MUST verify the `Signature` response header on synchronous acknowledgements as defined in [NFH-007 §5](./Authentication_and_Trust.md).
- Catalog infrastructure endpoints MUST follow operation-specific constraints defined in OpenAPI, including parameter and response semantics.

### Security and compatibility considerations

Endpoint misuse, weak signature validation, or misinterpreted callback behavior can create spoofing and state inconsistency risks. Implementations SHOULD enforce strict request authentication, response integrity checks, and message correlation controls.

This RFC-format restructuring preserves the existing v2.0.0 endpoint interpretation intent. Compatibility questions that remain relevant to future revisions include whether alias action forms should be deprecated over a defined compatibility window and whether endpoint conformance profiles should be published as machine-readable test suites.

## Conclusion

This document normalizes the Beckn v2.0.0 endpoint surface into a single RFC-style interpretation guide while preserving the canonical OpenAPI contract, endpoint groupings, lifecycle semantics, and transport security expectations. The current draft reflects the migration of the endpoint guide into RFC structure as Draft-01 dated 2026-04-10.

## Acknowledgements

This document reflects the work of Beckn Protocol contributors and the implementation, testing, and certification working groups that support endpoint interoperability, conformance, and operational guidance.

## References

- Keyword definitions: Click [here](./Keyword_Definitions.md)
- Canonical OpenAPI contract: `api/v2.0.0/beckn.yaml` (Click [here](../api/v2.0.0/beckn.yaml))
