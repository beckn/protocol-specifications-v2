# `beckn/select` — Retail Examples

## Endpoint

`POST /beckn/select`

**Direction:** BAP → BPP  
**Schema:** [`SelectAction/v2.0`](https://schema.beckn.io/SelectAction/v2.0)

## Purpose

The `select` action is sent by a BAP to a BPP to initiate a purchase intent. The BAP specifies which items/offers the consumer wants (via `message.contract.items[]`) and provides initial fulfillment preferences (delivery address, fulfillment type).

## Files in this folder

| File | Description |
|---|---|
| [`select.json`](./select.json) | BAP selects 2× Margherita Pizza with home delivery address |

## Key patterns

### Contract with `participants[]` and `items[]`

```json
{
  "message": {
    "contract": {
      "@type": "beckn:Contract",
      "participants": [
        { "@context": "https://schema.beckn.io/", "@type": "beckn:Participant",
          "id": "consumer@example.com", "role": "consumer" }
      ],
      "items": [
        { "itemId": "item-veg-margherita", "quantity": { "unitCode": "EA", "unitQuantity": 2 } }
      ]
    }
  }
}
```

[`Contract/v2.0`](https://schema.beckn.io/Contract/v2.0) requires `@type`, `participants[]`, and `items[]`. Items are [`ContractItem/v2.0`](https://schema.beckn.io/ContractItem/v2.0) objects with `itemId` (reference) and `quantity`.

### Fulfillment with delivery address

The `select` message sets the delivery endpoint via `contract.fulfillments[].stages[].end.location`.

## Scenario context

| Field | Value |
|---|---|
| Consumer | Arjun Sharma (`arjun.sharma@pizza-app.example.com`) |
| Provider | Pizzeria Roma — MG Road, Bangalore |
| BAP | `pizza-app.example.com` |
| BPP | `pizzeria-roma.example.com` |
| Items selected | 2× Margherita Pizza |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/on_discover` | [`../on_discover/`](../on_discover/) | Catalog from which items were selected |
| `beckn/on_select` | [`../on_select/`](../on_select/) | BPP response with pricing and delivery ETA |
