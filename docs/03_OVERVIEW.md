# Beckn Protocol v2.0.0 Overview

## Value-exchange fabric first

Beckn v2.0.0 is a protocol for open value exchange across independently operated participants.

The protocol is designed as infrastructure fabric:
- interoperable transport contract,
- cryptographic trust and non-repudiation,
- asynchronous action-callback communication,
- domain-extensible payload models.

## Core actor model

A Beckn network composes these roles:
- BAP (demand-side applications)
- BPP (supply-side applications)
- PS (catalog publishing)
- DS (catalog discovery)
- Registry (identity, endpoint, key discovery)

## API model in this repository

The authoritative API profile is defined in:
- ../api/v2.0.0/beckn.yaml

This profile is action-specific and endpoint-explicit. It does not use a single universal path token in the transport contract.

## Action groups

- Discovery: /discover, /on_discover
- Contracting: /select, /on_select, /init, /on_init, /confirm, /on_confirm
- Fulfillment: /status, /on_status, /track, /on_track, /update, /on_update, /cancel, /on_cancel
- Post-fulfillment: /rate, /on_rate, /support, /on_support
- Catalog publishing: /catalog/publish, /catalog/on_publish
- Catalog extension APIs:
  - /catalog/subscription, /catalog/subscriptions, /catalog/subscription/{subscriptionId}
  - /catalog/pull, /catalog/pull/result/{requestId}/{filename}
  - /catalog/master/search, /catalog/master/schemaTypes, /catalog/master/{masterItemId}

## Transport guarantees

- Every request is signed in Authorization.
- Ack includes CounterSignature.
- Context carries the action and routing identity.
- Asynchronous callbacks are first-class in the protocol lifecycle.
- context.try supports safe simulation flows for update/cancel/rate/support.

## Scope of use

Designed for interoperable value exchange across retail, mobility, logistics, energy, healthcare, skilling, financial services, carbon, hiring, data licensing, and related domains.
