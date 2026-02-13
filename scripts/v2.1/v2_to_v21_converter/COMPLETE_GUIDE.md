# Beckn Protocol Version Transformation - Complete Guide

## 🎯 Overview

This directory contains **two transformation approaches** for converting Beckn protocol JSON between versions:

1. **Hybrid Approach (v1)** - IRI resolution + YAML structural rules ✅ **Production Ready**
2. **Semantic Approach (v3)** - Pure JSON-LD/DCT/SHACL 🚧 **Requires Ontology Updates**

Both approaches are integrated into a **unified GUI** with mode selection.

---

## 📁 File Structure

```
v2_to_v21_converter/
├── becknVersionTransform.py              # v1: Hybrid transformer (IRI + structural rules)
├── becknVersionTransform_v1_backup.py    # Backup of v1
├── becknSemanticTransform.py             # v3: Pure semantic transformer
├── structural_transforms.yaml             # v1: YAML transformation rules
├── structural_transforms_v1_backup.yaml   # Backup of rules
├── transformerGUI.py                      # Unified GUI (supports both modes)
├── TRANSFORMATION_APPROACHES.md           # Detailed comparison
├── SEMANTIC_TRANSFORM_README.md           # v3 documentation
└── COMPLETE_GUIDE.md                      # This file
```

---

## 🚀 Quick Start

### Option A: Use the GUI (Recommended)

```bash
cd scripts/v2.1/v2_to_v21_converter
python3 transformerGUI.py
```

**In the GUI:**
1. Upload your input JSON file
2. Select transformation mode:
   - **Hybrid** (with structural_transforms.yaml) ← **Works Now!**
   - **Semantic** (requires ontology updates) ← **Future**
3. Optionally upload expected output for comparison
4. Click "Transform"
5. View diff report if differences found

### Option B: Use CLI - Hybrid Mode (v1)

```bash
python3 becknVersionTransform.py \
  -ov 2.1 \
  -i ../../../DEG/examples/ev-charging/v2/08_00_on_confirm/v2_0_ev-charging-on-confirm.json \
  -o output_v2.1.json \
  --structural-rules structural_transforms.yaml \
  -v
```

### Option C: Use CLI - Semantic Mode (v3)

```bash
python3 becknSemanticTransform.py \
  -ov 2.1 \
  -i input.json \
  -o output.json \
  -v
```

*(Note: Requires ontology files to be updated with DCT and @container)*

---

## ✅ Verified Working Transformations (v1 Hybrid)

| v2.0 Field | v2.1 Field | Status |
|------------|------------|--------|
| `order.buyer` | `order.consumer.person` | ✅ WORKING |
| `order.seller` | `order.provider.descriptor.id` | ✅ WORKING |
| `order.payment` | `order.paymentAction` + `order.paymentTerms` | ✅ WORKING |
| `payment.collectedBy` | `paymentTerms.collectedBy` | ✅ WORKING |

---

## 🔧 How It Works

### v1 Hybrid Approach

**Two-Phase Transformation:**

```
Phase 1: IRI Resolution
──────────────────────
Input JSON (beckn: prefixed)
    ↓
Expand IRIs using updated.context.jsonld
    ↓
Follow owl:equivalentProperty chains
    ↓
Follow rdfs:subPropertyOf chains
    ↓
Resolve to canonical IRIs
    ↓
Strip prefixes
    ↓
Intermediate JSON (no prefixes)

Phase 2: Structural Transformation
───────────────────────────────────
Intermediate JSON
    ↓
Apply structural_transforms.yaml rules:
  - nested_path (buyer → consumer.person)
  - object_split (payment → paymentAction + paymentTerms)
  - property_relocation (move properties)
    ↓
Final JSON (v2.1)
```

**Key Files:**
- `updated.context.jsonld` - IRI to keyword mappings
- `updated.vocab.jsonld` - OWL/RDFS relationships
- `structural_transforms.yaml` - Complex structural rules

### v3 Semantic Approach (Future)

**Single-Phase Semantic Reasoning:**

```
Input JSON
    ↓
IRI Expansion
    ↓
DCT Replacement Chain (dct:isReplacedBy)
    ↓
@container Transformation (singular ↔ plural)
    ↓
SHACL Shape Validation
    ↓
Output JSON
```

**Requirements:**
- Add DCT namespace to vocab
- Add @container to context
- Define SHACL shapes for constraints

---

## 📊 GUI Features

### Transformation Mode Selection
- **Hybrid Mode:** Uses structural_transforms.yaml for complex transformations
- **Semantic Mode:** Uses pure JSON-LD semantics (requires enhanced ontology)

### File Uploads
- **Input JSON** (required)
- **Context, Vocab, Attributes** (optional - uses defaults for v2.1)
- **Structural Rules** (hybrid mode only)
- **SHACL Shapes** (semantic mode only)
- **Expected Output** (optional - enables diff comparison)

### Features
- ✅ Dual-pane JSON viewer (input/output)
- ✅ Real-time transformation
- ✅ Expected output comparison
- ✅ HTML diff report generation
- ✅ Copy/Save output
- ✅ Transformation statistics
- ✅ Warning display

---

## 🧪 Testing

### Test the Hybrid Transformer

```bash
# Run the test pipeline
python3 test_full_pipeline.py
```

**Expected Output:**
```
✓ consumer field created
  ✓ consumer.person exists
✓ provider field created
  ✓ provider.descriptor.id = cpo1.com
✓ paymentAction created
```

### Test with Real Data

```bash
python3 becknVersionTransform.py \
  -ov 2.1 \
  -i ../../../DEG/examples/ev-charging/v2/08_00_on_confirm/v2_0_ev-charging-on-confirm.json \
  -o transformed_output.json \
  --structural-rules structural_transforms.yaml \
  --no-metadata
```

---

## 📝 Structural Transformation Rules

The `structural_transforms.yaml` file defines these transformations:

### 1. Buyer → Consumer.Person
```yaml
- name: "buyer_to_consumer_person"
  source_path: "$.message.order.buyer"
  target_path: "$.message.order.consumer.person"
  transform_type: "nested_path"
```

### 2. Seller → Provider.Descriptor.Id
```yaml
- name: "seller_to_provider_descriptor_id"
  source_path: "$.message.order.seller"
  target_path: "$.message.order.provider.descriptor.id"
  transform_type: "nested_path"
```

### 3. Payment Splitting
```yaml
- name: "split_payment_object"
  source_path: "$.message.order.payment"
  transform_type: "object_split"
  target_objects:
    paymentAction:
      target_path: "$.message.order.paymentAction"
      properties: ["method", "amount", "paymentURL", ...]
    paymentTerms:
      target_path: "$.message.order.paymentTerms"
      properties: ["collectedBy", "settlementTerms", ...]
```

---

## 🔮 Future: Semantic Approach

### What Needs to Be Added to Ontology

#### 1. Add DCT Namespace (updated.vocab.jsonld)
```jsonld
{
  "@context": {
    "dct": "http://purl.org/dc/terms/",
    "sh": "http://www.w3.org/ns/shacl#"
  }
}
```

#### 2. Add @container (updated.context.jsonld)
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

#### 3. Add DCT Predicates (updated.vocab.jsonld)
```jsonld
{
  "@id": "beckn:buyer",
  "dct:isReplacedBy": {"@id": "beckn:consumer"},
  "owl:deprecated": true
}
```

#### 4. Create SHACL Shapes (shapes/v2_to_v21.ttl)
```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix beckn: <...> .

:OrderV21Shape a sh:NodeShape ;
  sh:targetClass beckn:Order ;
  sh:property [
    sh:path beckn:consumer ;
    sh:minCount 1 ;
    sh:class beckn:Consumer ;
  ] .
```

---

## 🎓 Learning Resources

### For Hybrid Approach (v1)
- Read: `TRANSFORMATION_APPROACHES.md`
- Study: `structural_transforms.yaml`
- Run: `test_full_pipeline.py`

### For Semantic Approach (v3)
- Read: `SEMANTIC_TRANSFORM_README.md`
- Understand: JSON-LD @container
- Learn: Dublin Core Terms (DCT)
- Explore: SHACL constraints

---

## 🐛 Troubleshooting

### GUI doesn't start
```bash
# Check if tkinter is installed
python3 -m tkinter

# If not, install:
sudo apt-get install python3-tk
```

### Transformation fails
```bash
# Run with verbose mode to see details
python3 becknVersionTransform.py -ov 2.1 -i input.json -v
```

### Structural rules not applying
- Ensure rules file path is correct
- Check that prefixes are stripped before rules apply
- Run `test_full_pipeline.py` to debug

---

## 📞 Support

For issues or questions:
1. Check the test scripts: `test_full_pipeline.py`, `test_structural.py`
2. Review documentation: `TRANSFORMATION_APPROACHES.md`
3. Examine backups: `*_v1_backup.py`

---

## 🎉 Summary

**Current Status:** 
- ✅ v1 Hybrid approach is **production-ready**
- ✅ GUI supports both modes
- ✅ All 4 failing transformations now work correctly
- 🚧 v3 Semantic approach awaits ontology enhancements

**Recommendation:**
Use **v1 Hybrid mode** for immediate transformation needs. Plan migration to **v3 Semantic mode** as the ontology matures.

---

**Last Updated:** 2026-02-13  
**Version:** 1.0.0  
**Status:** Production Ready (v1), Experimental (v3)
