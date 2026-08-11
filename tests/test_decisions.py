from __future__ import annotations

from datetime import date

import pytest

from finops_cost_intelligence.connections import (
    AwsCostOptimizationConnector,
    AwsOptimizationConfig,
    aws_recommendation_to_decision,
)
from finops_cost_intelligence.contracts.ai import Fact, FactPack, Recommendation
from finops_cost_intelligence.decisions import (
    DecisionRecord,
    DecisionStore,
    merge_decisions,
    ranked_decisions,
    recommendations_to_decisions,
)


def _decision(**updates) -> DecisionRecord:
    values = {
        "decision_id": "decision-1",
        "title": "Review compute movement",
        "category": "Cost change",
        "status": "Proposed",
        "source_kind": "Metrora calculated signal",
        "source_reference": "recent_spend_increase_review",
        "evidence_summary": "Compute increased by a calculated amount.",
        "evidence_strength": "verified",
        "impact_kind": "observed_spend_movement",
        "impact_amount": 1200.0,
        "currency": "USD",
    }
    values.update(updates)
    return DecisionRecord(**values)


def test_verified_value_requires_actual_before_and_after_costs() -> None:
    implemented = _decision(status="Implemented")
    verified = implemented.with_updates(
        status="Verified",
        baseline_cost=5000.0,
        post_change_cost=4200.0,
        baseline_period="2026-06",
        measurement_period="2026-07",
    )

    assert implemented.verified_value == 0.0
    assert verified.actual_cost_change == 800.0
    assert verified.verified_value == 800.0


def test_provider_estimate_is_not_counted_as_verified_value() -> None:
    decision = aws_recommendation_to_decision(
        {
            "recommendationId": "rec-123",
            "actionType": "Rightsize",
            "resourceId": "i-123",
            "estimatedMonthlySavings": 325.5,
            "estimatedMonthlyCost": 900.0,
            "currencyCode": "USD",
            "implementationEffort": "Low",
            "rollbackPossible": True,
        }
    )

    assert decision.impact_amount == 325.5
    assert decision.impact_kind == "provider_estimated_monthly_savings"
    assert decision.verified_value == 0.0
    assert "provider estimate" in decision.evidence_summary.casefold()


def test_rejected_decision_requires_a_reason() -> None:
    with pytest.raises(ValueError, match="rejection reason"):
        _decision(status="Rejected")


def test_decision_store_round_trips_records(tmp_path) -> None:
    store = DecisionStore(tmp_path / "decisions.json")
    store.save(_decision(owner="Platform team"))

    restored = store.list()

    assert len(restored) == 1
    assert restored[0].owner == "Platform team"
    assert restored[0].impact_amount == 1200.0


def test_signal_refresh_preserves_human_disposition() -> None:
    current = _decision(
        status="Approved",
        owner="Compute lead",
        decision_note="Expected launch traffic.",
    )
    refreshed = _decision(
        impact_amount=1500.0,
        evidence_summary="The latest calculated movement is 1500.",
    )

    merged = merge_decisions([current], [refreshed])

    assert merged[0].status == "Approved"
    assert merged[0].owner == "Compute lead"
    assert merged[0].decision_note == "Expected launch traffic."
    assert merged[0].impact_amount == 1500.0


def test_priority_queue_uses_exposure_and_due_date_without_claiming_savings() -> None:
    urgent = _decision(due_date="2026-07-01", impact_amount=1000.0)
    later = _decision(
        decision_id="decision-2",
        title="Review storage",
        due_date="2026-12-01",
        impact_amount=100.0,
    )

    ranked = ranked_decisions([later, urgent], as_of=date(2026, 8, 1))

    assert ranked[0][0].decision_id == "decision-1"
    assert ranked[0][1] > ranked[1][1]


def test_fact_pack_recommendation_becomes_observed_exposure_not_savings() -> None:
    recommendation = Recommendation(
        recommendation_id="forecast_run_rate_review",
        title="Review forecast",
        priority="medium",
        action="Confirm the workload assumptions.",
        rationale="The outlook is above the recent run rate.",
        evidence_strength="modeled",
        fact_ids=("forecast_change_amount",),
    )
    fact_pack = FactPack(
        schema_version="1.0",
        generated_at="2026-08-01T00:00:00+00:00",
        ingestion_id="ingestion-1",
        source_name="billing.csv",
        period_start="2026-07-01",
        period_end="2026-07-31",
        filters={},
        quality_status="pass",
        quality_ready=True,
        facts=(
            Fact(
                fact_id="forecast_change_amount",
                label="Forecast gap",
                value=800.0,
                unit="USD",
                evidence="Forecast minus latest comparable actual.",
            ),
        ),
        recommendations=(recommendation,),
        caveats=(),
    )

    decision = recommendations_to_decisions(fact_pack)[0]

    assert decision.impact_kind == "modeled_forecast_gap"
    assert decision.impact_amount == 800.0
    assert decision.verified_value == 0.0


class _OptimizationClient:
    def __init__(self) -> None:
        self.calls = 0

    def list_recommendations(self, **request):
        self.calls += 1
        assert request["includeAllRecommendations"] is True
        if self.calls == 1:
            return {
                "items": [
                    {
                        "recommendationId": "aws-1",
                        "actionType": "Stop",
                        "resourceId": "i-idle",
                        "estimatedMonthlySavings": 200.0,
                        "currencyCode": "USD",
                        "implementationEffort": "VeryLow",
                    }
                ],
                "nextToken": "page-2",
            }
        assert request["nextToken"] == "page-2"
        return {
            "items": [
                {
                    "recommendationId": "aws-2",
                    "actionType": "Rightsize",
                    "resourceId": "db-1",
                    "estimatedMonthlySavings": 75.0,
                    "currencyCode": "USD",
                    "implementationEffort": "High",
                }
            ]
        }


def test_aws_optimization_connector_imports_bounded_pages() -> None:
    connector = AwsCostOptimizationConnector(
        AwsOptimizationConfig(),
        client=_OptimizationClient(),
    )

    decisions = connector.list_decisions(max_items=10)

    assert [item.resource_id for item in decisions] == ["i-idle", "db-1"]
    assert decisions[0].effort == "Low"
    assert decisions[1].effort == "High"
