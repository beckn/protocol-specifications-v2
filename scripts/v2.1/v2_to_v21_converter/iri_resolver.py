#!/usr/bin/env python3
"""
IRI Resolution Engine for Beckn v2.0 to v2.1 Transformation

This module implements a complete ontological IRI resolution algorithm that:
1. Always transforms input IRIs through the complete ontology chain
2. Follows equivalence, subclass, and deprecation relationships  
3. Resolves to canonical v2.1 IRIs and their corresponding keywords
4. Transforms JSON structure based on resolved schemas

Author: Beckn Protocol Team
Version: 1.0.0
"""

import json
import yaml
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class ResolutionSource(Enum):
    """Source of an IRI resolution step"""
    V2_INPUT = "v2.0_input"
    CONTEXT_MAPPING = "context_mapping"
    EQUIVALENT_CLASS = "owl:equivalentClass"
    EQUIVALENT_PROPERTY = "owl:equivalentProperty"
    SUBCLASS_OF = "rdfs:subClassOf"
    SUBPROPERTY_OF = "rdfs:subPropertyOf"
    CANONICAL = "canonical"


@dataclass
class ResolutionStep:
    """Single step in the IRI resolution chain"""
    step_number: int
    iri: str
    source: ResolutionSource
    deprecated: bool = False
    notes: str = ""


@dataclass
class ResolvedIRI:
    """Complete resolution result for an IRI"""
    canonical_iri: str
    v21_keyword: Optional[str]
    resolution_chain: List[ResolutionStep] = field(default_factory=list)
    is_deprecated: bool = False
    warnings: List[str] = field(default_factory=list)
    target_schema: Optional[Dict[str, Any]] = None


class IRIResolver:
    """
    Core IRI resolution engine implementing the canonical resolution algorithm.
    
    Key principle: ALWAYS transform and follow the ontology chain until reaching
    the canonical v2.1 IRI location.
    """
    
    def __init__(self, schema_base_path: str = None):
        """
        Initialize the IRI resolver with schema files.
        
        Args:
            schema_base_path: Base path to schema directory. If None, uses relative path.
        """
        if schema_base_path is None:
            # Default to schema/core/v2.1 relative to this script
            script_dir = Path(__file__).parent
            schema_base_path = script_dir.parent.parent.parent / "schema" / "core" / "v2.1"
        
        self.schema_path = Path(schema_base_path)
        
        # Load schema files
        self.v2_context = self._load_v2_context()
        self.v21_context = self._load_json(self.schema_path / "updated.context.jsonld")
        self.v21_vocab = self._load_json(self.schema_path / "updated.vocab.jsonld")
        self.v21_attributes = self._load_yaml(self.schema_path / "attributes.yaml")
        
        # Build lookup indexes for fast access
        self._build_indexes()
    
    def _load_v2_context(self) -> Dict[str, Any]:
        """Load v2.0 context for backward compatibility"""
        v2_path = self.schema_path.parent / "v2" / "context.jsonld"
        return self._load_json(v2_path)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load and parse a JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_indexes(self):
        """Build fast lookup indexes for contexts and vocab"""
        # Index v2.1 context: keyword -> IRI
        self.keyword_to_iri = {}
        self.iri_to_keyword = {}
        
        context = self.v21_context.get("@context", {})
        for keyword, value in context.items():
            if keyword in ["@version", "@protected"]:
                continue
            
            # Handle simple mappings
            if isinstance(value, str):
                self.keyword_to_iri[keyword] = value
                self.iri_to_keyword[value] = keyword
            # Handle object mappings with @id
            elif isinstance(value, dict) and "@id" in value:
                iri = value["@id"]
                self.keyword_to_iri[keyword] = iri
                self.iri_to_keyword[iri] = keyword
        
        # Index vocab: IRI -> vocab entry
        self.vocab_index = {}
        if "@graph" in self.v21_vocab:
            for entry in self.v21_vocab["@graph"]:
                if "@id" in entry:
                    self.vocab_index[entry["@id"]] = entry
    
    def expand_iri(self, compact_iri: str, context: Dict[str, Any]) -> str:
        """
        Expand a compact IRI to full form using context.
        
        Args:
            compact_iri: Compact IRI like "beckn:buyer" or "buyer"
            context: Context dictionary
            
        Returns:
            Full IRI
        """
        # Already expanded
        if compact_iri.startswith("http://") or compact_iri.startswith("https://"):
            return compact_iri
        
        # Check if it has a prefix
        if ":" in compact_iri:
            prefix, local = compact_iri.split(":", 1)
            ctx = context.get("@context", context)
            
            # Get namespace for prefix
            if prefix in ctx:
                ns = ctx[prefix]
                if isinstance(ns, str):
                    return ns + local
        
        # No prefix - look up directly in context
        ctx = context.get("@context", context)
        if compact_iri in ctx:
            value = ctx[compact_iri]
            if isinstance(value, str):
                return value
            elif isinstance(value, dict) and "@id" in value:
                return value["@id"]
        
        # Return as-is if can't expand
        return compact_iri
    
    def resolve_iri(self, input_iri: str, json_path: str = "") -> ResolvedIRI:
        """
        Resolve an IRI through the complete ontology chain to its canonical v2.1 form.
        
        This is the core implementation of the resolution algorithm that:
        1. Normalizes the input IRI
        2. Checks v2.1 context mappings
        3. Recursively resolves through vocabulary relationships
        4. Finds the v2.1 keyword
        5. Looks up the target schema
        
        Args:
            input_iri: Input IRI from v2.0 JSON (e.g., "beckn:buyer", "displayName")
            json_path: JSON path for debugging (e.g., "$.message.order.buyer")
            
        Returns:
            ResolvedIRI object with complete resolution information
        """
        result = ResolvedIRI(
            canonical_iri="",
            v21_keyword=None,
            resolution_chain=[],
            warnings=[]
        )
        
        # Step 1: Normalize input IRI
        full_iri = self.expand_iri(input_iri, self.v2_context)
        result.resolution_chain.append(ResolutionStep(
            step_number=0,
            iri=full_iri,
            source=ResolutionSource.V2_INPUT,
            notes=f"Input from v2.0 at {json_path}"
        ))
        
        current_iri = full_iri
        
        # Step 2: Check v2.1 context mapping
        v21_mapped = self.keyword_to_iri.get(input_iri.split(":")[-1])
        if v21_mapped:
            result.resolution_chain.append(ResolutionStep(
                step_number=len(result.resolution_chain),
                iri=v21_mapped,
                source=ResolutionSource.CONTEXT_MAPPING,
                notes=f"Mapped via v2.1 context: {input_iri} → {v21_mapped}"
            ))
            current_iri = v21_mapped
        
        # Step 3: Resolve recursively through vocabulary
        visited = set()  # Prevent infinite loops
        max_iterations = 20
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # Prevent loops
            if current_iri in visited:
                result.warnings.append(f"Circular reference detected at {current_iri}")
                break
            visited.add(current_iri)
            
            # Look up in vocabulary
            vocab_entry = self.vocab_index.get(current_iri)
            if not vocab_entry:
                # No vocab entry - current IRI is canonical
                break
            
            # Check for deprecation
            if vocab_entry.get("owl:deprecated") is True:
                result.is_deprecated = True
                result.resolution_chain[-1].deprecated = True
                result.warnings.append(f"{current_iri} is deprecated")
            
            # Follow owl:equivalentClass
            if "owl:equivalentClass" in vocab_entry:
                eq_class = vocab_entry["owl:equivalentClass"]
                next_iri = eq_class.get("@id") if isinstance(eq_class, dict) else eq_class
                
                result.resolution_chain.append(ResolutionStep(
                    step_number=len(result.resolution_chain),
                    iri=next_iri,
                    source=ResolutionSource.EQUIVALENT_CLASS,
                    notes=f"Following equivalentClass: {current_iri} → {next_iri}"
                ))
                current_iri = next_iri
                continue
            
            # Follow owl:equivalentProperty
            if "owl:equivalentProperty" in vocab_entry:
                eq_prop = vocab_entry["owl:equivalentProperty"]
                next_iri = eq_prop.get("@id") if isinstance(eq_prop, dict) else eq_prop
                
                result.resolution_chain.append(ResolutionStep(
                    step_number=len(result.resolution_chain),
                    iri=next_iri,
                    source=ResolutionSource.EQUIVALENT_PROPERTY,
                    notes=f"Following equivalentProperty: {current_iri} → {next_iri}"
                ))
                current_iri = next_iri
                continue
            
            # Follow rdfs:subClassOf (prefer beckn: namespace)
            if "rdfs:subClassOf" in vocab_entry:
                subclass_of = vocab_entry["rdfs:subClassOf"]
                
                # Handle array of parent classes
                if isinstance(subclass_of, list):
                    # Prefer beckn: namespace over schema: or others
                    beckn_classes = [
                        sc.get("@id") if isinstance(sc, dict) else sc
                        for sc in subclass_of
                        if (sc.get("@id") if isinstance(sc, dict) else sc).startswith("beckn:")
                    ]
                    next_iri = beckn_classes[0] if beckn_classes else (
                        subclass_of[0].get("@id") if isinstance(subclass_of[0], dict) else subclass_of[0]
                    )
                else:
                    next_iri = subclass_of.get("@id") if isinstance(subclass_of, dict) else subclass_of
                
                result.resolution_chain.append(ResolutionStep(
                    step_number=len(result.resolution_chain),
                    iri=next_iri,
                    source=ResolutionSource.SUBCLASS_OF,
                    notes=f"Following subClassOf: {current_iri} → {next_iri}"
                ))
                current_iri = next_iri
                continue
            
            # Follow rdfs:subPropertyOf
            if "rdfs:subPropertyOf" in vocab_entry:
                subprop_of = vocab_entry["rdfs:subPropertyOf"]
                next_iri = subprop_of.get("@id") if isinstance(subprop_of, dict) else subprop_of
                
                result.resolution_chain.append(ResolutionStep(
                    step_number=len(result.resolution_chain),
                    iri=next_iri,
                    source=ResolutionSource.SUBPROPERTY_OF,
                    notes=f"Following subPropertyOf: {current_iri} → {next_iri}"
                ))
                current_iri = next_iri
                continue
            
            # No further mappings found
            break
        
        # Mark as canonical
        result.canonical_iri = current_iri
        if result.resolution_chain:
            result.resolution_chain.append(ResolutionStep(
                step_number=len(result.resolution_chain),
                iri=current_iri,
                source=ResolutionSource.CANONICAL,
                notes="Canonical v2.1 IRI"
            ))
        
        # Step 4: Find v2.1 keyword
        result.v21_keyword = self.iri_to_keyword.get(current_iri)
        
        # Step 5: Lookup schema (will implement in separate method)
        result.target_schema = self._find_schema(result.v21_keyword or current_iri)
        
        return result
    
    def _find_schema(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Find schema definition in attributes.yaml
        
        Args:
            identifier: Keyword or IRI to search for
            
        Returns:
            Schema definition dictionary or None
        """
        # Look in components/schemas
        schemas = self.v21_attributes.get("components", {}).get("schemas", {})
        
        # Try direct lookup by keyword (e.g., "Consumer")
        keyword_capitalized = identifier.split(":")[-1]
        if keyword_capitalized in schemas:
            return schemas[keyword_capitalized]
        
        # Try common variations
        variations = [
            keyword_capitalized,
            keyword_capitalized.lower(),
            keyword_capitalized[0].upper() + keyword_capitalized[1:],
        ]
        
        for variant in variations:
            if variant in schemas:
                return schemas[variant]
        
        return None
    
    def print_resolution(self, resolved: ResolvedIRI, verbose: bool = True):
        """
        Pretty print a resolution result
        
        Args:
            resolved: ResolvedIRI object
            verbose: Whether to print detailed chain
        """
        print(f"\n{'='*80}")
        print(f"IRI Resolution Result")
        print(f"{'='*80}")
        print(f"Canonical IRI: {resolved.canonical_iri}")
        print(f"v2.1 Keyword:  {resolved.v21_keyword or 'N/A'}")
        print(f"Deprecated:    {resolved.is_deprecated}")
        
        if resolved.warnings:
            print(f"\nWarnings:")
            for warning in resolved.warnings:
                print(f"  ⚠ {warning}")
        
        if verbose and resolved.resolution_chain:
            print(f"\nResolution Chain ({len(resolved.resolution_chain)} steps):")
            for step in resolved.resolution_chain:
                deprecated_marker = " [DEPRECATED]" if step.deprecated else ""
                print(f"  [{step.step_number}] {step.iri}{deprecated_marker}")
                print(f"      via: {step.source.value}")
                if step.notes:
                    print(f"      note: {step.notes}")
        
        if resolved.target_schema:
            print(f"\nTarget Schema Found: {list(resolved.target_schema.keys())[:5]}...")
        
        print(f"{'='*80}\n")


def main():
    """Test the IRI resolver with example inputs"""
    print("Beckn IRI Resolver - Test Suite")
    print("="*80)
    
    resolver = IRIResolver()
    
    # Test cases from the v2.0 example
    test_cases = [
        ("beckn:buyer", "$.message.order.buyer"),
        ("beckn:displayName", "$.message.order.buyer.displayName"),
        ("beckn:seller", "$.message.order.seller"),
        ("beckn:orderedItem", "$.message.order.orderItems[0].orderedItem"),
        ("beckn:payment", "$.message.order.payment"),
        ("beckn:fulfillment", "$.message.order.fulfillment"),
        ("beckn:deliveryAttributes", "$.message.order.fulfillment.deliveryAttributes"),
    ]
    
    for iri, path in test_cases:
        resolved = resolver.resolve_iri(iri, path)
        resolver.print_resolution(resolved, verbose=True)


if __name__ == "__main__":
    main()
