"""Validation for human-approved source-to-canonical mappings."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence

from ..contracts.mapping import CANONICAL_FIELD_NAMES


class MappingValidationError(ValueError):
    """Raised when a mapping cannot safely be applied."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__(" ".join(self.errors))


def validate_mapping(
    selection: Mapping[str, str | None],
    source_columns: Sequence[str],
) -> dict[str, str | None]:
    """Validate required fields, known columns, and one-to-one source usage."""
    source_set = set(source_columns)
    canonical_set = set(CANONICAL_FIELD_NAMES)
    errors: list[str] = []
    unknown_fields = sorted(set(selection) - canonical_set)
    if unknown_fields:
        errors.append(f"Unknown canonical fields: {', '.join(unknown_fields)}.")

    normalized: dict[str, str | None] = {
        field_name: selection.get(field_name) or None
        for field_name in CANONICAL_FIELD_NAMES
    }
    for field_name, source_column in normalized.items():
        if source_column is not None and source_column not in source_set:
            errors.append(
                f"{field_name!r} points to missing source column {source_column!r}."
            )

    reverse_index: dict[str, list[str]] = defaultdict(list)
    for field_name, source_column in normalized.items():
        if source_column is not None:
            reverse_index[source_column].append(field_name)
    for source_column, fields in sorted(reverse_index.items()):
        if len(fields) > 1:
            errors.append(
                f"Source column {source_column!r} is mapped more than once: "
                f"{', '.join(fields)}."
            )

    for required_field in ("usage_date", "service", "cost"):
        if normalized[required_field] is None:
            errors.append(f"Required field {required_field!r} is not mapped.")

    if errors:
        raise MappingValidationError(errors)
    return normalized
