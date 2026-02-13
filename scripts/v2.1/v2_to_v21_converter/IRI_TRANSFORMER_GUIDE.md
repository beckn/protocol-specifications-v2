# Pure IRI-Based Transformation Algorithm

## Overview

This document describes the **pure IRI-based transformation algorithm** that converts Beckn v2.0 JSON payloads to v2.1 format using **only ontological resolution** through IRI mappings.

## Core Principles

### 1. No Hardcoded Mappings
- **Zero** hardcoded field name transformations
- All mappings come from ontology files at runtime
- Schema-driven validation

### 2. Runtime Context Resolution
- Reads `@context` from each JSON object
- Reads `@type` to determine schema
- Dynamically resolves IRIs based on local and global contexts

### 3. Three Input Files Only
The algorithm uses **exactly three files**:

```
schema/core/v2.1/updated.context.jsonld   # IRI to keyword mappings
schema/core/v2.1/updated.vocab.jsonld     # Ontology relationships
schema/core/v2.1/attributes.yaml          # v2.1 schema definitions
```

## Algorithm Flow

### Phase 1: Initialization

```python
# Load ontology files
context = load("updated.context.jsonld")
vocab = load("updated.vocab.jsonld")
schemas = load("attributes.yaml")

# Build indexes
keyword_to_iri = index(context)
iri_to_keyword = index(context)
vocab_index = index(vocab)
schema_index = index(schemas)
```

### Phase 2: IRI Expansion

For each JSON key:

```
Input: "beckn:buyer" or "buyer"
↓
1. Check if already expanded (starts with http://)
2. Try local @context if available
3. Check if prefixed (beckn:, schema:, etc.)
4. Lookup in global context
↓
Output: "https://schema.beckn.org/core/buyer"
```

### Phase 3: Ontological Resolution

Follow the ontology chain to find canonical v2.1 IRI:

```
Input IRI: "https://schema.beckn.org/core/v2/buyer"
↓
1. Lookup in vocab.jsonld
2. Check for owl:equivalentClass or owl:equivalentProperty
3. If not found, check rdfs:subClassOf or rdfs:subPropertyOf
4. Follow chain recursively (max 20 hops)
5. Detect and prevent circular references
↓
Canonical IRI: "https://schema.beckn.org/core/v2.1/consumer"
```

### Phase 4: Keyword Mapping

```
Canonical IRI: "https://schema.beckn.org/core/v2.1/consumer"
↓
Lookup in context.jsonld
↓
v2.1 Keyword: "consumer"
```

### Phase 5: Recursive Transformation

```python
def transform_object(obj):
    if obj is primitive:
        return obj
    
    if obj is array:
        return [transform_object(item) for item in obj]
    
    if obj is dict:
        # Extract @context and @type
        context = obj.get("@context")
        type = obj.get("@type")
        
        # For each property
        for key, value in obj.items():
            # Expand IRI
            key_iri = expand(key, context)
            
            # Resolve to canonical
            canonical_iri, v21_keyword = resolve(key_iri)
            
            # Transform value recursively
            new_value = transform_object(value)
            
            # Store with v2.1 keyword
            result[v21_keyword] = new_value
        
        # Update @context to v2.1 URL
        result["@context"] = "v2.1/context.jsonld"
        
        return result
```

## Ontology Relationship Priority

The algorithm follows ontology relationships in this order:

1. **owl:equivalentClass** (highest priority)
   - Direct equivalence between classes
   
2. **owl:equivalentProperty**
   - Direct equivalence between properties
   
3. **rdfs:subClassOf**
   - Class inheritance
   - Prefers `beckn:` namespace when multiple options exist
   
4. **rdfs:subPropertyOf** (lowest priority)
   - Property inheritance

## Example Transformation

### Input (v2.0)
```json
{
  "@context": "v2/context.jsonld",
  "@type": "beckn:Order",
  "beckn:buyer": {
    "@type": "beckn:Buyer",
    "beckn:id": "buyer-123",
    "beckn:displayName": "John Doe"
  }
}
```

### Resolution Process

1. **Expand `beckn:buyer`**:
   ```
   "beckn:buyer" → "https://schema.beckn.org/core/v2/buyer"
   ```

2. **Resolve through vocab**:
   ```json
   {
     "@id": "https://schema.beckn.org/core/v2/buyer",
     "owl:equivalentProperty": {
       "@id": "https://schema.beckn.org/core/v2.1/consumer"
     }
   }
   ```

3. **Get v2.1 keyword**:
   ```
   "https://schema.beckn.org/core/v2.1/consumer" → "consumer"
   ```

4. **Expand `beckn:Buyer` type**:
   ```
   "beckn:Buyer" → "https://schema.beckn.org/core/v2/Buyer"
   ```

5. **Resolve through vocab**:
   ```json
   {
     "@id": "https://schema.beckn.org/core/v2/Buyer",
     "owl:equivalentClass": {
       "@id": "https://schema.beckn.org/core/v2.1/Consumer"
     }
   }
   ```

6. **Get v2.1 keyword**:
   ```
   "https://schema.beckn.org/core/v2.1/Consumer" → "Consumer"
   ```

### Output (v2.1)
```json
{
  "@context": "v2.1/context.jsonld",
  "@type": "beckn:Order",
  "consumer": {
    "@type": "Consumer",
    "id": "buyer-123",
    "name": "John Doe"
  }
}
```

## Key Features

### ✅ Pure IRI Transformation
- No hardcoded rules
- All mappings from ontology files
- Semantic web standards (JSON-LD, OWL, RDFS)

### ✅ Context-Aware
- Reads `@context` from each object
- Handles both local and global contexts
- Supports context URLs and inline contexts

### ✅ Type-Driven
- Uses `@type` to determine schema
- Validates against v2.1 schema definitions
- Warns about missing or dropped properties

### ✅ Recursive
- Handles deeply nested objects
- Transforms arrays of objects
- Preserves primitive values

### ✅ Robust
- Circular reference detection
- Deprecation warnings
- Transformation statistics

### ✅ Schema-Validated
- Checks properties against v2.1 schemas
- Warns about schema mismatches
- Extensible for full JSON Schema validation

## Usage

### Python API

```python
from iri_transformer import IRITransformer

# Initialize transformer
transformer = IRITransformer()

# Transform v2.0 payload
v2_payload = {...}
v21_payload, warnings, stats = transformer.transform_and_validate(v2_payload)

# Or use simplified interface
v21_payload = transformer.transform_payload(v2_payload)
```

### Command Line

```bash
# Transform a file
python3 -m iri_transformer input_v2.json -o output_v21.json

# With verbose output
python3 -m iri_transformer input_v2.json -o output_v21.json -v

# Test with example
python3 scripts/v2.1/v2_to_v21_converter/iri_transformer.py
```

## Transformation Metadata

The transformer provides detailed metadata:

### Warnings
- Circular references detected
- Deprecated IRIs used
- Properties not in v2.1 schema
- Failed IRI expansions

### Statistics
- Number of transformations per field
- Total objects transformed
- Depth of nesting processed
- Resolution hops taken

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  IRITransformer                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Indexes:                                            │
│  ┌────────────────────────────────────────────┐    │
│  │ keyword_to_iri    (str → str)              │    │
│  │ iri_to_keyword    (str → str)              │    │
│  │ vocab_index       (str → dict)             │    │
│  │ schema_index      (str → dict)             │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  Methods:                                            │
│  ┌────────────────────────────────────────────┐    │
│  │ expand_iri()       - Compact → Full IRI    │    │
│  │ resolve_to_canonical() - Ontology chain    │    │
│  │ get_schema_for_type() - Type → Schema      │    │
│  │ transform_object() - Recursive transform   │    │
│  │ transform_payload() - Main entry point     │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
         ↑             ↑              ↑
         │             │              │
         │             │              │
    context.jsonld  vocab.jsonld  attributes.yaml
```

## Comparison with Old Converter

| Feature | Old Converter | IRI Transformer |
|---------|--------------|-----------------|
| Field Mappings | Hardcoded in rules.py | Pure IRI resolution |
| Context Reading | Static | Runtime dynamic |
| Ontology Use | Minimal | Full OWL/RDFS |
| Dropped Fields | Hardcoded list | Schema-driven |
| Extensibility | Requires code changes | Just update ontology |
| Standards | Custom | JSON-LD, OWL, RDFS |
| Maintainability | High coupling | Decoupled |

## Benefits

### 1. Maintainability
- No code changes needed for new field mappings
- Just update ontology files
- Self-documenting through semantics

### 2. Correctness
- Mappings verified through ontology
- Type-safe transformations
- Schema-validated output

### 3. Transparency
- Clear transformation chain
- Traceable through vocab
- Audit trail in metadata

### 4. Flexibility
- Works with any domain extension
- Handles custom contexts
- Extensible validation

### 5. Standards Compliance
- Pure JSON-LD transformation
- OWL ontology principles
- RDFS hierarchies

## Testing

```python
# Test with example payload
python3 scripts/v2.1/v2_to_v21_converter/iri_transformer.py

# Expected output:
# - Transformed payload in v2.1 format
# - @context URLs updated to v2.1
# - Field names transformed via IRI resolution
# - No hardcoded mappings used
```

## Future Enhancements

1. **Full JSON Schema Validation**
   - Validate transformed output against OpenAPI schemas
   - Type checking for all properties
   - Required field validation

2. **Bidirectional Transformation**
   - v2.1 → v2.0 reverse transformation
   - Round-trip validation

3. **Performance Optimization**
   - Cache IRI resolutions
   - Parallel object transformation
   - Lazy index building

4. **Extended Reporting**
   - Detailed transformation logs
   - Visual ontology chain diagrams
   - Compatibility reports

## Conclusion

This pure IRI-based transformation algorithm represents a **semantic web approach** to protocol version migration. By leveraging JSON-LD, OWL, and RDFS standards, it achieves:

- **Zero hardcoded mappings**
- **Runtime context resolution**
- **Ontology-driven transformation**
- **Schema-validated output**
- **Full traceability**

This makes it the **canonical** method for v2.0 → v2.1 conversion in the Beckn protocol ecosystem.
