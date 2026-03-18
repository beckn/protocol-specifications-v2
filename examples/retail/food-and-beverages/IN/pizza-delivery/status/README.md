# `beckn/status` — Retail Examples

## Endpoint

`POST /beckn/status`

**Direction:** BAP → BPP  
**Schema:** [`StatusAction/v2.0`](https://schema.beckn.io/StatusAction/v2.0)

## Purpose

The `status` action is sent by a BAP to a BPP to poll the current state of an active order. Only the contract `id` (UUID) is required.

## Files in this folder

| File | Description |
|---|---|
| [`status.json`](./status.json) | BAP polls order status using `message.order.id` |

## Key patterns

### Minimal status request

```json
{
  "message": {
    "order": {
      "id": "f7a8b9c0-d1e2-4f3a-b5c6-789012345678"
    }
  }
}
```

[`StatusAction/v2.0`](https://schema.beckn.io/StatusAction/v2.0) requires only the contract UUID in `message.order.id`. No other fields are needed.

## Scenario context

| Field | Value |
|---|---|
| Contract ID | `f7a8b9c0-d1e2-4f3a-b5c6-789012345678` |
| Transaction ID | `txn-0001-2026-retail-pizza` |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/on_confirm` | [`../on_confirm/`](../on_confirm/) | Source of the contract ID |
| `beckn/on_status` | [`../on_status/`](../on_status/) | BPP response with fulfillment state |
