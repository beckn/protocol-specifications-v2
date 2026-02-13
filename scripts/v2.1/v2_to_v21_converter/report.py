"""
Conversion report generator for tracking warnings, dropped fields, and statistics.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class WarningLevel(Enum):
    """Warning severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ConversionWarning:
    """Individual conversion warning"""
    level: WarningLevel
    path: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.level.value.upper()}] {self.path}: {self.message}"


@dataclass
class ConversionReport:
    """Report of conversion process with warnings and statistics"""
    warnings: List[ConversionWarning] = field(default_factory=list)
    dropped_fields: List[str] = field(default_factory=list)
    mapped_fields: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def add_warning(self, level: WarningLevel, path: str, message: str, **details):
        """Add a warning to the report"""
        self.warnings.append(ConversionWarning(level, path, message, details))

    def add_dropped_field(self, field_path: str, reason: str = ""):
        """Record a field that was dropped during conversion"""
        self.dropped_fields.append(field_path)
        self.add_warning(
            WarningLevel.WARNING,
            field_path,
            f"Field dropped: {reason or 'No v2.1 equivalent'}"
        )

    def add_mapped_field(self, field_path: str):
        """Record a successfully mapped field"""
        self.mapped_fields.append(field_path)

    def increment_stat(self, stat_name: str):
        """Increment a statistic counter"""
        self.stats[stat_name] = self.stats.get(stat_name, 0) + 1

    def summary(self) -> str:
        """Generate human-readable summary"""
        lines = [
            "=" * 60,
            "Beckn v2.0 → v2.1 Conversion Report",
            "=" * 60,
            "",
            "Statistics:",
            f"  • Mapped fields: {len(self.mapped_fields)}",
            f"  • Dropped fields: {len(self.dropped_fields)}",
            f"  • Warnings: {len([w for w in self.warnings if w.level == WarningLevel.WARNING])}",
            f"  • Errors: {len([w for w in self.warnings if w.level == WarningLevel.ERROR])}",
            ""
        ]

        if self.stats:
            lines.append("Conversions:")
            for key, value in sorted(self.stats.items()):
                lines.append(f"  • {key}: {value}")
            lines.append("")

        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  {warning}")
            lines.append("")

        if self.dropped_fields:
            lines.append("Dropped Fields:")
            for field in self.dropped_fields:
                lines.append(f"  • {field}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Export report as dictionary"""
        return {
            "warnings": [
                {
                    "level": w.level.value,
                    "path": w.path,
                    "message": w.message,
                    "details": w.details
                }
                for w in self.warnings
            ],
            "dropped_fields": self.dropped_fields,
            "mapped_fields": self.mapped_fields,
            "stats": self.stats
        }
