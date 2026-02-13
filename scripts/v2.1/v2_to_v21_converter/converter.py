"""
Main converter orchestrator for v2.0 → v2.1 payload transformation.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from copy import deepcopy

from .report import ConversionReport, WarningLevel
from .rules import (
    convert_envelope_keys,
    convert_entity,
    DROPPED_FIELDS
)


@dataclass
class ConversionResult:
    """Result of conversion with payload and report"""
    converted_payload: Dict[str, Any]
    report: ConversionReport
    original_payload: Dict[str, Any]


def convert_v2_to_v21(
    v2_payload: Dict[str, Any],
    strict: bool = False
) -> ConversionResult:
    """
    Convert a Beckn v2.0 payload to v2.1 format.
    
    Args:
        v2_payload: v2.0 formatted payload with context + message
        strict: If True, fail on any warnings (default: False)
    
    Returns:
        ConversionResult with converted payload and report
    
    Raises:
        ValueError: If strict=True and warnings are generated
    """
    report = ConversionReport()
    converted = deepcopy(v2_payload)
    
    # Step 1: Convert envelope context
    if "context" in converted:
        report.add_mapped_field("context")
        original_context = converted["context"]
        converted["context"] = convert_envelope_keys(original_context)
        report.increment_stat("envelope_context_converted")
        
        # Track specific envelope conversions
        for old_key in ["transaction_id", "message_id", "bap_id", "bpp_id"]:
            if old_key in original_context:
                report.increment_stat(f"envelope_key_{old_key}")
    
    # Step 2: Convert message entities
    if "message" in converted:
        report.add_mapped_field("message")
        message = converted["message"]
        
        # Detect and convert entities in message
        for key, value in list(message.items()):
            if isinstance(value, dict) and "@type" in value:
                entity_type = value.get("@type", "").replace("beckn:", "")
                
                # Check for dropped fields before conversion
                _check_dropped_fields(value, key, report)
                
                # Convert entity
                try:
                    converted_entity = convert_entity(value, entity_type)
                    message[key] = converted_entity
                    report.add_mapped_field(f"message.{key}")
                    report.increment_stat(f"entity_{entity_type}_converted")
                except Exception as e:
                    report.add_warning(
                        WarningLevel.ERROR,
                        f"message.{key}",
                        f"Failed to convert {entity_type}: {str(e)}"
                    )
            
            # Handle arrays of entities (e.g., catalogs)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict) and "@type" in item:
                        entity_type = item.get("@type", "").replace("beckn:", "")
                        
                        # Check for dropped fields
                        _check_dropped_fields(item, f"{key}[{idx}]", report)
                        
                        try:
                            converted_entity = convert_entity(item, entity_type)
                            value[idx] = converted_entity
                            report.add_mapped_field(f"message.{key}[{idx}]")
                            report.increment_stat(f"entity_{entity_type}_converted")
                        except Exception as e:
                            report.add_warning(
                                WarningLevel.ERROR,
                                f"message.{key}[{idx}]",
                                f"Failed to convert {entity_type}: {str(e)}"
                            )
    
    # Strict mode: fail if there are warnings
    if strict and report.warnings:
        error_count = len([w for w in report.warnings if w.level == WarningLevel.ERROR])
        warning_count = len([w for w in report.warnings if w.level == WarningLevel.WARNING])
        raise ValueError(
            f"Conversion failed in strict mode: {error_count} errors, {warning_count} warnings"
        )
    
    return ConversionResult(
        converted_payload=converted,
        report=report,
        original_payload=v2_payload
    )


def _check_dropped_fields(obj: Dict[str, Any], path: str, report: ConversionReport):
    """Recursively check for fields that will be dropped"""
    if not isinstance(obj, dict):
        return
    
    for key, value in obj.items():
        if key in DROPPED_FIELDS:
            field_path = f"{path}.{key}"
            reason = DROPPED_FIELDS[key]
            report.add_dropped_field(field_path, reason)
        
        # Recurse into nested objects
        if isinstance(value, dict):
            _check_dropped_fields(value, f"{path}.{key}", report)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    _check_dropped_fields(item, f"{path}.{key}[{idx}]", report)


def convert_batch(
    v2_payloads: list[Dict[str, Any]],
    continue_on_error: bool = True
) -> list[ConversionResult]:
    """
    Convert multiple v2.0 payloads to v2.1.
    
    Args:
        v2_payloads: List of v2.0 payloads
        continue_on_error: Continue processing on errors (default: True)
    
    Returns:
        List of ConversionResult objects
    """
    results = []
    
    for idx, payload in enumerate(v2_payloads):
        try:
            result = convert_v2_to_v21(payload, strict=False)
            results.append(result)
        except Exception as e:
            if not continue_on_error:
                raise
            
            # Create error result
            report = ConversionReport()
            report.add_warning(
                WarningLevel.ERROR,
                f"payload[{idx}]",
                f"Conversion failed: {str(e)}"
            )
            results.append(ConversionResult(
                converted_payload={},
                report=report,
                original_payload=payload
            ))
    
    return results
