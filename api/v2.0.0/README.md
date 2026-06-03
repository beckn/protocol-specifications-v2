# Beckn Protocol API v2.0.0

This directory contains the OpenAPI 3.1.1 definition for the Beckn v2.0.0 transport contract.

## Files

- beckn.yaml: authoritative API specification
- README.md: implementation guide for this API package

## API design summary

The specification uses one named endpoint per Beckn protocol action.

Primary action groups:
- Discovery
- Contracting / Ordering
- Fulfillment
- Post-Fulfillment
- Fabric API - Cataloging Service

Endpoints are **not** exclusive to a specific actor. Any action MAY be initiated by either network participant (CN or PN), so **both nodes MUST implement the complete set of endpoints** — every action endpoint and its `on_*` callback. The action/callback pairing expresses message correlation, not a fixed assignment of which actor hosts which endpoint.

## Endpoint families

Discovery:
- /discover
- /on_discover

Contracting / Ordering:
- /select, /on_select
- /init, /on_init
- /confirm, /on_confirm

Fulfillment:
- /status, /on_status
- /track, /on_track
- /update, /on_update
- /cancel, /on_cancel

Post-Fulfillment:
- /rate, /on_rate
- /support, /on_support

Fabric API - Cataloging Service:
- /catalog/publish
- /catalog/on_publish
- /catalog/push
- /catalog/subscription
- /catalog/pull
- /catalog/on_pull
- /catalog/search

## Security and acknowledgments

- Requests require a Beckn HTTP Signature in the `Authorization` header.
- Synchronous `Ack` responses carry a `message` envelope with `status` (ACK/NACK) and the `messageId` of the received request.
- The responding actor signs the response payload and returns the signature in the `Signature` response header; the caller verifies this to confirm authenticated receipt.
- Error responses follow NackBadRequest, NackUnauthorized, and ServerError schemas.

## Operational notes

- context.action must match endpoint semantics.
- context.try is supported for sandbox behavior in update/cancel/rate/support flows.
- Callbacks are protocol-native and must be implemented for asynchronous action pairs.
