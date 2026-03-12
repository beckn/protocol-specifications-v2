# `beckn/discover` — Retail Examples

## Endpoint

`POST /beckn/discover`

**Direction:** BAP → BPP  
**Schema:** [`DiscoverAction/v2.0`](https://schema.beckn.io/DiscoverAction/v2.0)

## Purpose

The `discover` action is sent by a BAP to a BPP to search for items, providers, or offers. The `message.intent` carries the search criteria — free-text, spatial, filters, or a combination.

## Files in this folder

| File | Description |
|---|---|
| [`discover.json`](./discover.json) | BAP discovers Domino's pizzas using `message.intent.textSearch` |

## Key patterns

### Intent with `textSearch`

```json
{
  "message": {
    "intent": {
      "textSearch": "Margherita Pizza near MG Road Bangalore"
    }
  }
}
```

[`Intent/v2.0`](https://schema.beckn.io/Intent/v2.0) supports:
- `textSearch` — free-text query string
- `filters` — JSONPath-based filters on catalog fields
- `spatial` — geographic bounding box or radius constraint

## Scenario context

This example is part of the end-to-end Beckn v2.0 retail flow:

> **Consumer** (`food-app.example.com`) searches for pizza → **BPP** (`zomato.com`) returns a catalog of Domino's India items and offers.

| Field | Value |
|---|---|
| BAP | `food-app.example.com` |
| BPP | `zomato.com` |
| Transaction ID | `txn-0001-2026-dominos-pizza` |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/on_discover` | [`../on_discover/`](../on_discover/) | BPP response with catalog |
| `beckn/select` | [`../select/`](../select/) | BAP selects an offer |
