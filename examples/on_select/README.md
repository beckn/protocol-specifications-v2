# `beckn/on_select` — Retail Examples

## Endpoint

`POST /beckn/on_select`

**Direction:** BPP → BAP  
**Schema:** [`OnSelectAction/v2.0`](https://schema.beckn.io/OnSelectAction/v2.0)

## Purpose

The `on_select` response is sent by a BPP to a BAP in reply to a `select` request. It returns an updated `contract` with:
- `contractValue` — total price breakdown (items + delivery fee)
- `fulfillments[].stages[]` — delivery ETAs (pickup and drop-off times)

## Files in this folder

| File | Description |
|---|---|
| [`on_select.json`](./on_select.json) | BPP returns pricing (INR 638) and delivery ETA for 2× Margherita Pizza |

## Key patterns

### `contractValue` with price breakdown

```json
{
  "contractValue": {
    "currency": "INR",
    "value": 638,
    "components": [
      { "type": "UNIT", "value": 598, "currency": "INR", "description": "2x Margherita Pizza" },
      { "type": "DELIVERY", "value": 40, "currency": "INR", "description": "Delivery fee" }
    ]
  }
}
```

### Fulfillment with stage endpoints and ETAs

The BPP populates `fulfillments[].stages[].start.time` and `end.time` with pickup and delivery windows.

### Fulfillment `modeAttributes` for SLA

```json
{
  "modeAttributes": {
    "@context": "https://schema.beckn.io/",
    "@type": "beckn:RetailCoreFulfillmentAttributes",
    "supportedFulfillmentTypes": ["DELIVERY"],
    "sla": { "min": "PT25M", "max": "PT45M", "unitBasis": "ORDER_CONFIRMATION" }
  }
}
```

## Scenario context

| Field | Value |
|---|---|
| Consumer | Arjun Sharma (`arjun.sharma@pizza-app.example.com`) |
| Provider | Pizzeria Roma — MG Road, Bangalore |
| Items | 2× Margherita Pizza @ INR 299 = INR 598 |
| Delivery Fee | INR 40 |
| Total | INR 638 |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/select` | [`../select/`](../select/) | BAP selection that triggered this response |
| `beckn/init` | [`../init/`](../init/) | Next step — BAP submits consumer details |
