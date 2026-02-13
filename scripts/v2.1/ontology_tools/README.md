# Beckn v2.0 → v2.1 Ontology Mapping Tools

This directory contains local scripts to maintain backward-compatible ontological mappings between Beckn Protocol v2.0 and v2.1.

## Scripts

### `update_updated_vocab.py`
Normalizes and patches `schema/core/v2.1/updated.vocab.jsonld`:
- **Deduplicates** `@graph` nodes by `@id` (keeps first occurrence)
- **Applies v2.0 → v2.1 mappings**:
  - Consumer hierarchy (Consumer, PersonAsConsumer, OrgAsConsumer)
  - Deprecated Buyer → PersonAsConsumer
  - FulfillmentState model (subclass of State)
  - Legacy property mappings (buyer→consumer, seller→provider)
  - Snake_case → camelCase property aliases
  - Scoped descriptor properties for each parent class
- **Adds beckn proxy terms** for schema.org classes/properties to avoid `schema:*` IRIs in context

### `update_updated_context.py`
Updates `schema/core/v2.1/updated.context.jsonld`:
- **Removes all `schema:*` IRIs** (replaced with beckn proxies)
- **Adds legacy aliases**:
  - `buyer` → `beckn:consumer`
  - `seller` → `beckn:provider`
  - `orderedItem` → `beckn:itemId`
  - Snake_case keys → camelCase IRIs
- **Adds scoped descriptor contexts** (nested `@context` per parent class)
- **Adds scoped fulfillment state** (`currentState` under Fulfillment)

## Usage

Run both scripts to regenerate the mapping files:

```bash
python3 scripts/v2.1/ontology_tools/update_updated_vocab.py
python3 scripts/v2.1/ontology_tools/update_updated_context.py
```

Or in one command:
```bash
python3 scripts/v2.1/ontology_tools/update_updated_vocab.py && \
python3 scripts/v2.1/ontology_tools/update_updated_context.py
```

## Validation

Check context coverage:
```bash
python3 scripts/v2.1/context-checker/check_context.py \
  --attributes schema/core/v2.1/attributes.yaml \
  --context schema/core/v2.1/updated.context.jsonld
```

Verify no schema.org IRIs in context:
```bash
grep -c '"schema:' schema/core/v2.1/updated.context.jsonld
# Should return 0
```

## Design Decisions

### Consumer Model
- v2.0 assumed consumer = person
- v2.1 supports both person and organization consumers
- Mapping: v2.0 `Buyer` → v2.1 `PersonAsConsumer`

### Descriptor Scoping
- Each parent class (Catalog, Item, Offer, etc.) gets a scoped descriptor property
- Example: `Catalog.descriptor` expands to `beckn:catalogDescriptor`
- Enables fine-grained ontological modeling while maintaining JSON simplicity

### Schema.org Alignment
- Context uses only `beckn:*` IRIs
- Vocab expresses schema.org equivalences via `owl:equivalentClass`/`owl:equivalentProperty`
- Keeps context clean while preserving semantic web interoperability

### Fulfillment State
- `FulfillmentState` is `rdfs:subClassOf` `State`
- `currentFulfillmentState` property for scoped current state
- Legacy `fulfillmentStatus` deprecated, subPropertyOf `currentFulfillmentState`

### Legacy Compatibility
- All v2.0 IRIs retained with `owl:deprecated: true`
- Equivalence mappings ensure v2.0 payloads expand to v2.1 semantics
- Payment decomposition deferred to later phase

## Files Modified
- `schema/core/v2.1/updated.vocab.jsonld` (deduped + patched)
- `schema/core/v2.1/updated.context.jsonld` (no schema IRIs + scoped contexts)
