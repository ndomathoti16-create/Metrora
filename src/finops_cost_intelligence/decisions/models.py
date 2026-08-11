"""Provider-neutral records for FinOps decisions and measured outcomes."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, date, datetime
from typing import Any

DECISION_STATUSES = (
    "Proposed",
    "Investigating",
    "Approved",
    "Implemented",
    "Verified",
    "Rejected",
)
OPEN_DECISION_STATUSES = frozenset({"Proposed", "Investigating", "Approved", "Implemented"})
EFFORT_LEVELS = ("Unknown", "Low", "Medium", "High")
RISK_LEVELS = ("Unknown", "Low", "Medium", "High")
CRITICALITY_LEVELS = ("Low", "Medium", "High")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _clean_required(value: str, label: str) -> str:
    cleaned = str(value).strip()
    if not cleaned:
        raise ValueError(f"{label} is required.")
    return cleaned


def _optional_amount(value: float | int | None, label: str) -> float | None:
    if value is None:
        return None
    amount = float(value)
    if not math.isfinite(amount):
        raise ValueError(f"{label} must be a finite number.")
    return amount


def _validate_date(value: str | None, label: str) -> str | None:
    if value is None or not str(value).strip():
        return None
    cleaned = str(value).strip()
    try:
        date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(f"{label} must use YYYY-MM-DD format.") from exc
    return cleaned


@dataclass(frozen=True)
class DecisionRecord:
    """One reviewable action with its evidence, owner, disposition, and outcome."""

    decision_id: str
    title: str
    category: str
    status: str
    source_kind: str
    source_reference: str
    evidence_summary: str
    evidence_strength: str
    impact_kind: str
    impact_amount: float | None
    currency: str
    owner: str = "Unassigned"
    due_date: str | None = None
    target_timing: str = "Next cost review"
    effort: str = "Unknown"
    operational_risk: str = "Unknown"
    business_criticality: str = "Medium"
    decision_note: str = ""
    rejection_reason: str = ""
    baseline_cost: float | None = None
    post_change_cost: float | None = None
    baseline_period: str = ""
    measurement_period: str = ""
    provider: str = "Metrora"
    account_id: str = ""
    region: str = ""
    resource_id: str = ""
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_id", _clean_required(self.decision_id, "Decision ID"))
        object.__setattr__(self, "title", _clean_required(self.title, "Decision title"))
        object.__setattr__(self, "category", _clean_required(self.category, "Category"))
        object.__setattr__(self, "source_kind", _clean_required(self.source_kind, "Source kind"))
        object.__setattr__(
            self,
            "source_reference",
            _clean_required(self.source_reference, "Source reference"),
        )
        object.__setattr__(
            self,
            "evidence_summary",
            _clean_required(self.evidence_summary, "Evidence summary"),
        )
        if self.status not in DECISION_STATUSES:
            raise ValueError(f"Unsupported decision status: {self.status!r}.")
        if self.effort not in EFFORT_LEVELS:
            raise ValueError(f"Unsupported implementation effort: {self.effort!r}.")
        if self.operational_risk not in RISK_LEVELS:
            raise ValueError(f"Unsupported operational risk: {self.operational_risk!r}.")
        if self.business_criticality not in CRITICALITY_LEVELS:
            raise ValueError(f"Unsupported business criticality: {self.business_criticality!r}.")
        object.__setattr__(self, "due_date", _validate_date(self.due_date, "Due date"))
        object.__setattr__(
            self,
            "impact_amount",
            _optional_amount(self.impact_amount, "Impact amount"),
        )
        baseline = _optional_amount(self.baseline_cost, "Baseline cost")
        post_change = _optional_amount(self.post_change_cost, "Post-change cost")
        if baseline is not None and baseline < 0:
            raise ValueError("Baseline cost cannot be negative.")
        if post_change is not None and post_change < 0:
            raise ValueError("Post-change cost cannot be negative.")
        object.__setattr__(self, "baseline_cost", baseline)
        object.__setattr__(self, "post_change_cost", post_change)
        object.__setattr__(self, "metadata", dict(self.metadata))
        if self.status == "Rejected" and not self.rejection_reason.strip():
            raise ValueError("A rejected decision requires a rejection reason.")
        if self.status == "Verified" and (baseline is None or post_change is None):
            raise ValueError("A verified decision requires baseline and post-change actual costs.")

    @property
    def is_open(self) -> bool:
        return self.status in OPEN_DECISION_STATUSES

    @property
    def actual_cost_change(self) -> float | None:
        """Return actual baseline cost minus post-change cost when both were supplied."""
        if self.baseline_cost is None or self.post_change_cost is None:
            return None
        return self.baseline_cost - self.post_change_cost

    @property
    def verified_value(self) -> float:
        """Return positive measured value only after the outcome has been verified."""
        change = self.actual_cost_change
        if self.status != "Verified" or change is None:
            return 0.0
        return max(change, 0.0)

    def with_updates(self, **updates: Any) -> DecisionRecord:
        """Return a validated update with a refreshed audit timestamp."""
        updates["updated_at"] = _utc_now()
        return replace(self, **updates)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["actual_cost_change"] = self.actual_cost_change
        payload["verified_value"] = self.verified_value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DecisionRecord:
        accepted = {field_name for field_name in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in payload.items() if key in accepted})


def decision_priority_score(
    decision: DecisionRecord,
    *,
    max_impact: float,
    as_of: date | None = None,
) -> int:
    """Calculate a transparent queue score; it is not a savings estimate.

    The score combines relative financial exposure (40), evidence strength (20),
    timing (20), implementation effort (10), and business criticality (10).
    """
    if not decision.is_open:
        return 0
    impact = abs(decision.impact_amount or 0.0)
    impact_points = 40.0 * min(impact / max_impact, 1.0) if max_impact > 0 else 0.0
    evidence_points = {
        "verified": 20,
        "provider_estimate": 16,
        "modeled": 12,
        "user_supplied": 10,
        "unconfirmed": 6,
    }.get(decision.evidence_strength.casefold(), 8)
    today = as_of or date.today()
    if decision.due_date:
        days = (date.fromisoformat(decision.due_date) - today).days
        timing_points = 20 if days < 0 else 17 if days <= 7 else 12 if days <= 30 else 6
    else:
        timing_points = 5
    effort_points = {"Low": 10, "Medium": 7, "High": 3, "Unknown": 5}[decision.effort]
    criticality_points = {"High": 10, "Medium": 6, "Low": 3}[decision.business_criticality]
    return int(
        round(
            min(
                100.0,
                impact_points
                + evidence_points
                + timing_points
                + effort_points
                + criticality_points,
            )
        )
    )


def ranked_decisions(
    decisions: list[DecisionRecord] | tuple[DecisionRecord, ...],
    *,
    as_of: date | None = None,
) -> list[tuple[DecisionRecord, int]]:
    """Rank open work first while preserving a deterministic order for auditability."""
    max_impact = max((abs(item.impact_amount or 0.0) for item in decisions), default=0.0)
    ranked = [
        (item, decision_priority_score(item, max_impact=max_impact, as_of=as_of))
        for item in decisions
    ]
    return sorted(
        ranked,
        key=lambda pair: (
            not pair[0].is_open,
            -pair[1],
            pair[0].due_date or "9999-12-31",
            pair[0].title.casefold(),
        ),
    )
