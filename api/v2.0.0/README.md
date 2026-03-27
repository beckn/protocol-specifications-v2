# Beckn Protocol API v2.0.0

This directory contains the OpenAPI 3.1.1 definition for the Beckn v2.0.0 transport contract.

## Files

- beckn.yaml: authoritative API specification
- README.md: implementation guide for this API package

## API design summary

The specification uses one named endpoint per Beckn protocol action.

Primary action groups:
- Discovery
- Transaction
- Fulfillment
- Post-Fulfillment
- Catalog Publishing
- Subscription
- Catalog Pull
- Master Resource Search

## Endpoint families

Discovery:
- /discover
- /on_discover

Transaction:
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

Catalog publishing:
- /catalog/publish
- /catalog/on_publish

Catalog extensions:
- /catalog/subscription
- /catalog/subscriptions
- /catalog/subscription/{subscriptionId}
- /catalog/pull
- /catalog/pull/result/{requestId}/{filename}
- /catalog/master/search
- /catalog/master/schemaTypes
- /catalog/master/{masterItemId}

## Security and acknowledgments

- Requests require Beckn HTTP Signature in Authorization.
- Ack includes CounterSignature.
- Error responses follow NackBadRequest, NackUnauthorized, and ServerError schemas.

## Operational notes

- context.action must match endpoint semantics.
- context.try is supported for sandbox behavior in update/cancel/rate/support flows.
- Callbacks are protocol-native and must be implemented for asynchronous action pairs.
