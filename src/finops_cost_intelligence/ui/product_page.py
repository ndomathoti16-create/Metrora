"""Public Metrora product pages and local-only demo access flow."""

# ruff: noqa: E501

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

from ..contracts.normalization import NormalizedTable
from ..contracts.profile import DataProfile
from ..contracts.quality import QualityReport
from ..ingestion import IngestionError, LoadedTable, load_table, profile_table
from ..mapping import MappingValidationError, suggest_mappings, validate_mapping
from ..normalization import normalize_billing_table
from ..quality import run_quality_checks
from .branding import METRORA_LOGO_SVG, reset_workspace_state
from .mapping_view import source_key_for

if TYPE_CHECKING:
    from ..config import Settings


PUBLIC_PAGES = ("Product", "Workflow", "Evidence", "Demo")


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


def _demo_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "demo" / "cloud_billing_demo.csv"


def _set_product_page(page: str) -> None:
    """Store the selected public product page for the next Streamlit rerun."""
    if page in PUBLIC_PAGES:
        st.session_state["product_page"] = page


def build_demo_artifacts(
    settings: Settings,
) -> tuple[
    LoadedTable,
    DataProfile,
    dict[str, str | None],
    NormalizedTable,
    QualityReport,
]:
    """Load and prepare the deterministic billing demo for a guided session."""
    demo_path = _demo_path()
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
        suggestion.canonical_field: suggestion.source_column
        for suggestion in review.suggestions
    }
    try:
        accepted_mapping = validate_mapping(suggested_mapping, review.source_columns)
        normalized = normalize_billing_table(loaded_table, accepted_mapping)
    except (MappingValidationError, ValueError, KeyError) as exc:
        raise IngestionError(f"The demo billing file could not be prepared: {exc}") from exc

    report = run_quality_checks(loaded_table, normalized)
    return loaded_table, profile, accepted_mapping, normalized, report


def activate_demo_session(settings: Settings) -> None:
    """Start a local guided demo with real Metrora analysis state."""
    loaded_table, profile, accepted_mapping, normalized, report = build_demo_artifacts(settings)
    reset_workspace_state()
    source_key = source_key_for(loaded_table, profile)
    st.session_state.update(
        {
            "demo_authenticated": True,
            "demo_mode": True,
            "demo_user_email": "demo@metrora.local",
            "demo_workspace": "Metrora guided demo",
            "loaded_table": loaded_table,
            "data_profile": profile,
            "mapping_source_key": source_key,
            "column_mapping": accepted_mapping,
            "normalized_table": normalized,
            "normalized_source_key": source_key,
            "quality_report": report,
            "quality_source_key": source_key,
            "auto_attempted_source_key": source_key,
            "workspace_page": "Home",
            "auto_analysis_message": (
                "Guided source ready. Metrora mapped, normalized, and checked the data "
                "automatically."
            ),
        }
    )


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


def _render_page_intro(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <section class="metrora-product-section">
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
        <div class="metrora-model-map">
            <div class="metrora-model-node">
                <small>01 / Source</small>
                <strong>Billing export</strong>
                <p>Provider rows, budgets, ownership, and business metrics.</p>
            </div>
            <div class="metrora-model-arrow">&rarr;</div>
            <div class="metrora-model-node">
                <small>02 / Model</small>
                <strong>Trusted cost model</strong>
                <p>Mapped, normalized, reconciled, and quality-checked data.</p>
            </div>
            <div class="metrora-model-arrow">&rarr;</div>
            <div class="metrora-model-node">
                <small>03 / Insight</small>
                <strong>Decision signals</strong>
                <p>Trends, drivers, forecasts, anomalies, and coverage.</p>
            </div>
            <div class="metrora-model-arrow">&rarr;</div>
            <div class="metrora-model-node">
                <small>04 / Action</small>
                <strong>Evidence-backed brief</strong>
                <p>Clear next steps with the numbers and caveats attached.</p>
            </div>
        </div>
        <p class="metrora-centered-caption metrora-model-caption">
            Python calculates the values first. The AI layer explains the evidence after
            the model is ready.
        </p>
        """,
        unsafe_allow_html=True,
    )


def _render_overview(settings: Settings) -> None:
    st.markdown(
        """
        <section class="metrora-product-hero metrora-premium-hero">
            <div class="metrora-hero-copy">
                <div class="metrora-product-kicker">Metrora / FinOps operating system</div>
                <h1>Make cloud spend <em>legible.</em></h1>
                <p>
                    Bring billing exports, budgets, ownership data, and business metrics into one
                    calm operating view for finance, FinOps, and cloud operations teams.
                </p>
                <div class="metrora-product-pills">
                    <span class="metrora-product-pill">Calculated before explained</span>
                    <span class="metrora-product-pill">Source traceable</span>
                </div>
            </div>
            <div class="metrora-hero-visual metrora-command-surface">
                <div class="metrora-visual-header">
                    <span>Cost position / demo signal</span>
                    <span class="metrora-visual-status">Model ready</span>
                </div>
                <div class="metrora-visual-metric">$48.2k <small>+8.4% / prior window</small></div>
                <div class="metrora-visual-chart metrora-line-visual" aria-label="Illustrative spend trend">
                    <svg viewBox="0 0 530 176" preserveAspectRatio="none" aria-hidden="true">
                        <defs>
                            <linearGradient id="metrora-area" x1="0" x2="0" y1="0" y2="1">
                                <stop offset="0" stop-color="#9bb8ff" stop-opacity=".30" />
                                <stop offset="1" stop-color="#9bb8ff" stop-opacity="0" />
                            </linearGradient>
                        </defs>
                        <path class="metrora-chart-area" d="M0 151 L45 143 L90 146 L135 122 L180 132 L225 104 L270 116 L315 53 L360 66 L405 39 L450 74 L495 60 L530 27 L530 176 L0 176 Z" />
                        <path class="metrora-chart-trace" d="M0 151 L45 143 L90 146 L135 122 L180 132 L225 104 L270 116 L315 53 L360 66 L405 39 L450 74 L495 60 L530 27" />
                        <circle class="metrora-chart-point" cx="405" cy="39" r="5" />
                    </svg>
                </div>
                <div class="metrora-visual-footer">
                    <span>Signal to review</span>
                    <strong>Compute / 42% of demo spend</strong>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    button_columns = st.columns([1, 1.45, 1], gap="small")
    with button_columns[1]:
        if st.button(
            "Try interactive demo",
            type="primary",
            width="stretch",
            key="product_demo_hero",
        ):
            try:
                activate_demo_session(settings)
            except IngestionError as exc:
                st.error(str(exc))
            else:
                st.rerun()
    st.markdown(
        '<p class="metrora-centered-caption">'
        'Illustrative signal using synthetic data. No cloud connection or credentials required.'
        '</p>',
        unsafe_allow_html=True,
    )

    _render_page_intro(
        "The operating view",
        "One reliable answer, without the billing-export archaeology.",
        "Metrora automates the normal path, then preserves the detail a reviewer needs to trust "
        "the result and decide what deserves attention.",
    )
    _render_model_map()
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
    ]
    output_columns = st.columns(3, gap="large")
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
        "AI explains evidence. It does not invent the numbers.",
        "Metrora calculates totals, trends, forecasts, and quality results in Python "
        "before any narrative layer sees them.",
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
            "Portable access",
            "The local preview uses synthetic data. A production deployment can add S3, "
            "Athena, and real identity controls later.",
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
            <h3>Preview now, production path later</h3>
            <p>
                The current product preview keeps data local and uses a guided demo workspace.
                The architecture is designed so a future hosted deployment can add cloud storage,
                query services, workspace permissions, and audited identity without changing
                the core
                analytical model.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_access_panel(settings: Settings) -> None:
    st.markdown(
        """
        <div class="metrora-product-access">
            <h3>Open the guided workspace</h3>
            <p>
                Metrora opens a preloaded, local workspace so you can explore the workflow
                without connecting an account or uploading a file first.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="metrora-access-note">
            <strong>What you will see:</strong>
            a deterministic billing export with a built-in spike, ownership gaps, budget
            pressure, and business metrics. The demo stays in the current local session.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "Open the guided demo",
        type="primary",
        width="stretch",
        key="product_demo_access",
    ):
        try:
            activate_demo_session(settings)
        except IngestionError as exc:
            st.error(str(exc))
        else:
            st.rerun()


def _render_demo_access(settings: Settings) -> None:
    _render_page_intro(
        "Workspace access",
        "See the workflow before connecting anything.",
        "Open a preloaded analysis workspace with one click and follow the evidence from "
        "source data to decision.",
    )
    columns = st.columns(3, gap="medium")
    demo_cards = [
        (
            "01",
            "Synthetic billing data",
            "A deterministic cloud billing export is already included for exploration.",
        ),
        (
            "02",
            "Ready to explore",
            "No credentials, cloud account, or external identity provider is needed for "
            "this preview.",
        ),
        (
            "03",
            "Traceable results",
            "The guided demo opens the same upload, mapping, quality, and analysis views "
            "used for a real source.",
        ),
    ]
    for column, (number, title, copy) in zip(columns, demo_cards, strict=True):
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
    _render_access_panel(settings)


def render_product_page(settings: Settings) -> None:
    """Render the public Metrora product experience before the analytical workspace."""
    st.markdown(PRODUCT_PAGE_CSS, unsafe_allow_html=True)
    st.markdown(PRODUCT_PAGE_DARK_CSS, unsafe_allow_html=True)
    st.markdown(PRODUCT_PAGE_REFINED_CSS, unsafe_allow_html=True)

    _render_brand_header()
    selected_page = st.session_state.get("product_page", "Product")
    if selected_page not in PUBLIC_PAGES:
        selected_page = "Product"
        st.session_state["product_page"] = selected_page

    with st.container(key="product-page-nav"):
        nav_columns = st.columns(len(PUBLIC_PAGES), gap="small")
        for column, page in zip(nav_columns, PUBLIC_PAGES, strict=True):
            with column:
                if page == selected_page:
                    st.markdown(
                        f'<div class="metrora-page-link" aria-current="page">{page}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.button(
                        page,
                        key=f"product_page_nav_{page.lower()}",
                        type="tertiary",
                        width="stretch",
                        on_click=_set_product_page,
                        args=(page,),
                    )

    if selected_page == "Product":
        _render_overview(settings)
    elif selected_page == "Workflow":
        _render_pipeline()
    elif selected_page == "Evidence":
        _render_trust()
    else:
        _render_demo_access(settings)

    st.markdown(
        '<div class="metrora-product-footer">'
        'Metrora - cloud FinOps intelligence - local product preview'
        '</div>',
        unsafe_allow_html=True,
    )
