# V2.0 → V2.1 Ontology Mapping Summary

**Date:** 2026-12-02  
**Files Updated:**
- `schema/core/v2.1/updated.vocab.jsonld`
- `schema/core/v2.1/updated.context.jsonld`

## Updates Applied

### 1. Consumer Hierarchy (Actor Model)
✅ **New v2.1 Classes:**
- `beckn:Consumer` (abstract parent)
- `beckn:PersonAsConsumer` (subClassOf Consumer + schema:Person)
- `beckn:OrgAsConsumer` (subClassOf Consumer + schema:Organization)

✅ **v2.0 Legacy Mapping:**
- `beckn:Buyer` → deprecated, equivalentClass to `PersonAsConsumer`

### 2. Actor Property Mappings
✅ **Deprecated v2.0 properties:**
- `buyer` → equivalentProperty `consumer`
- `seller` → equivalentProperty `provider`

✅ **Context mappings:**
- `"buyer": "beckn:consumer"`
- `"seller": "beckn:provider"`

### 3. Fulfillment State Hierarchy
✅ **New v2.1 Classes:**
- `beckn:FulfillmentState` (subClassOf State)
- `beckn:FulfillmentStateDescriptor` (subClassOf Descriptor)

✅ **Scoped property:**
- `beckn:currentFulfillmentState` (domain: Fulfillment)

✅ **Legacy mapping:**
- `fulfillmentStatus` → deprecated, subPropertyOf `currentFulfillmentState`

✅ **Nested context in Fulfillment:**
```json
"Fulfillment": {
  "@context": {
    "descriptor": "beckn:fulfillmentDescriptor",
    "currentState": "beckn:currentFulfillmentState"
  }
}
```

### 4. snake_case → camelCase Mappings
✅ **9 deprecated legacy properties:**
- `transaction_id` → `transactionId`
- `ack_status` → `ackStatus`
- `tl_method` → `tlMethod`
- `expires_at` → `expiresAt`
- `mime_type` → `mimeType`
- `submission_id` → `submissionId`
- `text_search` → `textSearch`
- `key_id` → `keyId`
- `media_search` → `mediaSearch`

### 5. Scoped Descriptors (23 classes)
✅ **All created as subClassOf beckn:Descriptor:**
- CatalogDescriptor
- ItemDescriptor
- OfferDescriptor
- ProviderDescriptor
- OrderDescriptor
- OrderItemDescriptor
- FulfillmentDescriptor
- PaymentDescriptor
- InvoiceDescriptor
- LocationDescriptor
- PolicyDescriptor
- StateDescriptor
- FulfillmentStateDescriptor
- AlertDescriptor
- InstructionDescriptor
- EntitlementDescriptor
- CredentialDescriptor
- SkillDescriptor
- ParticipantDescriptor
- FulfillmentAgentDescriptor
- SupportInfoDescriptor
- ConstraintDescriptor
- CancellationPolicyDescriptor

✅ **Nested contexts added** for each parent class in updated.context.jsonld

### 6. Schema.org Proxies
✅ **Created beckn: proxies to avoid schema: IRIs in context:**
- `beckn:Person` (equivalentClass schema:Person)
- `beckn:Organization` (equivalentClass schema:Organization)
- `beckn:PriceSpecification` (equivalentClass schema:PriceSpecification)
- Properties: email, telephone, age, duration, knowsLanguage, worksFor

✅ **Context updated:**
- Removed `"schema": "https://schema.org/"` prefix
- All schema.org references now via beckn: proxies
- `displayName` → `beckn:name` (Descriptor context)

### 7. Semantic Changes
✅ **Property mappings:**
- `orderedItem` → `beckn:itemId` (context mapping)
- `totals` → `beckn:costBreakup` (noted in vocab, not equivalent)

### 8. Removed Properties
✅ **Deprecated:**
- `trackingAction` → noted as replaced by trackingEnabled + attributes

## Validation Results

✅ **JSON validity:** Both files parse successfully  
✅ **Deduplication:** 1 minor conflict resolved (Consumer comment merge)  
✅ **Deprecation count:** 14 legacy entries marked deprecated  
✅ **Descriptor scoping:** 23 scoped descriptor classes + properties  

## Deferred to Future Tasks
- Payment decomposition (v2.0 Payment → v2.1 PaymentTerms/PaymentAction/SettlementTerm)
- Object → Array multiplicity conversions

## Tools Created
- `scripts/v2.1/ontology_tools/update_updated_vocab.py`
- `scripts/v2.1/ontology_tools/update_updated_context.py`
