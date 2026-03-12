# `beckn/on_init` — Retail Examples

## Endpoint

`POST /beckn/on_init`

**Direction:** BPP → BAP  
**Schema:** [`OnInitAction/v2.0`](https://schema.beckn.io/OnInitAction/v2.0)

## Purpose

The `on_init` response is sent by a BPP to a BAP in reply to an `init` request. It confirms payment terms, delivery SLA, and sets the contract status to `DRAFT`. The consumer can now proceed to payment and confirmation.

## Files in this folder

| File | Description |
|---|---|
| [`on_init.json`](./on_init.json) | BPP confirms payment terms (UPI/COD), 30-min SLA; contract status: `DRAFT` |

## Key patterns

### Contract status `DRAFT`

```json
{
  "contract": {
    "status": "DRAFT",
    "contractValue": {
      "currency": "INR",
      "value": 638
    }
  }
}
```

### Payment terms in `entitlements[]`

The BPP may include accepted payment methods and payment endpoint details in the contract's entitlements.

### Fulfillment SLA confirmed

The BPP confirms the delivery window in `fulfillments[].mode.modeAttributes.sla`.

## Scenario context

| Field | Value |
|---|---|
| Contract status | `DRAFT` |
| Total | INR 638 |
| Payment methods | UPI, COD, Cards |
| Delivery SLA | 25–45 minutes from order confirmation |

## Related endpoints

| Endpoint | Folder | Description |
|---|---|---|
| `beckn/init` | [`../init/`](../init/) | BAP request that triggered this response |
| `beckn/confirm` | [`../confirm/`](../confirm/) | Next step — BAP submits payment proof |
