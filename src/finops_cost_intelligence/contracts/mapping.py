"""Canonical field definitions and mapping-review contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CanonicalFieldSpec:
    """Business meaning and source-name hints for one canonical field."""

    name: str
    label: str
    required: bool
    kind: str
    aliases: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"aliases": list(self.aliases)}


CANONICAL_FIELD_SPECS: tuple[CanonicalFieldSpec, ...] = (
    CanonicalFieldSpec(
        "usage_date",
        "Usage date",
        True,
        "date",
        (
            "usage date",
            "usage_date",
            "date",
            "usage start date",
            "billing date",
            "charge date",
            "invoice date",
            "start date",
            "period date",
            "charge period start",
            "billing period start",
            "usage start time",
        ),
    ),
    CanonicalFieldSpec(
        "service",
        "Service",
        True,
        "string",
        (
            "service",
            "service name",
            "service category",
            "service description",
            "product",
            "product name",
            "product family",
            "meter category",
        ),
    ),
    CanonicalFieldSpec(
        "cost",
        "Cost",
        True,
        "numeric",
        (
            "cost",
            "amount",
            "charge",
            "unblended cost",
            "blended cost",
            "amortized cost",
            "net cost",
            "total cost",
            "usage cost",
            "line item cost",
            "amount usd",
            "billed cost",
            "effective cost",
            "contracted cost",
            "list cost",
            "cost in billing currency",
            "pretax cost",
        ),
    ),
    CanonicalFieldSpec(
        "currency",
        "Currency",
        False,
        "currency",
        (
            "currency",
            "currency code",
            "bill currency",
            "billing currency",
            "pricing currency",
        ),
    ),
    CanonicalFieldSpec(
        "provider",
        "Cloud provider",
        False,
        "string",
        ("provider", "provider name", "cloud provider", "vendor", "publisher name"),
    ),
    CanonicalFieldSpec(
        "account_id",
        "Account ID",
        False,
        "string",
        (
            "account id",
            "account_id",
            "account",
            "account number",
            "subscription id",
            "subscription",
            "billing account id",
            "sub account id",
        ),
    ),
    CanonicalFieldSpec(
        "account_name",
        "Account name",
        False,
        "string",
        (
            "account name",
            "account alias",
            "subscription name",
            "billing account name",
            "sub account name",
        ),
    ),
    CanonicalFieldSpec(
        "region",
        "Region",
        False,
        "string",
        (
            "region",
            "region name",
            "aws region",
            "cloud region",
            "availability region",
            "location",
            "resource location",
        ),
    ),
    CanonicalFieldSpec(
        "department",
        "Department",
        False,
        "string",
        ("department", "dept", "cost center", "cost centre", "business unit", "team"),
    ),
    CanonicalFieldSpec(
        "project",
        "Project",
        False,
        "string",
        (
            "project",
            "project id",
            "project name",
            "resource group",
            "application",
            "app",
            "workload",
        ),
    ),
    CanonicalFieldSpec(
        "environment",
        "Environment",
        False,
        "string",
        ("environment", "env", "deployment environment", "stage"),
    ),
    CanonicalFieldSpec(
        "resource_id",
        "Resource ID",
        False,
        "string",
        ("resource id", "resource_id", "resource identifier", "instance id", "arn"),
    ),
    CanonicalFieldSpec(
        "resource_name",
        "Resource name",
        False,
        "string",
        ("resource name", "resource_name", "resource"),
    ),
    CanonicalFieldSpec(
        "usage_quantity",
        "Usage quantity",
        False,
        "numeric",
        (
            "usage quantity",
            "quantity",
            "consumed quantity",
            "usage amount",
            "usage",
            "units consumed",
        ),
    ),
    CanonicalFieldSpec(
        "usage_unit",
        "Usage unit",
        False,
        "string",
        (
            "usage unit",
            "unit",
            "unit type",
            "unit of measure",
            "pricing quantity unit",
        ),
    ),
    CanonicalFieldSpec(
        "usage_type",
        "Usage type",
        False,
        "string",
        (
            "usage type",
            "usage category",
            "line item type",
            "sku id",
            "sku price id",
        ),
    ),
    CanonicalFieldSpec(
        "cost_type",
        "Cost type",
        False,
        "string",
        (
            "cost type",
            "charge type",
            "charge category",
            "pricing category",
            "record type",
        ),
    ),
    CanonicalFieldSpec(
        "tags_json",
        "Tags or labels",
        False,
        "tags",
        ("tags", "tag", "tags json", "resource tags", "labels"),
    ),
)


CANONICAL_FIELD_NAMES: tuple[str, ...] = tuple(field.name for field in CANONICAL_FIELD_SPECS)


@dataclass(frozen=True)
class MappingCandidate:
    """One source-column candidate for a canonical field."""

    source_column: str
    score: float
    confidence: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"reasons": list(self.reasons)}


@dataclass(frozen=True)
class MappingSuggestion:
    """Reviewable recommendation for one canonical field."""

    canonical_field: str
    label: str
    required: bool
    source_column: str | None
    score: float
    confidence: str
    reason: str
    candidates: tuple[MappingCandidate, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_field": self.canonical_field,
            "label": self.label,
            "required": self.required,
            "source_column": self.source_column,
            "score": self.score,
            "confidence": self.confidence,
            "reason": self.reason,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


@dataclass(frozen=True)
class MappingReview:
    """All detector output needed by a human mapping-review step."""

    source_columns: tuple[str, ...]
    suggestions: tuple[MappingSuggestion, ...]

    def suggestion_for(self, canonical_field: str) -> MappingSuggestion:
        for suggestion in self.suggestions:
            if suggestion.canonical_field == canonical_field:
                return suggestion
        raise KeyError(f"Unknown canonical field: {canonical_field}")

    def suggested_mapping(self) -> dict[str, str | None]:
        return {
            suggestion.canonical_field: suggestion.source_column for suggestion in self.suggestions
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_columns": list(self.source_columns),
            "suggestions": [suggestion.to_dict() for suggestion in self.suggestions],
        }
