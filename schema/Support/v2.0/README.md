# Support Schema v2.0

This directory contains the Support schema for Beckn Protocol v2.0.

## Overview

The Support schema defines structures for customer support and issue resolution on the Beckn network. It enables consumers to get help, raise issues, and track support tickets throughout the transaction lifecycle.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Support
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Support Components

Support-related schemas include:

- **SupportInfo** - Contact information and support channels
  - Phone, email, URL, hours of operation
  - Available channels (PHONE, EMAIL, WEB, CHAT, WHATSAPP, IN_APP)
  
- **SupportTicket** - Issue tracking and resolution
  - Ticket ID and status
  - Issue description and category
  - Resolution details and history

- **Form** - Dynamic forms for information collection
  - Support request forms
  - Feedback forms
  - Issue reporting forms

## Support Channels

Available support channels include:

- **PHONE** - Telephone support
- **EMAIL** - Email support
- **WEB** - Web-based support portal
- **CHAT** - Live chat support
- **WHATSAPP** - WhatsApp messaging
- **IN_APP** - In-application support

## Usage

Support information is included in Provider and Order objects. The `support` API enables consumers to raise issues and get help. Support tickets track issue resolution progress.

## Version

Current version: 2.0
