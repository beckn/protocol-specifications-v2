# `beckn/init` — Retail Examples

## Endpoint

`POST /beckn/init`

**Direction:** BAP → BPP  
**Schema:** [`InitAction/v2.0`](https://schema.beckn.io/InitAction/v2.0)

## Purpose

The `init` action is sent by a BAP to a BPP to submit consumer identity details and finalize fulfillment preferences before payment. The contract moves toward `DRAFT` status.

## Files in this folder

| File | Description |
|---|---|
| [`init.json`](./init.json) | BAP submits Arjun Sharma's name, phone, email, and confirmed delivery address |

## Key patterns

### Consumer details in `participants[]`

```json
{
  "participants": [
    {
      "@context": "https://schema.beckn.io/",
      "@type": "beckn:Participant",
      "id": "arjun.sharma@pizza-app.example.com",
      "role": "consumer",
      "displayName": "Arjun Sharma",
      "contact": {
        "phone": "+919876543210",
        "email": "arjun.sharma@pizza-app.example.com"
      }
    }
  ]
}
```

### Confirmed delivery address in fulfillment stage

The BAP confirms the delivery endpoint (the consumer's address) in `fulfillments[].stages[].end.location`.

## Scenario context

| Field | Value |
|---|---|
| Consumer | Arjun Sharma (`arjun.sharma@pizza-app.example.com`) |
| Delivery | Apt 204, Sunrise Heights, 12 MG Road, Bangalore |
| Transaction ID | `txn-0001-2026-retail-pizza` |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/on_select` | [`../on_select/`](../on_select/) | Pricing accepted before init |
| `beckn/on_init` | [`../on_init/`](../on_init/) | BPP confirms payment terms |
