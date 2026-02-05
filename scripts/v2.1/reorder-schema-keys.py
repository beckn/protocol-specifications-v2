#!/usr/bin/env python3
"""
Reorder OpenAPI schema keys according to Beckn specification standard order:
1. description
2. type
3. properties (if type = object)
4. items (if type = array)
5. enum (if any)
6. required
7. x-jsonld
"""

import yaml
import sys

# Custom representer to handle dict ordering without OrderedDict
def represent_dict_order(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(dict, represent_dict_order)

# Define the standard order for schema keys
KEY_ORDER = [
    'description',
    'type',
    'properties',
    'items',
    'enum',
    'required',
    'x-jsonld'
]

# Other keys that should come after the standard ones
SECONDARY_KEYS = [
    'additionalProperties',
    'allOf',
    'anyOf',
    'oneOf',
    'if',
    'then',
    'not',
    'minProperties',
    'maxProperties',
    'minItems',
    'maxItems',
    'minimum',
    'maximum',
    'format',
    'pattern',
    'default',
    'example',
    'examples',
    'const',
    'nullable'
]

def reorder_schema_keys(schema):
    """Reorder keys in a schema object according to the standard order."""
    if not isinstance(schema, dict):
        return schema
    
    ordered = {}
    
    # First, add keys in the standard order
    for key in KEY_ORDER:
        if key in schema:
            ordered[key] = schema[key]
    
    # Then add secondary standard keys
    for key in SECONDARY_KEYS:
        if key in schema:
            ordered[key] = schema[key]
    
    # Finally, add any remaining keys
    for key in schema:
        if key not in ordered:
            ordered[key] = schema[key]
    
    # Recursively process nested schemas
    if 'properties' in ordered and isinstance(ordered['properties'], dict):
        for prop_key, prop_value in ordered['properties'].items():
            ordered['properties'][prop_key] = reorder_schema_keys(prop_value)
    
    if 'items' in ordered:
        if isinstance(ordered['items'], dict):
            ordered['items'] = reorder_schema_keys(ordered['items'])
        elif isinstance(ordered['items'], list):
            ordered['items'] = [reorder_schema_keys(item) if isinstance(item, dict) else item for item in ordered['items']]
    
    if 'allOf' in ordered and isinstance(ordered['allOf'], list):
        ordered['allOf'] = [reorder_schema_keys(item) if isinstance(item, dict) else item for item in ordered['allOf']]
    
    if 'anyOf' in ordered and isinstance(ordered['anyOf'], list):
        ordered['anyOf'] = [reorder_schema_keys(item) if isinstance(item, dict) else item for item in ordered['anyOf']]
    
    if 'oneOf' in ordered and isinstance(ordered['oneOf'], list):
        ordered['oneOf'] = [reorder_schema_keys(item) if isinstance(item, dict) else item for item in ordered['oneOf']]
    
    return ordered

def process_yaml_file(input_file, output_file):
    """Process the YAML file and reorder schema keys."""
    
    # Load YAML
    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Process all schemas
    if 'components' in data and 'schemas' in data['components']:
        for schema_name, schema_def in data['components']['schemas'].items():
            data['components']['schemas'][schema_name] = reorder_schema_keys(schema_def)
    
    # Write back to file with proper formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, 
                  default_flow_style=False, 
                  allow_unicode=True,
                  sort_keys=False,
                  width=120,
                  indent=2)
    
    print(f"Successfully reordered schema keys in {output_file}")

if __name__ == '__main__':
    input_file = 'schema/core/v2.1/attributes.yaml'
    output_file = 'schema/core/v2.1/attributes.yaml'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    process_yaml_file(input_file, output_file)
