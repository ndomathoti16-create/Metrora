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
        if unit in {"", "cost units"}:
            return f"{value:,.2f}"
        return f"{value:,.2f} {unit}"
    if isinstance(value, int):
        return f"{value:,} {unit}" if unit else f"{value:,}"
    return html.escape(str(value))


def executive_report_html(fact_pack: FactPack, summary: SummaryResult) -> str:
    """Render a portable report with facts, caveats, and recommendations."""
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
        f"<td>{html.escape(', '.join(recommendation.fact_ids) or 'No numeric fact required')}</td>"
        "</tr>"
        for recommendation in fact_pack.recommendations
    )
    bullets = "\n".join(
        f"<li>{html.escape(bullet)}</li>" for bullet in summary.bullets
    )
    caveats = "\n".join(
        f"<li>{html.escape(caveat)}</li>"
        for caveat in (*fact_pack.caveats, *summary.caveats)
    ) or "<li>No additional caveats were recorded.</li>"
    period = (
        f"{fact_pack.period_start or 'Unavailable'} to "
        f"{fact_pack.period_end or 'Unavailable'}"
    )
    quality_status = html.escape(fact_pack.quality_status)
    provider = html.escape(summary.provider)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FinOps Executive Summary</title>
<style>
:root {{ color-scheme: light dark; font-family: Inter, system-ui, sans-serif; }}
body {{ max-width: 1100px; margin: 0 auto; padding: 2rem; line-height: 1.5; }}
.eyebrow {{ color: #2f6bff; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }}
.card {{ border: 1px solid #94a3b8; border-radius: 12px; padding: 1rem 1.25rem; margin: 1rem 0; }}
table {{ border-collapse: collapse; width: 100%; margin: .75rem 0 1.5rem; }}
th, td {{ border-bottom: 1px solid #94a3b8; padding: .65rem; }}
th {{ font-weight: 700; text-align: left; }}
small {{ color: #64748b; }}
</style>
</head>
<body>
<p class="eyebrow">FinOps Cost Intelligence</p>
<h1>Executive summary</h1>
<p><strong>Analysis period:</strong> {html.escape(period)}<br>
<strong>Source:</strong> {html.escape(fact_pack.source_name)}<br>
<strong>Quality status:</strong> {quality_status} ·
<strong>Summary provider:</strong> {provider}</p>
<section class="card">
<h2>What changed</h2>
<p>{html.escape(summary.headline)}</p><ul>{bullets}</ul>
</section>
<section>
<h2>Calculated evidence</h2>
<table><thead><tr><th>Fact</th><th>Value</th><th>Evidence definition</th></tr></thead>
<tbody>{fact_rows}</tbody></table>
</section>
<section>
<h2>Recommended next actions</h2>
<table><thead><tr><th>Priority</th><th>Recommendation</th><th>Action</th><th>Evidence</th></tr></thead>
<tbody>{recommendation_rows}</tbody></table>
</section>
<section class="card">
<h2>Caveats</h2><ul>{caveats}</ul>
<small>All financial values were calculated before this report was generated.
The summary layer does not calculate new amounts.</small>
</section>
</body>
</html>
"""
