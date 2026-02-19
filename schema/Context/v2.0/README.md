# Context Schema v2.0

This directory contains the Context schema for Beckn Protocol v2.0.

## Overview

Every API call in beckn protocol has a context. It provides a high-level overview to the receiver about the nature of the intended transaction. Typically, it is the BAP that sets the transaction context based on the consumer's location and action on their UI.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Context
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Context Fields

The context object contains four types of fields:

1. **Demographic information** - Fields like `domain`, `country`, and `region`
2. **Addressing details** - Sending and receiving platform's ID and API URL
3. **Interoperability information** - Protocol version implemented by the sender
4. **Transaction details** - Method, transaction_id, message_id, timestamp, ttl, and encryption key

## Usage

This object must be passed in every interaction between a BAP and a BPP. In HTTP/S implementations, it is not necessary to send the context during the synchronous response. However, in asynchronous protocols, the context must be sent during all interactions.

## Version

Current version: 2.0
