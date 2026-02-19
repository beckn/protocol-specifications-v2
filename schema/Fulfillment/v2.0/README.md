# Fulfillment Schema v2.0

This directory contains the Fulfillment schema for Beckn Protocol v2.0.

## Overview

The Fulfillment schema defines how orders are delivered or services are executed. It captures delivery methods, tracking information, agents involved, stages of fulfillment, and real-time status updates.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Fulfillment
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Fulfillment Structure

A Fulfillment includes:

- **id** - Unique fulfillment identifier
- **mode** - Mode of fulfillment (delivery, pickup, digital, etc.)
- **agent** - Entity performing the fulfillment (person, organization, system)
- **state** - Current state of fulfillment
- **stages** - Sequential stages with start/end locations and times
- **participants** - People entitled to receive the fulfillment
- **instructions** - Delivery or service instructions
- **trackingEnabled** - Whether tracking is available
- **fulfillmentAttributes** - Domain-specific attributes

## Fulfillment Modes

Common fulfillment modes include:

- **Delivery** - Physical delivery to a location
- **Pickup** - Consumer collects from a location
- **Digital** - Electronic/online delivery
- **Reservation** - Time-slot based service
- **In-Person** - Face-to-face service delivery

## Usage

Fulfillment details are included in orders and can be tracked using the `track` API. Status updates are provided via the `status` and `on_status` callbacks.

## Version

Current version: 2.0
