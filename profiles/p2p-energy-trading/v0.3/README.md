# P2P Energy Trading Profile v0.3

Profile schema for P2P Energy Trading on Beckn Protocol v2.

## Overview

This profile defines how domain-specific Energy Trade schemas slot into core Beckn entities for P2P energy trading use cases. Utility IDs for inter-discom trading are captured in EnergyCustomer (buyerAttributes.utilityId and providerAttributes.utilityId).

## Attribute Slot Mappings

| Core Entity | Attribute Slot | Domain Schema | Description |
|-------------|----------------|---------------|-------------|
| `Offer` | `beckn:price` | `PriceSpecification` | **REQUIRED:** Price with applicableQuantity (max kWh) |
| `Offer` | `beckn:offerAttributes` | `EnergyTradeOffer` | **REQUIRED:** pricingModel, deliveryWindow |
| `Order` | `beckn:orderAttributes` | `EnergyTradeOrder` | **REQUIRED:** BAP/BPP IDs, total_quantity |
| `Order` | `beckn:buyer` | `P2PEnergyBuyer` | **REQUIRED:** Buyer with EnergyCustomer attributes |
| `Item` | `beckn:provider` | `P2PEnergyProvider` | **REQUIRED:** Provider with EnergyCustomer attributes |
| `Item` | `beckn:itemAttributes` | `EnergyResource` | Source type, meterId |
| `Provider` | `beckn:providerAttributes` | `EnergyCustomer` | **REQUIRED:** meterId, utilityId |
| `Buyer` | `beckn:buyerAttributes` | `EnergyCustomer` | **REQUIRED:** meterId, utilityId |
| `OrderItem` | `beckn:orderItemAttributes` | `EnergyOrderItem` | **REQUIRED:** providerAttributes, fulfillmentAttributes |
| `EnergyOrderItem` | `providerAttributes` | `EnergyCustomer` | **REQUIRED:** Delivery destination meter |
| `EnergyOrderItem` | `fulfillmentAttributes` | `EnergyTradeDelivery` | **REQUIRED:** Meter readings, delivery status |

## Required Core Fields

When using this profile, the following core Beckn fields are REQUIRED beyond base schema requirements:

### On Offer (discover response, select response)

```yaml
beckn:price:              # REQUIRED - On parent Offer object
  "@type": "schema:PriceSpecification"
  schema:price: 4.50
  schema:priceCurrency: "INR"
  applicableQuantity:     # REQUIRED - Max quantity for this delivery window
    unitQuantity: 10
    unitText: "kWh"
beckn:offerAttributes:    # REQUIRED - Must be EnergyTradeOffer
  "@type": "EnergyTradeOffer"
  pricingModel: "PER_KWH"
  deliveryWindow: { ... }
```

### On Order (init, confirm, status)

```yaml
beckn:buyer:              # REQUIRED - Must include buyerAttributes
  "@type": "beckn:Buyer"
  beckn:buyerAttributes:
    "@type": "EnergyCustomer"
    meterId: "der://meter/123456"
    utilityId: "BESCOM-KA"
beckn:orderAttributes:    # REQUIRED - Must be EnergyTradeOrder
  "@type": "EnergyTradeOrder"
  bap_id: "buyer-platform.example.com"
  bpp_id: "seller-platform.example.com"
  total_quantity:
    unitQuantity: 25.0
    unitText: "kWh"
beckn:orderItems:         # REQUIRED - At least one
  - beckn:quantity: { ... }
    beckn:orderItemAttributes:
      "@type": "EnergyOrderItem"
      providerAttributes:   # REQUIRED
        "@type": "EnergyCustomer"
        meterId: "..."
      fulfillmentAttributes:  # REQUIRED in status responses
        "@type": "EnergyTradeDelivery"
        deliveryStatus: "IN_PROGRESS"
```

## Schema URLs

```
Base: https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/main/schema

Core Beckn:
  {base}/core/v2/attributes.yaml
  {base}/core/v2/context.jsonld

Energy Trade (combined):
  {base}/EnergyTrade/v0.3/attributes.yaml
  {base}/EnergyTrade/v0.3/context.jsonld

Energy Enrollment (separate):
  {base}/EnergyEnrollment/v0.2/attributes.yaml

Profile:
  {base}/../profiles/p2p-energy-trading/v0.3/profile.yaml
```

## Usage with Beckn-ONIX

### Schema Validation Config

In your ONIX handler configuration, the `schemav2validator` plugin validates payloads:

```yaml
schemaValidator:
  id: schemav2validator
  config:
    type: url
    location: https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/api/beckn.yaml
    extendedSchema_enabled: "true"
    extendedSchema_cacheTTL: "86400"
    extendedSchema_allowedDomains: "raw.githubusercontent.com,schemas.beckn.org"
    # Profile documentation (for reference)
    x-profile: https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/main/profiles/p2p-energy-trading/v0.3/profile.yaml
```

### How Validation Works

1. **Core validation**: ONIX validates request/response structure against `beckn.yaml`
2. **Extended schema validation**: When payloads contain `@context` URLs, ONIX loads and validates against those schemas
3. **Profile validation**: For additional profile-level checks (e.g., required fields), use the profile schema with external validation tools

### Example @context in Payloads

Your JSON payloads should reference the EnergyTrade schemas:

```json
{
  "context": { "domain": "deg:p2p-trading", ... },
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-v2/.../core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:orderAttributes": {
        "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-v2/.../EnergyTrade/v0.3/context.jsonld",
        "@type": "EnergyTradeOrder",
        ...
      }
    }
  }
}
```

## Profile Validation with Python

```python
import yaml
import jsonschema
from referencing import Registry, Resource

# Load profile schema
with open('profile.yaml') as f:
    profile = yaml.safe_load(f)

# Get the P2PEnergyOrder schema
order_schema = profile['components']['schemas']['P2PEnergyOrder']

# Validate an order
jsonschema.validate(order_payload, order_schema)
```

## Profile Validation with JavaScript (ajv)

```javascript
import Ajv from 'ajv';
import yaml from 'js-yaml';

const ajv = new Ajv({ allErrors: true });

// Load and compile profile schema
const profile = yaml.load(fs.readFileSync('profile.yaml'));
const validate = ajv.compile(profile.components.schemas.P2PEnergyOrder);

// Validate
if (!validate(orderPayload)) {
  console.log(validate.errors);
}
```
