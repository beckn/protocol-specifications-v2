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
| [`discover.json`](./discover.json) | BAP discovers pizzas using `message.intent.textSearch` (minimal example) |
| [`discover_01_text_veg_pizza.json`](./discover_01_text_veg_pizza.json) | Free-text search for vegetarian pizza in Bangalore |
| [`discover_02_text_nonveg_pizza.json`](./discover_02_text_nonveg_pizza.json) | Free-text search for non-veg chicken pizza |
| [`discover_03_text_pizza_mania.json`](./discover_03_text_pizza_mania.json) | Free-text search for budget pizza under ₹100 |
| [`discover_04_filter_veg_only.json`](./discover_04_filter_veg_only.json) | JSONPath filter for vegetarian-only items |
| [`discover_05_filter_price_range.json`](./discover_05_filter_price_range.json) | JSONPath filter for items in price range ₹100–₹400 |
| [`discover_06_text_sides_desserts.json`](./discover_06_text_sides_desserts.json) | Free-text search for sides and desserts |
| [`discover_07_text_beverages.json`](./discover_07_text_beverages.json) | Free-text search for cold drinks |
| [`discover_08_spatial_koramangala.json`](./discover_08_spatial_koramangala.json) | Spatial search (S_DWITHIN 2 km) combined with free-text |
| [`discover_09_filter_nonveg_chicken.json`](./discover_09_filter_nonveg_chicken.json) | JSONPath filter for non-veg chicken pizza category |
| [`discover_10_text_late_night.json`](./discover_10_text_late_night.json) | Free-text search for late-night pizza delivery in Indiranagar |

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

### Intent with `filters`

```json
{
  "message": {
    "intent": {
      "filters": {
        "type": "jsonpath",
        "expression": "$[?(@.itemAttributes['@type'] == 'beckn:RetailCoreItemAttributes' && @.itemAttributes.food.classification == 'VEG')]"
      }
    }
  }
}
```

> **Key pattern:** Because the CDS indexes catalogs from all sectors (food, mobility, jobs, etc.), a `filters.expression` that accesses `itemAttributes` sub-properties MUST first qualify the item type with an `itemAttributes['@type']` guard. Without the type guard, the path `@.itemAttributes.food.classification` is ambiguous across heterogeneous catalogs.

### Intent with `spatial`

```json
{
  "message": {
    "intent": {
      "textSearch": "pizza near me",
      "spatial": [
        {
          "op": "S_DWITHIN",
          "targets": "$['locations'][*]['geo']",
          "geometry": {
            "type": "Point",
            "coordinates": [77.6245, 12.9352]
          },
          "distanceMeters": 2000
        }
      ]
    }
  }
}
```

[`Intent/v2.0`](https://schema.beckn.io/Intent/v2.0) supports:
- `textSearch` — free-text query string
- `filters` — JSONPath-based filters on catalog fields
- `spatial` — array of [`SpatialConstraint/v2.0`](https://schema.beckn.io/SpatialConstraint/v2.0) using OGC CQL2 operators
- `media_search` — media-based search

> **Note:** `Intent/v2.0` uses `additionalProperties: false`. Only the four properties above are permitted in `message.intent`.

## Schema compliance notes

All examples conform to [`DiscoverAction/v2.0`](https://schema.beckn.io/DiscoverAction/v2.0):

- `context.messageId` and `context.transactionId` are valid UUID v4 strings (format: `uuid`)
- `message.intent` contains only schema-permitted properties (`textSearch`, `filters`, `spatial`, `media_search`)
- `spatial` constraints use the [`SpatialConstraint/v2.0`](https://schema.beckn.io/SpatialConstraint/v2.0) structure: `op` (OGC CQL2 enum), `targets` (JSONPath string), `geometry` (GeoJSON), and `distanceMeters` (number, metres) for `S_DWITHIN`

## Scenario context

This example set is part of the end-to-end Beckn v2.0 retail flow:

> **Consumer** (`food-app.example.com`) searches for pizza → **BPP** (`tomato.com`) returns a catalog of Domino's India items and offers.

| Field | Value |
|---|---|
| BAP | `food-app.example.com` |
| BPP | `tomato.com` |
| Transaction IDs | Per-file UUIDs (see each file) |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/on_discover` | [`../on_discover/`](../on_discover/) | BPP response with catalog |
| `beckn/select` | [`../select/`](../select/) | BAP selects an offer |
