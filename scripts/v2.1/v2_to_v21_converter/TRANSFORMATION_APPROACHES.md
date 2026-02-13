# Beckn Protocol Version Transformation - Approaches Comparison

## Overview

This document compares three approaches to transforming Beckn protocol JSON between versions, evolving from custom rules to pure semantic web standards.

## Version History

### v1: Hybrid Approach (IRI + Structural Rules)
**Status:** ✅ Working (backed up as `becknVersionTransform_v1_backup.py`)

**Components:**
- `becknVersionTransform.py` - IRI transformer + structural rules
- `structural_transforms.yaml` - YAML-based transformation rules
- `transformerGUI.py` - GUI with hybrid mode support

**How it works:**
```
Input → IRI Resolution → Strip Prefixes → Apply YAML Rules → Output
```

**Pros:**
- ✅ Works immediately
- ✅ Explicit transformation rules (debuggable)
- ✅ Handles complex structural changes

**Cons:**
- ❌ Requires manual YAML rule maintenance
- ❌ Not using standard vocabularies
- ❌ Beckn-specific (not portable)

**Use cases:**
- Quick prototyping
- Complex transformations not yet encoded in ontology
- Temporary migration bridge

---

### v3: Pure Semantic Approach (DCT + @container + SHACL)
**Status:** 🚧 Ready (requires ontology file updates)

**Components:**
- `becknSemanticTransform.py` - Pure semantic transformer
- `updated.context.jsonld` - Enhanced with @container
- `updated.vocab.jsonld` - Enhanced with DCT predicates
- `shapes/*.ttl` - Optional SHACL shapes (future)

**How it works:**
```
Input → IRI Expansion → DCT Replacement → @container Transform → SHACL Validation → Output
```

**Pros:**
- ✅ Uses W3C standards (JSON-LD, DCT, SHACL)
- ✅ Transformation encoded in ontology
- ✅ Portable and reusable
- ✅ No custom rules needed

**Cons:**
- ⚠️ Requires ontology updates to be functional
- ⚠️ More complex initial setup

**Use cases:**
- Production-grade transformations
- Standard-compliant systems
- Long-term maintainability

---

## Key Differences

| Feature | v1 Hybrid | v3 Semantic |
|---------|-----------|-------------|
| **Singular → Plural** | YAML rule: `$.order.fulfillment` → `$.order.fulfillments` | @container: `"@list"` in context |
| **Property Replacement** | YAML: source_path/target_path | DCT: `dct:isReplacedBy` |
| **Object Splitting** | YAML: object_split with property distribution | SHACL: shape-based restructuring |
| **Standards** | Custom YAML DSL | JSON-LD + DCT + SHACL |
| **Maintenance** | Update YAML file | Update ontology files |
| **Validation** | Manual checking | SHACL constraints |

---

## Examples

### Singular → Plural Transformation

**v1 Hybrid (structural_transforms.yaml):**
```yaml
- name: "fulfillment_to_fulfillments"
  source_path: "$.message.order.fulfillment"
  target_path: "$.message.order.fulfillments"
  transform_type: "nested_path"
  value_wrapping: "to_array"
```

**v3 Semantic (updated.context.jsonld):**
```jsonld
{
  "@context": {
    "fulfillment": "beckn:fulfillment",
    "fulfillments": {
      "@id": "beckn:fulfillment",
      "@container": "@list"
    }
  }
}
```

The transformation is **implicit** - JSON-LD handles it automatically!

---

### Property Replacement

**v1 Hybrid (structural_transforms.yaml):**
```yaml
- name: "buyer_to_consumer"
  source_path: "$.message.order.buyer"
  target_path: "$.message.order.consumer.person"
  transform_type: "nested_path"
```

**v3 Semantic (updated.vocab.jsonld):**
```jsonld
{
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

Plus in updated.context.jsonld:
```jsonld
{
  "@context": {
    "buyer": "beckn:consumer"  // Direct alias
  }
}
```

---

## Migration Path

### Phase 1: Current State ✅
- v1 Hybrid is working
- Transformations verified:
  - `buyer` → `consumer.person` ✅
  - `seller` → `provider.descriptor.id` ✅
  - `payment` → `paymentAction` ✅

### Phase 2: Ontology Enhancement 🚧
Update ontology files:

1. **Add DCT namespace** to `updated.vocab.jsonld`:
```jsonld
{
  "@context": {
    "dct": "http://purl.org/dc/terms/",
    "sh": "http://www.w3.org/ns/shacl#"
  }
}
```

2. **Add @container to context**:
```jsonld
"fulfillments": {
  "@id": "beckn:fulfillment",
  "@container": "@list"
}
```

3. **Add DCT predicates** to vocab entries:
```jsonld
{
  "@id": "beckn:buyer",
  "dct:isReplacedBy": {"@id": "beckn:consumer"}
}
```

### Phase 3: Testing & Validation 🔜
- Test semantic transformer with enhanced ontology
- Compare outputs between v1 and v3
- Validate SHACL shapes

### Phase 4: Production 🎯
- Use v3 semantic transformer as primary
- Keep v1 as fallback
- Deprecate YAML structural rules

---

## GUI Features

The unified GUI (`transformerGUI.py`) now supports both approaches:

**Radio Button Selection:**
- 🔘 Semantic (DCT + @container) - Pure semantic web
- 🔘 Hybrid (IRI + Structural Rules) - Hybrid approach

**Mode-Specific Controls:**
- **Hybrid Mode:** Upload structural_transforms.yaml
- **Semantic Mode:** Upload SHACL shapes (optional)

**Common Features:**
- Dual-pane JSON viewer
- Expected output comparison
- HTML diff report generation
- Copy/Save output

---

## Usage Examples

### Using Hybrid Mode (v1)
```bash
# CLI
python3 becknVersionTransform.py -ov 2.1 -i input.json -o output.json \
  --structural-rules structural_transforms.yaml

# GUI: Select "Hybrid" mode, upload structural_transforms.yaml
```

### Using Semantic Mode (v3)
```bash
# CLI
python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json \
  --shacl shapes/v2_to_v21.ttl

# GUI: Select "Semantic" mode, optionally upload SHACL shapes
```

---

## Recommendations

**For Immediate Use:**
- Use **v1 Hybrid** mode with `structural_transforms.yaml`
- All 4 failing transformations are now working

**For Long-Term:**
- Enhance ontology files with DCT and @container
- Migrate to **v3 Semantic** mode
- Remove dependency on YAML structural rules

**For Development:**
- Keep both modes in GUI for comparison
- Use diff report to verify equivalent behavior
- Gradually migrate rules to ontology

---

## References

- [JSON-LD 1.1 Specification](https://www.w3.org/TR/json-ld11/)
- [Dublin Core Terms](http://purl.org/dc/terms/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [OWL Web Ontology Language](https://www.w3.org/OWL/)

---

**Last Updated:** 2026-02-13
**Status:** v1 production-ready, v3 requires ontology updates
