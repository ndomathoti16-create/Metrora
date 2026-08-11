"""Public Metrora product pages and local-only demo access flow."""

# ruff: noqa: E501

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

from ..contracts.normalization import NormalizedTable
from ..contracts.profile import DataProfile
from ..contracts.quality import QualityReport
from ..ingestion import IngestionError, LoadedTable, load_table, profile_table
from ..mapping import MappingValidationError, suggest_mappings, validate_mapping
from ..normalization import normalize_billing_table
from ..normalization.budgets import normalize_budget_dataframe
from ..normalization.business_metrics import normalize_business_metrics
from ..quality import run_quality_checks
from ..runtime import resource_path
from .branding import METRORA_LOGO_SVG, reset_workspace_state
from .mapping_view import source_key_for
from .navigation import set_product_route, set_workspace_route

if TYPE_CHECKING:
    from ..config import Settings


PUBLIC_PAGES = ("Product", "Demo")

DEFAULT_DEMO_SCENARIO = "forecast_risk"
DEMO_SCENARIOS: dict[str, dict[str, str]] = {
    "healthy": {
        "label": "Healthy baseline",
        "status": "Ready to share",
        "description": "Clean, stable spend with complete ownership and comfortable budget headroom.",
        "lesson": "See what a low-risk, decision-ready review looks like.",
        "billing": "cloud_billing_healthy.csv",
        "budget": "budget_healthy.csv",
        "business": "business_metrics_healthy.csv",
    },
    "quality_risk": {
        "label": "Data needs review",
        "status": "Blocked on quality",
        "description": "Mixed currency, invalid required values, duplicates, and ownership gaps.",
        "lesson": "See how Metrora stops unreliable numbers before analysis.",
        "billing": "cloud_billing_quality_risk.csv",
        "budget": "budget_quality_risk.csv",
        "business": "business_metrics_quality_risk.csv",
    },
    "forecast_risk": {
        "label": "Hidden future risk",
        "status": "Healthy now, watch next",
        "description": "Reconciled spend that is currently controlled but accelerating into the forecast.",
        "lesson": "See why a clean current period can still require action.",
        "billing": "cloud_billing_demo.csv",
        "budget": "budget_demo.csv",
        "business": "business_metrics_demo.csv",
    },
}


PRODUCT_PAGE_CSS = """
<style>
.block-container {
    max-width: 1220px !important;
    margin: 0 auto !important;
    padding: 2.7rem 2.5rem 5.5rem !important;
}

.metrora-product-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.7rem;
}

.metrora-product-brand {
    display: flex;
    align-items: center;
    gap: .72rem;
}

.metrora-product-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.45rem;
    height: 2.45rem;
    border-radius: .8rem;
    background: transparent;
    box-shadow: none;
}

.metrora-product-name {
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 1.08rem;
    font-weight: 700;
    letter-spacing: -.04em;
}

.metrora-product-subtitle {
    color: #718097;
    font-size: .72rem;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metrora-product-nav-meta {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: .45rem;
}

.metrora-product-nav-meta span,
.metrora-product-pill {
    display: inline-flex;
    align-items: center;
    min-height: 1.9rem;
    padding: .38rem .65rem;
    border: 1px solid #dbe3ef;
    border-radius: 999px;
    background: #ffffff;
    color: #52627a;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.metrora-product-hero {
    display: grid;
    grid-template-columns: minmax(0, 1.03fr) minmax(320px, .97fr);
    gap: 2.5rem;
    align-items: center;
    max-width: 1120px;
    margin: 0 auto;
    padding: 3.8rem 3.8rem;
    border: 1px solid #d8e2ef;
    border-radius: 1.8rem;
    background:
        radial-gradient(circle at 92% 10%, rgba(217,243,107,.24), transparent 15rem),
        radial-gradient(circle at 5% 100%, rgba(91,213,181,.18), transparent 18rem),
        linear-gradient(135deg, #f8fafd 0%, #eef1fa 58%, #e5f4ed 100%);
    box-shadow: 0 22px 50px rgba(39, 58, 93, .09);
}

.metrora-product-kicker,
.metrora-product-section-kicker {
    margin-bottom: .72rem;
    color: #6658e8;
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
}

.metrora-product-hero h1 {
    max-width: 640px;
    margin: 0 0 1rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2.6rem, 5vw, 4.8rem);
    line-height: .98;
    letter-spacing: -.075em;
}

.metrora-product-hero p {
    max-width: 630px;
    margin: 0;
    color: #52627a;
    font-size: 1.04rem;
    line-height: 1.7;
}

.metrora-product-pills {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    margin-top: 1.45rem;
}

.metrora-hero-visual {
    padding: 1.25rem;
    border: 1px solid rgba(102,88,232,.17);
    border-radius: 1.35rem;
    background: rgba(248,250,253,.78);
    box-shadow: 0 16px 38px rgba(63, 77, 116, .12);
}

.metrora-visual-header,
.metrora-visual-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .75rem;
}

.metrora-visual-header {
    color: #718097;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.metrora-visual-status {
    color: #3d9f7d;
}

.metrora-visual-metric {
    margin: 1.25rem 0 .85rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -.06em;
}

.metrora-visual-metric small {
    margin-left: .35rem;
    color: #3d9f7d;
    font-family: 'DM Sans', sans-serif;
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: 0;
}

.metrora-visual-chart {
    display: flex;
    align-items: flex-end;
    gap: .55rem;
    height: 9.25rem;
    padding: 1rem .6rem .55rem;
    border-bottom: 1px solid #dfe6f0;
}

.metrora-visual-bar {
    flex: 1 1 0;
    min-width: 1rem;
    border-radius: .45rem .45rem .18rem .18rem;
    background: linear-gradient(180deg, #a99fff, #6658e8);
}

.metrora-visual-bar.is-mint {
    background: linear-gradient(180deg, #8be8d0, #3d9f7d);
}

.metrora-visual-footer {
    padding-top: .8rem;
    color: #718097;
    font-size: .75rem;
}

.metrora-visual-footer strong {
    color: #142033;
    font-size: .78rem;
}

.st-key-product-page-nav {
    width: min(100%, 560px);
    margin: 1.15rem auto 3.8rem;
    border-bottom: 1px solid #dbe3ef;
}

.st-key-product-page-nav [data-testid="stHorizontalBlock"] {
    gap: 1.15rem;
}

.st-key-product-page-nav [data-testid="stButton"] button,
.metrora-page-link {
    min-height: 2.45rem;
    width: 100%;
    padding: .55rem .1rem .7rem !important;
    border: 0 !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #66758a !important;
    font-size: .92rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    text-align: center;
    white-space: nowrap;
}

.st-key-product-page-nav [data-testid="stButton"] button:hover {
    border-bottom-color: #c7d0de !important;
    color: #142033 !important;
}

.st-key-product-page-nav [data-testid="stButton"] button p,
.st-key-product-page-nav [data-testid="stButton"] button span {
    color: inherit !important;
}

.st-key-product-page-nav [data-testid="stButton"] button * {
    color: inherit !important;
}

.metrora-page-link {
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom-color: #ff816b !important;
    color: #142033 !important;
}

.st-key-product_demo_hero {
    margin-top: 1rem;
}

.metrora-product-section {
    max-width: 1120px;
    margin: 0 auto 2.25rem;
    text-align: center;
}

.metrora-product-section h2 {
    max-width: 790px;
    margin: 0 auto .65rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.65rem);
    line-height: 1.08;
    letter-spacing: -.06em;
}

.metrora-product-section > p {
    max-width: 750px;
    margin: 0 auto;
    color: #66758a;
    font-size: 1rem;
    line-height: 1.7;
}

.metrora-centered-section {
    max-width: 920px;
    margin: 3.8rem auto 1.4rem;
    text-align: center;
}

.metrora-centered-section h3 {
    margin: 0 0 .6rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 1.55rem;
    letter-spacing: -.045em;
}

.metrora-centered-section p {
    margin: 0 auto;
    color: #66758a;
    font-size: .96rem;
    line-height: 1.65;
}

.metrora-product-card,
.metrora-product-step,
.metrora-product-access,
.metrora-product-output {
    border: 0;
    border-top: 1px solid #dbe3ef;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
}

.metrora-product-card {
    min-height: 215px;
    padding: 1.65rem .35rem 1.7rem;
}

.metrora-product-card .icon,
.metrora-output-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: .65rem;
    background: #edf0ff;
    color: #6658e8;
    font-size: .8rem;
    font-weight: 800;
}

.metrora-product-card h3,
.metrora-product-output h3 {
    margin: .85rem 0 .45rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 1.07rem;
    letter-spacing: -.035em;
}

.metrora-product-card p,
.metrora-product-output p {
    margin: 0;
    color: #66758a;
    font-size: .97rem;
    line-height: 1.7;
}

.metrora-product-split {
    margin-top: 3.1rem;
    padding: 1.85rem 0;
    border-top: 1px solid #dbe3ef;
}

.metrora-product-split h3 {
    margin: 0 0 .55rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    letter-spacing: -.04em;
}

.metrora-product-split p,
.metrora-product-split li {
    color: #66758a;
    font-size: .97rem;
    line-height: 1.75;
}

.metrora-product-split ul {
    margin: .7rem 0 0;
    padding-left: 1.15rem;
}

.metrora-signal-board {
    padding: .7rem 0;
}

.metrora-signal-line {
    display: flex;
    align-items: center;
    gap: .7rem;
    margin: .65rem 0;
    color: #52627a;
    font-size: .78rem;
}

.metrora-signal-line span {
    display: block;
    height: .52rem;
    border-radius: 999px;
    background: linear-gradient(90deg, #6658e8, #a99fff);
}

.metrora-signal-line:nth-child(3) span {
    background: linear-gradient(90deg, #3d9f7d, #8be8d0);
}

.metrora-signal-line:nth-child(4) span {
    background: linear-gradient(90deg, #ff816b, #ffc2b5);
}

.metrora-product-step {
    display: flex;
    gap: 1.1rem;
    margin: 0 auto;
    max-width: 920px;
    padding: 1.55rem 0;
}

.metrora-product-step-number {
    flex: 0 0 auto;
    color: #6658e8;
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
}

.metrora-product-step strong {
    color: #142033;
    font-size: .98rem;
}

.metrora-product-step p {
    margin: .32rem 0 0;
    color: #66758a;
    font-size: .96rem;
    line-height: 1.72;
}

.metrora-product-output {
    min-height: 165px;
    padding: 1.55rem 0;
}

.metrora-product-access {
    max-width: 920px;
    margin: 3.2rem auto 0;
    padding: 1.8rem 0;
}

.metrora-product-access h3 {
    margin: 0 0 .5rem;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 1.35rem;
    letter-spacing: -.04em;
}

.metrora-product-access p {
    margin: 0;
    color: #66758a;
    font-size: .95rem;
    line-height: 1.65;
}

.metrora-product-note {
    margin-top: .85rem;
    color: #718097;
    font-size: .8rem;
    line-height: 1.6;
}

.metrora-product-footer {
    margin: 4rem 0 .25rem;
    color: #718097;
    font-size: .8rem;
    text-align: center;
}

.metrora-centered-caption {
    margin: .85rem auto 1.5rem;
    padding: .35rem 0;
    color: #718097;
    font-size: .8rem;
    line-height: 1.6;
    text-align: center;
}

.metrora-model-caption {
    margin-bottom: 2.2rem;
    padding: .55rem 0;
}

.metrora-model-map {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
    gap: 1rem;
    align-items: center;
    max-width: 1120px;
    margin: 2.4rem auto 3.25rem;
}

.metrora-model-node {
    min-height: 7.25rem;
    padding: 1.15rem .15rem;
    border-top: 1px solid #dbe3ef;
    border-bottom: 1px solid #dbe3ef;
}

.metrora-model-node small {
    display: block;
    margin-bottom: .55rem;
    color: #6658e8;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.metrora-model-node strong {
    display: block;
    color: #142033;
    font-family: 'Outfit', sans-serif;
    font-size: 1.03rem;
}

.metrora-model-node p {
    margin: .35rem 0 0;
    color: #66758a;
    font-size: .88rem;
    line-height: 1.55;
}

.metrora-model-arrow {
    color: #6658e8;
    font-size: 1.35rem;
    font-weight: 700;
}

.metrora-access-note {
    max-width: 920px;
    margin: 2rem auto 0;
    padding: 1rem 0;
    border-top: 1px solid #dbe3ef;
    border-bottom: 1px solid #dbe3ef;
    color: #66758a;
    font-size: .92rem;
    line-height: 1.65;
}

.metrora-access-note strong {
    color: #142033;
}

@media (max-width: 900px) {
    .block-container {
        padding: 1.45rem 1rem 3.5rem !important;
    }

    .metrora-product-hero {
        grid-template-columns: 1fr;
        padding: 2rem 1.4rem;
    }

    .metrora-product-nav {
        align-items: flex-start;
        flex-direction: column;
    }

    .metrora-product-nav-meta {
        justify-content: flex-start;
    }

    .st-key-product-page-nav {
        width: 100%;
        margin-bottom: 3rem !important;
    }

    .st-key-product-page-nav [data-testid="stHorizontalBlock"] {
        gap: .35rem;
    }

    .metrora-model-map {
        grid-template-columns: 1fr;
        gap: .35rem;
    }

    .metrora-model-arrow {
        text-align: center;
        transform: rotate(90deg);
    }
}
</style>
"""


PRODUCT_PAGE_DARK_CSS = """
<style>
.metrora-product-name,
.metrora-product-hero h1,
.metrora-product-section h2,
.metrora-centered-section h3,
.metrora-product-card h3,
.metrora-product-output h3,
.metrora-product-step strong,
.metrora-product-access h3,
.metrora-product-split h3,
.metrora-visual-footer strong,
.metrora-visual-metric {
    color: #f4f7fb;
}

.metrora-product-subtitle,
.metrora-product-section > p,
.metrora-centered-section p,
.metrora-product-card p,
.metrora-product-output p,
.metrora-product-step p,
.metrora-product-access p,
.metrora-product-split p,
.metrora-product-split li,
.metrora-product-note,
.metrora-product-footer,
.metrora-centered-caption,
.metrora-visual-header,
.metrora-visual-footer,
.metrora-signal-line,
.metrora-model-node p,
.metrora-access-note {
    color: #aebbd0;
}

.metrora-model-node strong,
.metrora-access-note strong {
    color: #f4f7fb;
}

.metrora-model-node,
.metrora-access-note {
    border-color: #2b3a54;
}

.metrora-product-nav-meta span,
.metrora-product-pill {
    border-color: #33445f;
    background: #172238;
    color: #c6d2e3;
}

.metrora-product-hero {
    border-color: #33445f;
    background:
        radial-gradient(circle at 92% 10%, rgba(217,243,107,.18), transparent 15rem),
        radial-gradient(circle at 5% 100%, rgba(91,213,181,.16), transparent 18rem),
        linear-gradient(135deg, #111b30 0%, #1a2945 58%, #253560 100%);
    box-shadow: 0 24px 55px rgba(0, 0, 0, .22);
}

.metrora-product-hero p {
    color: #c2cee0;
}

.metrora-hero-visual {
    border-color: #2b3a54;
    background: #172238;
    box-shadow: 0 14px 34px rgba(0, 0, 0, .18);
}

.metrora-product-card,
.metrora-product-step,
.metrora-product-access,
.metrora-product-output,
.metrora-product-split {
    border-top-color: #2b3a54;
    background: transparent;
    box-shadow: none;
}

.metrora-visual-chart {
    border-bottom-color: #33445f;
}

.metrora-product-card .icon,
.metrora-output-mark {
    background: rgba(102,88,232,.22);
    color: #c4bdff;
}

.st-key-product-page-nav {
    border-bottom-color: #33445f;
}

.st-key-product-page-nav [data-testid="stButton"] button,
.metrora-page-link {
    color: #aebbd0 !important;
}

.st-key-product-page-nav [data-testid="stButton"] button:hover {
    border-bottom-color: #516685 !important;
    color: #f4f7fb !important;
}

.st-key-product-page-nav [data-testid="stButton"] button p,
.st-key-product-page-nav [data-testid="stButton"] button span {
    color: inherit !important;
}

.st-key-product-page-nav [data-testid="stButton"] button * {
    color: inherit !important;
}

.metrora-page-link {
    border-bottom-color: #ff816b !important;
    color: #f4f7fb !important;
}
</style>
"""


PRODUCT_PAGE_REFINED_CSS = """
<style>
.block-container {
    max-width: 1240px !important;
    padding: 2rem 2.5rem 7rem !important;
}

.metrora-product-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 3.4rem;
    gap: 1rem;
    margin: 0 0 1.55rem;
    padding: 0 .1rem;
}

.metrora-product-brand { gap: .76rem; }
.metrora-product-mark { width: 2.6rem; height: 2.6rem; }
.metrora-product-mark .metrora-logo { width: 2.6rem; height: 2.6rem; }

.metrora-product-name {
    color: #f5f7fb !important;
    font-family: 'Outfit', sans-serif;
    font-size: 1.08rem;
    font-weight: 700;
    letter-spacing: -.045em;
}

.metrora-product-subtitle,
.metrora-product-kicker,
.metrora-product-section-kicker {
    color: #9bb8ff !important;
    font-size: .64rem;
    font-weight: 700;
    letter-spacing: .15em;
    text-transform: uppercase;
}

.metrora-product-nav-meta { gap: .5rem; }
.metrora-product-nav-meta span,
.metrora-product-pill {
    border: 1px solid rgba(166, 185, 220, .22) !important;
    border-radius: 999px;
    background: rgba(17, 25, 39, .74) !important;
    color: #b8c4d5 !important;
    font-size: .64rem;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
}

.st-key-product-page-nav {
    width: min(100%, 34rem);
    margin: 0 auto 4.4rem;
    border-bottom: 1px solid #263246 !important;
}

.st-key-product-page-nav [data-testid="stButton"] button,
.metrora-page-link {
    min-height: 2.5rem !important;
    border: 0 !important;
    border-bottom: 1px solid transparent !important;
    border-radius: 0 !important;
    background: transparent !important;
    color: #8794a8 !important;
    font-size: .82rem;
    font-weight: 600;
    box-shadow: none !important;
}

.st-key-product-page-nav [data-testid="stButton"] button:hover {
    border-bottom-color: #51627d !important;
    background: transparent !important;
    color: #edf2fb !important;
}

.metrora-page-link {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #f5f7fb !important;
    border-bottom-color: #9bb8ff !important;
}

.metrora-premium-hero {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    min-height: 31rem;
    margin: 0 0 1.8rem;
    padding: clamp(2.2rem, 5vw, 5.4rem) clamp(1.8rem, 5vw, 5.4rem) !important;
    border: 1px solid #29364b !important;
    border-radius: 1.45rem !important;
    background:
        linear-gradient(120deg, rgba(155, 184, 255, .06), transparent 44%),
        linear-gradient(145deg, #0f1724 0%, #0c111a 58%, #111b27 100%) !important;
    box-shadow: 0 28px 90px rgba(0, 0, 0, .32) !important;
}

.metrora-premium-hero::before {
    position: absolute;
    z-index: -1;
    width: 38rem;
    height: 20rem;
    right: -9rem;
    top: -10rem;
    border: 1px solid rgba(155, 184, 255, .15);
    border-radius: 48% 52% 63% 37% / 54% 42% 58% 46%;
    background: radial-gradient(ellipse, rgba(126, 224, 208, .11), transparent 68%);
    content: '';
    filter: blur(.2px);
    animation: metrora-drift 16s ease-in-out infinite alternate;
}

.metrora-premium-hero::after {
    position: absolute;
    z-index: -1;
    width: 30rem;
    height: 7rem;
    left: -10rem;
    bottom: -4.2rem;
    border-top: 1px solid rgba(155, 184, 255, .17);
    border-radius: 50%;
    content: '';
    transform: rotate(-8deg);
}

.metrora-hero-copy { max-width: 37rem; animation: metrora-rise .7s ease both; }

.metrora-product-kicker { margin-bottom: 1.35rem; }

.metrora-product-hero h1 {
    max-width: 34rem;
    margin: 0;
    color: #f6f8fc !important;
    font-family: 'Outfit', sans-serif;
    font-size: clamp(3.2rem, 6.3vw, 6.2rem) !important;
    font-weight: 600;
    letter-spacing: -.08em;
    line-height: .92;
}

.metrora-product-hero h1 em {
    color: #a9c1ff;
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: .98em;
    font-weight: 400;
    letter-spacing: -.055em;
}

.metrora-product-hero p {
    max-width: 35rem;
    margin: 2rem 0 1.55rem;
    color: #b9c5d6 !important;
    font-size: 1.03rem;
    line-height: 1.75;
}

.metrora-product-pills { gap: .55rem; }
.metrora-product-pill { padding: .58rem .78rem; }

.metrora-command-surface {
    z-index: 1;
    align-self: end;
    width: min(100%, 31rem);
    margin-left: auto;
    border: 1px solid rgba(165, 184, 220, .24) !important;
    border-radius: 1rem !important;
    background: rgba(11, 17, 27, .8) !important;
    box-shadow: 0 20px 55px rgba(0, 0, 0, .24) !important;
    backdrop-filter: blur(16px);
    animation: metrora-rise .8s .12s ease both;
}

.metrora-visual-header,
.metrora-visual-footer {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    color: #93a1b5 !important;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
}

.metrora-visual-status { color: #7ee0d0 !important; }
.metrora-visual-metric { color: #f7f9fc !important; font-size: 2.3rem; letter-spacing: -.06em; }
.metrora-visual-metric small { margin-left: .48rem; color: #7ee0d0; font-size: .73rem; letter-spacing: 0; }

.metrora-line-visual {
    position: relative;
    height: 11rem;
    margin: 1.8rem 0 1.05rem;
    overflow: hidden;
    border-top: 1px solid rgba(165, 184, 220, .16);
    border-bottom: 1px solid rgba(165, 184, 220, .16) !important;
    background:
        repeating-linear-gradient(90deg, transparent 0, transparent calc(20% - 1px), rgba(165, 184, 220, .11) 20%),
        repeating-linear-gradient(0deg, transparent 0, transparent calc(33.333% - 1px), rgba(165, 184, 220, .10) 33.333%);
}

.metrora-line-visual svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.metrora-chart-area { fill: url(#metrora-area); }
.metrora-chart-trace {
    fill: none;
    stroke: #a9c1ff;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-width: 3;
    stroke-dasharray: 740;
    stroke-dashoffset: 740;
    animation: metrora-draw 2.5s .35s ease forwards;
}
.metrora-chart-point { fill: #7ee0d0; filter: drop-shadow(0 0 7px rgba(126, 224, 208, .56)); animation: metrora-pulse 2.8s 1.7s ease-in-out infinite; }
.metrora-visual-footer strong { color: #e8edf6 !important; font-size: .69rem; letter-spacing: 0; text-transform: none; }

.metrora-centered-caption {
    margin: 1rem 0 7.5rem !important;
    color: #8896aa !important;
    font-size: .76rem;
}

.metrora-product-section {
    max-width: 50rem;
    margin: 0 auto 3rem;
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    text-align: center;
}

.metrora-product-section h2,
.metrora-centered-section h3 {
    margin: .9rem 0 1rem;
    color: #f2f5fb !important;
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2.1rem, 3.5vw, 3.35rem) !important;
    font-weight: 600;
    letter-spacing: -.065em;
    line-height: 1.03;
}

.metrora-product-section > p,
.metrora-centered-section p {
    color: #aab6c7 !important;
    font-size: 1rem;
    line-height: 1.72;
}

.metrora-model-map {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0;
    margin: 0 0 1.6rem;
    border-top: 1px solid #273347;
    border-bottom: 1px solid #273347;
}

.metrora-model-node {
    position: relative;
    min-height: 13rem;
    padding: 1.35rem 1.35rem 1.55rem;
    border: 0 !important;
    border-right: 1px solid #273347 !important;
    border-radius: 0 !important;
    background: transparent !important;
}
.metrora-model-node:last-of-type { border-right: 0 !important; }
.metrora-model-node small { color: #9bb8ff; font-size: .62rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.metrora-model-node strong { display: block; margin: 1.65rem 0 .7rem; color: #edf2fb !important; font-family: 'Outfit', sans-serif; font-size: 1.02rem; letter-spacing: -.035em; }
.metrora-model-node p { margin: 0; color: #9ba8bb !important; font-size: .86rem; line-height: 1.65; }
.metrora-model-arrow { display: none; }
.metrora-model-caption { margin: 0 0 4.7rem !important; }

.metrora-product-principle {
    min-height: 12.8rem;
    margin-bottom: 5.2rem;
    padding: 1.15rem 0 0;
    border-top: 1px solid #273347;
}
.metrora-product-principle .icon,
.metrora-product-card .icon,
.metrora-output-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border: 1px solid rgba(155, 184, 255, .34) !important;
    border-radius: 50%;
    background: rgba(155, 184, 255, .09) !important;
    color: #b8ccff !important;
    font-size: .66rem;
    font-weight: 700;
}
.metrora-product-principle h3,
.metrora-product-card h3,
.metrora-product-output h3 {
    margin: 1.25rem 0 .72rem;
    color: #f0f4fa !important;
    font-family: 'Outfit', sans-serif;
    font-size: 1.16rem;
    letter-spacing: -.045em;
}
.metrora-product-principle p,
.metrora-product-card p,
.metrora-product-output p { color: #a7b4c5 !important; font-size: .91rem; line-height: 1.66; }

.metrora-product-story,
.metrora-evidence-visual {
    min-height: 17rem;
    margin-bottom: 4rem;
    padding: 2rem 0;
    border-top: 1px solid #273347;
    border-bottom: 1px solid #273347;
    background: transparent !important;
}
.metrora-product-story h3 { margin: .8rem 0 1rem; color: #f1f5fb !important; font-family: 'Outfit', sans-serif; font-size: 1.7rem; letter-spacing: -.06em; }
.metrora-product-story p { max-width: 32rem; color: #a8b5c5 !important; line-height: 1.7; }
.metrora-story-list { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.45rem; }
.metrora-story-list span { padding: .45rem .63rem; border: 1px solid #2c394e; border-radius: .35rem; color: #c2cddd; font-size: .74rem; }

.metrora-evidence-visual { padding: 1.55rem 1.65rem; border: 1px solid #29364a; border-radius: 1rem; background: linear-gradient(145deg, rgba(20, 30, 45, .72), rgba(12, 18, 27, .72)) !important; }
.metrora-evidence-title { display: flex; justify-content: space-between; margin-bottom: 1.45rem; color: #eaf0f9; font-size: .74rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.metrora-evidence-title b { color: #7ee0d0; font-size: .66rem; }
.metrora-evidence-row { display: grid; grid-template-columns: 8.6rem minmax(0, 1fr); gap: .7rem; align-items: center; margin: .8rem 0; color: #9ba8bb; font-size: .77rem; }
.metrora-evidence-row i { position: relative; display: block; height: .42rem; overflow: hidden; border-radius: 999px; background: #202c3d; }
.metrora-evidence-row i::before { position: absolute; inset: 0 auto 0 0; width: 100%; border-radius: inherit; background: linear-gradient(90deg, #7ee0d0, #9bb8ff); content: ''; transform-origin: left; animation: metrora-grow 1.1s ease both; }
.metrora-evidence-row:nth-child(3) i::before { animation-delay: .12s; }.metrora-evidence-row:nth-child(4) i::before { animation-delay: .24s; }.metrora-evidence-row:nth-child(5) i::before { animation-delay: .36s; }
.metrora-evidence-visual p { margin: 1.6rem 0 0; padding-top: 1rem; border-top: 1px solid #273347; color: #8090a5 !important; font-size: .76rem; }

.metrora-product-step,
.metrora-product-output,
.metrora-product-card,
.metrora-product-access,
.metrora-product-split {
    border-color: #273347 !important;
    background: transparent !important;
    box-shadow: none !important;
}
.metrora-product-step { max-width: 53rem; margin: 0 auto; padding: 1.5rem 0 !important; }
.metrora-product-step-number { color: #9bb8ff !important; font-family: 'Outfit', sans-serif; }
.metrora-product-step strong { color: #edf2fb !important; font-family: 'Outfit', sans-serif; }
.metrora-product-step p { color: #a8b5c5 !important; }
.metrora-centered-section { max-width: 50rem; margin: 5rem auto 2.8rem; padding-top: 0; border: 0; text-align: center; }
.metrora-product-output { padding: 1.3rem 0 0; border-top: 1px solid #273347 !important; }
.metrora-product-card { min-height: 14rem; padding: 1.25rem 0 0; border-top: 1px solid #273347 !important; }

.metrora-product-access,
.metrora-product-split { max-width: 50rem; margin: 3rem auto 1.35rem; padding: 2rem 0 !important; border-top: 1px solid #273347 !important; border-bottom: 1px solid #273347 !important; }
.metrora-product-access h3,
.metrora-product-split h3 { color: #f1f5fb !important; font-family: 'Outfit', sans-serif; font-size: 1.55rem; letter-spacing: -.055em; }
.metrora-product-access p,
.metrora-product-split p,
.metrora-product-split li { color: #a8b5c5 !important; line-height: 1.7; }
.metrora-access-note { max-width: 50rem; margin: 0 auto 1.2rem; border-color: #2b3a51 !important; background: rgba(155, 184, 255, .07) !important; color: #b5c1d0 !important; }
.metrora-access-note strong { color: #e8eef8 !important; }

.metrora-product-footer { margin-top: 6rem; padding-top: 1.4rem; border-top: 1px solid #222d3e; color: #718095 !important; font-size: .7rem; letter-spacing: .03em; }

@keyframes metrora-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes metrora-drift { from { transform: rotate(-7deg) translate3d(0, 0, 0); } to { transform: rotate(5deg) translate3d(-1.2rem, 1rem, 0); } }
@keyframes metrora-draw { to { stroke-dashoffset: 0; } }
@keyframes metrora-pulse { 0%, 100% { opacity: 1; r: 5; } 50% { opacity: .55; r: 7; } }
@keyframes metrora-grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

@media (max-width: 860px) {
    .block-container { padding: 1.35rem 1.15rem 4rem !important; }
    .metrora-product-nav { align-items: flex-start; }
    .metrora-product-nav-meta { display: none; }
    .st-key-product-page-nav { margin-bottom: 2.8rem; }
    .metrora-premium-hero { min-height: auto; }
    .metrora-command-surface { width: 100%; margin-top: 2.2rem; }
    .metrora-model-map { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metrora-model-node:nth-of-type(2) { border-right: 0 !important; }
    .metrora-model-node:nth-of-type(-n+2) { border-bottom: 1px solid #273347 !important; }
}

@media (max-width: 560px) {
    .metrora-product-hero h1 { font-size: 3.4rem !important; }
    .metrora-model-map { grid-template-columns: 1fr; }
    .metrora-model-node, .metrora-model-node:nth-of-type(2) { min-height: auto; border-right: 0 !important; border-bottom: 1px solid #273347 !important; }
    .metrora-model-node:last-of-type { border-bottom: 0 !important; }
    .metrora-evidence-row { grid-template-columns: 7.3rem minmax(0, 1fr); }
}
</style>
"""


PRODUCT_PAGE_V2_CSS = """
<style>
/* Product experience v2: one dark, restrained system with a visible analytical flow. */
:root {
    --metrora-bg: #070a0e;
    --metrora-surface: #0d1219;
    --metrora-surface-raised: #111821;
    --metrora-line-soft: #222c38;
    --metrora-text: #f3f6f8;
    --metrora-text-muted: #98a4b2;
    --metrora-blue-v2: #7da7ff;
    --metrora-teal-v2: #55d6c7;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 72% -8%, rgba(85, 214, 199, .09), transparent 30rem),
        radial-gradient(circle at 18% 18%, rgba(125, 167, 255, .08), transparent 36rem),
        var(--metrora-bg) !important;
}

.block-container {
    max-width: 1320px !important;
    padding: 1.65rem 2.5rem 7rem !important;
}

html { scroll-behavior: smooth; }

.metrora-product-section,
.metrora-premium-hero { scroll-margin-top: 1.5rem; }

.metrora-product-section:target,
.metrora-premium-hero:target {
    animation: metrora-section-focus .68s cubic-bezier(.2, .7, .2, 1) both;
}

.metrora-product-nav {
    min-height: 3.65rem;
    margin-bottom: .75rem;
}

.metrora-product-mark,
.metrora-product-mark .metrora-logo {
    width: 2.8rem;
    height: 2.8rem;
}

.metrora-product-name {
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: 1.12rem;
    letter-spacing: -.04em;
}

.metrora-product-subtitle { color: #8491a1 !important; }
.metrora-product-nav-meta span {
    border: 0 !important;
    background: transparent !important;
    color: #8592a3 !important;
}

.st-key-product-page-nav {
    width: min(100%, 35rem);
    margin: 0 auto 4.8rem;
    border-bottom: 1px solid var(--metrora-line-soft) !important;
}

.st-key-product-page-nav [data-testid="stButton"] button,
.metrora-page-link {
    min-height: 2.85rem !important;
    color: #798594 !important;
    font-size: .8rem;
}

.st-key-product-page-nav [data-testid="stButton"] button:hover,
.metrora-page-link {
    color: var(--metrora-text) !important;
}

.metrora-page-link { border-bottom-color: var(--metrora-teal-v2) !important; }

.metrora-premium-hero {
    position: relative;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 25rem), 1fr));
    align-items: center;
    gap: clamp(2.25rem, 4cqw, 4.5rem);
    min-height: 39rem;
    margin: 0 auto 2.4rem;
    padding: clamp(3rem, 6vw, 6rem) clamp(2rem, 6vw, 6rem) !important;
    overflow: hidden;
    border: 1px solid rgba(126, 145, 170, .20) !important;
    border-radius: 1.6rem !important;
    background:
        linear-gradient(120deg, rgba(125, 167, 255, .075), transparent 42%),
        linear-gradient(155deg, #0d131b 0%, #080c11 60%, #0b1118 100%) !important;
    box-shadow: 0 35px 110px rgba(0, 0, 0, .44) !important;
}

.metrora-premium-hero::before {
    width: 34rem;
    height: 34rem;
    right: -13rem;
    top: -15rem;
    border: 1px solid rgba(85, 214, 199, .13);
    border-radius: 50%;
    background: radial-gradient(circle, rgba(85, 214, 199, .10), transparent 66%);
    animation: metrora-halo 18s ease-in-out infinite alternate;
}

.metrora-premium-hero::after {
    width: 26rem;
    height: 26rem;
    left: -16rem;
    bottom: -18rem;
    border: 1px solid rgba(125, 167, 255, .14);
    border-radius: 50%;
    transform: none;
}

.metrora-hero-orbit {
    position: absolute;
    z-index: -1;
    inset: 0;
    overflow: hidden;
    opacity: .44;
    pointer-events: none;
}

.metrora-hero-orbit svg { width: 100%; height: 100%; }
.metrora-hero-orbit path {
    fill: none;
    stroke: rgba(177, 198, 231, .23);
    stroke-width: 1;
    stroke-dasharray: 9 15;
    animation: metrora-orbit 22s linear infinite;
}
.metrora-hero-orbit path + path {
    stroke: rgba(85, 214, 199, .16);
    animation-direction: reverse;
    animation-duration: 28s;
}

.metrora-hero-copy {
    position: relative;
    z-index: 2;
    max-width: 35rem;
    animation: metrora-enter .7s cubic-bezier(.2,.7,.2,1) both;
}

.metrora-product-kicker {
    margin-bottom: 1.45rem;
    color: var(--metrora-teal-v2) !important;
}

.metrora-product-hero h1 {
    max-width: 38rem;
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: clamp(3.35rem, 6.2cqw, 5.65rem) !important;
    font-weight: 620;
    letter-spacing: -.075em;
    line-height: .96;
    text-wrap: balance;
}
.metrora-product-hero h1 > span { display: block; }

.metrora-product-hero h1 em {
    display: block;
    margin-top: .12em;
    color: #b9d0ff;
    font-family: 'DM Serif Display', Georgia, serif;
    font-weight: 400;
    letter-spacing: -.045em;
}

.metrora-product-hero p {
    max-width: 34rem;
    margin: 2rem 0 1.7rem;
    color: #aab5c2 !important;
    font-size: 1.05rem;
    line-height: 1.76;
}

.metrora-product-pill {
    border-color: rgba(144, 166, 198, .2) !important;
    background: rgba(14, 20, 29, .68) !important;
    color: #a8b4c3 !important;
}

.metrora-command-surface {
    position: relative;
    z-index: 2;
    align-self: center;
    width: 100%;
    margin: 0;
    padding: 1.35rem !important;
    border: 1px solid rgba(137, 160, 192, .24) !important;
    border-radius: 1.1rem !important;
    background: rgba(9, 14, 20, .88) !important;
    box-shadow: 0 24px 70px rgba(0, 0, 0, .34) !important;
    backdrop-filter: blur(18px);
    animation: metrora-command-enter .85s .12s cubic-bezier(.2,.7,.2,1) both;
}

.metrora-visual-status {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    color: #84e3d8 !important;
}
.metrora-visual-status i {
    width: .38rem;
    height: .38rem;
    border-radius: 50%;
    background: var(--metrora-teal-v2);
    box-shadow: 0 0 0 4px rgba(85, 214, 199, .09);
    animation: metrora-status 3.2s ease-in-out infinite;
}

.metrora-visual-metric {
    margin-top: .8rem;
    color: var(--metrora-text) !important;
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: clamp(2rem, 3.6vw, 3rem);
}
.metrora-visual-metric small {
    color: #8d99a8 !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
}

.metrora-line-visual {
    height: 11.5rem;
    margin: 1.35rem 0 1rem;
    border-color: rgba(137, 160, 192, .15) !important;
    background:
        repeating-linear-gradient(90deg, transparent 0, transparent calc(20% - 1px), rgba(143, 163, 190, .08) 20%),
        repeating-linear-gradient(0deg, transparent 0, transparent calc(33.333% - 1px), rgba(143, 163, 190, .07) 33.333%);
}

.metrora-chart-trace {
    stroke: var(--metrora-teal-v2);
    stroke-width: 2.5;
    stroke-dasharray: 1800;
    stroke-dashoffset: 1800;
    filter: drop-shadow(0 0 5px rgba(85, 214, 199, .25));
    animation: metrora-draw-v2 2.4s .45s ease forwards;
}
.metrora-chart-area { opacity: 0; animation: metrora-area-in .7s 1.55s ease forwards; }

.metrora-visual-footer strong { color: #dfe7f1 !important; font-size: .69rem; }

.metrora-command-flow {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr) 1.5rem) minmax(0, 1fr);
    align-items: stretch;
    margin-top: 1.25rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(137, 160, 192, .16);
}
.metrora-command-node {
    min-width: 0;
    padding: .72rem;
    border-radius: .7rem;
    background: #0e151e;
}
.metrora-command-node i {
    display: inline-grid;
    width: 1.45rem;
    height: 1.45rem;
    margin-bottom: .7rem;
    place-items: center;
    border-radius: .42rem;
    background: rgba(125, 167, 255, .12);
    color: #a9c2f4;
    font-size: .55rem;
    font-style: normal;
    font-weight: 800;
}
.metrora-command-node span,
.metrora-command-node b { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.metrora-command-node span { color: #778495; font-size: .58rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.metrora-command-node b { margin-top: .28rem; color: #dfe6ef; font-size: .67rem; font-weight: 650; }
.metrora-command-node.is-ready { background: rgba(85, 214, 199, .045); }
.metrora-command-node.is-ready i { background: rgba(85, 214, 199, .12); color: #8be4da; }
.metrora-command-node.is-ready span { color: #91cfc8; }
.metrora-command-node.is-current { background: rgba(85, 214, 199, .09); }
.metrora-command-node.is-current i { background: rgba(85, 214, 199, .18); color: #c4fff7; }
.metrora-command-link { position: relative; min-width: 0; }
.metrora-command-link::before {
    position: absolute;
    top: 50%;
    right: .1rem;
    left: .1rem;
    height: 1px;
    background: #2b3746;
    content: '';
}
.metrora-command-link span {
    position: absolute;
    top: calc(50% - 2px);
    left: .1rem;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--metrora-teal-v2);
    box-shadow: 0 0 8px rgba(85, 214, 199, .55);
    animation: metrora-flow-dot 4.4s ease-in-out infinite;
}

.st-key-product_demo_hero,
.st-key-product_workflow_hero { margin-top: .55rem; }
.st-key-product_workflow_hero button {
    border-color: #2a3542 !important;
    background: #0d131b !important;
    color: #dbe3ed !important;
}

.metrora-hero-secondary-link {
    display: inline-flex;
    width: 100%;
    min-height: 2.5rem;
    align-items: center;
    justify-content: center;
    border: 1px solid #2a3542;
    border-radius: .58rem;
    background: #0d131b;
    color: #dbe3ed !important;
    font-size: .84rem;
    font-weight: 650;
    text-decoration: none !important;
    transition: border-color .18s ease, background .18s ease, transform .18s ease;
}

.metrora-hero-secondary-link:hover {
    border-color: #3c526d;
    background: #111b26;
    transform: translateY(-1px);
}

.metrora-centered-caption { color: #738091 !important; }
.metrora-product-section { margin: 8rem auto 3.4rem; }
.metrora-product-section-kicker { color: var(--metrora-teal-v2) !important; }
.metrora-product-section h2 {
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: clamp(2.5rem, 4.7vw, 4.8rem) !important;
    letter-spacing: -.075em;
    line-height: 1.02;
}
.metrora-product-section > p { color: #9ca8b6 !important; font-size: 1rem; }

.metrora-model-map {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    align-items: stretch;
    gap: 1px;
    margin: 3.5rem auto 0;
    overflow: hidden;
    border: 1px solid var(--metrora-line-soft) !important;
    border-radius: 1rem;
    background: var(--metrora-line-soft) !important;
}
.metrora-model-node {
    position: relative;
    min-width: 0;
    min-height: 12rem;
    padding: 1.75rem clamp(1rem, 1.6vw, 1.4rem) !important;
    border: 0 !important;
    background: linear-gradient(155deg, #0d151e, #0a1118) !important;
}
.metrora-model-node small {
    display: block;
    color: var(--metrora-teal-v2) !important;
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}
.metrora-model-node strong {
    display: block;
    margin-top: 1.55rem;
    color: #edf2f7 !important;
    font-family: 'Manrope', sans-serif;
    font-size: 1rem;
    line-height: 1.35;
    overflow-wrap: normal;
    word-break: normal;
}
.metrora-model-node p {
    margin: .8rem 0 0;
    color: #8f9ba9 !important;
    font-size: .82rem;
    line-height: 1.62;
    overflow-wrap: normal;
    word-break: normal;
}
.metrora-model-caption {
    margin: 2.2rem auto 0 !important;
    padding: 0 1rem !important;
    border: 0 !important;
    line-height: 1.65;
}

.metrora-access-note {
    min-height: 4.8rem;
    margin: 2.1rem auto 1.2rem !important;
    padding: 1.15rem 1.35rem !important;
    border-radius: .82rem !important;
    line-height: 1.65;
}

.metrora-scenario-card {
    min-height: 15.25rem;
    padding: 1.45rem 1.35rem 1.35rem;
    border-top: 1px solid #293544;
    background: linear-gradient(180deg, rgba(17, 24, 33, .58), transparent);
}
.metrora-scenario-card,
.metrora-product-step,
.metrora-product-output,
.metrora-product-principle,
.metrora-product-card,
.metrora-product-story,
.metrora-evidence-visual,
.metrora-product-split,
.metrora-access-note {
    animation: metrora-section-enter .62s cubic-bezier(.2, .7, .2, 1) both;
}
.metrora-scenario-card small {
    color: var(--metrora-teal-v2);
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}
.metrora-scenario-card h3 {
    margin: 1rem 0 .75rem;
    color: #eef3f7 !important;
    font-family: 'Manrope', sans-serif;
    font-size: 1.25rem;
}
.metrora-scenario-card p {
    margin: 0 0 1.1rem;
    color: #98a5b4 !important;
    font-size: .88rem;
    line-height: 1.65;
}
.metrora-scenario-card span {
    display: block;
    color: #c6d0dc;
    font-size: .74rem;
    line-height: 1.55;
}
.st-key-product_demo_scenario_healthy,
.st-key-product_demo_scenario_quality_risk,
.st-key-product_demo_scenario_forecast_risk { margin-top: .75rem; }
.st-key-product_demo_scenario_healthy button,
.st-key-product_demo_scenario_quality_risk button,
.st-key-product_demo_scenario_forecast_risk button {
    border-color: #2a3542 !important;
    background: #101925 !important;
    color: #dbe3ed !important;
    box-shadow: none !important;
}
.st-key-product_demo_scenario_healthy button:hover,
.st-key-product_demo_scenario_quality_risk button:hover,
.st-key-product_demo_scenario_forecast_risk button:hover {
    border-color: #3c526d !important;
    background: #142131 !important;
}

.metrora-product-principle { padding-top: 1.5rem; border-top-color: #27313e; }
.metrora-product-principle .icon { background: rgba(85, 214, 199, .11); color: #80ddd3 !important; }
.metrora-product-story { padding: 1rem 2rem 1rem 0; }
.metrora-evidence-visual {
    border-color: #26313e !important;
    background: linear-gradient(145deg, rgba(17, 24, 33, .92), rgba(11, 16, 23, .86)) !important;
    box-shadow: 0 22px 60px rgba(0, 0, 0, .2);
}
.metrora-evidence-title b { color: var(--metrora-teal-v2); }
.metrora-evidence-row i::before { background: linear-gradient(90deg, var(--metrora-teal-v2), var(--metrora-blue-v2)); }

.metrora-native-bridge {
    margin: 8rem auto 2rem;
    padding: clamp(2.2rem, 5vw, 4.5rem);
    border: 1px solid #253241;
    border-radius: 1.35rem;
    background:
        radial-gradient(circle at 84% 12%, rgba(85, 214, 199, .08), transparent 20rem),
        linear-gradient(140deg, rgba(16, 24, 34, .94), rgba(8, 13, 19, .9));
}
.metrora-native-bridge header {
    max-width: 59rem;
    margin: 0 auto 3rem;
    text-align: center;
}
.metrora-native-bridge header > span {
    color: var(--metrora-teal-v2);
    font-size: .66rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
}
.metrora-native-bridge h2 {
    max-width: 55rem;
    margin: 1rem auto 1.3rem;
    color: #f1f5f8 !important;
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: clamp(2.35rem, 4.4vw, 4.35rem) !important;
    letter-spacing: -.065em;
    line-height: 1.02;
}
.metrora-native-bridge header p {
    max-width: 50rem;
    margin: 0 auto;
    color: #98a5b4 !important;
    line-height: 1.75;
}
.metrora-native-lanes {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1px;
    overflow: hidden;
    border: 1px solid #263444;
    border-radius: 1rem;
    background: #263444;
}
.metrora-native-lane {
    min-width: 0;
    min-height: 17rem;
    padding: clamp(1.7rem, 3vw, 2.25rem);
    background: #0c121a;
}
.metrora-native-lane.metrora { background: linear-gradient(145deg, #101a25, #0d151e); }
.metrora-native-lane small {
    color: #718197;
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.metrora-native-lane.metrora small { color: #6ed9cc; }
.metrora-native-lane h3 {
    margin: .85rem 0 1.1rem;
    color: #eaf0f6 !important;
    font-family: 'Manrope', sans-serif;
}
.metrora-native-lane ul {
    display: grid;
    gap: .65rem;
    margin: 0;
    padding-left: 1.15rem;
    color: #98a6b6;
    font-size: .82rem;
    line-height: 1.55;
}
.metrora-native-lane li { padding-left: .2rem; }
.metrora-accountability-loop {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin: 1.5rem auto 0;
    border-top: 1px solid #273646;
    border-bottom: 1px solid #273646;
}
.metrora-accountability-loop div {
    position: relative;
    min-width: 0;
    padding: 1.35rem 1.75rem;
    text-align: center;
}
.metrora-accountability-loop div:not(:last-child)::after {
    position: absolute;
    top: 50%;
    right: -.7rem;
    width: 1.4rem;
    height: 1px;
    background: linear-gradient(90deg, #34465a, #55d6c7);
    content: '';
    transform: translateY(-50%);
}
.metrora-accountability-loop span {
    display: block;
    color: #68d9cc;
    font-size: .58rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.metrora-accountability-loop strong {
    display: block;
    margin-top: .55rem;
    color: #dfe7f0;
    font-size: .8rem;
}

@keyframes metrora-enter {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes metrora-section-enter {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes metrora-section-focus {
    0% { filter: brightness(.9); }
    55% { filter: brightness(1.08); }
    100% { filter: brightness(1); }
}
@keyframes metrora-command-enter {
    from { opacity: 0; transform: translate3d(18px, 10px, 0) scale(.985); }
    to { opacity: 1; transform: translate3d(0, 0, 0) scale(1); }
}
@keyframes metrora-orbit { to { stroke-dashoffset: -240; } }
@keyframes metrora-halo {
    from { transform: translate3d(0, 0, 0) scale(.96); opacity: .72; }
    to { transform: translate3d(-1.5rem, 1rem, 0) scale(1.06); opacity: 1; }
}
@keyframes metrora-draw-v2 { to { stroke-dashoffset: 0; } }
@keyframes metrora-area-in { to { opacity: 1; } }
@keyframes metrora-status { 50% { opacity: .45; box-shadow: 0 0 0 7px rgba(85, 214, 199, .04); } }
@keyframes metrora-flow-dot { 0%, 12% { left: .1rem; opacity: 0; } 30%, 72% { opacity: 1; } 88%, 100% { left: calc(100% - 5px); opacity: 0; } }

@media (max-width: 980px) {
    .metrora-premium-hero { min-height: auto; }
    .metrora-command-surface { max-width: 44rem; }
    .metrora-model-map { grid-template-columns: repeat(6, minmax(0, 1fr)); }
    .metrora-model-node { grid-column: span 2; }
    .metrora-model-node:nth-child(4) { grid-column: 2 / span 2; }
    .metrora-model-node:nth-child(5) { grid-column: 4 / span 2; }
    .metrora-model-node { min-height: 9rem; }
}

@media (max-width: 620px) {
    .block-container { padding: 1.1rem 1rem 4.5rem !important; }
    .metrora-premium-hero { padding: 2.4rem 1.35rem !important; border-radius: 1.2rem !important; }
    .metrora-product-hero h1 { font-size: clamp(3rem, 15vw, 4.4rem) !important; }
    .metrora-command-flow { grid-template-columns: 1fr; gap: .5rem; }
    .metrora-command-link { display: none; }
    .metrora-product-section { margin-top: 6rem; }
    .metrora-model-map { grid-template-columns: 1fr; }
    .metrora-model-node {
        grid-column: 1 / -1 !important;
        min-height: auto;
        padding: 1.4rem 1.25rem !important;
        border: 0 !important;
    }
    .metrora-native-lanes { grid-template-columns: 1fr; }
    .metrora-accountability-loop { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metrora-accountability-loop div:nth-child(2)::after { content: none; }
}

@media (prefers-reduced-motion: reduce) {
    .metrora-hero-orbit path,
    .metrora-premium-hero::before,
    .metrora-hero-copy,
    .metrora-command-surface,
    .metrora-chart-trace,
    .metrora-chart-area,
    .metrora-visual-status i,
    .metrora-command-link span,
    .metrora-scenario-card,
    .metrora-product-step,
    .metrora-product-output,
    .metrora-product-principle,
    .metrora-product-card,
    .metrora-product-story,
    .metrora-evidence-visual,
    .metrora-product-split,
    .metrora-access-note { animation: none !important; }
    .metrora-chart-trace { stroke-dashoffset: 0 !important; }
    .metrora-chart-area { opacity: 1 !important; }
}

.metrora-live-connections {
    max-width: 76rem;
    margin: 8rem auto 1rem;
    padding: 0;
}

.metrora-live-connections > header {
    max-width: 53rem;
    margin: 0 auto 3rem;
    text-align: center;
}

.metrora-live-connections > header span {
    color: #55d6c7;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.metrora-live-connections h2 {
    max-width: 49rem;
    margin: .9rem auto 1.15rem;
    color: #f3f6fa;
    font-family: Manrope, sans-serif;
    font-size: clamp(2.1rem, 4vw, 4.2rem);
    letter-spacing: -.055em;
    line-height: 1.02;
}

.metrora-live-connections header p {
    max-width: 47rem;
    margin: 0 auto;
    color: #9aa7b8;
    font-size: 1rem;
    line-height: 1.7;
}

.metrora-connection-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1px;
    overflow: hidden;
    border: 1px solid #273441;
    border-radius: 1rem;
    background: #273441;
}

.metrora-connection-grid article {
    display: flex;
    min-width: 0;
    min-height: 13rem;
    flex-direction: column;
    padding: 1.65rem 1.4rem;
    background: linear-gradient(180deg, rgba(18,28,39,.66), rgba(10,16,23,.12));
}

.metrora-connection-grid small {
    color: #7da7ff;
    font-size: .66rem;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
}

.metrora-connection-grid h3 {
    margin: 1.6rem 0 .7rem;
    color: #eef3f8;
    font-size: 1.05rem;
}

.metrora-connection-grid p {
    margin: 0;
    color: #8f9dad;
    font-size: .82rem;
    line-height: 1.65;
    overflow-wrap: anywhere;
}

.metrora-connection-footnote {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .8rem;
    max-width: 62rem;
    margin: 1.5rem auto 0 !important;
    padding: 1rem 1.2rem !important;
    border: 1px solid #22303d;
    border-radius: .8rem;
    background: rgba(14, 22, 31, .7);
    color: #7f8c9c;
    font-size: .78rem;
    line-height: 1.6;
    text-align: left;
}

.metrora-connection-footnote strong {
    flex: 0 0 auto;
    color: #66d9cc;
    font-size: .64rem;
    letter-spacing: .1em;
    text-transform: uppercase;
}

.metrora-connection-footnote span {
    color: #8f9dac;
}

@media (max-width: 900px) {
    .metrora-connection-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metrora-live-connections { padding: 0 .5rem; }
}

@media (max-width: 600px) {
    .metrora-connection-grid { grid-template-columns: 1fr; }
    .metrora-connection-grid article { min-height: auto; }
    .metrora-connection-footnote {
        align-items: flex-start;
        flex-direction: column;
        padding: 1rem !important;
    }
}
</style>
"""


def _demo_scenario(scenario_id: str) -> dict[str, str]:
    """Return validated metadata for one guided scenario."""
    scenario = DEMO_SCENARIOS.get(scenario_id)
    if scenario is None:
        allowed = ", ".join(DEMO_SCENARIOS)
        raise IngestionError(f"Unknown demo scenario {scenario_id!r}; choose one of: {allowed}.")
    return scenario


def _demo_path(scenario_id: str = DEFAULT_DEMO_SCENARIO) -> Path:
    scenario = _demo_scenario(scenario_id)
    return _demo_supporting_path(scenario["billing"])


def _demo_supporting_path(filename: str) -> Path:
    """Return one of the checked-in supporting files used by the guided demo."""
    return resource_path("data", "demo", filename)


def _load_demo_planning_context(settings: Settings, scenario_id: str):
    """Load normalized budget and business context for a complete guided demo."""
    scenario = _demo_scenario(scenario_id)
    budget_path = _demo_supporting_path(scenario["budget"])
    business_path = _demo_supporting_path(scenario["business"])
    missing = [path.name for path in (budget_path, business_path) if not path.is_file()]
    if missing:
        raise IngestionError("The demo support file(s) are missing: " + ", ".join(missing))
    try:
        budget = normalize_budget_dataframe(
            load_table(budget_path, max_bytes=settings.max_upload_mb * 1024 * 1024).dataframe
        )
        business_metrics = normalize_business_metrics(
            load_table(business_path, max_bytes=settings.max_upload_mb * 1024 * 1024).dataframe
        )
    except (IngestionError, ValueError) as exc:
        raise IngestionError(f"The demo planning context could not be prepared: {exc}") from exc
    return budget, business_metrics


def _set_product_page(page: str) -> None:
    """Store the selected public product page for the next Streamlit rerun."""
    if page in PUBLIC_PAGES:
        set_product_route(page)


def build_demo_artifacts(
    settings: Settings,
    scenario_id: str = DEFAULT_DEMO_SCENARIO,
) -> tuple[
    LoadedTable,
    DataProfile,
    dict[str, str | None],
    NormalizedTable,
    QualityReport,
]:
    """Load and prepare one deterministic billing scenario for a guided session."""
    demo_path = _demo_path(scenario_id)
    if not demo_path.is_file():
        raise IngestionError(
            "The demo billing file is missing. Run data/demo/generate_demo_data.py first."
        )

    loaded_table = load_table(
        demo_path,
        max_bytes=settings.max_upload_mb * 1024 * 1024,
    )
    profile = profile_table(loaded_table)
    review = suggest_mappings(profile)
    suggested_mapping = {
        suggestion.canonical_field: suggestion.source_column for suggestion in review.suggestions
    }
    try:
        accepted_mapping = validate_mapping(suggested_mapping, review.source_columns)
        normalized = normalize_billing_table(loaded_table, accepted_mapping)
    except (MappingValidationError, ValueError, KeyError) as exc:
        raise IngestionError(f"The demo billing file could not be prepared: {exc}") from exc

    report = run_quality_checks(loaded_table, normalized)
    return loaded_table, profile, accepted_mapping, normalized, report


def activate_demo_session(
    settings: Settings,
    scenario_id: str = DEFAULT_DEMO_SCENARIO,
    *,
    persist_route: bool = True,
) -> None:
    """Start a local guided demo with real Metrora analysis state."""
    scenario = _demo_scenario(scenario_id)
    loaded_table, profile, accepted_mapping, normalized, report = build_demo_artifacts(
        settings,
        scenario_id,
    )
    budget, business_metrics = _load_demo_planning_context(settings, scenario_id)
    reset_workspace_state()
    source_key = source_key_for(loaded_table, profile)
    st.session_state.update(
        {
            "demo_authenticated": True,
            "demo_mode": True,
            "demo_scenario": scenario_id,
            "demo_user_email": "demo@metrora.local",
            "demo_workspace": f"Metrora / {scenario['label']}",
            "loaded_table": loaded_table,
            "data_profile": profile,
            "mapping_source_key": source_key,
            "column_mapping": accepted_mapping,
            "normalized_table": normalized,
            "normalized_source_key": source_key,
            "quality_report": report,
            "quality_source_key": source_key,
            "budget_table": budget,
            "budget_upload_key": f"demo:{scenario['budget']}",
            "business_metrics_table": business_metrics,
            "business_upload_key": f"demo:{scenario['business']}",
            "auto_attempted_source_key": source_key,
            "workspace_page": "Home" if report.ready_for_analysis else "Advanced",
            "auto_analysis_message": (
                "Guided scenario ready. Metrora mapped, normalized, and checked the source "
                "automatically."
                if report.ready_for_analysis
                else "Metrora stopped the analysis because the guided source contains "
                "blocking quality issues. Review the highlighted checks before using its totals."
            ),
        }
    )
    if persist_route:
        set_workspace_route(
            "Home" if report.ready_for_analysis else "Advanced",
            scenario_id=scenario_id,
        )


def _demo_preview_facts(settings: Settings) -> dict[str, object]:
    """Calculate the public demo visual from the checked-in synthetic source."""
    cache_key = "_metrora_product_demo_facts"
    cached = st.session_state.get(cache_key)
    if isinstance(cached, dict):
        return cached

    loaded, profile, _, normalized, report = build_demo_artifacts(settings)
    dataframe = normalized.dataframe.copy()
    total = float(dataframe["cost"].sum())
    currencies = dataframe["currency"].dropna().astype(str).unique().tolist()
    currency = currencies[0] if len(currencies) == 1 else "Mixed"
    total_label = f"${total:,.0f}" if currency == "USD" else f"{currency} {total:,.0f}"

    daily = dataframe.groupby("usage_date", as_index=False)["cost"].sum().sort_values("usage_date")
    values = daily["cost"].astype(float).tolist()
    minimum = min(values)
    span = max(max(values) - minimum, 1.0)
    width, top, bottom = 530.0, 24.0, 150.0
    points: list[str] = []
    for index, value in enumerate(values):
        x = width * index / max(len(values) - 1, 1)
        y = bottom - ((value - minimum) / span) * (bottom - top)
        points.append(f"{x:.1f} {y:.1f}")
    chart_path = "M" + " L".join(points)
    area_path = f"{chart_path} L{width:.1f} 176 L0 176 Z"

    services = (
        dataframe.groupby("service", as_index=False)["cost"]
        .sum()
        .sort_values("cost", ascending=False)
    )
    lead_service = str(services.iloc[0]["service"])
    lead_share = float(services.iloc[0]["cost"]) / total if total else 0.0
    difference = report.reconciliation.absolute_difference or 0.0
    facts: dict[str, object] = {
        "source": loaded.source_name,
        "rows": profile.row_count,
        "total": total_label,
        "currency": currency,
        "lead_service": lead_service,
        "lead_share": lead_share,
        "difference": difference,
        "chart_path": chart_path,
        "area_path": area_path,
        "date_start": str(daily["usage_date"].min().date()),
        "date_end": str(daily["usage_date"].max().date()),
    }
    st.session_state[cache_key] = facts
    return facts


def _render_brand_header() -> None:
    """Render a compact product header without competing controls."""
    st.markdown(
        f"""
        <header class="metrora-product-nav">
            <div class="metrora-product-brand">
                <span class="metrora-product-mark">{METRORA_LOGO_SVG}</span>
                <div>
                    <div class="metrora-product-name">Metrora</div>
                    <div class="metrora-product-subtitle">Cloud FinOps intelligence</div>
                </div>
            </div>
            <div class="metrora-product-nav-meta">
                <span>Local-first</span>
                <span>Evidence-led</span>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def _render_page_intro(
    kicker: str,
    title: str,
    copy: str,
    *,
    anchor_id: str | None = None,
) -> None:
    st.markdown(
        f"""
        <section{f' id="{anchor_id}"' if anchor_id else ""} class="metrora-product-section">
            <div class="metrora-product-section-kicker">{kicker}</div>
            <h2>{title}</h2>
            <p>{copy}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_model_map() -> None:
    """Show the calculation-to-explanation model in a compact visual map."""
    st.markdown(
        """
        <div class="metrora-model-map" role="list" aria-label="Metrora operating model">
            <div class="metrora-model-node" role="listitem">
                <small>01 / Source</small>
                <strong>Billing export</strong>
                <p>Provider rows, budgets, ownership, and business metrics.</p>
            </div>
            <div class="metrora-model-node" role="listitem">
                <small>02 / Model</small>
                <strong>Trusted cost model</strong>
                <p>Mapped, normalized, reconciled, and quality-checked data.</p>
            </div>
            <div class="metrora-model-node" role="listitem">
                <small>03 / Insight</small>
                <strong>Decision signals</strong>
                <p>Trends, drivers, forecasts, anomalies, and coverage.</p>
            </div>
            <div class="metrora-model-node" role="listitem">
                <small>04 / Action</small>
                <strong>Owned decision</strong>
                <p>Owner, due date, disposition, and evidence in one operating record.</p>
            </div>
            <div class="metrora-model-node" role="listitem">
                <small>05 / Outcome</small>
                <strong>Verified value</strong>
                <p>Before-and-after actuals prove what changed after implementation.</p>
            </div>
        </div>
        <p class="metrora-centered-caption metrora-model-caption">
            Calculated first. Explained second. Traceable throughout.
        </p>
        """,
        unsafe_allow_html=True,
    )


def _render_native_bridge() -> None:
    """Explain why Metrora complements provider-native cost products."""
    st.markdown(
        """
        <section class="metrora-native-bridge metrora-scroll-reveal">
            <header>
                <span>Designed to complement the cloud</span>
                <h2>Native tools find opportunities. Metrora closes the loop.</h2>
                <p>AWS, Azure, and Google Cloud remain the best source for provider-specific
                billing and resource recommendations. Metrora gives finance and engineering a
                neutral place to validate the evidence, assign the decision, and verify the
                result across providers.</p>
            </header>
            <div class="metrora-native-lanes">
                <article class="metrora-native-lane">
                    <small>Native cloud platforms</small>
                    <h3>Provider depth</h3>
                    <ul>
                        <li>Detailed billing and resource telemetry</li>
                        <li>Provider-specific optimization recommendations</li>
                        <li>Commitment, rightsizing, and service expertise</li>
                    </ul>
                </article>
                <article class="metrora-native-lane metrora">
                    <small>Metrora decision layer</small>
                    <h3>Cross-provider accountability</h3>
                    <ul>
                        <li>Reconciled evidence and one provider-neutral cost model</li>
                        <li>Budget, ownership, and business-unit context</li>
                        <li>Owner, decision, due date, rejection reason, and verified outcome</li>
                    </ul>
                </article>
            </div>
            <div class="metrora-accountability-loop" aria-label="Decision accountability loop">
                <div><span>01</span><strong>Detect</strong></div>
                <div><span>02</span><strong>Prove</strong></div>
                <div><span>03</span><strong>Assign</strong></div>
                <div><span>04</span><strong>Verify</strong></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_overview(settings: Settings) -> None:
    facts = _demo_preview_facts(settings)
    st.markdown(
        f"""
        <section id="metrora-overview" class="metrora-product-hero metrora-premium-hero">
            <div class="metrora-hero-orbit" aria-hidden="true">
                <svg viewBox="0 0 1200 560" preserveAspectRatio="none">
                    <path d="M-40 108 C250 22 410 178 650 94 S1030 24 1260 132" />
                    <path d="M-80 164 C210 76 430 234 700 142 S1030 92 1280 196" />
                </svg>
            </div>
            <div class="metrora-hero-copy">
                <div class="metrora-product-kicker">Metrora / FinOps decision system</div>
                <h1><span>Know what changed.</span> <em>Prove the number.</em></h1>
                <p>
                    Turn billing exports, budgets, ownership data, and business metrics into one
                    calm operating view—then keep every finding traceable to source.
                </p>
                <div class="metrora-product-pills">
                    <span class="metrora-product-pill">One-click guided analysis</span>
                    <span class="metrora-product-pill">Evidence before AI</span>
                </div>
            </div>
            <div class="metrora-hero-visual metrora-command-surface">
                <div class="metrora-visual-header">
                    <span>Guided workspace / live sample</span>
                    <span class="metrora-visual-status"><i></i> Model ready</span>
                </div>
                <div class="metrora-visual-metric">{facts["total"]}
                    <small>{facts["rows"]:,} reconciled rows</small>
                </div>
                <div class="metrora-visual-chart metrora-line-visual" aria-label="Calculated synthetic-demo spend trend">
                    <svg viewBox="0 0 530 176" preserveAspectRatio="none" aria-hidden="true">
                        <defs>
                            <linearGradient id="metrora-area" x1="0" x2="0" y1="0" y2="1">
                                <stop offset="0" stop-color="#55d6c7" stop-opacity=".30" />
                                <stop offset="1" stop-color="#55d6c7" stop-opacity="0" />
                            </linearGradient>
                        </defs>
                        <path class="metrora-chart-area" d="{facts["area_path"]}" />
                        <path class="metrora-chart-trace" d="{facts["chart_path"]}" />
                    </svg>
                </div>
                <div class="metrora-visual-footer">
                    <span>Largest service driver</span>
                    <strong>{escape(str(facts["lead_service"]))} / {facts["lead_share"]:.0%} of spend</strong>
                </div>
                <div class="metrora-command-flow" aria-label="Metrora analysis flow">
                    <div class="metrora-command-node is-ready"><i>01</i><span>Source</span><b>{escape(str(facts["source"]))}</b></div>
                    <div class="metrora-command-link"><span></span></div>
                    <div class="metrora-command-node is-ready"><i>02</i><span>Model</span><b>{escape(str(facts["currency"]))} {float(facts["difference"]):,.2f} difference</b></div>
                    <div class="metrora-command-link"><span></span></div>
                    <div class="metrora-command-node is-ready is-current"><i>03</i><span>Decision</span><b>Review {escape(str(facts["lead_service"]))}</b></div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    button_columns = st.columns([1, 1.05, 1.05, 1], gap="small")
    with button_columns[1]:
        st.button(
            "Explore demo scenarios",
            type="primary",
            width="stretch",
            key="product_demo_hero",
            on_click=_set_product_page,
            args=("Demo",),
        )
    with button_columns[2]:
        st.markdown(
            '<a class="metrora-hero-secondary-link" '
            'href="https://github.com/ndomathoti16-create/Metrora/releases/latest" '
            'target="_blank" rel="noopener">Download for Windows</a>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<p class="metrora-centered-caption">'
        f"Calculated from {facts['rows']:,} synthetic billing rows. No cloud connection or "
        "credentials required."
        "</p>",
        unsafe_allow_html=True,
    )

    _render_page_intro(
        "A visible operating loop",
        "From export to action, without losing the evidence.",
        "Metrora automates the normal path, keeps the workflow legible, and opens the technical "
        "detail only when a reviewer needs it.",
    )
    _render_model_map()
    st.markdown(
        """
        <section class="metrora-live-connections metrora-scroll-reveal" id="metrora-connections">
            <header>
                <span>Live cost data</span>
                <h2>Connect the exports you already schedule.</h2>
                <p>The desktop workspace imports the newest complete provider export, then
                applies the same mapping, reconciliation, quality, and decision pipeline used
                for every file.</p>
            </header>
            <div class="metrora-connection-grid" role="list" aria-label="Supported cost data sources">
                <article role="listitem"><small>01 / AWS</small><h3>Data Exports &amp; CUR</h3>
                <p>Read the latest complete CSV.GZ or Parquet batch from an S3 prefix through
                AWS SSO or an IAM role.</p></article>
                <article role="listitem"><small>02 / Azure</small><h3>Cost Management</h3>
                <p>Refresh recurring ActualCost or AmortizedCost exports from Blob Storage
                through Entra ID.</p></article>
                <article role="listitem"><small>03 / Google Cloud</small><h3>Cloud Billing</h3>
                <p>Query a BigQuery billing export with Application Default Credentials and
                include credits in effective cost.</p></article>
                <article role="listitem"><small>04 / Portable</small><h3>Files &amp; FOCUS</h3>
                <p>Open CSV, Excel, Parquet, or FOCUS-shaped exports from other cloud and
                technology providers.</p></article>
            </div>
            <p class="metrora-connection-footnote">
                <strong>Read-only by design</strong>
                <span>Metrora stores export locations and refresh history&mdash;not passwords,
                access keys, tokens, or cloud resource controls.</span>
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    _render_native_bridge()
    principles = [
        (
            "01",
            "Start with the signal",
            "See the position, movement, outlook, and exceptions that should be reviewed now.",
        ),
        (
            "02",
            "Keep the proof attached",
            "Mappings, quality checks, reconciliation, and source context remain one click away.",
        ),
        (
            "03",
            "Move the next decision forward",
            "Connect budgets and business metrics to forecasts, anomalies, and a concise brief.",
        ),
    ]
    columns = st.columns(3, gap="large")
    for column, (number, title, copy) in zip(columns, principles, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="metrora-product-principle">
                    <span class="icon">{number}</span>
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            """
            <div class="metrora-product-story">
                <div class="metrora-product-section-kicker">Designed for the handoff</div>
                <h3>A decision should travel with its evidence.</h3>
                <p>Finance, engineering, and FinOps teams see the same source-backed story -
                including the data caveats that change how confidently to act.</p>
                <div class="metrora-story-list">
                    <span>Mapped source fields</span><span>Reconciled totals</span>
                    <span>Visible caveats</span><span>Named next move</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="metrora-evidence-visual" aria-label="Evidence visual">
                <div class="metrora-evidence-title"><span>Decision evidence</span><b>Complete</b></div>
                <div class="metrora-evidence-row"><span>Spend movement</span><i style="width: 86%"></i></div>
                <div class="metrora-evidence-row"><span>Ownership coverage</span><i style="width: 72%"></i></div>
                <div class="metrora-evidence-row"><span>Budget context</span><i style="width: 58%"></i></div>
                <div class="metrora-evidence-row"><span>Business metric</span><i style="width: 42%"></i></div>
                <p>Every finding keeps its supporting inputs visible.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_pipeline() -> None:
    _render_page_intro(
        "The pipeline",
        "One defensible path from raw export to recommendation.",
        "Each stage turns uncertainty into a clear next action while keeping financial "
        "calculations deterministic.",
        anchor_id="metrora-workflow",
    )
    steps = [
        (
            "01",
            "Ingest",
            "Upload CSV, Excel, or Parquet and profile its shape, types, nulls, and duplicates.",
        ),
        (
            "02",
            "Map",
            "Review Metrora's column suggestions and correct the semantic fields that matter.",
        ),
        (
            "03",
            "Validate",
            "Normalize to a canonical model, reconcile source totals, and surface quality caveats.",
        ),
        (
            "04",
            "Explore",
            "Slice spend by service, account, department, project, environment, and region.",
        ),
        (
            "05",
            "Decide",
            "Forecast, investigate anomalies, connect business metrics, and export the brief.",
        ),
        (
            "06",
            "Verify",
            "Assign the owner, record the disposition, and measure the result against actuals.",
        ),
    ]
    for number, title, copy in steps:
        st.markdown(
            f"""
            <div class="metrora-product-step">
                <div class="metrora-product-step-number">{number}</div>
                <div><strong>{title}</strong><p>{copy}</p></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="metrora-centered-section">
            <h3>What the workflow produces</h3>
            <p>
                Each output gives the next team a clearer answer without losing the source context.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    outputs = [
        (
            "A",
            "Trusted cost model",
            "Normalized billing rows with mapping decisions, quality flags, and "
            "reconciliation context.",
        ),
        (
            "B",
            "Decision-ready analysis",
            "Trends, drivers, forecasts, anomalies, allocation coverage, and budget comparisons.",
        ),
        (
            "C",
            "Evidence-backed brief",
            "A concise explanation of what changed, why it matters, and what to investigate next.",
        ),
        (
            "D",
            "Decision record",
            "An accountable owner, disposition, due date, and actual verified outcome.",
        ),
    ]
    output_columns = st.columns(len(outputs), gap="large")
    for column, (mark, title, copy) in zip(output_columns, outputs, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="metrora-product-output">
                    <span class="metrora-output-mark">{mark}</span>
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_trust() -> None:
    _render_page_intro(
        "Trust by design",
        "Numbers first. Narrative second.",
        "Every value is calculated and checked before Metrora explains what it means.",
        anchor_id="metrora-evidence",
    )
    columns = st.columns(3, gap="medium")
    trust_cards = [
        (
            "01",
            "Deterministic calculations",
            "Financial values are computed by the analytical pipeline first. AI receives "
            "the results and supporting evidence only.",
        ),
        (
            "02",
            "Visible caveats",
            "Missing fields, duplicates, invalid values, and reconciliation differences "
            "remain visible instead of being hidden in a summary.",
        ),
        (
            "03",
            "Read-only access",
            "Cloud exports and native AWS recommendations are imported through least-privilege "
            "identities; Metrora does not change resources.",
        ),
    ]
    for column, (number, title, copy) in zip(columns, trust_cards, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="metrora-product-card">
                    <span class="icon">{number}</span>
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="metrora-product-split">
            <h3>Provider depth, neutral accountability</h3>
            <p>
                Use AWS, Azure, and Google Cloud for their native telemetry and optimization
                engines. Use Metrora to reconcile the cost story, connect it to business context,
                record what people decided, and verify the outcome from actual billing.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_access_panel(settings: Settings) -> None:
    st.markdown(
        """
        <div class="metrora-product-access">
            <h3>Choose the story you want to test</h3>
            <p>
                Each scenario opens the complete workspace with its billing, budget, and
                business context already connected.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(len(DEMO_SCENARIOS), gap="large")
    for column, (scenario_id, scenario) in zip(
        columns,
        DEMO_SCENARIOS.items(),
        strict=True,
    ):
        with column:
            st.markdown(
                f"""
                <article class="metrora-scenario-card">
                    <small>{escape(scenario["status"])}</small>
                    <h3>{escape(scenario["label"])}</h3>
                    <p>{escape(scenario["description"])}</p>
                    <span>{escape(scenario["lesson"])}</span>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Open {scenario['label'].lower()}",
                type="secondary",
                width="stretch",
                key=f"product_demo_scenario_{scenario_id}",
            ):
                try:
                    activate_demo_session(settings, scenario_id)
                except IngestionError as exc:
                    st.error(str(exc))
                else:
                    st.rerun()
    st.markdown(
        """
        <div class="metrora-access-note">
            <strong>Safe to explore.</strong>
            Every scenario is synthetic and deterministic. No account, credentials, or cloud
            connection is required, and nothing leaves the current app session.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_demo_access(settings: Settings) -> None:
    _render_page_intro(
        "Workspace access",
        "Test the decisions, not the setup.",
        "Open one of three preloaded business situations and follow the evidence from source "
        "data to decision.",
    )
    _render_access_panel(settings)


def render_product_page(settings: Settings) -> None:
    """Render the public Metrora product experience before the analytical workspace."""
    st.markdown(PRODUCT_PAGE_CSS, unsafe_allow_html=True)
    st.markdown(PRODUCT_PAGE_DARK_CSS, unsafe_allow_html=True)
    st.markdown(PRODUCT_PAGE_REFINED_CSS, unsafe_allow_html=True)
    st.markdown(PRODUCT_PAGE_V2_CSS, unsafe_allow_html=True)

    selected_page = st.session_state.get("product_page", "Product")
    if selected_page not in PUBLIC_PAGES:
        selected_page = "Product"
        st.session_state["product_page"] = selected_page

    if selected_page == "Demo":
        _render_demo_access(settings)
    else:
        _render_overview(settings)
        _render_pipeline()
        _render_trust()

    st.markdown(
        '<div class="metrora-product-footer">'
        "Metrora - cloud FinOps intelligence - local product preview"
        "</div>",
        unsafe_allow_html=True,
    )
