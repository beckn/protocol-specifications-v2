#!/usr/bin/env python3
"""
Pure IRI-Based Transformer for Beckn v2.0 → v2.1 Conversion

This module implements a pure IRI transformation algorithm that:
1. Reads @context and @type from each JSON object at runtime
2. Uses updated.context.jsonld and updated.vocab.jsonld for IRI mappings
3. Uses attributes.yaml for schema validation and structure
4. Does NOT use hardcoded field mappings

The algorithm ensures ALL transformations happen through ontological resolution.

Author: Beckn Protocol Team
Version: 2.0.0
License: MIT
"""

import json
import yaml
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


class IRITransformer:
    """
    Pure IRI-based transformer that converts v2 → v2.1 using only:
    - Runtime @context and @type reading
    - IRI resolution through vocab.jsonld
    - Schema lookup in attributes.yaml
    """
    
    def __init__(self, schema_base_path: str = None):
        """Initialize with schema files"""
        if schema_base_path is None:
            script_dir = Path(__file__).parent
            schema_base_path = script_dir.parent.parent.parent / "schema" / "core" / "v2.1"
        
        self.schema_path = Path(schema_base_path)
        
        # Load ontology files
        self.v21_context = self._load_json(self.schema_path / "updated.context.jsonld")
        self.v21_vocab = self._load_json(self.schema_path / "updated.vocab.jsonld")
        self.v21_attributes = self._load_yaml(self.schema_path / "attributes.yaml")
        
        # Build indexes
        self._build_indexes()
    
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
        context = self.v21_context.get("@context", {})
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
        if "@graph" in self.v21_vocab:
            for entry in self.v21_vocab["@graph"]:
                if "@id" in entry:
                    self.vocab_index[entry["@id"]] = entry
        
        # Build schema index
        schemas = self.v21_attributes.get("components", {}).get("schemas", {})
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
            ctx = self.v21_context.get("@context", {})
            if prefix in ctx:
                ns = ctx[prefix]
                if isinstance(ns, str):
                    return ns + local_part
        
        # Lookup in global context
        ctx = self.v21_context.get("@context", {})
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
        Resolve IRI to its canonical v2.1 form through ontology chain.
        
        Args:
            iri: Input IRI (expanded form)
            ctx: Transformation context for tracking
            
        Returns:
            Tuple of (canonical_iri, v21_keyword)
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
        3. Reconstructs object with v2.1 keywords
        4. Validates against v2.1 schema
        
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
        
        # Preserve @context with v2.1 value
        if "@context" in obj:
            # Always use v2.1 context URL for transformed objects
            v21_context_url = "https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/context.jsonld"
            transformed["@context"] = v21_context_url
        
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
            canonical_key_iri, v21_keyword = self.resolve_to_canonical(key_iri, resolution_ctx)
            
            # Use v2.1 keyword if found, otherwise keep original key
            new_key = v21_keyword if v21_keyword else key
            
            # Update context path
            old_path = ctx.current_path
            ctx.current_path = f"{old_path}.{key}" if old_path else key
            
            # Check if this key should exist in v2.1 schema
            if schema and "properties" in schema:
                schema_props = schema["properties"]
                
                # Check if property exists in schema
                if new_key not in schema_props and key not in schema_props:
                    # Property not in schema - might be dropped or extended
                    ctx.warnings.append(
                        f"Property '{key}' at {ctx.current_path} not found in v2.1 schema for {obj_type}"
                    )
            
            # Recursively transform value
            transformed[new_key] = self.transform_object(value, ctx)
            
            # Restore path
            ctx.current_path = old_path
            
            # Track stats
            if new_key != key:
                ctx.stats[f"transformed_{key}_to_{new_key}"] = ctx.stats.get(f"transformed_{key}_to_{new_key}", 0) + 1
        
        return transformed
    
    def transform_payload(self, v2_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a complete v2.0 payload to v2.1.
        
        This is the main entry point that:
        1. Creates transformation context
        2. Recursively transforms the payload
        3. Returns transformed payload with stats
        
        Args:
            v2_payload: Complete v2.0 payload
            
        Returns:
            Transformed v2.1 payload
        """
        ctx = TransformationContext()
        transformed = self.transform_object(v2_payload, ctx)
        
        # Attach transformation metadata
        if ctx.warnings:
            transformed["_transformation_warnings"] = ctx.warnings
        if ctx.stats:
            transformed["_transformation_stats"] = ctx.stats
        
        return transformed
    
    def transform_and_validate(
        self,
        v2_payload: Dict[str, Any],
        validate: bool = True
    ) -> Tuple[Dict[str, Any], List[str], Dict[str, int]]:
        """
        Transform payload and optionally validate against v2.1 schema.
        
        Args:
            v2_payload: v2.0 payload
            validate: Whether to validate against schema
            
        Returns:
            Tuple of (transformed_payload, warnings, stats)
        """
        ctx = TransformationContext()
        transformed = self.transform_object(deepcopy(v2_payload), ctx)
        
        # Optional: Validate against JSON Schema
        if validate:
            # TODO: Implement JSON Schema validation
            pass
        
        return transformed, ctx.warnings, ctx.stats


def main():
    """Test the transformer with example"""
    print("=" * 80)
    print("Beckn IRI-Based Transformer - Test")
    print("=" * 80)
    
    transformer = IRITransformer()
    
    # Example v2.0 payload
    v2_example = {
        "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/context.jsonld",
        "context": {
            "version": "2.0.0",
            "action": "on_confirm",
            "transaction_id": "txn-123",
            "message_id": "msg-456"
        },
        "message": {
            "order": {
                "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/context.jsonld",
                "@type": "beckn:Order",
                "beckn:id": "order-001",
                "beckn:orderStatus": "CONFIRMED",
                "beckn:buyer": {
                    "@type": "beckn:Buyer",
                    "beckn:id": "buyer-123",
                    "beckn:displayName": "John Doe",
                    "beckn:email": "john@example.com"
                },
                "beckn:seller": {
                    "@type": "beckn:Provider",
                    "beckn:id": "provider-456",
                    "beckn:descriptor": {
                        "@type": "beckn:Descriptor",
                        "schema:name": "ACME Corp"
                    }
                },
                "beckn:orderItems": [
                    {
                        "@type": "beckn:OrderItem",
                        "beckn:lineId": "line-1",
                        "beckn:orderedItem": "item-001",
                        "beckn:quantity": {
                            "unitQuantity": 2,
                            "unitText": "units"
                        }
                    }
                ],
                "beckn:payment": {
                    "@type": "beckn:Payment",
                    "beckn:id": "pay-789",
                    "beckn:paymentStatus": "COMPLETED",
                    "beckn:amount": {
                        "currency": "USD",
                        "value": 99.99
                    }
                }
            }
        }
    }
    
    # Transform
    print("\nTransforming v2.0 payload...\n")
    transformed, warnings, stats = transformer.transform_and_validate(v2_example)
    
    # Output results
    print("=" * 80)
    print("TRANSFORMED PAYLOAD (v2.1)")
    print("=" * 80)
    print(json.dumps(transformed, indent=2))
    
    if warnings:
        print("\n" + "=" * 80)
        print("WARNINGS")
        print("=" * 80)
        for warning in warnings:
            print(f"⚠ {warning}")
    
    if stats:
        print("\n" + "=" * 80)
        print("TRANSFORMATION STATISTICS")
        print("=" * 80)
        for key, count in sorted(stats.items()):
            print(f"{key}: {count}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
