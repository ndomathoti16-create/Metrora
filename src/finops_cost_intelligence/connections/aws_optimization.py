"""Read-only import of AWS Cost Optimization Hub recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

from ..decisions import DecisionRecord
from .contracts import CloudConnectionError


@dataclass(frozen=True)
class AwsOptimizationConfig:
    """Non-secret identity selectors for Cost Optimization Hub."""

    region: str = "us-east-1"
    profile_name: str | None = None

    def __post_init__(self) -> None:
        if not self.region.strip():
            raise ValueError("An AWS region is required.")


def _text(value: object, fallback: str = "") -> str:
    return str(value).strip() if value not in {None, ""} else fallback


def _amount(value: object) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _humanize(value: object) -> str:
    text = _text(value, "Review recommendation")
    output: list[str] = []
    for index, character in enumerate(text.replace("_", " ")):
        if index and character.isupper() and text[index - 1].islower():
            output.append(" ")
        output.append(character)
    return " ".join("".join(output).split()).capitalize()


def _decision_id(recommendation_id: str) -> str:
    digest = sha256(recommendation_id.encode("utf-8")).hexdigest()[:20]
    return f"aws-coh-{digest}"


def _operational_risk(item: dict[str, Any]) -> str:
    if item.get("rollbackPossible") is False:
        return "High"
    if item.get("restartNeeded") is True:
        return "Medium"
    return "Low"


def _effort(value: object) -> str:
    normalized = _text(value, "Unknown").replace("_", "").casefold()
    if normalized in {"verylow", "low"}:
        return "Low"
    if normalized in {"veryhigh", "high"}:
        return "High"
    if normalized == "medium":
        return "Medium"
    return "Unknown"


def aws_recommendation_to_decision(item: dict[str, Any]) -> DecisionRecord:
    """Normalize one provider estimate into Metrora's decision contract."""
    recommendation_id = _text(item.get("recommendationId"))
    if not recommendation_id:
        raise ValueError("AWS returned a recommendation without an ID.")
    action = _humanize(item.get("actionType"))
    resource_id = _text(item.get("resourceId"), "Unspecified resource")
    estimated_savings = _amount(item.get("estimatedMonthlySavings"))
    estimated_cost = _amount(item.get("estimatedMonthlyCost"))
    currency = _text(item.get("currencyCode"), "USD")
    current_type = _text(item.get("currentResourceType"), "current configuration")
    recommended_type = _text(item.get("recommendedResourceType"), "recommended configuration")
    savings_text = (
        f" AWS estimates {currency} {estimated_savings:,.2f} in monthly savings."
        if estimated_savings is not None
        else " AWS did not return a monthly savings estimate."
    )
    cost_text = (
        f" Estimated current monthly cost is {currency} {estimated_cost:,.2f}."
        if estimated_cost is not None
        else ""
    )
    return DecisionRecord(
        decision_id=_decision_id(recommendation_id),
        title=f"{action}: {resource_id}",
        category="Optimization",
        status="Proposed",
        source_kind="AWS Cost Optimization Hub",
        source_reference=recommendation_id,
        evidence_summary=(
            f"AWS recommends moving from {current_type} to {recommended_type}."
            f"{savings_text}{cost_text} Treat this as a provider estimate until actual "
            "post-change billing verifies the outcome."
        ),
        evidence_strength="provider_estimate",
        impact_kind="provider_estimated_monthly_savings",
        impact_amount=estimated_savings,
        currency=currency,
        owner="Unassigned",
        target_timing="Review during the next optimization cycle",
        effort=_effort(item.get("implementationEffort")),
        operational_risk=_operational_risk(item),
        business_criticality="Medium",
        provider="AWS",
        account_id=_text(item.get("accountId")),
        region=_text(item.get("region")),
        resource_id=resource_id,
        metadata={
            "action_type": item.get("actionType"),
            "current_resource_type": item.get("currentResourceType"),
            "recommended_resource_type": item.get("recommendedResourceType"),
            "estimated_monthly_cost": estimated_cost,
            "estimated_savings_percentage": _amount(item.get("estimatedSavingsPercentage")),
            "restart_needed": item.get("restartNeeded"),
            "rollback_possible": item.get("rollbackPossible"),
            "source": item.get("source"),
            "tags": item.get("tags") or [],
        },
    )


class AwsCostOptimizationConnector:
    """List AWS recommendations without changing any cloud resource."""

    def __init__(self, config: AwsOptimizationConfig, *, client: Any | None = None) -> None:
        self.config = config
        self._client = client

    @property
    def client(self):
        if self._client is None:
            session = boto3.Session(
                profile_name=(self.config.profile_name or None),
                region_name=self.config.region,
            )
            self._client = session.client(
                "cost-optimization-hub",
                region_name=self.config.region,
            )
        return self._client

    def list_decisions(self, *, max_items: int = 1000) -> list[DecisionRecord]:
        """Import bounded recommendation pages and normalize them to decisions."""
        if max_items <= 0:
            raise ValueError("max_items must be greater than zero.")
        items: list[dict[str, Any]] = []
        token: str | None = None
        try:
            while len(items) < max_items:
                request: dict[str, Any] = {
                    "includeAllRecommendations": True,
                    "maxResults": min(100, max_items - len(items)),
                }
                if token:
                    request["nextToken"] = token
                response = self.client.list_recommendations(**request)
                page_items = response.get("items", [])
                if not isinstance(page_items, list):
                    raise CloudConnectionError(
                        "AWS returned an invalid Cost Optimization Hub response."
                    )
                items.extend(item for item in page_items if isinstance(item, dict))
                token = response.get("nextToken")
                if not token or not page_items:
                    break
        except (BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError) as exc:
            raise CloudConnectionError(
                "AWS recommendations could not be read. Confirm Cost Optimization Hub is "
                "enabled and the selected identity can call "
                "cost-optimization-hub:ListRecommendations."
            ) from exc
        decisions: list[DecisionRecord] = []
        for item in items[:max_items]:
            try:
                decisions.append(aws_recommendation_to_decision(item))
            except ValueError:
                continue
        return decisions
