# Action Schema v2.0

This directory contains the Action enumeration schema for Beckn Protocol v2.0.

## Overview

The Action schema defines all standard protocol actions supported by Beckn Protocol. It provides a centralized enumeration of actions that occur throughout the transaction lifecycle.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Action enumerations
- `context.jsonld` - JSON-LD context mapping for semantic interoperability
- `vocab.jsonld` - RDF vocabulary definitions for action terms
- `README.md` - This documentation file

## Action Categories

### Discovery Actions
- **discover** - Discover catalogs on a network
- **on_discover** - Callback response to discover request

### Ordering Actions
- **select** - BAP requests for quote
- **on_select** - BPP sends quote with optional additional forms
- **init** - BAP requests final draft order with terms
- **on_init** - BPP sends final draft of order with terms of service
- **confirm** - BAP confirms the order
- **on_confirm** - BPP sends confirmed order

### Fulfillment Actions
- **status** - BAP requests latest state of the order
- **on_status** - BPP sends the latest state of the order
- **update** - Request to update an active order
- **on_update** - BPP sends updated order with updated terms
- **cancel** - Request to cancel an order
- **on_cancel** - Provider returns cancelled order
- **track** - Track order in real-time
- **on_track** - Send real-time tracking handles

### Post-fulfillment Actions
- **rate** - Rate any aspect of an order
- **on_rate** - Provider acknowledges/returns rating receipt
- **support** - Request support details
- **on_support** - Provider returns support details

### Catalog Publishing Actions
- **catalog/publish** - Publish one or more catalogs for indexing
- **catalog/on_publish** - Callback with catalog publish processing results

## Usage

The Action enumeration is referenced in the Context schema's `action` property. Every API call in Beckn Protocol must specify the action being performed.

## Extensibility

While this schema defines the standard actions, implementations may add domain-specific actions as needed. The schema allows additional enumeration values to support evolving use cases.

## Version

Current version: 2.0
