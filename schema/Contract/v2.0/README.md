# Contract Schema v2.0

## Overview

The **Contract** schema represents a purchase agreement containing items, pricing, and fulfillment details in the Beckn Protocol v2.1. This schema has been relocated from `common_schema/Order` and renamed to better reflect its role as a contractual agreement between consumer and provider.

## Schema Structure

### Core Components

- **attributes.yaml**: OpenAPI 3.1.1 schema definition for Contract
- **context.jsonld**: JSON-LD context mapping for Contract properties
- **vocab.jsonld**: Vocabulary definitions and semantic relationships

## Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `@context` | URI | JSON-LD context reference |
| `@type` | string | Must be "Contract" |
| `consumer` | Consumer | The consumer entity (person or organization) |
| `provider` | Provider | The provider entity offering the service/product |
| `contractItems` | OrderItem[] | Line items included in the contract |
| `contractStatus` | enum | Current status of the contract |
| `contractNumber` | string | Human-readable contract identifier |
| `contractValue` | PriceSpecification | Total value of the contract |
| `fulfillments` | Fulfillment[] | Fulfillment methods for delivering the contract |
| `invoices` | Invoice[] | Associated invoices |
| `paymentTerms` | PaymentTerms | Payment agreement terms |
| `paymentAction` | PaymentAction | Payment execution details |
| `participants` | Participant[] | Additional participants in the contract |
| `policies` | Policy[] | Applicable policies (cancellation, refund, etc.) |
| `contractDocs` | Document[] | Supporting documents |
| `contractAttributes` | Attributes | Domain-specific attribute pack |

## Contract Status Values

The `contractStatus` property supports the following lifecycle states:

- `UNDER_NEGOTIATION` - Terms are being negotiated
- `CREATED` - Contract has been created
- `PENDING` - Awaiting approval/processing
- `CONFIRMED` - Contract confirmed by all parties
- `INPROGRESS` - Contract execution in progress
- `PARTIALLYFULFILLED` - Partially completed
- `COMPLETED` - Fully executed
- `CANCELLED` - Contract cancelled
- `REJECTED` - Contract rejected
- `FAILED` - Contract execution failed
- `RETURNED` - Goods/services returned
- `REFUNDED` - Payment refunded
- `ONHOLD` - Contract temporarily suspended

## IRI Mappings

All Contract-related IRIs use the `beckn:` namespace:

- `beckn:Contract` - The Contract class
- `beckn:contractStatus` - Contract status property
- `beckn:contractNumber` - Contract number property
- `beckn:contractValue` - Contract value property
- `beckn:contractItems` - Contract items property
- `beckn:contractAttributes` - Contract attributes property
- `beckn:contractDocs` - Contract documents property
- `beckn:contractDescriptor` - Contract descriptor property

## Usage Example

```json
{
  "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/context.jsonld",
  "@type": "Contract",
  "id": "contract-123",
  "contractNumber": "CNT-2024-001",
  "contractStatus": "CONFIRMED",
  "consumer": {
    "@type": "beckn:Consumer",
    "person": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "provider": {
    "id": "provider-456",
    "descriptor": {
      "name": "Example Provider Inc."
    }
  },
  "contractItems": [
    {
      "lineId": "line-1",
      "itemId": "item-789",
      "quantity": {
        "unitQuantity": 2
      }
    }
  ],
  "contractValue": {
    "currency": "USD",
    "value": 1500.00
  },
  "paymentTerms": {
    "collectedBy": "BPP",
    "checkoutAt": "BPP_CHECKOUT"
  }
}
```

## Migration from Order Schema

This schema was previously located at `common_schema/Order/v2.0/`. Key changes:

1. **Location**: Moved from `common_schema/Order` to `schema/Contract`
2. **Naming**: All "Order" references renamed to "Contract"
3. **IRI Updates**: All IRIs updated to use Contract terminology
4. **Semantics**: Better reflects the contractual nature of the agreement

## Related Schemas

- **Consumer**: Consumer/buyer entity
- **Provider**: Service/product provider
- **OrderItem**: Line items within the contract
- **Fulfillment**: Delivery/execution methods
- **Invoice**: Billing documents
- **PaymentTerms**: Payment agreement
- **PaymentAction**: Payment execution
- **Participant**: Additional contract participants

## Version History

- **v2.0** (2024): Initial version as Contract schema (migrated from Order)
  - Renamed from Order to Contract
  - Updated all IRIs and property names
  - Maintained backward compatibility through vocabulary mappings
