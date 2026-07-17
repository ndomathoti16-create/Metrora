"""Explainable candidate detection for source-to-canonical mappings."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from ..contracts.mapping import (
    CANONICAL_FIELD_SPECS,
    CanonicalFieldSpec,
    MappingCandidate,
    MappingReview,
    MappingSuggestion,
)
from ..contracts.profile import ColumnProfile, DataProfile

MIN_SUGGESTION_SCORE = 0.55


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _tokens(value: str) -> set[str]:
    return set(_normalize_label(value).split())


def _confidence(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.65:
        return "medium"
    return "low"


def _type_bonus(spec: CanonicalFieldSpec, column: ColumnProfile) -> tuple[float, str | None]:
    if spec.kind == "date" and column.datetime_parse_rate >= 0.8:
        return 0.12, f"datetime parse rate {column.datetime_parse_rate:.0%}"
    if spec.kind == "numeric" and column.numeric_parse_rate >= 0.8:
        return 0.12, f"numeric parse rate {column.numeric_parse_rate:.0%}"
    if spec.kind in {"string", "currency", "tags"} and column.inferred_type in {
        "string",
        "datetime-like",
        "numeric-like",
    }:
        return 0.02, f"compatible source type {column.inferred_type}"
    return 0.0, None


def _score_candidate(spec: CanonicalFieldSpec, column: ColumnProfile) -> MappingCandidate:
    source_name = column.name
    source_normalized = _normalize_label(source_name)
    source_tokens = _tokens(source_name)
    alias_matches: list[str] = []
    name_score = 0.0

    for alias in (spec.name, *spec.aliases):
        alias_normalized = _normalize_label(alias)
        alias_tokens = _tokens(alias)
        if source_normalized == alias_normalized:
            name_score = max(name_score, 0.96 if alias != spec.name else 1.0)
            alias_matches.append(alias)
            continue
        if alias_tokens and alias_tokens.issubset(source_tokens):
            name_score = max(name_score, 0.86)
            alias_matches.append(alias)
            continue
        overlap = len(alias_tokens & source_tokens) / max(len(alias_tokens), 1)
        fuzzy_score = SequenceMatcher(None, source_normalized, alias_normalized).ratio()
        if overlap >= 0.5:
            name_score = max(name_score, 0.58 + 0.2 * overlap)
            alias_matches.append(alias)
        elif fuzzy_score >= 0.78:
            name_score = max(name_score, 0.55 + 0.2 * fuzzy_score)
            alias_matches.append(alias)

    type_bonus, type_reason = _type_bonus(spec, column)
    score = min(1.0, name_score + type_bonus)
    reasons: list[str] = []
    if alias_matches:
        reasons.append(f"name matched {alias_matches[0]!r}")
    if type_reason:
        reasons.append(type_reason)
    if not reasons:
        reasons.append("no strong semantic or type signal")
    return MappingCandidate(
        source_column=source_name,
        score=round(score, 4),
        confidence=_confidence(score),
        reasons=tuple(reasons),
    )


def suggest_mappings(profile: DataProfile) -> MappingReview:
    """Rank explainable source-column candidates for every canonical field."""
    profile_by_name = {column.name: column for column in profile.columns}
    source_columns = tuple(profile_by_name)
    raw_candidates: dict[str, tuple[MappingCandidate, ...]] = {}

    for spec in CANONICAL_FIELD_SPECS:
        ranked = sorted(
            (
                _score_candidate(spec, column)
                for column in profile_by_name.values()
            ),
            key=lambda candidate: (-candidate.score, candidate.source_column.casefold()),
        )
        raw_candidates[spec.name] = tuple(ranked[:3])

    used_columns: set[str] = set()
    suggestions: list[MappingSuggestion] = []
    for spec in CANONICAL_FIELD_SPECS:
        candidates = raw_candidates[spec.name]
        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate.score >= MIN_SUGGESTION_SCORE
                and candidate.source_column not in used_columns
            ),
            None,
        )
        if selected is not None:
            used_columns.add(selected.source_column)
            source_column = selected.source_column
            reason = "; ".join(selected.reasons)
            score = selected.score
            confidence = selected.confidence
        else:
            source_column = None
            score = 0.0
            confidence = "none"
            reason = "No sufficiently strong unique candidate; choose manually."

        suggestions.append(
            MappingSuggestion(
                canonical_field=spec.name,
                label=spec.label,
                required=spec.required,
                source_column=source_column,
                score=score,
                confidence=confidence,
                reason=reason,
                candidates=candidates,
            )
        )

    return MappingReview(source_columns=source_columns, suggestions=tuple(suggestions))
