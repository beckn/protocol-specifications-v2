"""
Beckn v2.0 → v2.1 Payload Converter

Gateway/adapter tool for converting Beckn Protocol v2.0 API payloads to v2.1-compatible format.
Enables backward compatibility for legacy v2.0 clients communicating with v2.1 implementations.
"""

from .converter import convert_v2_to_v21, ConversionResult
from .report import ConversionReport

__version__ = "1.0.0"
__all__ = ["convert_v2_to_v21", "ConversionResult", "ConversionReport"]
