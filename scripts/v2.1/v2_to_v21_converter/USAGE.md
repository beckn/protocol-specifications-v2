# Beckn Version Transform - Usage Guide

## Quick Start

Transform Beckn protocol JSON between versions using pure IRI-based transformation:

```bash
python3 becknVersionTransform.py -ov 2.1 -i path/to/input.json -o path/to/output.json
```

## Command-Line Interface

### Basic Syntax

```bash
python3 becknVersionTransform.py -ov <version> -i <input> -o <output>
```

### Required Arguments

- `-ov, --output-version` - Target version (e.g., `2.1`)
- `-i, --input` - Path to input JSON file

### Optional Arguments

- `-o, --output` - Path to output JSON file (if omitted, prints to stdout)
- `-v, --verbose` - Show warnings and transformation statistics
- `--no-metadata` - Exclude transformation metadata from output
- `-h, --help` - Show help message

## Examples

### 1. Basic Transformation

Transform v2.0 to v2.1:

```bash
python3 becknVersionTransform.py -ov 2.1 -i order_v2.json -o order_v2.1.json
```

### 2. Verbose Output

See warnings and statistics:

```bash
python3 becknVersionTransform.py -ov 2.1 -i order_v2.json -o order_v2.1.json -v
```

Output:
```
Initializing transformer for version 2.1...
Transforming payload...
✓ Transformed payload written to: order_v2.1.json

============================================================
TRANSFORMATION STATISTICS
============================================================
transformed_buyer_to_consumer: 1
transformed_seller_to_provider: 1

✓ Transformation completed successfully!
```

### 3. Output to Stdout

Pipe to other commands:

```bash
python3 becknVersionTransform.py -ov 2.1 -i order_v2.json | jq .
```

### 4. Clean Output (No Metadata)

Exclude transformation warnings and stats from output JSON:

```bash
python3 becknVersionTransform.py -ov 2.1 -i order_v2.json -o order_v2.1.json --no-metadata
```

### 5. Batch Processing

Transform multiple files:

```bash
for file in v2_payloads/*.json; do
    output="v2.1_payloads/$(basename $file)"
    python3 becknVersionTransform.py -ov 2.1 -i "$file" -o "$output" -v
done
```

## Integration Examples

### With jq for Validation

```bash
# Transform and validate structure
python3 becknVersionTransform.py -ov 2.1 -i input.json | jq 'keys'
```

### In CI/CD Pipeline

```bash
#!/bin/bash
# Transform and check for warnings
output=$(python3 becknVersionTransform.py -ov 2.1 -i input.json -o output.json -v 2>&1)

if echo "$output" | grep -q "⚠"; then
    echo "Warnings detected during transformation"
    exit 1
fi

echo "Transformation successful"
```

### Python Integration

```python
import subprocess
import json

def transform_payload(input_file, output_file, version="2.1"):
    """Transform Beckn payload to target version"""
    cmd = [
        "python3",
        "becknVersionTransform.py",
        "-ov", version,
        "-i", input_file,
        "-o", output_file,
        "-v"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Transformation failed: {result.stderr}")
    
    return result.stdout

# Usage
transform_payload("order_v2.json", "order_v2.1.json")
```

## Output Format

### With Metadata (Default)

```json
{
  "@context": "https://.../v2.1/context.jsonld",
  "context": { ... },
  "message": { ... },
  "_transformation_warnings": [
    "Property 'x' not found in v2.1 schema"
  ],
  "_transformation_stats": {
    "transformed_buyer_to_consumer": 1
  }
}
```

### Without Metadata (`--no-metadata`)

```json
{
  "@context": "https://.../v2.1/context.jsonld",
  "context": { ... },
  "message": { ... }
}
```

## How It Works

The transformer uses **pure IRI resolution**:

1. **Reads @context** from each JSON object at runtime
2. **Expands IRIs** using context mappings
3. **Resolves through ontology** using `vocab.jsonld` relationships
4. **Maps to target keywords** using target version's `context.jsonld`
5. **Validates** against `attributes.yaml` schemas

**No hardcoded field mappings** - all transformations are semantic!

## Transformation Process

```
Input (v2.0)
    ↓
[Read @context & @type]
    ↓
[Expand IRIs]
    ↓
[Resolve through vocab.jsonld]
 - owl:equivalentProperty
 - owl:equivalentClass
 - rdfs:subPropertyOf
 - rdfs:subClassOf
    ↓
[Map to v2.1 keywords]
    ↓
[Validate against schema]
    ↓
Output (v2.1)
```

## Files Used

The transformer uses **only 3 files**:

1. `schema/core/v{version}/updated.context.jsonld` - IRI ↔ keyword mappings
2. `schema/core/v{version}/updated.vocab.jsonld` - Ontology relationships
3. `schema/core/v{version}/attributes.yaml` - Schema definitions

## Troubleshooting

### Error: Schema path does not exist

```
ValueError: Schema path does not exist: schema/core/v2.1
```

**Solution**: Ensure you're running from the repository root or the schema files exist for the target version.

### Error: Input file not found

```
Error: Input file not found: input.json
```

**Solution**: Check the input file path is correct and accessible.

### Warnings About Missing Properties

```
⚠ Property 'oldField' at path not found in v2.1 schema
```

**Meaning**: The property exists in source but not in target schema. This is normal for deprecated fields.

## Performance

- **Small payloads** (<100KB): ~100ms
- **Medium payloads** (100KB-1MB): ~500ms
- **Large payloads** (>1MB): ~2s

Performance depends on:
- Payload size and nesting depth
- Number of IRI resolutions needed
- Schema validation complexity

## Best Practices

1. **Always use verbose mode** during development: `-v`
2. **Check warnings** for deprecated or missing fields
3. **Keep metadata** in development, remove in production: `--no-metadata`
4. **Validate output** against target schema separately
5. **Test with sample data** before batch processing

## Support

For issues or questions:
- Check `IRI_TRANSFORMER_GUIDE.md` for algorithm details
- Review `IRI_RESOLUTION_ALGORITHM.md` for technical specs
- See examples in `tests/v2_v2_1_conversion/`

## License

MIT License - See LICENSE file in repository root.
