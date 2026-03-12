# `beckn/on_confirm` — Retail Examples

## Endpoint

`POST /beckn/on_confirm`

**Direction:** BPP → BAP  
**Schema:** [`OnConfirmAction/v2.0`](https://schema.beckn.io/OnConfirmAction/v2.0)

## Purpose

The `on_confirm` response is sent by a BPP to a BAP confirming that the order has been accepted and placed. The BPP assigns a contract `id` (UUID) and `displayId` (human-readable order number). The contract status becomes `ACTIVE`.

## Files in this folder

| File | Description |
|---|---|
| [`on_confirm.json`](./on_confirm.json) | BPP assigns order ID and `displayId`; contract status: `ACTIVE` |

## Key patterns

### Contract with `id`, `displayId`, and status `ACTIVE`

```json
{
  "contract": {
    "id": "f7a8b9c0-d1e2-4f3a-b5c6-789012345678",
    "displayId": "ORD-20260310-001",
    "status": "ACTIVE",
    "contractValue": { "currency": "INR", "value": 638 }
  }
}
```

The `id` is the stable UUID used for all subsequent `status`, `cancel`, and `support` calls. The `displayId` is what's shown to the consumer.

## Scenario context

| Field | Value |
|---|---|
| Contract ID | `f7a8b9c0-d1e2-4f3a-b5c6-789012345678` |
| Display ID | `ORD-20260310-001` |
| Status | `ACTIVE` |
| Total | INR 638 |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/confirm` | [`../confirm/`](../confirm/) | BAP confirmation that triggered this response |
| `beckn/status` | [`../status/`](../status/) | Next step — BAP polls order status |
