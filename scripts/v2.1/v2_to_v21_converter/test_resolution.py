#!/usr/bin/env python3
"""
Test the IRI resolver on the actual v2.0 on_confirm EV charging example
"""

import json
import sys
from pathlib import Path
from iri_resolver import IRIResolver

def extract_fields_from_json(data, path="$", prefix="beckn:"):
    """
    Recursively extract all field names from JSON that start with prefix
    
    Returns list of (field_name, json_path, value) tuples
    """
    fields = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Skip @ fields
            if key.startswith("@"):
                continue
            
            current_path = f"{path}.{key}"
            
            # Check if this field uses beckn: prefix
            if key.startswith(prefix):
                fields.append((key, current_path, value))
            else:
                # Also check non-prefixed fields that might be v2.0 keywords
                fields.append((key, current_path, value))
            
            # Recurse
            if isinstance(value, (dict, list)):
                fields.extend(extract_fields_from_json(value, current_path, prefix))
    
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            current_path = f"{path}[{idx}]"
            if isinstance(item, (dict, list)):
                fields.extend(extract_fields_from_json(item, current_path, prefix))
    
    return fields


def main():
    print("="*80)
    print("IRI Resolution Test on v2.0 EV Charging on_confirm")
    print("="*80)
    
    # Load v2.0 example
    v2_file = Path(__file__).parent.parent.parent.parent.parent / "DEG" / "examples" / "ev-charging" / "v2" / "08_00_on_confirm" / "v2_0_ev-charging-on-confirm.json"
    
    if not v2_file.exists():
        print(f"Error: File not found: {v2_file}")
        sys.exit(1)
    
    with open(v2_file, 'r') as f:
        v2_data = json.load(f)
    
    print(f"\nLoaded v2.0 file: {v2_file.name}")
    
    # Initialize resolver
    resolver = IRIResolver()
    
    # Extract all beckn: prefixed fields
    fields = extract_fields_from_json(v2_data, "$", "beckn:")
    
    # Get unique field names from order section only
    order_fields = [
        (f, p, v) for f, p, v in fields 
        if ".message.order." in p
    ]
    
    # Get unique field names
    unique_fields = {}
    for field_name, path, value in order_fields:
        clean_name = field_name.replace("beckn:", "")
        if clean_name not in unique_fields:
            unique_fields[clean_name] = path
    
    print(f"\nFound {len(unique_fields)} unique field names in order object")
    print("\n" + "="*80)
    print("Resolution Results")
    print("="*80)
    
    # Resolve each unique field
    results = {}
    for field_name in sorted(unique_fields.keys()):
        path = unique_fields[field_name]
        input_iri = f"beckn:{field_name}"
        
        resolved = resolver.resolve_iri(input_iri, path)
        results[field_name] = resolved
    
    # Print summary table
    print("\n{:<25} {:<25} {:<15} {:<15}".format(
        "v2.0 Field", "v2.1 Keyword", "Deprecated", "Chain Length"
    ))
    print("-"*80)
    
    for field_name in sorted(results.keys()):
        resolved = results[field_name]
        deprecated = "⚠ YES" if resolved.is_deprecated else "No"
        chain_len = len(resolved.resolution_chain)
        v21_kw = resolved.v21_keyword or "N/A"
        
        print("{:<25} {:<25} {:<15} {:<15}".format(
            field_name, v21_kw, deprecated, chain_len
        ))
    
    # Print detailed resolution chains for deprecated fields
    deprecated_fields = [
        (fn, res) for fn, res in results.items() if res.is_deprecated
    ]
    
    if deprecated_fields:
        print("\n" + "="*80)
        print(f"Deprecated Fields Detail ({len(deprecated_fields)} found)")
        print("="*80)
        
        for field_name, resolved in deprecated_fields:
            print(f"\n⚠ {field_name}")
            for step in resolved.resolution_chain:
                marker = " [DEPRECATED]" if step.deprecated else ""
                print(f"  [{step.step_number}] {step.iri}{marker}")
                print(f"      via: {step.source.value}")
    
    # Print key transformations
    print("\n" + "="*80)
    print("Key Transformations")
    print("="*80)
    
    transformations = [
        ("buyer", "consumer"),
        ("seller", "provider"),
        ("displayName", "name"),
        ("orderedItem", "itemId"),
        ("deliveryAttributes", "fulfillmentAttributes"),
        ("paymentAttributes", "paymentTermsAttributes"),
    ]
    
    for v2_field, expected_v21 in transformations:
        if v2_field in results:
            resolved = results[v2_field]
            actual_v21 = resolved.v21_keyword
            match = "✓" if actual_v21 == expected_v21 else "✗"
            print(f"{match} {v2_field:<25} → {actual_v21:<25} (expected: {expected_v21})")
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80)


if __name__ == "__main__":
    main()
