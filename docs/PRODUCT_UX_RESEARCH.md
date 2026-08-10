# Metrora product UX research

Last reviewed: 2026-08-09

This note records the product decisions behind the authenticated Metrora workspace. It is
not a style-inspiration list; it translates current FinOps operating needs and enterprise
application patterns into testable interface requirements.

## What FinOps users need from the product

The [FinOps Framework Reporting & Analytics capability](https://www.finops.org/framework/capabilities/reporting-analytics/)
describes self-service reporting, ad hoc investigation, anomaly analysis, budget and forecast
variance, allocation coverage, persona-specific outputs, exports, and a centralized source of
truth. Its success measures include reducing the time needed to investigate usage and cost
questions.

The [FinOps Finance persona](https://framework.finops.org/framework/persona/finance/) emphasizes
accurate budgeting, forecasting, cost categorization, predictability, consistent reporting,
unit economics, and financial accountability.

Current cloud-cost products reinforce the same operating model:

- [AWS Billing and Cost Management Home](https://docs.aws.amazon.com/cost-management/latest/userguide/view-billing-dashboard.html)
  starts with trends and drivers, anomalies or budget overruns requiring attention,
  allocation coverage, and prioritized recommended actions.
- [Vantage Cost Reports](https://docs.vantage.sh/cost_reports) separates an overview of saved
  reports from deeper filtering, grouping, forecasting, and drilldown.
- The FinOps Framework expects reporting to serve finance, engineering, product, leadership,
  and FinOps users without requiring every persona to become a billing-schema expert.

## Interface requirements derived from the research

1. **Home must answer “where are we and what needs attention?”** It should show the current
   cost position, comparable movement, outlook, exceptions, and a short action queue.
2. **Exploration must be a dedicated task.** Date, grouping, filters, charts, and exact values
   belong in Cost explorer rather than competing with the operating overview.
3. **Planning signals belong together.** Forecast, anomalies, budgets, ownership, and unit
   economics form one Plans & alerts workflow.
4. **The normal path should be automated.** Upload, mapping, normalization, reconciliation, and
   validation run before results appear. Manual mapping is an exception path.
5. **Advanced controls should be progressively disclosed.** Source profiling, semantic mapping,
   reconciliation detail, forecast horizon, anomaly sensitivity, and chart depth belong in
   Advanced. Standard users should not need them.
6. **Exact values remain available.** Charts provide orientation; bounded tables and exports
   provide the auditable values behind them.
7. **Recommendations need ownership and evidence.** A useful action states what to inspect,
   why it matters, who should own it, and what evidence is still missing.

These decisions also follow the Carbon disclosure guidance: hide optional settings until they
are useful, but do not hide critical workflow status or required actions. See the
[Carbon disclosure pattern](https://carbondesignsystem.com/patterns/disclosures-pattern/) and
[data-table guidance](https://carbondesignsystem.com/components/data-table/usage/).

## Evidence standard for “why”

Metrora separates three levels of explanation:

1. **Observed movement:** which service, account, region, or owner changed and by how much.
2. **Billing-observed mechanism:** when a consistent usage unit is available, decompose the
   service movement into usage and effective cost-per-unit effects.
3. **Operational root cause:** deployment, incident, workload, price, discount, commitment, or
   configuration cause. This remains unconfirmed until matching operational or pricing data is
   connected.

“Effective rate / mix” is intentionally not labelled “price.” Cost divided by usage can move
because of list price, discounts, commitments, credits, resource mix, or allocation changes.
The interface therefore reports medium evidence for comparable billing plus usage and low
evidence for billing-only attribution.

## Workspace information architecture

| Destination | Primary question | Default user |
|---|---|---|
| Home | What is the current position and what should I do next? | Every user |
| Cost explorer | Which scope or dimension is driving cost? | FinOps and finance analysts |
| Plans & alerts | What risk is emerging against forecast, budget, or ownership? | FinOps, FP&A, operations |
| Reports | What should be shared, with which evidence and caveats? | Finance and leadership |
| Advanced | What automation or model detail needs expert review? | FinOps power users and data owners |

## Acceptance criteria

- A guided demo opens Home with no required setup.
- A new source reaches a complete analysis after one upload when required fields map safely.
- Every primary workspace destination is reachable from persistent, plainly named navigation.
- Standard forecast and anomaly views use saved defaults without exposing model controls.
- Long service labels and cost-axis values remain visible at common desktop widths.
- Driver explanations state what the evidence supports and what remains unconfirmed.
- The single dark visual system preserves readable text, controls, tables, charts, and disclosures.
