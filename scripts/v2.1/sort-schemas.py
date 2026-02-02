#!/usr/bin/env python3
"""
Script to reorganize schemas in attributes.yaml in alphabetical order.
This script sorts both the schemas and their properties alphabetically.

Usage:
    python3 sort-schemas.py [input_file] [output_file]
    
    If no arguments provided, defaults to:
    - input: schema/core/v2-rc2/attributes.yaml
    - output: schema/core/v2-rc2/attributes.sorted.yaml
"""

import sys
import yaml
from pathlib import Path
from collections import OrderedDict


def represent_ordereddict(dumper, data):
    """Custom representer for OrderedDict to maintain order in YAML output."""
    return dumper.represent_dict(data.items())


def represent_none(dumper, data):
    """Represent None as null in YAML."""
    return dumper.represent_scalar('tag:yaml.org,2002:null', 'null')


def setup_yaml():
    """Configure YAML to preserve formatting and use OrderedDict."""
    yaml.add_representer(OrderedDict, represent_ordereddict)
    yaml.add_representer(type(None), represent_none)


def sort_dict_keys(obj, exclude_keys=None):
    """
    Recursively sort dictionary keys alphabetically.
    
    Args:
        obj: The object to sort (dict, list, or other)
        exclude_keys: List of keys to exclude from sorting (keep their original order)
    
    Returns:
        Sorted object
    """
    if exclude_keys is None:
        exclude_keys = []
    
    if isinstance(obj, dict):
        sorted_dict = OrderedDict()
        
        # Separate keys to exclude from sorting
        excluded = OrderedDict()
        to_sort = {}
        
        for key, value in obj.items():
            if key in exclude_keys:
                excluded[key] = value
            else:
                to_sort[key] = value
        
        # Add excluded keys first (in original order)
        for key, value in excluded.items():
            sorted_dict[key] = sort_dict_keys(value, exclude_keys)
        
        # Add sorted keys
        for key in sorted(to_sort.keys()):
            sorted_dict[key] = sort_dict_keys(to_sort[key], exclude_keys)
        
        return sorted_dict
    
    elif isinstance(obj, list):
        return [sort_dict_keys(item, exclude_keys) for item in obj]
    
    else:
        return obj


def sort_schemas_in_yaml(input_file, output_file):
    """
    Read a YAML file, sort schemas and their properties alphabetically, and write to output.
    
    Args:
        input_file: Path to input YAML file
        output_file: Path to output YAML file
    """
    print(f"Reading from: {input_file}")
    
    # Read the YAML file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Keys that should maintain their original order at the top level
    top_level_order = ['openapi', 'info', 'components']
    
    # Sort the entire structure, but preserve some top-level ordering
    if 'components' in data and 'schemas' in data['components']:
        print(f"Found {len(data['components']['schemas'])} schemas to sort")
        
        # Sort schemas alphabetically
        sorted_schemas = OrderedDict(sorted(data['components']['schemas'].items()))
        
        # Sort properties within each schema
        for schema_name, schema_def in sorted_schemas.items():
            if isinstance(schema_def, dict):
                # Sort the schema definition keys
                sorted_schema = sort_dict_keys(schema_def)
                sorted_schemas[schema_name] = sorted_schema
        
        data['components']['schemas'] = sorted_schemas
    
    # Reorganize top-level keys
    sorted_data = OrderedDict()
    
    # First add keys in preferred order
    for key in top_level_order:
        if key in data:
            sorted_data[key] = data[key]
    
    # Then add any remaining keys alphabetically
    remaining_keys = sorted([k for k in data.keys() if k not in top_level_order])
    for key in remaining_keys:
        sorted_data[key] = data[key]
    
    print(f"Writing sorted schemas to: {output_file}")
    
    # Write the sorted YAML to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(sorted_data, f, 
                  default_flow_style=False, 
                  sort_keys=False,  # We've already sorted manually
                  allow_unicode=True,
                  width=120,
                  indent=2)
    
    print("✓ Schemas sorted successfully!")
    print(f"  - Input:  {input_file}")
    print(f"  - Output: {output_file}")


def main():
    """Main function to handle command-line arguments and execute sorting."""
    setup_yaml()
    
    # Get script directory for relative path resolution
    script_dir = Path(__file__).parent.parent.parent  # Go up to repo root
    
    # Default paths
    default_input = script_dir / "schema/core/v2-rc2/attributes.yaml"
    default_output = script_dir / "schema/core/v2-rc2/attributes.sorted.yaml"
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = default_input
    
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        output_file = default_output
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Sort and save
    try:
        sort_schemas_in_yaml(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
