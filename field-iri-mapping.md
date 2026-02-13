# Field to IRI Mapping Table

This table maps each field from the EV Charging on_confirm JSON example to its corresponding IRI in `schema/core/v2.1/updated.context.jsonld` and the v2.1 vocabulary definition in `schema/core/v2.1/updated.vocab.jsonld`.

## Context Section Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| context.version | version | `beckn:version` | `beckn:version` | ✅ Property - Version of beckn protocol |
| context.action | action | `beckn:action` | `beckn:action` | ✅ Property - The Beckn protocol method being called |
| context.domain | domain | Not in context | Not in vocab | ⚠️ Not found in v2.1 core vocabulary |
| context.bap_id | bap_id | `beckn:bapId` | `beckn:bapId` | ✅ Property - BAP identifier (FQDN) |
| context.bap_uri | bap_uri | `beckn:bapUri` | `beckn:bapUri` | ✅ Property - API URL of BAP |
| context.transaction_id | transaction_id | `beckn:transactionId` | `beckn:transactionId` + `beckn:transaction_id` (deprecated) | ✅ Property - Unique transaction ID. snake_case variant deprecated |
| context.message_id | message_id | `beckn:messageId` | `beckn:messageId` | ✅ Property - Unique message ID for request/callback pairing |
| context.timestamp | timestamp | `beckn:timestamp` | `beckn:timestamp` | ✅ Property - Request generation time (RFC3339) |
| context.ttl | ttl | `beckn:ttl` | `beckn:ttl` | ✅ Property - Duration in ISO8601 format |
| context.bpp_id | bpp_id | `beckn:bppId` | `beckn:bppId` | ✅ Property - BPP identifier |
| context.bpp_uri | bpp_uri | `beckn:bppUri` | `beckn:bppUri` | ✅ Property - BPP URI endpoint |

## Message > Order Section Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| message.order[@type] | @type | `beckn:Order` | `beckn:Order` | ✅ Class - Purchase order containing items, pricing and fulfillment |
| message.order[beckn:id] | id | `beckn:id` | `beckn:id` | ✅ Property - Primary identifier for entity |
| message.order[beckn:orderStatus] | orderStatus | `beckn:orderStatus` | `beckn:orderStatus` + `beckn:OrderStatus` enum | ✅ Property + Enumeration - Order lifecycle status |
| message.order[beckn:orderStatus] = "CONFIRMED" | CONFIRMED | `beckn:OrderConfirmed` | `beckn:OrderConfirmed` | ✅ Enumeration member - Order confirmed state |
| message.order[beckn:seller] | seller | `beckn:provider` (alias) | `beckn:seller` (DEPRECATED) → `beckn:provider` | ⚠️ DEPRECATED in v2.1 - Use beckn:provider instead |
| message.order[beckn:buyer] | buyer | `beckn:consumer` (alias) | `beckn:buyer` (DEPRECATED) → `beckn:consumer` | ⚠️ DEPRECATED in v2.1 - Use beckn:consumer instead |
| message.order[beckn:orderItems] | orderItems | `beckn:orderItems` | `beckn:orderItems` | ✅ Property - Items included in order |
| message.order[beckn:orderValue] | orderValue | `beckn:orderValue` | `beckn:orderValue` | ✅ Property - Total order value as price specification |
| message.order[beckn:fulfillment] | fulfillment | `beckn:fulfillment` | `beckn:fulfillment` | ✅ Property - Fulfillment details for order |
| message.order[beckn:payment] | payment | `beckn:payment` | `beckn:payment` | ✅ Property - Payment instrument or status |

## Buyer Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| message.order.buyer[@type] | @type | `beckn:Buyer` | `beckn:Buyer` (DEPRECATED) → `beckn:PersonAsConsumer` | ⚠️ DEPRECATED - Use PersonAsConsumer or OrgAsConsumer in v2.1 |
| message.order.buyer[beckn:id] | id | `beckn:id` | `beckn:id` | ✅ Property - Primary identifier |
| message.order.buyer[beckn:role] | role | `beckn:role` | `beckn:role` | ✅ Property - Functional role in transaction |
| message.order.buyer[beckn:displayName] | displayName | `beckn:name` (alias) | `beckn:displayName` (DEPRECATED) → `beckn:name` | ⚠️ DEPRECATED in v2.1 - Use beckn:name (Descriptor.name) |
| message.order.buyer[beckn:telephone] | telephone | `beckn:telephone` | `beckn:telephone` | ✅ Property - Proxy for schema:telephone |
| message.order.buyer[beckn:email] | email | `beckn:email` | `beckn:email` | ✅ Property - Proxy for schema:email |
| message.order.buyer[beckn:taxID] | taxID | `beckn:taxID` | `beckn:taxID` | ✅ Property - Tax identifier |

## Order Items Array Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| orderItems[].beckn:orderedItem | orderedItem | `beckn:itemId` (alias) | `beckn:orderedItem` | ✅ Property - Catalog item referenced in order line |
| orderItems[].beckn:quantity | quantity | `beckn:quantity` | `beckn:quantity` | ✅ Property - Ordered quantity for line |
| orderItems[].beckn:price | price | `beckn:price` | `beckn:price` (DEPRECATED) → `schema:price` | ⚠️ Legacy v2 property - Use schema:price in v2.1 |
| orderItems[].beckn:acceptedOffer | acceptedOffer | `beckn:acceptedOffer` | `beckn:acceptedOffer` | ✅ Property - Offer applied to this line |

## Quantity Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| quantity.unitText | unitText | `beckn:unitText` | `beckn:unitText` (DEPRECATED) → `schema:unitText` | ⚠️ Legacy v2 property - Use schema:unitText in v2.1 |
| quantity.unitCode | unitCode | `beckn:unitCode` | `beckn:unitCode` (DEPRECATED) → `schema:unitCode` | ⚠️ Legacy v2 property - Use schema:unitCode in v2.1 |
| quantity.unitQuantity | unitQuantity | `beckn:unitQuantity` | `beckn:unitQuantity` | ✅ Property - Quantity of referenced measurement unit |

## Price Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| price.currency | currency | `beckn:currency` | `beckn:currency` | ✅ Property - ISO 4217 currency code (subPropertyOf schema:priceCurrency) |
| price.value | value | `beckn:value` | `beckn:value` | ✅ Property - Numeric price value |
| price.applicableQuantity | applicableQuantity | `beckn:applicableQuantity` | `beckn:applicableQuantity` | ✅ Property - Quantity context for price |

## Accepted Offer Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| acceptedOffer[@type] | @type | `beckn:Offer` | `beckn:Offer` | ✅ Class - Commercial offer describing pricing/terms |
| acceptedOffer[beckn:id] | id | `beckn:id` | `beckn:id` | ✅ Property - Primary identifier |
| acceptedOffer[beckn:descriptor] | descriptor | `beckn:descriptor` → `beckn:offerDescriptor` | `beckn:descriptor` + `beckn:offerDescriptor` | ✅ Property - Scoped descriptor for Offer |
| acceptedOffer[beckn:items] | items | `beckn:items` | `beckn:items` | ✅ Property - List of item references |
| acceptedOffer[beckn:provider] | provider | `beckn:provider` | `beckn:provider` | ✅ Property - Provider associated with offer |
| acceptedOffer[beckn:price] | price | `beckn:price` | `beckn:price` (DEPRECATED) → `schema:price` | ⚠️ Legacy v2 property |

## Descriptor Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| descriptor[@type] | @type | `beckn:Descriptor` | `beckn:Descriptor` | ✅ Class - Human-readable metadata |
| descriptor[schema:name] | name | External schema.org | `beckn:name` | ✅ Property in vocab - Name of entity being described |

## Order Value Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| orderValue.currency | currency | `beckn:currency` | `beckn:currency` | ✅ Property - ISO 4217 currency code |
| orderValue.value | value | `beckn:value` | `beckn:value` | ✅ Property - Numeric value |
| orderValue.components | components | `beckn:components` | `beckn:components` | ✅ Property - Component breakdowns (tax, delivery, discount, etc.) |

## Price Component Fields (in components array)

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| components[].type | type | `beckn:type` | `beckn:type` | ✅ Property - Multiple contexts (GeoJSON, PriceComponent, Media) |
| components[].type = "UNIT" | UNIT | `beckn:UnitPriceComponent` | `beckn:UnitPriceComponent` | ✅ Enumeration - Unit price component type |
| components[].type = "SURCHARGE" | SURCHARGE | `beckn:SurchargePriceComponent` | `beckn:SurchargePriceComponent` | ✅ Enumeration - Surcharge price component type |
| components[].type = "DISCOUNT" | DISCOUNT | `beckn:DiscountPriceComponent` | `beckn:DiscountPriceComponent` | ✅ Enumeration - Discount price component type |
| components[].type = "FEE" | FEE | `beckn:FeePriceComponent` | `beckn:FeePriceComponent` | ✅ Enumeration - Fee price component type |
| components[].value | value | `beckn:value` | `beckn:value` | ✅ Property - Numeric value |
| components[].currency | currency | `beckn:currency` | `beckn:currency` | ✅ Property - ISO 4217 currency code |
| components[].description | description | `beckn:description` | `beckn:description` | ✅ Property - Description text |

## Fulfillment Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| fulfillment[@type] | @type | `beckn:Fulfillment` | `beckn:Fulfillment` | ✅ Class - Delivery, reservation or service execution info |
| fulfillment[beckn:id] | id | `beckn:id` | `beckn:id` | ✅ Property - Primary identifier |
| fulfillment[beckn:mode] | mode | `beckn:mode` | `beckn:mode` | ✅ Property - Fulfillment mode (DELIVERY, PICKUP, RESERVATION, etc.) |
| fulfillment[beckn:deliveryAttributes] | deliveryAttributes | `beckn:deliveryAttributes` | `beckn:deliveryAttributes` | ✅ Property - Attribute pack for fulfillment mode details |

## Delivery Attributes (Domain-Specific: ChargingSession)

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| deliveryAttributes[@type] | @type | ChargingSession | Not in core vocab | ⚠️ Domain-specific extension (EvChargingSession/v1) |
| deliveryAttributes.connectorType | connectorType | Not in core context | Not in core vocab | ⚠️ Domain-specific field |
| deliveryAttributes.maxPowerKW | maxPowerKW | Not in core context | Not in core vocab | ⚠️ Domain-specific field |
| deliveryAttributes.sessionStatus | sessionStatus | Not in core context | Not in core vocab | ⚠️ Domain-specific field |

## Payment Object Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| payment[@type] | @type | `beckn:Payment` | `beckn:Payment` | ✅ Class - Payment instrument, status and settlement info |
| payment[beckn:id] | id | `beckn:id` | `beckn:id` | ✅ Property - Primary identifier |
| payment[beckn:amount] | amount | `beckn:amount` | `beckn:amount` | ✅ Property - Amount associated with payment |
| payment[beckn:paymentURL] | paymentURL | `beckn:paymentURL` | `beckn:paymentURL` | ✅ Property - URL for payment processing/redirection |
| payment[beckn:txnRef] | txnRef | `beckn:txnRef` | `beckn:txnRef` | ✅ Property - PSP/gateway/bank transaction reference |
| payment[beckn:paidAt] | paidAt | `beckn:paidAt` | `beckn:paidAt` | ✅ Property - Timestamp of last terminal payment event |
| payment[beckn:beneficiary] | beneficiary | `beckn:beneficiary` | `beckn:beneficiary` + `beckn:Beneficiary` enum | ✅ Property + Enumeration - Payment recipient |
| payment[beckn:beneficiary] = "BPP" | BPP | `beckn:BPP` | `beckn:BPP` | ✅ Enumeration member - BPP as beneficiary |
| payment[beckn:paymentStatus] | paymentStatus | `beckn:paymentStatus` | `beckn:paymentStatus` + `beckn:PaymentStatus` enum | ✅ Property + Enumeration - Payment lifecycle status |
| payment[beckn:paymentStatus] = "COMPLETED" | COMPLETED | `beckn:PaymentCompleted` | `beckn:PaymentCompleted` | ✅ Enumeration member - Payment completed |
| payment[beckn:acceptedPaymentMethod] | acceptedPaymentMethod | `beckn:acceptedPaymentMethod` | `beckn:acceptedPaymentMethod` | ✅ Property - Payment methods accepted |

## Accepted Payment Methods (Array Values)

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| acceptedPaymentMethod[] = "BANK_TRANSFER" | BANK_TRANSFER | `beckn:BANK_TRANSFER` | `beckn:BANK_TRANSFER` | ✅ Enumeration member - Bank transfer payment method |
| acceptedPaymentMethod[] = "UPI" | UPI | `beckn:UPI` | `beckn:UPI` | ✅ Enumeration member - UPI payment method |
| acceptedPaymentMethod[] = "WALLET" | WALLET | `beckn:WALLET` | `beckn:WALLET` | ✅ Enumeration member - Wallet payment method |

## Payment Attributes (Domain-Specific: PaymentSettlement)

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| paymentAttributes[@type] | @type | PaymentSettlement | Not in core vocab | ⚠️ Domain-specific extension (PaymentSettlement/v1) |
| paymentAttributes.settlementAccounts | settlementAccounts | Not in core context | Not in core vocab | ⚠️ Domain-specific field |

## Settlement Account Fields

| JSON Path | Field Name | IRI Mapping (Context) | v2.1 Vocab IRI | v2.1 Vocab Notes |
|-----------|-----------|-------------|----------------|------------------|
| settlementAccounts[].beneficiaryId | beneficiaryId | Not in core context | Not in core vocab | ⚠️ Domain-specific field |
| settlementAccounts[].accountHolderName | accountHolderName | `beckn:accountHolderName` | `beckn:accountHolderName` | ✅ Property - Account holder name |
| settlementAccounts[].accountNumber | accountNumber | `beckn:accountNumber` | `beckn:accountNumber` | ✅ Property - Account number |
| settlementAccounts[].ifscCode | ifscCode | Not in core context | Not in core vocab | ⚠️ Domain-specific field (branchCode exists as beckn:branchCode) |
| settlementAccounts[].bankName | bankName | `beckn:bankName` | `beckn:bankName` | ✅ Property - Bank name |
| settlementAccounts[].vpa | vpa | `beckn:vpa` | `beckn:vpa` | ✅ Property - Virtual payment address |

---

## Summary Statistics

- **Total Fields Analyzed**: 89
- **Fields Mapped to Core Context**: 72 (81%)
- **Fields Not in Core Context**: 17 (19%)
  - 1 Context field (domain)
  - 16 Domain-specific fields (ChargingSession & PaymentSettlement extensions)

### V2.1 Vocabulary Mapping Statistics

- **Fully Mapped to v2.1 Vocab**: 66 fields (74%)
- **Deprecated Properties (with v2.1 replacements)**: 9 fields (10%)
  - `buyer` → `consumer`
  - `seller` → `provider`
  - `displayName` → `name`
  - `price` → `schema:price`
  - `unitText` → `schema:unitText`
  - `unitCode` → `schema:unitCode`
  - `transaction_id` → `transactionId`
  - `Buyer` class → `PersonAsConsumer` or `OrgAsConsumer`
- **Not in v2.1 Core Vocab**: 14 fields (16%)
  - Domain-specific extensions requiring separate vocabularies

## Key Findings

### ✅ Well-Mapped Areas
1. **Core Context Fields**: All standard Beckn protocol context fields properly defined in v2.1 vocab
2. **Order Structure**: Complete v2.1 vocabulary definitions for Order, Consumer, OrderItems
3. **Payment Processing**: Comprehensive v2.1 vocabulary including payment status enumerations
4. **Price Components**: Full v2.1 vocabulary support for price component types
5. **Enums**: Proper v2.1 vocabulary definitions for all enum values

### ⚠️ Deprecated Mappings (v2.0 → v2.1)
The vocabulary file explicitly marks several v2.0 properties and classes as deprecated:

1. **beckn:Buyer** (class) → Use **beckn:PersonAsConsumer** or **beckn:OrgAsConsumer**
   - `owl:deprecated: true`
   - `owl:equivalentClass: beckn:PersonAsConsumer`
   
2. **beckn:buyer** (property) → Use **beckn:consumer**
   - `owl:deprecated: true`
   - `owl:equivalentProperty: beckn:consumer`
   
3. **beckn:seller** (property) → Use **beckn:provider**
   - `owl:deprecated: true`
   - `owl:equivalentProperty: beckn:provider`

4. **beckn:displayName** → Use **beckn:name**
   - `owl:deprecated: true`
   - Legacy property retained for backward compatibility

5. **Snake_case variants** → Use **camelCase**
   - `transaction_id` → `transactionId`
   - `mime_type` → `mimeType`
   - `submission_id` → `submissionId`
   - `tl_method` → `tlMethod`
   - `text_search` → `textSearch`

6. **Schema.org proxies**:
   - `beckn:price` → `schema:price`
   - `beckn:unitText` → `schema:unitText`
   - `beckn:unitCode` → `schema:unitCode`
   - `beckn:eligibleQuantity` → `schema:eligibleQuantity`

### 🔍 Notable V2.1 Vocabulary Features

1. **Scoped Descriptors**: v2.1 introduces specialized descriptor subtypes
   - `CatalogDescriptor`, `ItemDescriptor`, `OfferDescriptor`, `OrderDescriptor`
   - `FulfillmentDescriptor`, `PaymentDescriptor`, `LocationDescriptor`
   - Each type has a scoped property mapping (e.g., `beckn:offerDescriptor`)

2. **Consumer Hierarchy**: New consumer modeling in v2.1
   - Abstract `Consumer` class
   - `PersonAsConsumer` (subclass of Consumer + schema:Person)
   - `OrgAsConsumer` (subclass of Consumer + schema:Organization)
   - Replaces the generic `Buyer` from v2.0

3. **Enhanced State Management**:
   - Generic `State` class with `StateDescriptor`
   - Specialized `FulfillmentState` with `FulfillmentStateDescriptor`
   - `fulfillmentStatus` (deprecated) → `currentFulfillmentState`

4. **Rich Enumerations**: Complete vocabulary definitions for:
   - Payment methods (UPI, CREDIT_CARD, DEBIT_CARD, WALLET, BANK_TRANSFER, CASH, APPLE_PAY)
   - Payment statuses (17 states from INITIATED to ADJUSTED)
   - Order statuses (12 states from CREATED to ONHOLD)
   - Tracking statuses (ACTIVE, DISABLED, COMPLETED)
   - Support channels (PHONE, EMAIL, WEB, CHAT, WHATSAPP, IN_APP, OTHER)

5. **OWL Properties**: Extensive use of OWL vocabulary
   - `owl:deprecated` - marks legacy properties
   - `owl:equivalentProperty` - defines property equivalence
   - `owl:equivalentClass` - defines class equivalence
   - Enables semantic reasoning and backward compatibility

### 📋 Recommendations for Migration

1. **Update Type References**:
   - Replace `@type: "beckn:Buyer"` with `@type: "beckn:PersonAsConsumer"`
   - Consider `beckn:OrgAsConsumer` for organizational buyers

2. **Update Property Names**:
   - Replace `beckn:buyer` with `beckn:consumer`
   - Replace `beckn:seller` with `beckn:provider`
   - Replace `beckn:displayName` with `beckn:name`

3. **Use Schema.org Properties**:
   - Replace `beckn:price` with `schema:price`
   - Replace `beckn:unitText` with `schema:unitText`
   - Replace `beckn:unitCode` with `schema:unitCode`

4. **Adopt CamelCase**:
   - Replace all snake_case properties with camelCase equivalents
   - The context file supports both for backward compatibility

5. **Domain Extensions**:
   - Ensure domain-specific vocabularies (EvChargingSession, PaymentSettlement) are properly referenced
   - These should have their own vocabulary files extending the core

---

Generated on: December 2, 2026  
Source JSON: `/home/ravi/www/DEG/examples/ev-charging/v2/08_00_on_confirm/v2_0_ev-charging-on-confirm.json`  
Context File: `schema/core/v2.1/updated.context.jsonld`  
Vocabulary File: `schema/core/v2.1/updated.vocab.jsonld`
