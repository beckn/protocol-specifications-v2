# IRI Resolution Algorithm Documentation

## Overview

This document describes the **canonical IRI resolution algorithm** used for transforming Beckn v2.0 JSON payloads to v2.1 format. The algorithm ensures that **every IRI is always transformed** through the complete ontology chain until reaching its canonical v2.1 location.

## Core Principle

**Never stop at the first mapping**. Follow the ontology chain through equivalence, subclass, and deprecation relationships until reaching the canonical v2.1 IRI and its corresponding keyword.

---

## Algorithm Steps

### Step 1: Normalize Input IRI

**Purpose**: Expand compact IRIs to their full form

```
INPUT:  "beckn:buyer" or "buyer"
OUTPUT: "beckn:consumer" (after context lookup)

Process:
1. Check if IRI has prefix (e.g., "beckn:")
2. Look up in v2.0 context to expand
3. Record as chain[0]
```

**Example**:
- `"buyer"` → `"./vocab.jsonld#buyer"` (from v2.0 context)
- `"beckn:displayName"` → `"./vocab.jsonld#displayName"`

---

### Step 2: Check v2.1 Context Mapping

**Purpose**: Map v2.0 keywords to v2.1 keywords

```
INPUT:  beckn:buyer
LOOKUP: updated.context.jsonld → "buyer": "beckn:consumer"
OUTPUT: beckn:consumer

Record in chain as CONTEXT_MAPPING
```

**Key mappings**:
- `buyer` → `beckn:consumer` (aliased)
- `seller` → `beckn:provider` (aliased)
- `displayName` → `beckn:name` (aliased)
- `orderedItem` → `beckn:itemId` (aliased)

---

### Step 3: Resolve Through Vocabulary (RECURSIVE)

**Purpose**: Follow ontological relationships to canonical IRI

This is the **critical step** where we follow the chain through:
1. `owl:equivalentClass` / `owl:equivalentProperty`
2. `rdfs:subClassOf` / `rdfs:subPropertyOf`
3. Check for `owl:deprecated` flags

```python
while not_at_canonical:
    vocab_entry = lookup_in_vocab(current_iri)
    
    if vocab_entry.deprecated:
        mark_as_deprecated()
    
    if vocab_entry.equivalentClass:
        current_iri = vocab_entry.equivalentClass
        continue  # KEEP RESOLVING
    
    if vocab_entry.subClassOf:
        current_iri = vocab_entry.subClassOf
        continue  # KEEP RESOLVING
    
    # No further mappings → current_iri is CANONICAL
    break
```

**Example chain for "buyer"**:
```
beckn:buyer (v2.0)
  → beckn:consumer (context mapping)
  → beckn:Buyer (vocab lookup)
  → beckn:PersonAsConsumer (equivalentClass)
  → beckn:Consumer (subClassOf)
  → ✓ CANONICAL (no further mappings)
```

---

### Step 4: Find v2.1 Keyword

**Purpose**: Identify the JSON keyword that maps to canonical IRI

```
INPUT:  beckn:consumer (canonical IRI)
LOOKUP: updated.context.jsonld reverse mapping
OUTPUT: "consumer" (v2.1 keyword)
```

Build reverse index: `iri_to_keyword[beckn:consumer] = "consumer"`

---

### Step 5: Lookup Target Schema

**Purpose**: Get schema definition from attributes.yaml

```
INPUT:  "consumer" (keyword) or "beckn:Consumer" (IRI)
LOOKUP: attributes.yaml → components.schemas.Consumer
OUTPUT: Schema definition with:
        - type (object, array, string)
        - required fields
        - @context/@type requirements
        - oneOf/allOf/anyOf structures
        - nested properties
```

---

### Step 6: Transform Value Structure

**Purpose**: Restructure the JSON value according to v2.1 schema

This step handles:
- Property renaming (`displayName` → `name`)
- Structure changes (flat → nested, or vice versa)
- Wrapper objects (`Person` → `person: {...}`)
- Array conversions
- Attribute pack placement

---

## Resolution Chain Examples

### Example 1: Simple Alias (buyer → consumer)

```
[0] ./vocab.jsonld#buyer
    via: v2.0_input
    
[1] beckn:consumer
    via: context_mapping
    note: Mapped via v2.1 context: buyer → beckn:consumer
    
[2] beckn:consumer
    via: canonical
    ✓ Final keyword: "consumer"
```

### Example 2: Complex Chain (fulfillmentStatus → currentState)

```
[0] beckn:fulfillmentStatus (v2.0)
    via: v2.0_input
    
[1] beckn:fulfillmentStatus
    via: context_mapping
    deprecated: TRUE
    
[2] beckn:currentFulfillmentState
    via: owl:equivalentProperty
    note: fulfillmentStatus deprecated, use currentFulfillmentState
    
[3] beckn:currentState
    via: rdfs:subPropertyOf
    
[4] beckn:currentState
    via: canonical
    ✓ Final keyword: "currentState"
    ⚠ Warning: Original IRI was deprecated
```

### Example 3: Nested Context Scoping

```
Order.buyer → 
  Check Order's @context first
  Then check global context
  
Resolution:
  beckn:buyer → beckn:consumer → "consumer"
```

---

## Critical Decision Points

### When is an IRI Canonical?

An IRI is canonical when ALL of the following are true:

1. ✅ **NOT deprecated**: `owl:deprecated != true`
2. ✅ **NO equivalence**: No `owl:equivalentClass` or `owl:equivalentProperty`
3. ✅ **Reachable via keyword**: Exists in v2.1 context as a keyword
4. ✅ **No further mappings**: No `rdfs:subClassOf` or `rdfs:subPropertyOf`

### Multiple Inheritance Handling

When an IRI has multiple parent classes:
```
beckn:PersonAsConsumer 
  rdfs:subClassOf: [beckn:Consumer, schema:Person]
```

**Strategy**: Prefer `beckn:` namespace over `schema:` or others

---

## Special Cases

### 1. Snake_case → camelCase

```
v2.0: "display_name"
     ↓
     "displayName" (normalized)
     ↓
     beckn:name
     ↓
v2.1: "name"
```

### 2. Attribute Packs

When target is an `Attributes` type:
```json
{
  "@context": "https://..../context.jsonld",
  "@type": "ChargingSession",
  "connectorType": "CCS2",
  "maxPowerKW": 50
}
```

Check parent schema to determine correct pack placement.

### 3. Structure Transformations

**v2.0 Payment** (single object):
```json
{
  "beckn:payment": {
    "beckn:id": "...",
    "beckn:paymentStatus": "COMPLETED",
    "beckn:beneficiary": "BPP",
    "beckn:paymentAttributes": {
      "settlementAccounts": [...]
    }
  }
}
```

**v2.1 PaymentTerms + PaymentAction** (split structure):
```json
{
  "paymentTerms": {
    "@type": "PaymentTerms",
    "collectedBy": "BPP",
    "settlements": [
      {
        "@type": "SettlementTerm",
        "amount": {...},
        "payTo": {...}
      }
    ]
  },
  "paymentAction": {
    "@type": "PaymentAction",
    "paymentStatus": "COMPLETED",
    "amount": {...}
  }
}
```

---

## Implementation Notes

### Circular Reference Prevention

Use a `visited` set to track IRIs already processed:
```python
visited = set()
while True:
    if current_iri in visited:
        break  # Circular reference
    visited.add(current_iri)
    # ... resolution logic
```

### Maximum Iterations

Set a maximum iteration count (e.g., 20) to prevent infinite loops:
```python
max_iterations = 20
for i in range(max_iterations):
    # ... resolution logic
```

### Resolution Chain Audit Trail

Maintain complete chain for debugging:
```python
ResolutionStep(
    step_number=n,
    iri="beckn:consumer",
    source=ResolutionSource.CONTEXT_MAPPING,
    deprecated=False,
    notes="Mapped via context"
)
```

---

## API Reference

### `IRIResolver.resolve_iri(input_iri, json_path="")`

**Parameters**:
- `input_iri` (str): IRI from v2.0 JSON (e.g., "beckn:buyer", "displayName")
- `json_path` (str): JSON path for debugging (e.g., "$.message.order.buyer")

**Returns**: `ResolvedIRI` object with:
- `canonical_iri`: Final canonical IRI
- `v21_keyword`: Corresponding v2.1 keyword
- `resolution_chain`: Complete resolution steps
- `is_deprecated`: Whether original IRI was deprecated
- `warnings`: List of warnings
- `target_schema`: Schema definition from attributes.yaml

---

## Testing

Run the test suite:
```bash
cd /home/ravi/www/protocol-specifications-v2
python3 scripts/v2.1/v2_to_v21_converter/iri_resolver.py
```

Expected output shows resolution chains for common v2.0 fields.

---

## Future Enhancements

1. **Value Transformation**: Implement Step 6 to actually transform JSON values
2. **Nested Resolution**: Recursively resolve all nested fields in a JSON object
3. **Validation**: Validate transformed JSON against v2.1 schemas
4. **Performance**: Cache resolution results for frequently used IRIs
5. **Reporting**: Generate transformation reports showing all changes

---

## References

- v2.0 Context: `schema/core/v2/context.jsonld`
- v2.1 Context: `schema/core/v2.1/updated.context.jsonld`
- v2.1 Vocabulary: `schema/core/v2.1/updated.vocab.jsonld`
- v2.1 Schemas: `schema/core/v2.1/attributes.yaml`

---

**Version**: 1.0.0  
**Last Updated**: 2026-12-02  
**Author**: Beckn Protocol Team
