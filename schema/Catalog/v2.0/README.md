# Catalog Schema v2.0

This directory contains the Catalog schema for Beckn Protocol v2.0.

## Overview

The Catalog schema defines the structure for representing product and service catalogs published by providers on the Beckn network. A catalog contains items, offers, and associated metadata that enable discovery and selection.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Catalog
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Catalog Structure

A Catalog includes:

- **id** - Unique identifier for the catalog
- **descriptor** - Human-readable description and metadata
- **bppId** - BPP identifier that publishes this catalog
- **bppUri** - BPP URI endpoint
- **items** - Array of sellable items/services
- **offers** - Commercial offers with pricing and terms
- **providerId** - Reference to the provider
- **validity** - Time period for which the catalog is valid
- **isActive** - Whether the catalog is currently active

## Key Entities

- **Item** - Individual products, services, or offerings
- **Offer** - Pricing, terms, and conditions for items
- **Provider** - Entity that owns and operates the catalog

## Usage

Catalogs are returned in response to `search` queries via the `on_search` callback. They enable consumers to discover available products and services on the network.

## Version

Current version: 2.0
