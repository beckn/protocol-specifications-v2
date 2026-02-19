# Message Schema v2.0

This directory contains the Message schema for Beckn Protocol v2.0.

## Overview

Message schemas define the payload structures for all API interactions in the Beckn Protocol. Messages are exchanged between BAPs (Beckn Application Platforms) and BPPs (Beckn Provider Platforms) to facilitate discovery, ordering, fulfillment, and post-fulfillment operations.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Message payloads
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Message Types

Messages in Beckn Protocol include:

- **Discovery Messages** - search, on_search
- **Order Messages** - select, on_select, init, on_init, confirm, on_confirm
- **Fulfillment Messages** - status, on_status, track, on_track
- **Post-Fulfillment Messages** - update, on_update, cancel, on_cancel
- **Support Messages** - support, on_support
- **Rating Messages** - rating, on_rating

## Usage

Each message contains a context object and a message-specific payload. The context provides transaction metadata while the message payload contains the business data.

## Version

Current version: 2.0
