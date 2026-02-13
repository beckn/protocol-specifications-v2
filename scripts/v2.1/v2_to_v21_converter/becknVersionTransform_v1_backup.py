#!/usr/bin/env python3
"""
Pure IRI-Based Transformer for Beckn Protocol Version Conversion

This module implements a pure IRI transformation algorithm that:
1. Reads @context and @type from each JSON object at runtime
2. Uses updated.context.jsonld and updated.vocab.jsonld for IRI mappings
3. Uses attributes.yaml for schema validation and structure
4. Does NOT use hardcoded field mappings

The algorithm ensures ALL transformations happen through ontological resolution.

Usage:
    python3 becknVersionTransform.py -ov 2.1 -i input.json -o output.json

Author: Beckn Protocol Team
Version: 2.0.0
License: MIT
"""

import json
import yaml
import argparse
import sys
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class TransformationContext:
    """Context for tracking transformation state"""
    current_path: str = ""
    parent_type: Optional[str] = None
    depth: int = 0
    visited_iris: Set[str] = field(default_factory=set)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)


class StructuralTransformer:
    """
    Handles complex structural transformations that cannot be expressed
    through pure IRI/ontology mappings.
    """
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize with structural transformation rules
        
        Args:
            rules_file: Path to YAML file containing structural transformation rules
        """
        self.rules = []
        self.settings = {}
        
        if rules_file:
            self.load_rules(rules_file)
    
    def load_rules(self, rules_file: str):
        """Load transformation rules from YAML file"""
        rules_path = Path(rules_file)
        if not rules_path.exists():
            raise ValueError(f"Rules file not found: {rules_file}")
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self.rules = data.get("rules", [])
        self.settings = data.get("settings", {})
    
    def get_value_at_path(self, obj: Any, jsonpath: str) -> Tuple[Any, bool]:
        """
        Get value at JSONPath expression
        
        Args:
            obj: JSON object
            jsonpath: JSONPath expression (e.g., "$.message.order.buyer")
        
        Returns:
            Tuple of (value, found)
        """
        # Simple JSONPath implementation for basic paths
        # Remove leading $. if present
        path = jsonpath.lstrip('$').lstrip('.')
        
        if not path:
            return obj, True
        
        parts = path.split('.')
        current = obj
        
        for part in parts:
            # Handle array access like "fulfillments[*]" or "fulfillments[0]"
            if '[' in part and ']' in part:
                key = part[:part.index('[')]
                index_part = part[part.index('[')+1:part.index(']')]
                
                if not isinstance(current, dict) or key not in current:
                    return None, False
                
                current = current[key]
                
                if index_part == '*':
                    # Return the whole array for wildcard
                    return current, True
                else:
                    # Specific index
                    try:
                        idx = int(index_part)
                        if not isinstance(current, list) or idx >= len(current):
                            return None, False
                        current = current[idx]
                    except (ValueError, TypeError):
                        return None, False
            else:
                # Regular key access
                if not isinstance(current, dict) or part not in current:
                    return None, False
                current = current[part]
        
        return current, True
    
    def set_value_at_path(self, obj: Dict, jsonpath: str, value: Any, create_intermediates: bool = True):
        """
        Set value at JSONPath expression, creating intermediate objects if needed
        
        Args:
            obj: JSON object
            jsonpath: JSONPath expression
            value: Value to set
            create_intermediates: Whether to create missing intermediate objects
        """
        # Remove leading $. if present
        path = jsonpath.lstrip('$').lstrip('.')
        
        if not path:
            return
        
        parts = path.split('.')
        current = obj
        
        # Navigate to parent of target
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                if create_intermediates:
                    current[part] = {}
                else:
                    return
            current = current[part]
            
            if not isinstance(current, dict):
                return
        
        # Set final value
        final_key = parts[-1]
        current[final_key] = value
    
    def delete_value_at_path(self, obj: Dict, jsonpath: str):
        """Delete value at JSONPath expression"""
        # Remove leading $. if present
        path = jsonpath.lstrip('$').lstrip('.')
        
        if not path:
            return
        
        parts = path.split('.')
        current = obj
        
        # Navigate to parent
        for part in parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                return
            current = current[part]
        
        # Delete final key
        final_key = parts[-1]
        if isinstance(current, dict) and final_key in current:
            del current[final_key]
    
    def apply_nested_path_transform(self, obj: Dict, rule: Dict) -> bool:
        """
        Apply nested path transformation (e.g., buyer → consumer.person.name)
        
        Args:
            obj: JSON object to transform
            rule: Transformation rule
        
        Returns:
            True if transformation was applied
        """
        source_path = rule.get("source_path")
        target_path = rule.get("target_path")
        
        if not source_path or not target_path:
            return False
        
        # Get source value
        value, found = self.get_value_at_path(obj, source_path)
        
        if not found:
            return False
        
        # Set target value
        create_intermediates = self.settings.get("create_intermediate_objects", True)
        self.set_value_at_path(obj, target_path, value, create_intermediates)
        
        # Remove source if configured
        if self.settings.get("remove_source_after_transform", True):
            self.delete_value_at_path(obj, source_path)
        
        return True
    
    def apply_object_split_transform(self, obj: Dict, rule: Dict) -> bool:
        """
        Apply object split transformation (e.g., payment → paymentAction + paymentTerms)
        
        Args:
            obj: JSON object to transform
            rule: Transformation rule
        
        Returns:
            True if transformation was applied
        """
        source_path = rule.get("source_path")
        target_objects = rule.get("target_objects", {})
        
        if not source_path or not target_objects:
            return False
        
        # Get source object
        source_obj, found = self.get_value_at_path(obj, source_path)
        
        if not found or not isinstance(source_obj, dict):
            return False
        
        # Distribute properties to target objects
        for target_name, target_config in target_objects.items():
            target_path = target_config.get("target_path")
            properties = target_config.get("properties", [])
            
            if not target_path:
                continue
            
            # Build target object from selected properties
            target_obj = {}
            for prop in properties:
                if prop in source_obj:
                    target_obj[prop] = source_obj[prop]
            
            # Set target object if it has any properties
            if target_obj:
                create_intermediates = self.settings.get("create_intermediate_objects", True)
                self.set_value_at_path(obj, target_path, target_obj, create_intermediates)
        
        # Remove source if configured
        if self.settings.get("remove_source_after_transform", True):
            self.delete_value_at_path(obj, source_path)
        
        return True
    
    def apply_property_relocation_transform(self, obj: Dict, rule: Dict) -> bool:
        """
        Apply property relocation (e.g., payment.collectedBy → paymentTerms.collectedBy)
        
        Args:
            obj: JSON object to transform
            rule: Transformation rule
        
        Returns:
            True if transformation was applied
        """
        # This is essentially the same as nested_path for single properties
        return self.apply_nested_path_transform(obj, rule)
    
    def apply_rules(self, obj: Dict) -> Tuple[Dict, List[str]]:
        """
        Apply all transformation rules to the object
        
        Args:
            obj: JSON object to transform
        
        Returns:
            Tuple of (transformed_object, applied_rules)
        """
        transformed = deepcopy(obj)
        applied_rules = []
        
        # Get execution order from settings
        execution_order = self.settings.get("execution_order", [])
        
        # Build rule index by name
        rules_by_name = {rule.get("name"): rule for rule in self.rules if rule.get("enabled", True)}
        
        # Apply rules in order
        for rule_name in execution_order:
            if rule_name not in rules_by_name:
                continue
            
            rule = rules_by_name[rule_name]
            transform_type = rule.get("transform_type")
            
            try:
                success = False
                
                if transform_type == "nested_path":
                    success = self.apply_nested_path_transform(transformed, rule)
                elif transform_type == "object_split":
                    success = self.apply_object_split_transform(transformed, rule)
                elif transform_type == "property_relocation":
                    success = self.apply_property_relocation_transform(transformed, rule)
                
                if success:
                    applied_rules.append(rule_name)
            
            except Exception as e:
                # Log error but continue with other rules
                print(f"Warning: Rule '{rule_name}' failed: {e}", file=sys.stderr)
        
        return transformed, applied_rules


class IRITransformer:
    """
    Pure IRI-based transformer that converts between Beckn protocol versions using only:
    - Runtime @context and @type reading
    - IRI resolution through vocab.jsonld
    - Schema lookup in attributes.yaml
    """
    
    def __init__(
        self,
        output_version: str = "2.1",
        schema_base_path: str = None,
        context_file: str = None,
        vocab_file: str = None,
        attributes_file: str = None,
        structural_rules_file: str = None
    ):
        """
        Initialize with schema files
        
        Args:
            output_version: Target version (e.g., "2.1")
            schema_base_path: Path to schema directory (used if individual files not specified)
            context_file: Path to context.jsonld file
            vocab_file: Path to vocab.jsonld file
            attributes_file: Path to attributes.yaml file
            structural_rules_file: Path to structural transformation rules YAML file
        """
        self.output_version = output_version
        self.structural_rules_file = structural_rules_file
        
        # If individual files are provided, use them
        if context_file and vocab_file and attributes_file:
            context_path = Path(context_file)
            vocab_path = Path(vocab_file)
            attributes_path = Path(attributes_file)
            
            if not context_path.exists():
                raise ValueError(f"Context file does not exist: {context_file}")
            if not vocab_path.exists():
                raise ValueError(f"Vocab file does not exist: {vocab_file}")
            if not attributes_path.exists():
                raise ValueError(f"Attributes file does not exist: {attributes_file}")
            
            # Load ontology files from specified paths
            self.context = self._load_json(context_path)
            self.vocab = self._load_json(vocab_path)
            self.attributes = self._load_yaml(attributes_path)
        else:
            # Fallback to schema_base_path or default version path
            if schema_base_path is None:
                script_dir = Path(__file__).parent
                # Map version to path
                version_path = f"v{output_version}" if not output_version.startswith("v") else output_version
                schema_base_path = script_dir.parent.parent.parent / "schema" / "core" / version_path
            
            self.schema_path = Path(schema_base_path)
            
            if not self.schema_path.exists():
                raise ValueError(f"Schema path does not exist: {self.schema_path}")
            
            # Load ontology files from directory
            self.context = self._load_json(self.schema_path / "updated.context.jsonld")
            self.vocab = self._load_json(self.schema_path / "updated.vocab.jsonld")
            self.attributes = self._load_yaml(self.schema_path / "attributes.yaml")
        
        # Build indexes
        self._build_indexes()
        
        # Initialize structural transformer if rules file provided
        self.structural_transformer = None
        if structural_rules_file:
            self.structural_transformer = StructuralTransformer(structural_rules_file)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_indexes(self):
        """Build fast lookup indexes"""
        # Index: keyword <-> IRI bidirectional mapping
        self.keyword_to_iri: Dict[str, str] = {}
        self.iri_to_keyword: Dict[str, str] = {}
        
        # Index: IRI -> vocab entry
        self.vocab_index: Dict[str, Dict[str, Any]] = {}
        
        # Index: schema name -> schema definition
        self.schema_index: Dict[str, Dict[str, Any]] = {}
        
        # Build context mappings
        context = self.context.get("@context", {})
        for keyword, value in context.items():
            if keyword in ["@version", "@protected"]:
                continue
            
            if isinstance(value, str):
                self.keyword_to_iri[keyword] = value
                self.iri_to_keyword[value] = keyword
            elif isinstance(value, dict) and "@id" in value:
                iri = value["@id"]
                self.keyword_to_iri[keyword] = iri
                self.iri_to_keyword[iri] = keyword
        
        # Build vocab index
        if "@graph" in self.vocab:
            for entry in self.vocab["@graph"]:
                if "@id" in entry:
                    self.vocab_index[entry["@id"]] = entry
        
        # Build schema index
        schemas = self.attributes.get("components", {}).get("schemas", {})
        for schema_name, schema_def in schemas.items():
            self.schema_index[schema_name] = schema_def
    
    def expand_iri(self, compact_form: str, local_context: Any = None) -> str:
        """
        Expand compact IRI to full form.
        
        Args:
            compact_form: Compact IRI like "beckn:buyer" or "buyer"
            local_context: Optional local @context from JSON object (can be string URL or dict)
            
        Returns:
            Expanded IRI
        """
        # Already expanded
        if compact_form.startswith("http://") or compact_form.startswith("https://"):
            return compact_form
        
        # Try local context first (only if it's a dict, not a URL string)
        if local_context and isinstance(local_context, dict):
            ctx = local_context.get("@context", local_context)
            if isinstance(ctx, dict) and compact_form in ctx:
                value = ctx[compact_form]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict) and "@id" in value:
                    return value["@id"]
        
        # Check if prefixed (e.g., "beckn:buyer")
        if ":" in compact_form:
            prefix, local_part = compact_form.split(":", 1)
            
            # Get namespace from global context
            ctx = self.context.get("@context", {})
            if prefix in ctx:
                ns = ctx[prefix]
                if isinstance(ns, str):
                    return ns + local_part
        
        # Lookup in global context
        ctx = self.context.get("@context", {})
        if compact_form in ctx:
            value = ctx[compact_form]
            if isinstance(value, str):
                return value
            elif isinstance(value, dict) and "@id" in value:
                return value["@id"]
        
        # Return as-is if can't expand
        return compact_form
    
    def resolve_to_canonical(self, iri: str, ctx: TransformationContext) -> Tuple[str, Optional[str]]:
        """
        Resolve IRI to its canonical form through ontology chain.
        
        Args:
            iri: Input IRI (expanded form)
            ctx: Transformation context for tracking
            
        Returns:
            Tuple of (canonical_iri, keyword)
        """
        if iri in ctx.visited_iris:
            ctx.warnings.append(f"Circular reference detected: {iri}")
            return iri, self.iri_to_keyword.get(iri)
        
        ctx.visited_iris.add(iri)
        current = iri
        max_hops = 20
        hops = 0
        
        while hops < max_hops:
            hops += 1
            
            # Check vocab for relationships
            vocab_entry = self.vocab_index.get(current)
            if not vocab_entry:
                break  # No more mappings
            
            # Check deprecation
            if vocab_entry.get("owl:deprecated") is True:
                ctx.warnings.append(f"Using deprecated IRI: {current}")
            
            # Follow equivalence (highest priority)
            next_iri = None
            
            if "owl:equivalentClass" in vocab_entry:
                eq = vocab_entry["owl:equivalentClass"]
                next_iri = eq.get("@id") if isinstance(eq, dict) else eq
                
            elif "owl:equivalentProperty" in vocab_entry:
                eq = vocab_entry["owl:equivalentProperty"]
                next_iri = eq.get("@id") if isinstance(eq, dict) else eq
                
            elif "rdfs:subClassOf" in vocab_entry:
                sub = vocab_entry["rdfs:subClassOf"]
                if isinstance(sub, list):
                    # Prefer beckn: namespace
                    beckn_classes = [
                        (s.get("@id") if isinstance(s, dict) else s)
                        for s in sub
                        if (s.get("@id") if isinstance(s, dict) else s).startswith("beckn:")
                    ]
                    next_iri = beckn_classes[0] if beckn_classes else (
                        sub[0].get("@id") if isinstance(sub[0], dict) else sub[0]
                    )
                else:
                    next_iri = sub.get("@id") if isinstance(sub, dict) else sub
                    
            elif "rdfs:subPropertyOf" in vocab_entry:
                sub = vocab_entry["rdfs:subPropertyOf"]
                next_iri = sub.get("@id") if isinstance(sub, dict) else sub
            
            if next_iri:
                current = next_iri
            else:
                break  # No more hops
        
        # Find keyword for canonical IRI
        keyword = self.iri_to_keyword.get(current)
        return current, keyword
    
    def get_schema_for_type(self, type_iri: str) -> Optional[Dict[str, Any]]:
        """
        Get schema definition for a type IRI.
        
        Args:
            type_iri: Type IRI (e.g., "beckn:Order", "beckn:Consumer")
            
        Returns:
            Schema definition or None
        """
        # Extract local name from IRI
        if ":" in type_iri:
            local_name = type_iri.split(":")[-1]
        elif "#" in type_iri:
            local_name = type_iri.split("#")[-1]
        elif "/" in type_iri:
            local_name = type_iri.split("/")[-1]
        else:
            local_name = type_iri
        
        # Try direct lookup
        if local_name in self.schema_index:
            return self.schema_index[local_name]
        
        # Try variations
        for variant in [local_name, local_name.capitalize(), local_name.lower()]:
            if variant in self.schema_index:
                return self.schema_index[variant]
        
        return None
    
    def transform_object(self, obj: Any, ctx: TransformationContext) -> Any:
        """
        Transform a JSON object recursively using IRI resolution.
        
        This is the core transformation method that:
        1. Reads @context and @type from object
        2. Resolves all keys through IRI chain
        3. Reconstructs object with target version keywords
        4. Validates against target schema
        
        Args:
            obj: JSON object to transform
            ctx: Transformation context
            
        Returns:
            Transformed object
        """
        # Base cases
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        
        # Handle arrays
        if isinstance(obj, list):
            return [self.transform_object(item, ctx) for item in obj]
        
        # Must be dict at this point
        if not isinstance(obj, dict):
            return obj
        
        # Create new transformed object
        transformed = {}
        
        # Extract local context and type
        local_context = obj.get("@context")
        obj_type = obj.get("@type")
        
        # Get schema if type is specified
        schema = None
        if obj_type:
            type_iri = self.expand_iri(obj_type, local_context)
            canonical_type, type_keyword = self.resolve_to_canonical(type_iri, ctx)
            schema = self.get_schema_for_type(canonical_type)
            
            if type_keyword:
                transformed["@type"] = type_keyword
            elif obj_type:
                transformed["@type"] = obj_type  # Keep original if can't resolve
        
        # Preserve @context with target version value
        if "@context" in obj:
            # Use target version context URL
            context_url = f"https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v{self.output_version}/context.jsonld"
            transformed["@context"] = context_url
        
        # Transform all other keys
        for key, value in obj.items():
            if key in ["@context", "@type"]:
                continue  # Already handled
            
            # Expand and resolve key IRI
            # Create a fresh visited set for each key resolution to avoid false circular reference warnings
            resolution_ctx = TransformationContext(
                current_path=ctx.current_path,
                parent_type=ctx.parent_type,
                depth=ctx.depth,
                warnings=ctx.warnings,
                stats=ctx.stats
            )
            key_iri = self.expand_iri(key, local_context)
            canonical_key_iri, target_keyword = self.resolve_to_canonical(key_iri, resolution_ctx)
            
            # Use target keyword if found, otherwise keep original key
            new_key = target_keyword if target_keyword else key
            
            # Update context path
            old_path = ctx.current_path
            ctx.current_path = f"{old_path}.{key}" if old_path else key
            
            # Check if this key should exist in target schema
            if schema and "properties" in schema:
                schema_props = schema["properties"]
                
                # Check if property exists in schema
                if new_key not in schema_props and key not in schema_props:
                    # Property not in schema - might be dropped or extended
                    ctx.warnings.append(
                        f"Property '{key}' at {ctx.current_path} not found in v{self.output_version} schema for {obj_type}"
                    )
            
            # Recursively transform value
            transformed[new_key] = self.transform_object(value, ctx)
            
            # Restore path
            ctx.current_path = old_path
            
            # Track stats
            if new_key != key:
                ctx.stats[f"transformed_{key}_to_{new_key}"] = ctx.stats.get(f"transformed_{key}_to_{new_key}", 0) + 1
        
        return transformed
    
    def transform_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a complete payload to target version.
        
        Args:
            payload: Input payload
            
        Returns:
            Transformed payload
        """
        ctx = TransformationContext()
        transformed = self.transform_object(payload, ctx)
        
        # Attach transformation metadata
        if ctx.warnings:
            transformed["_transformation_warnings"] = ctx.warnings
        if ctx.stats:
            transformed["_transformation_stats"] = ctx.stats
        
        return transformed
    
    def transform_and_validate(
        self,
        payload: Dict[str, Any],
        validate: bool = True
    ) -> Tuple[Dict[str, Any], List[str], Dict[str, int], List[str]]:
        """
        Transform payload and optionally validate against target schema.
        
        Args:
            payload: Input payload
            validate: Whether to validate against schema
            
        Returns:
            Tuple of (transformed_payload, warnings, stats, applied_structural_rules)
        """
        ctx = TransformationContext()
        
        # Step 1: IRI-based transformation
        transformed = self.transform_object(deepcopy(payload), ctx)
        
        # Step 2: Strip prefixes BEFORE structural transformation
        # (Structural rules expect keys without beckn:/schema: prefixes)
        transformed = strip_prefixes(transformed)
        
        # Step 3: Apply structural transformations if configured
        applied_structural_rules = []
        if self.structural_transformer:
            transformed, applied_structural_rules = self.structural_transformer.apply_rules(transformed)
            if applied_structural_rules:
                ctx.stats["structural_rules_applied"] = len(applied_structural_rules)
        
        # Optional: Validate against JSON Schema
        if validate:
            # TODO: Implement JSON Schema validation
            pass
        
        return transformed, ctx.warnings, ctx.stats, applied_structural_rules


def strip_prefixes(obj: Any, prefixes: List[str] = None) -> Any:
    """
    Recursively strip namespace prefixes from JSON keys.
    
    Args:
        obj: JSON object to process
        prefixes: List of prefixes to strip (default: ["beckn:", "schema:"])
        
    Returns:
        Object with prefixes stripped from keys
    """
    if prefixes is None:
        prefixes = ["beckn:", "schema:"]
    
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    
    if isinstance(obj, list):
        return [strip_prefixes(item, prefixes) for item in obj]
    
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Strip prefix from key
            new_key = key
            for prefix in prefixes:
                if key.startswith(prefix):
                    new_key = key[len(prefix):]
                    break
            
            # Recursively process value
            result[new_key] = strip_prefixes(value, prefixes)
        
        return result
    
    return obj


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Beckn Protocol Version Transformer - Pure IRI-based transformation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform v2.0 to v2.1
  python3 becknVersionTransform.py -ov 2.1 -i input.json -o output.json
  
  # With verbose output
  python3 becknVersionTransform.py -ov 2.1 -i input.json -o output.json -v
  
  # Output to stdout
  python3 becknVersionTransform.py -ov 2.1 -i input.json
        """
    )
    
    parser.add_argument(
        "-ov", "--output-version",
        help="Output version (e.g., 2.1) - required if not using custom files"
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to input JSON file"
    )
    
    parser.add_argument(
        "--context-file",
        help="Path to context.jsonld file (overrides version-based lookup)"
    )
    
    parser.add_argument(
        "--vocab-file",
        help="Path to vocab.jsonld file (overrides version-based lookup)"
    )
    
    parser.add_argument(
        "--attributes-file",
        help="Path to attributes.yaml file (overrides version-based lookup)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Path to output JSON file (if not specified, prints to stdout)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show warnings and statistics"
    )
    
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude transformation metadata from output"
    )
    
    parser.add_argument(
        "--add-beckn-prefix",
        action="store_true",
        help="Keep beckn: and schema: prefixes in output keys (default: strip them)"
    )
    
    parser.add_argument(
        "--structural-rules",
        help="Path to structural transformation rules YAML file"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate arguments
        using_custom_files = args.context_file or args.vocab_file or args.attributes_file
        
        if using_custom_files:
            # If any custom file is specified, all three must be provided
            if not (args.context_file and args.vocab_file and args.attributes_file):
                print("Error: If using custom files, all three must be provided:", file=sys.stderr)
                print("  --context-file, --vocab-file, --attributes-file", file=sys.stderr)
                sys.exit(1)
        else:
            # If not using custom files, output-version is required
            if not args.output_version:
                print("Error: Either --output-version or all custom files (--context-file, --vocab-file, --attributes-file) must be provided", file=sys.stderr)
                sys.exit(1)
        
        # Load input file
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            input_payload = json.load(f)
        
        # Initialize transformer
        if args.verbose:
            if using_custom_files:
                print(f"Initializing transformer with custom files...", file=sys.stderr)
                print(f"  Context: {args.context_file}", file=sys.stderr)
                print(f"  Vocab: {args.vocab_file}", file=sys.stderr)
                print(f"  Attributes: {args.attributes_file}", file=sys.stderr)
            else:
                print(f"Initializing transformer for version {args.output_version}...", file=sys.stderr)
        
        transformer = IRITransformer(
            output_version=args.output_version or "custom",
            context_file=args.context_file,
            vocab_file=args.vocab_file,
            attributes_file=args.attributes_file,
            structural_rules_file=args.structural_rules
        )
        
        # Transform
        if args.verbose:
            print(f"Transforming payload...", file=sys.stderr)
            if args.structural_rules:
                print(f"  Using structural rules: {args.structural_rules}", file=sys.stderr)
        
        transformed, warnings, stats, applied_rules = transformer.transform_and_validate(input_payload)
        
        # Add applied rules to stats if present
        if applied_rules:
            stats["applied_structural_rules"] = applied_rules
        
        # Remove metadata if requested
        if args.no_metadata:
            transformed.pop("_transformation_warnings", None)
            transformed.pop("_transformation_stats", None)
        
        # Note: Prefixes are already stripped during transform_and_validate
        # before structural rules are applied. The --add-beckn-prefix option
        # is not applicable when using structural rules.
        if args.add_beckn_prefix and not args.structural_rules:
            # Re-add prefixes if requested (only when NOT using structural rules)
            pass  # Transformed already has prefixes stripped
        
        # Output results
        # Always print to console
        output_json = json.dumps(transformed, indent=2, ensure_ascii=False)
        print(output_json)
        
        # Also write to file if specified
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_json)
            
            if args.verbose:
                print(f"\n✓ Transformed payload written to: {args.output}", file=sys.stderr)
        
        # Show warnings and stats if verbose
        if args.verbose and warnings:
            print(f"\n{'='*60}", file=sys.stderr)
            print("WARNINGS", file=sys.stderr)
            print('='*60, file=sys.stderr)
            for warning in warnings:
                print(f"⚠ {warning}", file=sys.stderr)
        
        if args.verbose and stats:
            print(f"\n{'='*60}", file=sys.stderr)
            print("TRANSFORMATION STATISTICS", file=sys.stderr)
            print('='*60, file=sys.stderr)
            for key, count in sorted(stats.items()):
                print(f"{key}: {count}", file=sys.stderr)
        
        if args.verbose:
            print(f"\n✓ Transformation completed successfully!", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
