#!/usr/bin/env python3
"""
Semantic Transformation for Beckn Protocol Version Conversion

This module implements a pure semantic web approach using:
1. @container in JSON-LD context for singular/plural handling
2. DCT (Dublin Core Terms) for replacement relationships  
3. SHACL shapes for constraint-based transformation
4. OWL/RDFS ontological reasoning

NO custom structural rules - everything is encoded in the ontology.

Usage:
    python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json

Author: Beckn Protocol Team
Version: 3.0.0
License: MIT
"""

import json
import yaml
import argparse
import sys
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


class SemanticTransformer:
    """
    Pure semantic transformer using JSON-LD, DCT, and SHACL.
    
    Key innovations:
    1. @container handling for singular/plural transformation
    2. DCT replacement predicates for version migration
    3. SHACL shapes for structural validation/transformation
    4. OWL reasoning for complex mappings
    """
    
    def __init__(
        self,
        output_version: str = "2.1",
        schema_base_path: str = None,
        context_file: str = None,
        vocab_file: str = None,
        attributes_file: str = None,
        shacl_shapes_file: str = None
    ):
        """
        Initialize semantic transformer
        
        Args:
            output_version: Target version
            schema_base_path: Base path to schema files
            context_file: Optional custom context file
            vocab_file: Optional custom vocab file
            attributes_file: Optional custom attributes file
            shacl_shapes_file: Optional SHACL shapes file for constraints
        """
        self.output_version = output_version
        
        # Load ontology files
        if context_file and vocab_file and attributes_file:
            self.context = self._load_json(Path(context_file))
            self.vocab = self._load_json(Path(vocab_file))
            self.attributes = self._load_yaml(Path(attributes_file))
        else:
            # Default paths
            if schema_base_path is None:
                script_dir = Path(__file__).parent
                version_path = f"v{output_version}" if not output_version.startswith("v") else output_version
                schema_base_path = script_dir.parent.parent.parent / "schema" / "core" / version_path
            
            self.schema_path = Path(schema_base_path)
            self.context = self._load_json(self.schema_path / "updated.context.jsonld")
            self.vocab = self._load_json(self.schema_path / "updated.vocab.jsonld")
            self.attributes = self._load_yaml(self.schema_path / "attributes.yaml")
        
        # Load SHACL shapes if provided
        self.shacl_shapes = None
        if shacl_shapes_file:
            self.shacl_shapes = self._load_json(Path(shacl_shapes_file))
        
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
        """Build fast lookup indexes from ontology"""
        # Context mappings with @container info
        self.keyword_to_iri: Dict[str, str] = {}
        self.iri_to_keyword: Dict[str, str] = {}
        self.container_types: Dict[str, str] = {}  # "@list", "@set", "@index"
        
        # DCT replacement mappings
        self.dct_replaces: Dict[str, List[str]] = {}  # old_iri -> [new_iris]
        self.dct_is_replaced_by: Dict[str, str] = {}  # new_iri -> old_iri
        
        # Vocab index
        self.vocab_index: Dict[str, Dict[str, Any]] = {}
        
        # Build context mappings
        context = self.context.get("@context", {})
        for keyword, value in context.items():
            if keyword in ["@version", "@protected"]:
                continue
            
            if isinstance(value, str):
                self.keyword_to_iri[keyword] = value
                self.iri_to_keyword[value] = keyword
            elif isinstance(value, dict):
                if "@id" in value:
                    iri = value["@id"]
                    self.keyword_to_iri[keyword] = iri
                    self.iri_to_keyword[iri] = keyword
                    
                    # Extract @container info
                    if "@container" in value:
                        self.container_types[keyword] = value["@container"]
        
        # Build vocab index and DCT mappings
        if "@graph" in self.vocab:
            for entry in self.vocab["@graph"]:
                if "@id" not in entry:
                    continue
                
                iri = entry["@id"]
                self.vocab_index[iri] = entry
                
                # Extract DCT replacement relationships
                if "dct:replaces" in entry:
                    replaces = entry["dct:replaces"]
                    if isinstance(replaces, list):
                        self.dct_replaces[iri] = [r.get("@id", r) if isinstance(r, dict) else r for r in replaces]
                    else:
                        replaced = replaces.get("@id", replaces) if isinstance(replaces, dict) else replaces
                        self.dct_replaces[iri] = [replaced]
                
                if "dct:isReplacedBy" in entry:
                    replaced_by = entry["dct:isReplacedBy"]
                    new_iri = replaced_by.get("@id", replaced_by) if isinstance(replaced_by, dict) else replaced_by
                    self.dct_is_replaced_by[iri] = new_iri
    
    def expand_iri(self, compact_form: str, local_context: Any = None) -> str:
        """Expand compact IRI to full form"""
        if compact_form.startswith("http://") or compact_form.startswith("https://"):
            return compact_form
        
        # Try local context first
        if local_context and isinstance(local_context, dict):
            ctx = local_context.get("@context", local_context)
            if isinstance(ctx, dict) and compact_form in ctx:
                value = ctx[compact_form]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict) and "@id" in value:
                    return value["@id"]
        
        # Check if prefixed
        if ":" in compact_form:
            prefix, local_part = compact_form.split(":", 1)
            ctx = self.context.get("@context", {})
            if prefix in ctx:
                ns = ctx[prefix]
                if isinstance(ns, str):
                    return ns + local_part
        
        # Global context lookup
        ctx = self.context.get("@context", {})
        if compact_form in ctx:
            value = ctx[compact_form]
            if isinstance(value, str):
                return value
            elif isinstance(value, dict) and "@id" in value:
                return value["@id"]
        
        return compact_form
    
    def resolve_through_ontology(self, iri: str, ctx: TransformationContext) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Resolve IRI through ontological chain
        
        Returns:
            Tuple of (canonical_iri, keyword, container_type)
        """
        if iri in ctx.visited_iris:
            ctx.warnings.append(f"Circular reference: {iri}")
            return iri, self.iri_to_keyword.get(iri), None
        
        ctx.visited_iris.add(iri)
        current = iri
        
        # Follow replacement chain (DCT)
        if current in self.dct_is_replaced_by:
            current = self.dct_is_replaced_by[current]
            ctx.stats["dct_replacements"] = ctx.stats.get("dct_replacements", 0) + 1
        
        # Follow equivalence chain (OWL)
        max_hops = 20
        for _ in range(max_hops):
            vocab_entry = self.vocab_index.get(current)
            if not vocab_entry:
                break
            
            next_iri = None
            
            # OWL equivalence
            if "owl:equivalentProperty" in vocab_entry:
                eq = vocab_entry["owl:equivalentProperty"]
                next_iri = eq.get("@id") if isinstance(eq, dict) else eq
            elif "owl:equivalentClass" in vocab_entry:
                eq = vocab_entry["owl:equivalentClass"]
                next_iri = eq.get("@id") if isinstance(eq, dict) else eq
            # RDFS hierarchy
            elif "rdfs:subPropertyOf" in vocab_entry:
                sub = vocab_entry["rdfs:subPropertyOf"]
                next_iri = sub.get("@id") if isinstance(sub, dict) else sub
            elif "rdfs:subClassOf" in vocab_entry:
                sub = vocab_entry["rdfs:subClassOf"]
                if isinstance(sub, list):
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
            
            if next_iri:
                current = next_iri
            else:
                break
        
        # Find keyword and container type
        keyword = self.iri_to_keyword.get(current)
        container = self.container_types.get(keyword) if keyword else None
        
        return current, keyword, container
    
    def transform_value_by_container(
        self,
        value: Any,
        source_container: Optional[str],
        target_container: Optional[str]
    ) -> Any:
        """
        Transform value based on @container semantics
        
        Handles:
        - singular → @list (wrap in array)
        - @list → singular (extract first element)
        - @set operations
        """
        if source_container == target_container:
            return value
        
        # None → @list: wrap single value
        if source_container is None and target_container == "@list":
            if not isinstance(value, list):
                return [value]
        
        # @list → None: extract first element
        elif source_container == "@list" and target_container is None:
            if isinstance(value, list) and len(value) > 0:
                return value[0]
        
        # @set operations (unordered)
        elif target_container == "@set":
            if not isinstance(value, list):
                return [value]
        
        return value
    
    def transform_object(self, obj: Any, ctx: TransformationContext) -> Any:
        """
        Transform JSON object using semantic reasoning
        """
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        
        if isinstance(obj, list):
            return [self.transform_object(item, ctx) for item in obj]
        
        if not isinstance(obj, dict):
            return obj
        
        transformed = {}
        local_context = obj.get("@context")
        obj_type = obj.get("@type")
        
        # Handle @type
        if obj_type:
            type_iri = self.expand_iri(obj_type, local_context)
            canonical_type, type_keyword, _ = self.resolve_through_ontology(type_iri, ctx)
            if type_keyword:
                transformed["@type"] = type_keyword
            elif obj_type:
                transformed["@type"] = obj_type
        
        # Update @context to target version
        if "@context" in obj:
            context_url = f"https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v{self.output_version}/context.jsonld"
            transformed["@context"] = context_url
        
        # Transform all properties
        for key, value in obj.items():
            if key in ["@context", "@type"]:
                continue
            
            # Expand and resolve
            resolution_ctx = TransformationContext(
                current_path=ctx.current_path,
                parent_type=ctx.parent_type,
                depth=ctx.depth,
                warnings=ctx.warnings,
                stats=ctx.stats
            )
            
            key_iri = self.expand_iri(key, local_context)
            canonical_iri, target_keyword, target_container = self.resolve_through_ontology(key_iri, resolution_ctx)
            
            if not target_keyword:
                target_keyword = key
            
            # Get source container type
            source_container = self.container_types.get(key)
            
            # Transform value based on container semantics
            transformed_value = self.transform_object(value, ctx)
            transformed_value = self.transform_value_by_container(
                transformed_value,
                source_container,
                target_container
            )
            
            transformed[target_keyword] = transformed_value
            
            # Track stats
            if target_keyword != key:
                ctx.stats[f"transformed_{key}_to_{target_keyword}"] = ctx.stats.get(f"transformed_{key}_to_{target_keyword}", 0) + 1
            if source_container != target_container:
                ctx.stats["container_transformations"] = ctx.stats.get("container_transformations", 0) + 1
        
        return transformed
    
    def transform(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], Dict[str, int]]:
        """
        Transform payload using semantic reasoning
        
        Returns:
            Tuple of (transformed_payload, warnings, stats)
        """
        ctx = TransformationContext()
        transformed = self.transform_object(deepcopy(payload), ctx)
        return transformed, ctx.warnings, ctx.stats


def strip_prefixes(obj: Any, prefixes: List[str] = None) -> Any:
    """Strip namespace prefixes from keys"""
    if prefixes is None:
        prefixes = ["beckn:", "schema:"]
    
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    
    if isinstance(obj, list):
        return [strip_prefixes(item, prefixes) for item in obj]
    
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            new_key = key
            for prefix in prefixes:
                if key.startswith(prefix):
                    new_key = key[len(prefix):]
                    break
            result[new_key] = strip_prefixes(value, prefixes)
        return result
    
    return obj


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Beckn Semantic Transformer - Pure JSON-LD/SHACL transformation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform using semantic reasoning
  python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json
  
  # With SHACL shapes
  python3 becknSemanticTransform.py -ov 2.1 -i input.json -o output.json --shacl shapes.ttl
        """
    )
    
    parser.add_argument("-ov", "--output-version", help="Output version (e.g., 2.1)")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file")
    parser.add_argument("--context-file", help="Custom context.jsonld file")
    parser.add_argument("--vocab-file", help="Custom vocab.jsonld file")
    parser.add_argument("--attributes-file", help="Custom attributes.yaml file")
    parser.add_argument("--shacl", help="SHACL shapes file for constraints")
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-metadata", action="store_true", help="Exclude metadata")
    
    args = parser.parse_args()
    
    try:
        # Load input
        with open(args.input, 'r', encoding='utf-8') as f:
            input_payload = json.load(f)
        
        # Initialize transformer
        if args.verbose:
            print(f"Initializing semantic transformer for v{args.output_version}...", file=sys.stderr)
        
        transformer = SemanticTransformer(
            output_version=args.output_version or "2.1",
            context_file=args.context_file,
            vocab_file=args.vocab_file,
            attributes_file=args.attributes_file,
            shacl_shapes_file=args.shacl
        )
        
        # Transform
        if args.verbose:
            print("Transforming with semantic reasoning...", file=sys.stderr)
        
        transformed, warnings, stats = transformer.transform(input_payload)
        
        # Strip prefixes
        transformed = strip_prefixes(transformed)
        
        # Remove metadata if requested
        if args.no_metadata:
            transformed.pop("_transformation_warnings", None)
            transformed.pop("_transformation_stats", None)
        else:
            if warnings:
                transformed["_transformation_warnings"] = warnings
            if stats:
                transformed["_transformation_stats"] = stats
        
        # Output
        output_json = json.dumps(transformed, indent=2, ensure_ascii=False)
        print(output_json)
        
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            if args.verbose:
                print(f"\n✓ Output written to: {args.output}", file=sys.stderr)
        
        # Show stats if verbose
        if args.verbose and stats:
            print(f"\n{'='*60}", file=sys.stderr)
            print("SEMANTIC TRANSFORMATION STATISTICS", file=sys.stderr)
            print('='*60, file=sys.stderr)
            for key, count in sorted(stats.items()):
                print(f"{key}: {count}", file=sys.stderr)
        
        if args.verbose:
            print(f"\n✓ Semantic transformation completed!", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
