# Ack Schema v2.0

This directory contains the Acknowledgment (Ack) schema for Beckn Protocol v2.0.

## Overview

The AckResponse schema defines the synchronous acknowledgment structure returned by receivers upon receiving a request. It indicates whether the request was accepted for processing or rejected due to errors.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Ack responses
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Ack Response Structure

The acknowledgment response contains:

- **ackStatus** - Status of acknowledgment (ACK or NACK)
- **error** - Error details (required when ackStatus is NACK)
- **timestamp** - Timestamp of the acknowledgment
- **transactionId** - Transaction identifier from the request context

## Status Values

- **ACK** - Request accepted for processing
- **NACK** - Request rejected (must include error details)

## Usage

Every asynchronous API call in Beckn Protocol receives an immediate AckResponse. This indicates whether the request was accepted and will be processed asynchronously, or was rejected due to validation or other errors.

## Version

Current version: 2.0
