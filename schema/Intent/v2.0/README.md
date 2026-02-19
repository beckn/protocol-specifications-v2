# Intent Schema v2.0

This directory contains the Intent schema for Beckn Protocol v2.0.

## Overview

The Intent schema defines the structure for expressing consumer search intent during catalog discovery. It allows consumers to specify what they are looking for using text queries, filters, spatial constraints, and multimodal inputs.

## Files

- `attributes.yaml` - OpenAPI schema definitions for Intent
- `context.jsonld` - JSON-LD context mapping
- `vocab.jsonld` - RDF vocabulary definitions
- `README.md` - This documentation file

## Intent Components

An Intent can include:

- **textSearch** - Free text search query
- **filters** - Structured filter criteria (JSONPath expressions)
- **spatial** - Spatial/geographic constraints (CQL2-JSON semantics)
- **media_search** - Multimodal search using images, audio, or video

## Search Capabilities

- **Text-based search** - Natural language queries
- **Filtered search** - Precise criteria matching (price, rating, category, etc.)
- **Geographic search** - Location-based discovery using GeoJSON geometries
- **Image search** - Visual similarity and object detection
- **Audio/Video search** - Semantic matching and transcription

## Usage

Intent is primarily used in the `search` API call to express what the consumer is looking for. The BPP processes the intent and returns matching catalog items in the `on_search` response.

## Version

Current version: 2.0
