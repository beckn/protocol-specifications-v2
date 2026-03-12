# `beckn/confirm` — Retail Examples

## Endpoint

`POST /beckn/confirm`

**Direction:** BAP → BPP  
**Schema:** [`ConfirmAction/v2.0`](https://schema.beckn.io/ConfirmAction/v2.0)

## Purpose

The `confirm` action is sent by a BAP to a BPP to place the order. The BAP includes payment proof (transaction ID, payment method) in `contract.entitlements[]`. The contract transitions to `ACTIVE` upon BPP acknowledgement.

## Files in this folder

| File | Description |
|---|---|
| [`confirm.json`](./confirm.json) | BAP confirms the order with UPI payment proof in `entitlements[]` |

## Key patterns

### Payment proof in `entitlements[]`

```json
{
  "contract": {
    "entitlements": [
      {
        "@context": "https://schema.beckn.io/",
        "@type": "beckn:Entitlement",
        "descriptor": { "@type": "beckn:Descriptor", "name": "UPI Payment" },
        "type": "PAYMENT",
        "proof": {
          "transactionId": "upi-txn-20260310-001",
          "method": "UPI",
          "amount": { "currency": "INR", "value": 638 }
        }
      }
    ]
  }
}
```

[`Entitlement/v2.0`](https://schema.beckn.io/Entitlement/v2.0) carries payment receipts, vouchers, credentials, and other proof objects.

## Scenario context

| Field | Value |
|---|---|
| Payment method | UPI |
| Amount | INR 638 |
| Transaction ID | `txn-0001-2026-retail-pizza` |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/on_init` | [`../on_init/`](../on_init/) | Payment terms accepted before confirm |
| `beckn/on_confirm` | [`../on_confirm/`](../on_confirm/) | BPP assigns order ID; contract becomes ACTIVE |
