"""Self-contained HTML executive report export."""

from __future__ import annotations

import html

from ..contracts.ai import FactPack, SummaryResult


def _display_value(value: object, unit: str) -> str:
    if value is None:
        return "Unavailable"
    if isinstance(value, float):
        if unit == "share":
            return f"{value:.1%}"
        if len(unit) == 3 and unit.isalpha() and unit.upper() == unit:
            return f"{unit} {value:,.2f}"
        if unit in {"", "cost units"}:
            return f"{value:,.2f}"
        return f"{value:,.2f} {unit}"
    if isinstance(value, int):
        return f"{value:,} {unit}" if unit else f"{value:,}"
    return html.escape(str(value))


def _fact_map(fact_pack: FactPack) -> dict[str, object]:
    return {fact.fact_id: fact for fact in fact_pack.facts}


def _service_mover_rows(fact_pack: FactPack) -> str:
    facts = _fact_map(fact_pack)
    rows: list[str] = []
    for rank in range(1, 4):
        prefix = f"service_mover_{rank}"
        name = facts.get(f"{prefix}_name")
        recent = facts.get(f"{prefix}_recent_spend")
        prior = facts.get(f"{prefix}_prior_spend")
        change = facts.get(f"{prefix}_change_amount")
        driver_type = facts.get(f"{prefix}_driver_type")
        explanation = facts.get(f"{prefix}_explanation")
        evidence_level = facts.get(f"{prefix}_evidence_level")
        if any(value is None for value in (name, recent, prior, change)):
            continue
        change_value = float(change.value)
        signed_change = (
            f"{'+' if change_value > 0 else ''}{_display_value(change_value, change.unit)}"
        )
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(name.value))}</td>"
            f"<td>{_display_value(recent.value, recent.unit)}</td>"
            f"<td>{_display_value(prior.value, prior.unit)}</td>"
            f"<td>{html.escape(signed_change)}</td>"
            f"<td>{html.escape(str(driver_type.value)) if driver_type else 'Billing-only'}</td>"
            f"<td>{html.escape(str(explanation.value)) if explanation else 'Context required'}</td>"
            f"<td>{html.escape(str(evidence_level.value)) if evidence_level else 'Low'}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _review_questions(fact_pack: FactPack) -> tuple[str, ...]:
    facts = _fact_map(fact_pack)
    questions: list[str] = []
    if "budget_total" not in facts:
        questions.append(
            "Which approved budget or operating forecast should this scope be measured against?"
        )
    if "cost_per_business_unit" not in facts:
        questions.append(
            "Which business output should be paired with cloud spend to measure unit economics?"
        )
    questions.append(
        "Do utilization, commitment coverage, and pricing data support a quantified "
        "optimization decision?"
    )
    return tuple(questions)


def executive_report_html(fact_pack: FactPack, summary: SummaryResult) -> str:
    """Render a portable answer-first decision brief with traceable evidence."""
    facts = _fact_map(fact_pack)
    fact_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(fact.label)}</td>"
        f"<td>{_display_value(fact.value, fact.unit)}</td>"
        f"<td>{html.escape(fact.evidence)}</td>"
        "</tr>"
        for fact in fact_pack.facts
    )
    recommendation_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(recommendation.priority.title())}</td>"
        f"<td>{html.escape(recommendation.title)}</td>"
        f"<td>{html.escape(recommendation.action)}</td>"
        f"<td>{html.escape(recommendation.owner)}</td>"
        f"<td>{html.escape(recommendation.timeframe)}</td>"
        f"<td>{html.escape(recommendation.rationale)}</td>"
        "</tr>"
        for recommendation in fact_pack.recommendations
    )
    bullets = "\n".join(f"<li>{html.escape(bullet)}</li>" for bullet in summary.bullets)
    caveat_values = tuple(dict.fromkeys((*fact_pack.caveats, *summary.caveats)))
    caveats = (
        "\n".join(f"<li>{html.escape(caveat)}</li>" for caveat in caveat_values)
        or "<li>No additional caveats were recorded.</li>"
    )
    questions = "\n".join(
        f"<li>{html.escape(question)}</li>" for question in _review_questions(fact_pack)
    )
    mover_rows = _service_mover_rows(fact_pack)
    mover_section = ""
    if mover_rows:
        mover_section = f"""
<section>
<p class="eyebrow">Drivers</p>
<h2>What changed and why</h2>
<p class="section-copy">Observed cost movement is separated from operational root cause.
Usage and effective-rate evidence is used only when the source supports it.</p>
<table><thead><tr><th>Service</th><th>Latest</th><th>Prior</th><th>Change</th>
<th>Observed mechanism</th><th>Why</th><th>Evidence</th></tr></thead>
<tbody>{mover_rows}</tbody></table>
</section>
"""
    total = facts.get("total_spend")
    change = facts.get("spend_change_pct")
    forecast = facts.get("forecast_total")
    budget = facts.get("budget_utilization")
    anomaly = facts.get("anomaly_estimated_increase_total")
    period = f"{fact_pack.period_start or 'Unavailable'} to {fact_pack.period_end or 'Unavailable'}"
    kpis = [
        (
            "Selected spend",
            _display_value(total.value, total.unit) if total is not None else "Unavailable",
            period,
        ),
        (
            "Recent movement",
            f"{float(change.value):+.1%}" if change is not None else "Unavailable",
            "Latest equal window versus prior window",
        ),
        (
            "14-day outlook",
            _display_value(forecast.value, forecast.unit)
            if forecast is not None
            else "Unavailable",
            "Deterministic forecast",
        ),
        (
            "Budget / flagged impact",
            (
                f"{float(budget.value):.1%} used"
                if budget is not None and budget.value is not None
                else _display_value(anomaly.value, anomaly.unit)
                if anomaly is not None
                else "Unavailable"
            ),
            (
                "Budget position"
                if budget is not None and budget.value is not None
                else "Spend above anomaly baselines"
            ),
        ),
    ]
    kpi_html = "".join(
        f"<div><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong>"
        f"<small>{html.escape(detail)}</small></div>"
        for label, value, detail in kpis
    )
    quality_status = html.escape(fact_pack.quality_status)
    provider = html.escape(summary.provider)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metrora Executive Brief</title>
<style>
:root {{ color-scheme: light; font-family: Inter, system-ui, sans-serif; color: #142033; }}
body {{
    max-width: 1120px; margin: 0 auto; padding: 3rem 2rem 5rem;
    line-height: 1.55; background: #f7f9fc;
}}
h1, h2, h3 {{ letter-spacing: -.035em; }}
h1 {{ max-width: 820px; font-size: 2.7rem; line-height: 1.08; }}
section {{ margin-top: 3rem; }}
.eyebrow {{
    color: #245fba; font-size: .76rem; font-weight: 800;
    letter-spacing: .1em; text-transform: uppercase;
}}
.meta {{ color: #64748b; }}
.kpis {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    margin: 2rem 0; border-block: 1px solid #dbe3ef;
}}
.kpis div {{ padding: 1rem; border-left: 1px solid #dbe3ef; }}
.kpis div:first-child {{ border-left: 0; }}
.kpis span, .kpis small, .kpis strong {{ display: block; }}
.kpis span {{
    color: #64748b; font-size: .7rem; font-weight: 700;
    letter-spacing: .07em; text-transform: uppercase;
}}
.kpis strong {{ margin: .35rem 0; font-size: 1.35rem; }}
.kpis small {{ color: #64748b; }}
.bottom-line {{ padding: .3rem 0 .3rem 1.1rem; border-left: 4px solid #2878f0; }}
.bottom-line p {{ margin: 0; font-size: 1.3rem; font-weight: 650; }}
.section-copy {{ color: #64748b; }}
table {{ border-collapse: collapse; width: 100%; margin: .75rem 0 1.5rem; background: #fff; }}
th, td {{ border-bottom: 1px solid #dbe3ef; padding: .75rem; vertical-align: top; }}
th {{ font-weight: 700; text-align: left; }}
small {{ color: #64748b; }}
@media (max-width: 760px) {{
    .kpis {{ grid-template-columns: 1fr 1fr; }}
    body {{ padding: 1.5rem 1rem 3rem; }}
}}
</style>
</head>
<body>
<p class="eyebrow">Metrora · Cloud FinOps intelligence</p>
<h1>Executive decision brief</h1>
<p class="meta"><strong>Analysis period:</strong> {html.escape(period)}<br>
<strong>Source:</strong> {html.escape(fact_pack.source_name)}<br>
<strong>Quality status:</strong> {quality_status} ·
<strong>Summary provider:</strong> {provider}</p>
<div class="kpis">{kpi_html}</div>
<section>
<p class="eyebrow">Bottom line</p>
<div class="bottom-line"><p>{html.escape(summary.headline)}</p></div>
<h2>Key findings</h2><ul>{bullets}</ul>
</section>
{mover_section}
<section>
<p class="eyebrow">Actions</p>
<h2>Recommended next actions</h2>
<table><thead><tr>
<th>Priority</th><th>Recommendation</th><th>Action</th>
<th>Owner</th><th>When</th><th>Why now</th>
</tr></thead>
<tbody>{recommendation_rows}</tbody></table>
</section>
<section>
<p class="eyebrow">Open questions</p>
<h2>Questions for the next review</h2><ul>{questions}</ul>
</section>
<section>
<p class="eyebrow">Audit trail</p>
<h2>Calculated evidence</h2>
<table><thead><tr><th>Fact</th><th>Value</th><th>Evidence definition</th></tr></thead>
<tbody>{fact_rows}</tbody></table>
<h2>Limitations</h2><ul>{caveats}</ul>
<small>All financial values were calculated before this report was generated.
The summary layer does not calculate new amounts.</small>
</section>
</body>
</html>
"""
