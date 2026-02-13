# Beckn Semantic Transformer

## Overview

This is a **pure semantic web transformation** approach that eliminates the need for custom structural rules by encoding all transformation logic directly in the ontology using standard vocabularies.

## Key Innovations

### 1. @container for Singular/Plural Transformation

Instead of custom rules to transform `fulfillment` → `fulfillments`, we use JSON-LD's native `@container` mechanism:

```jsonld
{
  "@context": {
    "fulfillment": {
      "@id": "beckn:fulfillment",
      "@container": null  // v2.0: singular
    },
    "fulfillments": {
      "@id": "beckn:fulfillment",  // Same IRI!
      "@container": "@list"  // v2.1: ordered list
    }
  }
}
```

The transformer automatically:
- Wraps single values in arrays when going to `@list`
- Extracts first element when going from `@list` to singular

### 2. DCT (Dublin Core Terms) for Version Migration

Instead of `owl:deprecated`, we use **DCT replacement predicates**:

```turtle
beckn:buyer 
  dct:isReplacedBy beckn:consumer ;
  owl:deprecated true .

beckn:consumer
  dct:replaces beckn:buyer .
```

This creates a **bidirectional replacement chain** that the transformer follows automatically.

### 3. SHACL Shapes for Structural Constraints

SHACL (Shapes Constraint Language) validates and guides transformation:

```turtle
:OrderV2Shape a sh:NodeShape ;
  sh:targetClass beckn:Order ;
  sh:property [
    sh:path beckn:buyer ;
    sh:class beckn:Buyer ;
    sh:maxCount 1 ;
  ] .

:OrderV21Shape a sh:NodeShape ;
  sh:targetClass beckn:Order ;
  sh:property [
    sh:path beckn:consumer ;
    sh:class beckn:Consumer ;
    sh:minCount 1 ;
  ] .
```

## Implementation Status

### ✅ Completed
- Core semantic transformer with @container support
- DCT replacement chain resolution
- OWL/RDFS ontological reasoning
- CLI interface

### 🔧 Next Steps

To make this fully operational, we need to **update the ontology files**:

#### 1. Update `updated.context.jsonld`

Add @container specifications:

```jsonld
{
  "@context": {
    "fulfillment": {
      "@id": "beckn:fulfillment"
      // No @container (singular in v2.0)
    },
    "fulfillments": {
      "@id": "beckn:fulfillment",
      "@container": "@list"  // ADD THIS
    }
  }
}
```

#### 2. Update `updated.vocab.jsonld`

Add DCT namespace and predicates:

```jsonld
{
  "@context": {
    "dct": "http://purl.org/dc/terms/",
    // ... existing namespaces
  },
  "@graph": [
    {
      "@id": "beckn:buyer",
      "dct:isReplacedBy": {"@id": "beckn:consumer"},
      "owl:deprecated": true
    },
    {
      "@id": "beckn:consumer",
      "dct:replaces": {"@id": "beckn:buyer"}
    }
  ]
}
```

#### 3. Optional: Create SHACL Shapes

Create `shapes/v2_to_v21.ttl`:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix beckn: <https://...> .

:V2OrderShape a sh:NodeShape ;
  sh:targetClass beckn:Order ;
  sh:property [
    sh:path beckn:buyer ;
    sh:maxCount 1 ;
  ] .

:V21OrderShape a sh:NodeShape ;
  sh:targetClass beckn:Order ;
  sh:property [
    sh:path beckn:consumer ;
    sh:minCount 1 ;
  ] .
```

## Usage

```bash
# Basic transformation
python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json

# With SHACL validation
python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json \
  --shacl shapes/v2_to_v21.ttl

# Verbose mode
python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json -v
```

## Benefits Over Structural Rules

| Aspect | Structural Rules (v1) | Semantic Transform (v3) |
|--------|----------------------|-------------------------|
| **Approach** | Custom YAML rules | Standard vocabularies |
| **Singular/Plural** | Manual JSONPath rules | Native @container |
| **Replacements** | Hardcoded paths | DCT predicates |
| **Validation** | Manual checks | SHACL shapes |
| **Maintenance** | Update YAML file | Update ontology |
| **Standards** | Custom | W3C standards |
| **Portability** | Beckn-specific | Universal |

## Architecture

```
Input JSON (v2.0)
       ↓
[1] IRI Expansion
       ↓
[2] DCT Replacement Chain
       ↓
[3] OWL/RDFS Resolution
       ↓
[4] @container Transformation
       ↓
[5] SHACL Validation (optional)
       ↓
Output JSON (v2.1)
```

## Comparison: v1 vs v3

### v1 (Hybrid: IRI + Structural Rules)
```yaml
# structural_transforms.yaml
- source_path: "$.message.order.buyer"
  target_path: "$.message.order.consumer.person"
```

### v3 (Pure Semantic)
```jsonld
// updated.vocab.jsonld
{
  "@id": "beckn:buyer",
  "dct:isReplacedBy": {"@id": "beckn:consumer"}
}
```

The transformation is **implicit** in the ontology!

## Next Actions

1. **Review** this approach with the team
2. **Update** ontology files with @container and DCT predicates  
3. **Test** with real transformation scenarios
4. **Create** SHACL shapes for complex constraints
5. **Deprecate** structural_transforms.yaml once migration is complete

## References

- [JSON-LD @container](https://www.w3.org/TR/json-ld11/#sets-and-lists)
- [Dublin Core Terms](http://purl.org/dc/terms/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [OWL Web Ontology Language](https://www.w3.org/OWL/)
