# Beckn v2.0 → v2.1 Payload Converter

**Gateway/adapter tool** that converts Beckn Protocol v2.0 API payloads to v2.1-compatible format, enabling seamless backward compatibility for legacy clients.

## Features

- ✅ **Envelope context conversion**: `snake_case` → `camelCase` (e.g., `transaction_id` → `transactionId`)
- ✅ **JSON-LD key migration**: Removes prefixes (`beckn:id` → `id`, `schema:name` → `name`)
- ✅ **Structural transformations**:
  - `Order.seller` → `Order.provider`
  - `Order.buyer` → `Order.consumer.person`
  - `Payment` → `PaymentTerms` + `PaymentAction` decomposition
  - `fulfillment` → `fulfillments[]` (cardinality change)
  - `invoice` → `invoices[]`
- ✅ **Descriptor field migration**: `schema:name` → `name`, `schema:image[0]` → `thumbnailImage`
- ✅ **Tracking field updates**: `expires_at` → `expiresAt`, drop `tl_method` with warning
- ✅ **Form field updates**: `mime_type` → `mimeType`, `submission_id` → `submissionId`
- ✅ **Version override**: Sets `context.version` to `"2.1.0"`
- ✅ **Conversion reports**: Warnings for unmappable/dropped fields

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using the package directly
cd scripts/v2.1/v2_to_v21_converter
python -m pip install -e .
```

## Usage

### Command Line

```bash
# Convert a single v2.0 payload file
python -m v2_to_v21_converter.cli convert input_v2.json -o output_v21.json

# Convert with verbose reporting
python -m v2_to_v21_converter.cli convert input_v2.json -o output_v21.json --verbose

# Convert and validate against v2.1 schemas
python -m v2_to_v21_converter.cli convert input_v2.json -o output_v21.json --validate
```

### Python API

```python
from v2_to_v21_converter import convert_v2_to_v21

# Convert a v2.0 payload
v2_payload = {
    "context": {
        "transaction_id": "abc-123",
        "message_id": "def-456",
        "version": "2.0.0"
    },
    "message": {
        "order": {
            "@context": "https://...",
            "@type": "beckn:Order",
            "beckn:id": "order-001",
            "beckn:seller": {"beckn:id": "provider-123"},
            "beckn:buyer": {"beckn:id": "buyer-456"},
            "beckn:payment": {
                "beckn:method": "UPI",
                "beckn:paymentStatus": "COMPLETED"
            }
        }
    }
}

result = convert_v2_to_v21(v2_payload)

print(result.converted_payload)
print(result.report.summary())
```

## Conversion Rules

### Envelope Context

| v2.0 (snake_case) | v2.1 (camelCase) |
|-------------------|------------------|
| `transaction_id` | `transactionId` |
| `message_id` | `messageId` |
| `bap_id` | `bapId` |
| `bap_uri` | `bapUri` |
| `bpp_id` | `bppId` |
| `bpp_uri` | `bppUri` |
| `schema_context` | `schemas` |

### Entity Keys (JSON-LD)

| v2.0 (prefixed) | v2.1 (unprefixed) |
|-----------------|-------------------|
| `beckn:id` | `id` |
| `beckn:descriptor` | `descriptor` |
| `schema:name` | `name` |
| `schema:image` | `thumbnailImage` (first image) |
| `beckn:shortDesc` | `shortDesc` |

### Structural Mappings

#### Order Entity
- `beckn:seller` → `provider`
- `beckn:buyer` → `consumer` (with nested `person` identity)
- `beckn:orderItems` → `orderItems`
- `beckn:fulfillment` → `fulfillments[]` (wrap single to array)
- `beckn:invoice` → `invoices[]` (wrap single to array)
- `beckn:payment` → Split into:
  - `paymentTerms` (terms, settlement info)
  - `paymentAction` (status, transaction refs)

#### Payment Decomposition
```python
# v2.0 Payment
{
    "beckn:method": "UPI",
    "beckn:paymentStatus": "COMPLETED",
    "beckn:amount": {...},
    "beckn:beneficiary": "BPP"
}

# v2.1 PaymentTerms + PaymentAction
{
    "paymentTerms": {
        "@context": "...",
        "@type": "beckn:PaymentTerms",
        "collectedBy": "BPP",
        "settlementTerms": [...]
    },
    "paymentAction": {
        "@context": "...",
        "@type": "beckn:PaymentAction",
        "paymentStatus": "COMPLETED",
        "amount": {...}
    }
}
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_converter.py -v

# Run with coverage
pytest --cov=v2_to_v21_converter tests/
```

## Architecture

```
v2_to_v21_converter/
├── __init__.py          # Public API
├── converter.py         # Main conversion orchestrator
├── rules.py            # Mapping rules & transformations
├── report.py           # Conversion report generator
└── cli.py              # Command-line interface

tests/
├── fixtures/           # v2.0 payload test data
├── test_converter.py   # Conversion tests
├── test_rules.py       # Rule-specific tests
└── test_report.py      # Report generation tests
```

## Limitations

1. **Context URL References**: Does not modify `@context` URLs (left as-is)
2. **Custom Attributes**: Attribute packs are passed through unchanged
3. **Validation**: Optional schema validation requires external validator
4. **One-way Conversion**: v2.1 → v2.0 conversion not supported

## License

Same as parent project (CC-BY-NC-SA 4.0 International)
