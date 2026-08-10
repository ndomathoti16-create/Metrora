"""Validation rules that keep optional AI output grounded in the fact pack."""

from __future__ import annotations

import re
from collections.abc import Iterable

from ..contracts.ai import FactPack


class AIResponseValidationError(ValueError):
    """Raised when an external summary references unsupported evidence."""


def validate_fact_references(
    fact_pack: FactPack,
    *,
    used_fact_ids: Iterable[str],
    recommendation_ids: Iterable[str],
) -> None:
    """Ensure returned references belong to the exact supplied fact pack."""
    fact_ids = {fact.fact_id for fact in fact_pack.facts}
    recommendation_id_set = {
        recommendation.recommendation_id for recommendation in fact_pack.recommendations
    }
    unknown_facts = sorted(set(used_fact_ids) - fact_ids)
    unknown_recommendations = sorted(set(recommendation_ids) - recommendation_id_set)
    if unknown_facts or unknown_recommendations:
        raise AIResponseValidationError(
            "AI response referenced unsupported evidence: "
            f"facts={unknown_facts}, recommendations={unknown_recommendations}."
        )


def validate_numeric_claims(text: str, fact_pack: FactPack) -> None:
    """Reject numeric claims that are not represented in calculated facts.

    This is intentionally conservative. A provider can use words freely, but a
    numeric statement must match a value in the fact pack or the application falls
    back to its deterministic summary.
    """
    allowed: set[float] = set()
    allowed_percentages: set[float] = set()
    for fact in fact_pack.facts:
        if isinstance(fact.value, (int, float)) and not isinstance(fact.value, bool):
            allowed.add(float(fact.value))
            if fact.unit == "share":
                allowed_percentages.add(float(fact.value) * 100)
    number_pattern = re.compile(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?%?")
    for token in number_pattern.findall(text):
        normalized = token.replace(",", "").removesuffix("%")
        try:
            value = float(normalized)
        except ValueError:
            continue
        candidates = allowed_percentages if token.endswith("%") else allowed
        grounded = any(
            abs(value - candidate) <= max(0.01, abs(candidate) * 1e-6) for candidate in candidates
        )
        if not grounded:
            raise AIResponseValidationError(
                f"AI response contains unsupported numeric claim {token!r}."
            )
