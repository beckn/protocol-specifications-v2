# Scripts for v2-rc2

This directory contains utility scripts for managing the Beckn Protocol v2-rc2 specifications.

## sort-schemas.py

A Python script to reorganize schemas in `attributes.yaml` files in alphabetical order, including all properties within each schema.

### Features

- **Alphabetically sorts schemas**: All schemas in the `components/schemas` section are sorted alphabetically by name
- **Sorts properties within schemas**: All properties within each schema definition are also sorted alphabetically
- **Preserves structure**: Maintains the OpenAPI 3.1.1 structure and metadata
- **Recursive sorting**: Sorts nested objects throughout the entire schema structure
- **Configurable input/output**: Supports custom input and output file paths

### Prerequisites

- Python 3.6 or higher
- PyYAML library

Install PyYAML if not already installed:
```bash
pip install pyyaml
```

### Usage

#### Default usage (processes schema/core/v2-rc2/attributes.yaml)

```bash
python3 scripts/v2-rc2/sort-schemas.py
```

This will:
- Read from: `schema/core/v2-rc2/attributes.yaml`
- Write to: `schema/core/v2-rc2/attributes.sorted.yaml`

#### Custom input file

```bash
python3 scripts/v2-rc2/sort-schemas.py path/to/input.yaml
```

Outputs to: `schema/core/v2-rc2/attributes.sorted.yaml` (default)

#### Custom input and output files

```bash
python3 scripts/v2-rc2/sort-schemas.py path/to/input.yaml path/to/output.yaml
```

### Example

```bash
# Sort the default attributes.yaml file
cd /home/ravi/www/protocol-specifications-v2
python3 scripts/v2-rc2/sort-schemas.py

# Sort a specific file with custom output
python3 scripts/v2-rc2/sort-schemas.py \
  schema/PaymentSettlement/v2-rc2/attributes.yaml \
  schema/PaymentSettlement/v2-rc2/attributes.sorted.yaml
```

### Output

The script will display progress information:

```
Reading from: /home/ravi/www/protocol-specifications-v2/schema/core/v2-rc2/attributes.yaml
Found 31 schemas to sort
Writing sorted schemas to: /home/ravi/www/protocol-specifications-v2/schema/core/v2-rc2/attributes.sorted.yaml
✓ Schemas sorted successfully!
  - Input:  /home/ravi/www/protocol-specifications-v2/schema/core/v2-rc2/attributes.yaml
  - Output: /home/ravi/www/protocol-specifications-v2/schema/core/v2-rc2/attributes.sorted.yaml
```

### What Gets Sorted

1. **Schema names**: All schemas under `components/schemas` are sorted alphabetically
2. **Schema properties**: All keys within each schema definition (type, required, properties, etc.)
3. **Nested objects**: All nested objects are recursively sorted
4. **Property keys**: All property keys within the `properties` section of each schema

### What Is Preserved

- OpenAPI metadata (openapi, info, etc.)
- Required fields and validation rules
- JSON-LD context and type information
- Examples and descriptions
- All schema relationships and $ref references

### Example Before and After

**Before** (schemas in declaration order):
```yaml
components:
  schemas:
    Catalog:
      # ...
    Item:
      # ...
    Offer:
      # ...
    Attributes:
      # ...
```

**After** (schemas in alphabetical order):
```yaml
components:
  schemas:
    AcceptedPaymentMethod:
      # ...
    AckResponse:
      # ...
    Address:
      # ...
    Attributes:
      # ...
    Buyer:
      # ...
    Catalog:
      # ...
```

## network-scaffold/

Contains scripts for network provisioning and scaffolding. See [network-scaffold/README.md](network-scaffold/README.md) for details.

---

## Contributing

When adding new scripts to this directory:

1. Add appropriate documentation in this README
2. Include usage examples
3. Add error handling and validation
4. Make scripts executable: `chmod +x script-name.sh` or `chmod +x script-name.py`
5. Include a shebang line at the top of the file
