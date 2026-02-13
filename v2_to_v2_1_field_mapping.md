# Beckn Protocol v2.0 to v2.1 Field Mapping

## EV Charging on_confirm Example Conversion

This document provides a comprehensive field-by-field mapping from the v2.0 EV charging `on_confirm` payload to its v2.1 equivalent, showing ontological relationships and schema structure.

---

## Key Conversion Principles

### 1. **Compact Terms vs Full IRIs**
- v2.1 JSON uses **compact terms** (e.g., `"buyer"`, `"seller"`, `"price"`)
- These compact terms are defined in `updated.context.jsonld` and map to full IRIs
- Example: `"buyer"` → `"beckn:consumer"` (from context.jsonld)

### 2. **Ontological Relationships (from updated.vocab.jsonld)**
- **Deprecated properties**: `beckn:buyer` → `owl:equivalentProperty` → `beckn:consumer`
- **Deprecated classes**: `beckn:Buyer` → `owl:equivalentClass` → `beckn:PersonAsConsumer`
- **Schema.org proxies**: `beckn:price` → `owl:equivalentProperty` → `schema:price`

### 3. **Schema Structure (from beckn.yaml + attributes.yaml)**
- Container schemas define the structure (Order, Consumer, Provider, etc.)
- Attribute packs allow domain-specific extensions
- Type discriminators use `@type` for JSON-LD

---

## Field-by-Field Mapping

### Context Object

| v2.0 Field | v2.1 Field | IRI Mapping | Notes |
|------------|------------|-------------|-------|
| `context.version` | `context.version` | `beckn:version` | Changed from "2.0.0" to "2.1.0" |
| `context.action` | `context.action` | `beckn:action` | No change |
| `context.bap_id` | `context.bapId` | `beckn:bapId` | Camel case |
| `context.bap_uri` | `context.bapUri` | `beckn:bapUri` | Camel case |
| `context.transaction_id` | `context.transactionId` | `beckn:transactionId` | Camel case |
| `context.message_id` | `context.messageId` | `beckn:messageId` | Camel case |
| `context.bpp_id` | `context.bppId` | `beckn:bppId` | Camel case |
| `context.bpp_uri` | `context.bppUri` | `beckn:bppUri` | Camel case |

---

### Order Object

| v2.0 Field | v2.1 Field | IRI Mapping | Ontological Note |
|------------|------------|-------------|------------------|
| `order.beckn:id` | `order.id` | `beckn:id` | Compact term usage |
| `order.beckn:orderStatus` | `order.orderStatus` | `beckn:orderStatus` | Compact term; enum value unchanged |
| `order.beckn:seller` | `order.provider` | `beckn:provider` | **DEPRECATED**: `beckn:seller` → `owl:equivalentProperty` → `beckn:provider` |

**Order Structure Change:**
- v2.0: Flat structure with prefixed properties (`beckn:id`)
- v2.1: Uses `@context` and `@type` for JSON-LD typing

---

### Buyer → Consumer Transformation

**Major v2.1 Change**: `beckn:Buyer` class is deprecated in favor of `beckn:Consumer`

| v2.0 Structure | v2.1 Structure | Ontological Mapping |
|----------------|----------------|---------------------|
| `order.beckn:buyer` | `order.consumer` | `beckn:buyer` → `owl:equivalentProperty` → `beckn:consumer` |
| `beckn:Buyer` (class) | `beckn:Consumer` (class) | `beckn:Buyer` → `owl:equivalentClass` → `beckn:PersonAsConsumer` |

#### v2.0 Buyer Object
```json
"beckn:buyer": {
  "@context": "...",
  "@type": "beckn:Buyer",
  "beckn:id": "user-123",
  "beckn:role": "BUYER",
  "beckn:displayName": "Ravi Kumar",
  "beckn:telephone": "+91-9876543210",
  "beckn:email": "ravi.kumar@example.com",
  "beckn:taxID": "GSTIN29ABCDE1234F1Z5"
}
```

#### v2.1 Consumer Object
```json
"consumer": {
  "@context": "...",
  "@type": "Consumer",
  "role": "BUYER",
  "person": {
    "@context": "...",
    "@type": "Person",
    "id": "user-123",
    "name": "Ravi Kumar",
    "telephone": "+91-9876543210",
    "email": "ravi.kumar@example.com"
  },
  "consumerAttributes": {
    "@context": "https://example.org/consumer/tax-ids/v1/context.jsonld",
    "@type": "TaxIdentifiers",
    "taxID": "GSTIN29ABCDE1234F1Z5"
  }
}
```

**Key Changes:**
1. **Class structure**: `Buyer` is now `Consumer` (abstract) containing either `person` or `organization`
2. **displayName → name**: `beckn:displayName` → `owl:equivalentProperty` → `beckn:name`
3. **Attribute packs**: Domain-specific data moved to `consumerAttributes`
4. **Person object**: v2.1 uses `schema:Person` proxy for person data

---

### Buyer Field Mappings

| v2.0 Field | v2.1 Field | IRI Mapping | Ontological Note |
|------------|------------|-------------|------------------|
| `beckn:buyer` | `consumer` | `beckn:consumer` | Property deprecated and replaced |
| `beckn:Buyer` (type) | `Consumer` (type) | `beckn:Consumer` | Class type change |
| `beckn:id` | `person.id` | `beckn:id` → `schema:identifier` | Moved to Person object |
| `beckn:displayName` | `person.name` | `beckn:name` | **DEPRECATED**: `beckn:displayName` → `owl:equivalentProperty` → `beckn:name` |
| `beckn:telephone` | `person.telephone` | `beckn:telephone` → `schema:telephone` | Proxy to schema.org |
| `beckn:email` | `person.email` | `beckn:email` → `schema:email` | Proxy to schema.org |
| `beckn:taxID` | `consumerAttributes.taxID` | `beckn:taxID` | Moved to attribute pack |

---

### OrderItems

| v2.0 Field | v2.1 Field | IRI Mapping | Ontological Note |
|------------|------------|-------------|------------------|
| `beckn:orderedItem` | `itemId` | `beckn:itemId` | **CHANGED**: Context mapping `"orderedItem": "beckn:itemId"` |
| `beckn:quantity` | `quantity` | `beckn:quantity` | Compact term |
| `beckn:price` | `price` | `beckn:price` → `schema:price` | Proxy to schema.org |

#### Quantity Object Fields

| v2.0 Field | v2.1 Field | IRI Mapping | Ontological Note |
|------------|------------|-------------|------------------|
| `unitText` | `unitText` | `beckn:unitText` → `schema:unitText` | **PROXY**: `owl:equivalentProperty` → `schema:unitText` |
| `unitCode` | `unitCode` | `beckn:unitCode` → `schema:unitCode` | **PROXY**: `owl:equivalentProperty` → `schema:unitCode` |
| `unitQuantity` | `unitQuantity` | `beckn:unitQuantity` | Direct mapping |

---

### Price Specification

| v2.0 Field | v2.1 Field | IRI Mapping | Ontological Note |
|------------|------------|-------------|------------------|
| `currency` | `currency` | `beckn:currency` → `schema:priceCurrency` | Proxy via `rdfs:subPropertyOf` |
| `value` | `value` | `beckn:value` → `schema:price` | Value property |
| `applicableQuantity` | `applicableQuantity` | `beckn:applicableQuantity` → `schema:eligibleQuantity` | Via `rdfs:seeAlso` |

---

### Fulfillment Transformation

**Major v2.1 Change**: Fulfillment mode separated into structured object

| v2.0 Structure | v2.1 Structure | Schema Change |
|----------------|----------------|---------------|
| `beckn:fulfillment` (single) | `fulfillments` (array) | v2.1 allows multiple fulfillments |
| `beckn:mode` (string) | `mode` (object) | v2.1 uses `FulfillmentMode` schema |
| `beckn:deliveryAttributes` | `mode.modeAttributes` | Domain-specific attributes moved |

#### v2.0 Fulfillment
```json
"beckn:fulfillment": {
  "beckn:id": "fulfillment-001",
  "beckn:mode": "RESERVATION",
  "beckn:deliveryAttributes": {
    "@type": "ChargingSession",
    "connectorType": "CCS2",
    "maxPowerKW": 50,
    "sessionStatus": "PENDING"
  }
}
```

#### v2.1 Fulfillment
```json
"fulfillments": [
  {
    "@context": "...",
    "@type": "Fulfillment",
    "id": "fulfillment-001",
    "mode": {
      "@context": "...",
      "@type": "FulfillmentMode",
      "id": "RESERVATION",
      "modeAttributes": {
        "@context": "https://.../EvChargingSession/v1/context.jsonld",
        "@type": "ChargingSession",
        "connectorType": "CCS2",
        "maxPowerKW": 50,
        "sessionStatus": "PENDING"
      }
    }
  }
]
```

---

### Payment Transformation

**Major v2.1 Change**: Payment split into `paymentTerms` and `paymentAction`

| v2.0 Field | v2.1 Mapping | Schema Change |
|------------|--------------|---------------|
| `beckn:payment` | Split into two objects | Separation of terms and actions |
| Payment terms fields | → `paymentTerms` | Who collects, settlement terms |
| Payment action fields | → `paymentAction` | Status, amount, transaction ref |

#### Payment Field Mappings

| v2.0 Field | v2.1 Field | IRI Mapping | Notes |
|------------|------------|-------------|-------|
| `beckn:id` | (removed) | - | Payment ID not in v2.1 schema |
| `beckn:amount` | `paymentAction.amount` | `beckn:amount` | Moved to action |
| `beckn:paymentURL` | `paymentAction.paymentUrl` | `beckn:paymentUrl` | Camel case change |
| `beckn:txnRef` | `paymentAction.txnRef` | `beckn:txnRef` | Moved to action |
| `beckn:paidAt` | `paymentAction.paidAt` | `beckn:paidAt` | Moved to action |
| `beckn:beneficiary` | (removed) | - | Not in v2.1 schema |
| `beckn:paymentStatus` | `paymentAction.paymentStatus` | `beckn:paymentStatus` | Moved to action |
| `beckn:acceptedPaymentMethod` | `paymentTerms.acceptedPaymentMethod` | `beckn:acceptedPaymentMethod` | Moved to terms |
| `beckn:paymentAttributes` | `paymentTerms.paymentTermsAttributes` | `beckn:paymentTermsAttributes` | Renamed and moved |

#### v2.0 Payment Object
```json
"beckn:payment": {
  "beckn:id": "payment-123e4567-e89b-12d3-a456-426614174000",
  "beckn:amount": { "currency": "INR", "value": 143.95 },
  "beckn:paymentStatus": "COMPLETED",
  "beckn:acceptedPaymentMethod": ["BANK_TRANSFER", "UPI", "WALLET"],
  "beckn:paymentAttributes": { ... }
}
```

#### v2.1 Payment Structure
```json
"paymentTerms": {
  "@type": "PaymentTerms",
  "collectedBy": "BPP",
  "acceptedPaymentMethod": ["BANK_TRANSFER", "UPI", "WALLET"],
  "paymentTermsAttributes": { ... }
},
"paymentAction": {
  "@type": "PaymentAction",
  "paymentStatus": "COMPLETED",
  "amount": { "currency": "INR", "value": 143.95 },
  "txnRef": "TXN-123456789",
  "paidAt": "2025-12-19T10:05:00Z"
}
```

---

## Summary of Major Changes

### 1. **Deprecated Properties (use equivalents)**
- `beckn:buyer` → `beckn:consumer`
- `beckn:seller` → `beckn:provider`
- `beckn:displayName` → `beckn:name`
- `beckn:orderedItem` → `beckn:itemId`

### 2. **Schema.org Proxies**
Properties that now map to schema.org:
- `beckn:price` → `schema:price`
- `beckn:unitText` → `schema:unitText`
- `beckn:unitCode` → `schema:unitCode`
- `beckn:telephone` → `schema:telephone`
- `beckn:email` → `schema:email`

### 3. **Structural Changes**
- **Buyer → Consumer**: Changed from flat `Buyer` to `Consumer` with nested `Person`/`Organization`
- **Fulfillment**: Changed from single object to array with structured `FulfillmentMode`
- **Payment**: Split into `paymentTerms` and `paymentAction`
- **Attribute Packs**: Domain-specific data moved to `*Attributes` objects

### 4. **Naming Conventions**
- Snake case → Camel case (e.g., `bap_id` → `bapId`)
- Removed `beckn:` prefixes in JSON (kept only in IRIs)
- Added `@context` and `@type` for JSON-LD typing

---

## Validation Against Schemas

The converted v2.1 JSON follows these schema definitions:

1. **beckn.yaml**: Defines message structure for `on_confirm`
2. **attributes.yaml**: Defines core schemas (Order, Consumer, Provider, etc.)
3. **updated.context.jsonld**: Maps compact terms to IRIs
4. **updated.vocab.jsonld**: Defines ontological relationships

---

## References

- v2.0 Source: `/home/ravi/www/DEG/examples/ev-charging/v2/08_00_on_confirm/v2_0_ev-charging-on-confirm.json`
- v2.1 Output: `v2_1_ev-charging-on-confirm-CORRECTED.json`
- OpenAPI Schema: `api/v2.1/beckn.yaml`
- Core Attributes: `schema/core/v2.1/attributes.yaml`
- Context File: `schema/core/v2.1/updated.context.jsonld`
- Vocabulary: `schema/core/v2.1/updated.vocab.jsonld`
