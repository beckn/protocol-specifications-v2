# `beckn/on_discover` — Retail Examples

## Endpoint

`POST /beckn/on_discover`

**Direction:** BPP → BAP  
**Schema:** [`OnDiscoverAction/v2.0`](https://schema.beckn.io/OnDiscoverAction/v2.0)

## Purpose

The `on_discover` response is sent by a BPP to a BAP in reply to a `discover` request. It carries `message.catalogs[]` — one catalog per provider — containing `items[]` and `offers[]` that match the search intent.

## Files in this folder

| File | Description |
|---|---|
| [`on_discover.json`](./on_discover.json) | Full Domino's India catalog via Zomato — explicit `@context` on every attribute pack object |
| [`on_discover_explicit_context.json`](./on_discover_explicit_context.json) | Same as `on_discover.json` — alias with descriptive name |
| [`on_discover_implicit_context.json`](./on_discover_implicit_context.json) | Same catalog with `@context` omitted from `itemAttributes` and `offerAttributes` — relies on context inheritance from parent objects |

## Catalog structure

```
Catalog (catalog-dominos-india-blr-001)
 ├── BPP: zomato.com
 ├── Provider: provider-dominos-india (Domino's India)
 │    └── Locations: MG Road · Koramangala · Indiranagar (Bangalore)
 ├── items[] — 25 items across 8 categories
 │    ├── VEG_PIZZA (7): Margherita, Double Cheese Margherita, Farmhouse, Peppy Paneer,
 │    │                   Veggie Paradise, Mexican Green Wave, Veg Extravaganza
 │    ├── NON_VEG_PIZZA (4): Chicken Dominator, Chicken Pepperoni, Chicken Fiesta,
 │    │                       Keema Do Pyaza
 │    ├── PIZZA_MANIA (3): Tomato, Paneer & Onion, Chicken Sausage
 │    ├── SIDES (3): Garlic Breadsticks, Stuffed Garlic Breadsticks, Crinkle Fries
 │    ├── SPECIALITY_CHICKEN (2): Boneless Chicken Wings Peri-Peri,
 │    │                            Chicken Meatballs Peri-Peri Sauce
 │    ├── DESSERTS (2): Choco Lava Cake, Brownie Fantasy
 │    ├── BEVERAGES (2): Pepsi 300ml, 7UP 300ml
 │    └── DIPS (2): Cheesy Dip, Cheesy Jalapeno Dip
 └── offers[] — 41 offers
      ├── Pizzas: 3 offers per pizza (Regular / Medium / Large) with size-specific pricing
      └── Non-pizza items: 1 offer per item (flat price)
```

## Key schema patterns

### Catalog with items + offers (flat structure)

```json
{
  "@context": "https://schema.beckn.io/",
  "@type": "beckn:Catalog",
  "id": "catalog-dominos-india-blr-001",
  "providerId": "provider-dominos-india",
  "items": [ ... ],
  "offers": [ ... ]
}
```

[`Catalog/v2.0`](https://schema.beckn.io/Catalog/v2.0) is flat — no nested provider hierarchy. Each [`Item/v2.0`](https://schema.beckn.io/Item/v2.0) carries its own `provider` reference.

### Item with `itemAttributes`

```json
{
  "@context": "https://schema.beckn.io/",
  "@type": "beckn:Item",
  "id": "item-veg-margherita",
  "itemAttributes": {
    "@context": "https://schema.beckn.io/",
    "@type": "beckn:RetailCoreItemAttributes",
    "food": { "classification": "VEG" },
    "identity": { "brand": "Domino's India" }
  }
}
```

Domain attributes live in `itemAttributes` typed as [`beckn:RetailCoreItemAttributes`](https://schema.beckn.io/RetailCoreItem/v2.0).

### Offer with price + `offerAttributes`

```json
{
  "@context": "https://schema.beckn.io/",
  "@type": "beckn:Offer",
  "id": "offer-margherita-regular",
  "items": ["item-veg-margherita"],
  "price": {
    "currency": "INR",
    "value": 395,
    "components": [{ "type": "UNIT", "value": 395, "currency": "INR" }]
  },
  "offerAttributes": {
    "@context": "https://schema.beckn.io/",
    "@type": "beckn:RetailCoreOfferAttributes",
    "policies": {
      "cancellation": { "allowed": true, "window": "PT30M", "cutoffEvent": "BEFORE_PACKING" },
      "replacement": { "allowed": true, "window": "PT30M", "method": "SELLER_PICKUP" }
    },
    "serviceability": { "distanceConstraint": { "maxDistance": 5, "unit": "KM" } }
  }
}
```

Pricing uses [`PriceSpecification/v2.0`](https://schema.beckn.io/PriceSpecification/v2.0). Retail policies and serviceability use [`beckn:RetailCoreOfferAttributes`](https://schema.beckn.io/RetailCoreOffer/v2.0).

### Size variants as separate Offers

Domino's pizzas come in Regular (₹395), Medium (₹595), Large (₹795) variants. Each size is a separate `Offer` object pointing to the same `Item`:

```
item-veg-margherita
  ← offer-margherita-regular  (INR 395, ~7 inch, serves 1)
  ← offer-margherita-medium   (INR 595, ~10 inch, serves 2–3)
  ← offer-margherita-large    (INR 795, ~13 inch, serves 3–4)
```

### Explicit vs implicit `@context` on attribute packs

| Variant | `@context` on `itemAttributes`/`offerAttributes` | JSON-LD behaviour |
|---|---|---|
| `on_discover.json` | ✓ Present | Attribute pack terms fully resolved — domain-specific properties mapped to `beckn:` IRIs |
| `on_discover_implicit_context.json` | ✗ Absent | Core terms inherited from parent context; domain-specific property terms (`cutoffEvent`, `distanceConstraint`, etc.) remain unmapped |

### Provider locations as `beckn:Location` objects

```json
{
  "@type": "beckn:Location",
  "id": "store-dominos-blr-mgroad",
  "geo": { "type": "Point", "coordinates": [77.5946, 12.9716] },
  "address": {
    "streetAddress": "No. 15, Ground Floor, MG Road",
    "addressLocality": "Bangalore",
    "postalCode": "560001",
    "addressCountry": "IN"
  }
}
```

GeoJSON coordinate order is **[longitude, latitude]** (RFC 7946). Address uses `schema.org PostalAddress` field names.

## Scenario context

| Field | Value |
|---|---|
| BAP | `food-app.example.com` |
| BPP | `zomato.com` |
| Provider | Domino's India (`provider-dominos-india`) |
| Transaction ID | `txn-0001-2026-dominos-pizza` |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/discover` | [`../discover/`](../discover/) | BAP search request |
| `beckn/select` | [`../select/`](../select/) | BAP selects an offer from this catalog |
