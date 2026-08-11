# Metrora differentiation strategy

## Executive decision

Metrora should not compete with AWS, Azure, or Google Cloud on the number of provider-specific
charts or optimization algorithms. The cloud providers already own the richest billing,
resource, commitment, and utilization signals inside their ecosystems.

Metrora's defensible role is the **provider-neutral FinOps decision and outcome layer**:

> Bring trusted cost evidence and native provider recommendations into one place, connect them
> to business context, assign a human decision, and verify the result from actual billing.

The target customer is a small or midsize finance, FinOps, or platform team that already has
billing exports and provider recommendations but lacks a consistent operating record across
clouds, teams, budgets, and review cycles.

## What the cloud providers already solve

| Existing capability | Provider strength | Metrora response |
| --- | --- | --- |
| Cost dashboards and drilldowns | AWS Cloud Intelligence Dashboards offer extensive CUDOS, KPI, optimization, and resource views. | Ingest or link the provider evidence; do not rebuild every visual. |
| Provider optimization | AWS Cost Optimization Hub, Azure Advisor, and Google Cloud FinOps Hub surface native opportunities. | Normalize recommendations into one decision contract and preserve the provider estimate as an estimate. |
| Allocation and cost management | Each provider supports native allocation, budgets, and cost analysis. | Reconcile allocation across providers and connect it to owners and business metrics. |
| Savings signals | Providers can estimate or report savings within their own methods and scope. | Separate estimated, observed, modeled, and verified financial values; verify with comparable actuals. |

This means "multi-cloud dashboard" is not enough differentiation. Multi-cloud is an input
property. Accountability and verified outcomes are the product.

## The product wedge

### 1. Trust gate before analysis

Every source is profiled, mapped, normalized, reconciled, and quality checked. Blocking failures
pause planning and reporting. This matters when exports from several providers use different
grains, currencies, terminology, and ownership fields.

### 2. Evidence classification

Every financial value must state what it is:

- **Observed** - calculated from billing actuals.
- **Modeled** - produced by a transparent forecast or anomaly baseline.
- **Provider estimate** - returned by a native cloud recommendation service.
- **Verified** - calculated from comparable baseline and post-change actual costs.

Metrora must never roll these categories into one misleading "savings" total.

### 3. Accountable decision register

Each material signal becomes a durable record with:

- source and evidence reference;
- financial basis and confidence;
- owner, due date, effort, operational risk, and business criticality;
- proposed, investigating, approved, rejected, implemented, or verified status;
- decision note and required rejection reason;
- actual baseline and measurement periods for outcome verification.

### 4. Business and executive context

The same decision can be evaluated against budget, allocation, customers, revenue,
transactions, or product usage. Executive reporting should answer: what changed, why the data
supports that statement, what is still unknown, who owns the next action, and what decision is
required.

### 5. Native tools as inputs

Metrora should import native provider recommendations instead of claiming to have better
resource telemetry. AWS Cost Optimization Hub intake is the first adapter. Azure Advisor and
Google Cloud recommendation intake should follow the same provider-neutral contract.

## What is implemented now

- Automatic conversion of calculated Metrora recommendations into decision records.
- Priority queue based on relative exposure, evidence, timing, effort, and criticality. The
  priority score is explicitly not a savings estimate.
- Owner, due date, disposition, risk, effort, note, and rejection-reason workflow.
- Actual baseline-versus-post-change outcome verification.
- Verified-value total that excludes proposed and provider-estimated savings.
- Read-only AWS Cost Optimization Hub recommendation import.
- CSV and JSON decision-register exports.
- Product and repository messaging that clearly separates provider depth from Metrora's role.

## Roadmap in the right order

### Next: complete provider-neutral recommendation intake

1. Azure Advisor recommendation adapter.
2. Google Cloud recommendation adapter.
3. Generic FOCUS or CSV recommendation contract for Kubernetes, SaaS, and internal tooling.

**Completion gate:** the same decision fields and evidence classifications are produced for all
providers, with no provider-specific status logic leaking into the register.

### Next: shared operating workflow

1. Shared team workspace with SSO and role-based access.
2. Immutable decision events rather than mutable local JSON only.
3. Comments, approval policy, reminders, and owner notifications.
4. Jira, ServiceNow, Slack, Teams, and email routing.

**Completion gate:** a reviewer can reconstruct who changed a decision, when, why, and from
which evidence without relying on application logs.

### Then: stronger outcome attribution

1. Comparable-scope checks for baseline and measurement periods.
2. Normalization for seasonality, usage growth, credits, commitments, and one-time charges.
3. Confidence and caveats for realized-value attribution.
4. Portfolio-level estimate-to-verified conversion reporting.

**Completion gate:** Metrora can explain why a measured cost change is or is not attributable to
an implemented action.

### Later: optimization evidence beyond billing

1. Utilization and rightsizing telemetry.
2. Commitment coverage and rate optimization evidence.
3. Kubernetes allocation and shared-platform unit economics.
4. Policy-as-code for allocation, anomaly, and approval thresholds.

**Completion gate:** a quantified optimization recommendation identifies its utilization,
pricing, commitment, and operational-risk evidence instead of inferring waste from cost alone.

## What Metrora should deliberately avoid

- Rebuilding hundreds of provider-specific dashboards.
- Claiming billing-only spend is waste.
- Presenting estimated savings as realized value.
- Writing to cloud resources before enterprise identity, approval, audit, and rollback controls
  exist.
- Adding AI-generated numbers or unsupported root-cause claims.
- Expanding to every technology vendor before the common decision contract is stable.

## Product message

**Primary:** Native tools find opportunities. Metrora closes the loop.

**Supporting:** Reconcile the evidence. Assign the decision. Verify the outcome.

**Interview explanation:** Metrora does not attempt to out-AWS AWS. It demonstrates how a FinOps
product can use provider-native telemetry while solving the cross-provider finance problem the
telemetry alone does not solve: trusted evidence, business context, accountability, and measured
outcomes.

## Primary sources

- AWS Cloud Intelligence Dashboards: <https://docs.aws.amazon.com/guidance/latest/cloud-intelligence-dashboards/dashboards.html>
- AWS CUDOS, Cost Intelligence, and KPI dashboards: <https://docs.aws.amazon.com/guidance/latest/cloud-intelligence-dashboards/cudos-cid-kpi.html>
- AWS Cost Optimization Hub recommendations: <https://docs.aws.amazon.com/cost-management/latest/userguide/coh-savings-opportunities.html>
- AWS Cost Optimization Hub API: <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_Operations_Cost_Optimization_Hub.html>
- Azure cost allocation: <https://learn.microsoft.com/azure/cost-management-billing/costs/cost-allocation-introduction>
- Azure Advisor cost recommendations: <https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-opt-recommendations>
- Google Cloud FinOps Hub: <https://docs.cloud.google.com/billing/docs/how-to/finops-hub>
- FinOps unit economics capability: <https://www.finops.org/framework/capabilities/unit-economics/>
- FinOps allocation capability: <https://www.finops.org/framework/capabilities/allocation/>
- FinOps usage optimization capability: <https://www.finops.org/framework/capabilities/usage-optimization/>
- 2026 FinOps Framework changes: <https://www.finops.org/insights/2026-finops-framework/>
