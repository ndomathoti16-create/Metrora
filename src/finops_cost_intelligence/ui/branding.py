"""Shared Metrora visual identity and Streamlit presentation helpers."""

# ruff: noqa: E501

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Settings


PRODUCT_NAME = "Metrora"
PRODUCT_SUBTITLE = "Cloud FinOps intelligence"
PRODUCT_DESCRIPTION = (
    "Turn messy cloud billing exports into trusted cost signals, forecasts, and decisions."
)

METRORA_LOGO_SVG = """
<svg class="metrora-logo" viewBox="0 0 48 48" role="img" aria-label="Metrora logo">
    <defs>
        <linearGradient id="metrora-ribbon" x1="8" x2="39" y1="35" y2="10" gradientUnits="userSpaceOnUse">
            <stop stop-color="#91A8FF"/>
            <stop offset="1" stop-color="#6FE2D3"/>
        </linearGradient>
    </defs>
    <rect x="1" y="1" width="46" height="46" rx="14" fill="#0E1522" stroke="#2B3A51"/>
    <path d="M9 32.5H39" fill="none" stroke="#EAF0FA" stroke-linecap="round" stroke-width="1.6" opacity=".25"/>
    <path d="M10 29.5 17.2 20 23.5 27.6 33.8 13 39 19.3"
        fill="none" stroke="url(#metrora-ribbon)" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.25"/>
    <path d="M10 29.5 17.2 20 23.5 27.6" fill="none" stroke="#EAF0FA"
        stroke-linecap="round" stroke-linejoin="round" stroke-width="1.25" opacity=".58"/>
    <circle cx="33.8" cy="13" r="3" fill="#0E1522" stroke="#6FE2D3" stroke-width="1.6"/>
</svg>
"""


METRORA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
    color-scheme: light;
    --metrora-ink: #142033;
    --metrora-muted: #66758a;
    --metrora-line: #e6ebf2;
    --metrora-paper: #eef2f7;
    --metrora-white: #ffffff;
    --metrora-violet: #6658e8;
    --metrora-blue: #2878f0;
    --metrora-mint: #5bd5b5;
    --metrora-lime: #d9f36b;
    --metrora-coral: #ff816b;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
    color: var(--metrora-ink);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--metrora-ink);
}

[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
    color: var(--metrora-ink);
}

[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--metrora-muted);
}

[data-testid="stAlert"] {
    color: var(--metrora-ink);
}

[data-testid="stAlert"] p {
    color: var(--metrora-ink);
}

[data-testid="stAlert"] {
    border: 1px solid #d6e1f2;
    background: #edf4ff;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 92% 2%, rgba(217, 243, 107, .16), transparent 22rem),
        radial-gradient(circle at 4% 24%, rgba(91, 213, 181, .10), transparent 26rem),
        var(--metrora-paper);
}

[data-testid="stHeader"] {
    background: transparent;
}

/* Metrora supplies its own navigation and appearance controls. */
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
#MainMenu {
    display: none !important;
}

.block-container {
    max-width: 1480px;
    padding: 2rem 3rem 5rem;
}

[data-testid="stMarkdownContainer"] p {
    font-size: .98rem;
    line-height: 1.55;
}

[data-testid="stCaptionContainer"] {
    font-size: .88rem;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    font-size: .92rem;
    font-weight: 600;
    color: var(--metrora-ink);
}

button[aria-label^="Help for"] {
    color: #66758a !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button {
    border: 1px solid #dbe3ef !important;
    background: #ffffff !important;
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button p,
[data-testid="stAppViewContainer"] [data-testid="stButton"] button span,
[data-testid="stAppViewContainer"] [data-testid="stButton"] button div {
    color: inherit !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"] {
    border-color: var(--metrora-violet) !important;
    background: var(--metrora-violet) !important;
    color: #ffffff !important;
}

[data-testid="stButton"] button:disabled,
[data-testid="stDownloadButton"] button:disabled {
    border-color: #e1e6ee !important;
    background: #edf0f4 !important;
    color: #7f8b9d !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

[data-testid="stButton"] button:disabled *,
[data-testid="stDownloadButton"] button:disabled * {
    color: #7f8b9d !important;
}

[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea,
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div {
    border-color: #dbe3ef !important;
    background: #ffffff !important;
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] input::placeholder,
[data-testid="stAppViewContainer"] textarea::placeholder {
    color: #8a96a8 !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    border-color: #dbe3ef !important;
    background: #ffffff !important;
    color: var(--metrora-ink) !important;
}

[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="option"] {
    background: #ffffff !important;
    color: var(--metrora-ink) !important;
}

[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #eef3fb !important;
    color: var(--metrora-ink) !important;
}

[data-baseweb="calendar"],
[data-baseweb="calendar"] > div {
    background: #ffffff !important;
    color: var(--metrora-ink) !important;
}

[data-baseweb="calendar"] button,
[data-baseweb="calendar"] [role="gridcell"],
[data-baseweb="calendar"] [role="columnheader"] {
    color: var(--metrora-ink) !important;
}

[data-baseweb="calendar"] button[aria-selected="true"] {
    background: var(--metrora-violet) !important;
    color: #ffffff !important;
}

[data-baseweb="tag"] {
    background: #edf0ff !important;
    color: #4f43bf !important;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e6ebf2;
}

[data-testid="stSidebar"] * {
    color: var(--metrora-ink);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
    color: #52627a;
}

.metrora-sidebar-brand {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: .4rem 0 1.3rem;
}

.metrora-sidebar-mark,
.metrora-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    width: 2.65rem;
    height: 2.65rem;
    border-radius: .85rem;
    background: transparent;
    box-shadow: none;
}

.metrora-logo {
    display: block;
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 8px 12px rgba(41, 75, 107, .12));
}

.metrora-sidebar-name {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -.04em;
}

.metrora-sidebar-subtitle {
    color: #718097;
    font-size: .76rem;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.metrora-sidebar-label {
    color: #718097;
    font-size: .69rem;
    font-weight: 700;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.metrora-sidebar-status {
    margin: .65rem 0 1.25rem;
    padding: .75rem .85rem;
    border: 1px solid #e1e7ef;
    border-radius: .9rem;
    background: #f6f8fb;
    color: #52627a;
    font-size: .86rem;
}

.metrora-sidebar-status strong {
    color: #3d9f7d;
    font-weight: 600;
}

.metrora-hero {
    position: relative;
    overflow: hidden;
    margin-bottom: 1.25rem;
    padding: 2.8rem 3rem 2.65rem;
    border: 1px solid #d9e1ec;
    border-radius: 2rem;
    background:
        radial-gradient(circle at 86% 18%, rgba(217,243,107,.28), transparent 14rem),
        radial-gradient(circle at 16% 118%, rgba(91,213,181,.24), transparent 17rem),
        linear-gradient(120deg, #f8fafd 0%, #eef1fb 57%, #e6f5ef 100%);
    box-shadow: 0 24px 50px rgba(31, 48, 86, .10);
}

.metrora-hero::after {
    position: absolute;
    right: 3.2rem;
    bottom: -5.5rem;
    width: 15rem;
    height: 15rem;
    border: 1px solid rgba(217,243,107,.22);
    border-radius: 50%;
    content: '';
}

.metrora-kicker,
.metrora-section-kicker {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .16em;
    text-transform: uppercase;
}

.metrora-kicker {
    color: #2b6f5d;
}

.metrora-hero h1 {
    position: relative;
    z-index: 1;
    max-width: 760px;
    margin: .55rem 0 .65rem;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2.2rem, 5vw, 4.55rem);
    line-height: .98;
    letter-spacing: -.075em;
}

.metrora-hero p {
    position: relative;
    z-index: 1;
    max-width: 650px;
    margin: 0;
    color: #52627a;
    font-size: 1.05rem;
    line-height: 1.6;
}

.metrora-hero-meta {
    position: relative;
    z-index: 1;
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1.5rem;
}

.metrora-hero-meta span {
    padding: .42rem .7rem;
    border: 1px solid #dbe3ef;
    border-radius: 999px;
    background: rgba(255,255,255,.72);
    color: #465570;
    font-size: .73rem;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
}

.metrora-section-kicker {
    margin: 1.7rem 0 .65rem;
    color: var(--metrora-violet);
}

.metrora-feature-card {
    min-height: 148px;
    padding: 1.2rem 1.25rem;
    border: 1px solid var(--metrora-line);
    border-radius: 1.25rem;
    background: rgba(255,255,255,.82);
    box-shadow: 0 12px 30px rgba(43, 59, 87, .05);
}

.metrora-feature-card .icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: .7rem;
    background: #edf0ff;
    color: var(--metrora-violet);
    font-size: 1rem;
    font-weight: 700;
}

.metrora-feature-card h3 {
    margin: .8rem 0 .3rem;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: 1.05rem;
    letter-spacing: -.035em;
}

.metrora-feature-card p {
    margin: 0;
    color: var(--metrora-muted);
    font-size: .94rem;
    line-height: 1.45;
}

.metrora-workspace-heading {
    margin: 2rem 0 .85rem;
}

.metrora-workspace-heading span {
    color: var(--metrora-violet);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .16em;
}

.metrora-workspace-heading h2 {
    margin: .35rem 0 .2rem;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: clamp(1.65rem, 3vw, 2.45rem);
    letter-spacing: -.06em;
}

.metrora-workspace-heading p {
    margin: 0;
    color: var(--metrora-muted);
}

.metrora-workspace-topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1.5rem;
    margin: .25rem 0 1.4rem;
    padding-bottom: 1.15rem;
    border-bottom: 1px solid var(--metrora-line);
}

.metrora-workspace-topbar small {
    display: block;
    margin-bottom: .35rem;
    color: var(--metrora-violet);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.metrora-workspace-topbar h1 {
    margin: 0;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.55rem);
    letter-spacing: -.055em;
}

.metrora-workspace-topbar p {
    max-width: 760px;
    margin: .35rem 0 0;
    color: var(--metrora-muted);
}

.metrora-workspace-state {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    flex: 0 0 auto;
    margin-top: .35rem;
    padding: .5rem .8rem;
    border: 1px solid rgba(42, 142, 118, .24);
    border-radius: 999px;
    background: rgba(91, 213, 181, .13);
    color: #246f5f;
    font-size: .78rem;
    font-weight: 700;
}

.metrora-workspace-state::before {
    width: .45rem;
    height: .45rem;
    border-radius: 50%;
    background: #2f9f83;
    content: '';
}

.metrora-automation-note {
    display: flex;
    align-items: flex-start;
    gap: .8rem;
    margin: .25rem 0 1.2rem;
    padding: .9rem 1rem;
    border-left: 3px solid #6d8ca6;
    border-radius: .2rem .8rem .8rem .2rem;
    background: rgba(255,255,255,.58);
    color: var(--metrora-muted);
}

.metrora-automation-note strong {
    color: var(--metrora-ink);
}

.metrora-source-strip {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) repeat(3, minmax(110px, .7fr));
    gap: .8rem;
    margin: .75rem 0 1.2rem;
    padding: 1rem 1.1rem;
    border: 1px solid var(--metrora-line);
    border-radius: 1rem;
    background: rgba(255,255,255,.72);
}

.metrora-source-strip div {
    min-width: 0;
}

.metrora-source-strip small {
    display: block;
    margin-bottom: .2rem;
    color: var(--metrora-muted);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metrora-source-strip strong {
    display: block;
    overflow: hidden;
    color: var(--metrora-ink);
    font-size: .94rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.metrora-stepbar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: .45rem;
    margin: .55rem 0 1.35rem;
}

.metrora-stepbar-label {
    margin-right: .35rem;
    color: #8a96a8;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .12em;
}

.metrora-step {
    display: inline-flex;
    align-items: center;
    gap: .38rem;
    padding: .38rem .62rem;
    border: 1px solid var(--metrora-line);
    border-radius: 999px;
    background: rgba(255,255,255,.68);
    color: #98a4b5;
    font-size: .74rem;
    font-weight: 600;
}

.metrora-step b {
    color: #aeb8c7;
    font-size: .65rem;
}

.metrora-step.is-ready {
    border-color: rgba(91,213,181,.35);
    background: rgba(91,213,181,.12);
    color: #277c6a;
}

.metrora-step.is-ready b {
    color: #277c6a;
}

.metrora-empty-state {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    max-width: 720px;
    margin: 2rem auto;
    padding: 1.5rem;
    border: 1px solid var(--metrora-line);
    border-radius: 1.25rem;
    background: rgba(255,255,255,.8);
    box-shadow: 0 14px 34px rgba(43, 59, 87, .05);
}

.metrora-empty-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    flex: 0 0 auto;
    border-radius: .8rem;
    background: #edf0ff;
    color: var(--metrora-violet);
    font-family: 'Outfit', sans-serif;
    font-size: 1.35rem;
    font-weight: 600;
}

.metrora-empty-state h3 {
    margin: 0 0 .3rem;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    letter-spacing: -.035em;
}

.metrora-empty-state p {
    margin: 0 0 .7rem;
    color: var(--metrora-muted);
    font-size: .96rem;
    line-height: 1.5;
}

.metrora-next-step {
    color: var(--metrora-violet);
    font-size: .78rem;
    font-weight: 700;
}

[data-testid="stMetric"] {
    min-height: 110px;
    padding: 1rem 1.05rem;
    border: 1px solid var(--metrora-line);
    border-radius: 1rem;
    background: rgba(255,255,255,.88);
    box-shadow: 0 10px 22px rgba(43, 59, 87, .04);
}

[data-testid="stMetricLabel"] {
    color: var(--metrora-muted);
    font-size: .76rem;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    letter-spacing: -.045em;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 2.65rem;
    border: 0;
    border-radius: .8rem;
    background: var(--metrora-violet) !important;
    color: #fff !important;
    font-weight: 600;
    box-shadow: 0 8px 18px rgba(102, 88, 232, .18);
    transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}

.stButton > button p,
.stDownloadButton > button p,
.stButton > button *,
.stDownloadButton > button *,
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploaderDropzone"] button span {
    color: #fff !important;
}

[data-testid="stFileUploaderDropzone"] button {
    border: 0 !important;
    border-radius: .7rem !important;
    background: var(--metrora-violet) !important;
}

.stButton > button *,
.stDownloadButton > button * {
    color: #fff !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border: 0;
    background: #5649d1 !important;
    color: #fff !important;
    box-shadow: 0 12px 22px rgba(102, 88, 232, .27);
    transform: translateY(-1px);
}

[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #b5c0d3;
    border-radius: 1.1rem;
    background: rgba(255,255,255,.74);
}

[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: #52627a;
}

[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button * {
    color: #ffffff !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: .35rem;
    border-bottom: 1px solid var(--metrora-line);
}

.stTabs [data-baseweb="tab"] {
    padding: .6rem .9rem;
    color: var(--metrora-muted);
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: var(--metrora-violet);
}

.stExpander {
    border: 1px solid var(--metrora-line);
    border-radius: .95rem;
    background: rgba(255,255,255,.62);
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--metrora-line);
    border-radius: .85rem;
    overflow: hidden;
}

.metrora-table-shell {
    max-width: 100%;
    overflow: auto;
    border: 1px solid var(--metrora-line);
    border-radius: .9rem;
    background: rgba(255,255,255,.78);
}

.metrora-data-table {
    width: 100%;
    border: 0;
    border-collapse: collapse;
    color: var(--metrora-ink);
    font-size: .84rem;
}

.metrora-data-table th {
    padding: .72rem .8rem;
    border-bottom: 1px solid var(--metrora-line);
    background: #f5f7fb;
    color: var(--metrora-muted);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .04em;
    text-align: left;
    text-transform: uppercase;
    white-space: nowrap;
}

.metrora-data-table td {
    padding: .68rem .8rem;
    border-bottom: 1px solid var(--metrora-line);
    color: var(--metrora-ink);
    line-height: 1.4;
    vertical-align: top;
}

.metrora-data-table tr:last-child td {
    border-bottom: 0;
}

.metrora-data-table tbody tr:hover {
    background: #f7f9fc;
}

.metrora-driver-list {
    margin: .7rem 0 1.2rem;
    border-top: 1px solid var(--metrora-line);
}

.metrora-driver-row {
    padding: 1rem 0 1.1rem;
    border-bottom: 1px solid var(--metrora-line);
}

.metrora-driver-head,
.metrora-driver-head > div {
    display: flex;
    align-items: center;
    gap: .65rem;
}

.metrora-driver-head {
    justify-content: space-between;
}

.metrora-driver-head strong {
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: 1.05rem;
}

.metrora-driver-head span {
    padding: .24rem .48rem;
    border-radius: .35rem;
    background: #edf0ff;
    color: #4f43bf;
    font-size: .68rem;
    font-weight: 700;
}

.metrora-driver-head b {
    color: var(--metrora-ink);
    font-size: .94rem;
    white-space: nowrap;
}

.metrora-driver-body {
    display: grid;
    grid-template-columns:
        minmax(240px, 1.8fr) minmax(90px, .55fr)
        minmax(90px, .55fr) minmax(150px, .85fr);
    gap: 1.25rem;
    margin-top: .75rem;
}

.metrora-driver-body.report {
    grid-template-columns:
        minmax(240px, 1.65fr) minmax(190px, 1fr)
        minmax(130px, .7fr) minmax(150px, .8fr);
}

.metrora-driver-body small {
    display: block;
    margin-bottom: .22rem;
    color: var(--metrora-muted);
    font-size: .68rem;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
}

.metrora-driver-body strong {
    color: var(--metrora-ink);
    font-size: .82rem;
    line-height: 1.4;
}

.metrora-driver-why p {
    margin: 0;
    color: var(--metrora-ink);
    font-size: .88rem !important;
    line-height: 1.48 !important;
}

@media (max-width: 1050px) {
    .metrora-driver-body,
    .metrora-driver-body.report {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    .metrora-driver-head {
        align-items: flex-start;
    }

    .metrora-driver-head > div {
        align-items: flex-start;
        flex-direction: column;
    }

    .metrora-driver-body,
    .metrora-driver-body.report {
        grid-template-columns: minmax(0, 1fr);
    }
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button {
    justify-content: flex-start;
    min-height: 2.35rem;
    padding: .35rem .55rem;
    border: 0 !important;
    border-left: 3px solid transparent !important;
    border-radius: .25rem !important;
    background: transparent !important;
    color: #52627a !important;
    box-shadow: none !important;
    text-align: left;
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_reports button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button[kind="primary"] {
    border-left-color: var(--metrora-violet) !important;
    background: #f1f0ff !important;
    color: #4f43bf !important;
}

.metrora-sidebar-guidance {
    margin: .45rem 0 1rem;
    color: #728096;
    font-size: .78rem;
    line-height: 1.5;
}

.metrora-report-kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin: 1.15rem 0 1.65rem;
    border-top: 1px solid var(--metrora-line);
    border-bottom: 1px solid var(--metrora-line);
}

.metrora-report-kpi {
    min-width: 0;
    padding: 1.05rem 1rem 1.05rem 0;
}

.metrora-report-kpi + .metrora-report-kpi {
    padding-left: 1rem;
    border-left: 1px solid var(--metrora-line);
}

.metrora-report-kpi span,
.metrora-report-kpi small,
.metrora-report-kpi strong {
    display: block;
}

.metrora-report-kpi span {
    color: var(--metrora-muted);
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metrora-report-kpi strong {
    margin: .35rem 0 .22rem;
    overflow: hidden;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: 1.45rem;
    letter-spacing: -.045em;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.metrora-report-kpi small {
    color: var(--metrora-muted);
    font-size: .78rem;
    line-height: 1.45;
}

.metrora-report-kpi.risk strong {
    color: #a54434;
}

.metrora-report-kpi.positive strong {
    color: #277863;
}

.metrora-report-bottom-line {
    margin: .3rem 0 1.55rem;
    padding: .15rem 0 .15rem 1.1rem;
    border-left: 3px solid var(--metrora-blue);
}

.metrora-report-bottom-line span {
    color: #245fba;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
}

.metrora-report-bottom-line p {
    max-width: 1000px;
    margin: .42rem 0 0;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: clamp(1.2rem, 2vw, 1.65rem) !important;
    font-weight: 600;
    line-height: 1.35 !important;
    letter-spacing: -.025em;
}

.metrora-report-action {
    display: grid;
    grid-template-columns: 5.25rem minmax(0, 1fr);
    gap: 1rem;
    padding: 1.05rem 0;
    border-top: 1px solid var(--metrora-line);
}

.metrora-report-action:last-of-type {
    border-bottom: 1px solid var(--metrora-line);
}

.metrora-report-priority {
    align-self: start;
    width: fit-content;
    padding: .28rem .48rem;
    border-radius: .4rem;
    background: #edf0f5;
    color: #536176;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .08em;
}

.metrora-report-priority.high {
    background: #fff0ed;
    color: #9d3b2c;
}

.metrora-report-priority.medium {
    background: #fff7df;
    color: #805f12;
}

.metrora-report-action h4 {
    margin: 0 0 .35rem;
    color: var(--metrora-ink);
    font-family: 'Outfit', sans-serif;
    font-size: 1.03rem;
    letter-spacing: -.02em;
}

.metrora-report-action p {
    max-width: 920px;
    margin: 0 0 .48rem;
    color: var(--metrora-ink);
}

.metrora-report-action small {
    display: block;
    margin-top: .2rem;
    color: var(--metrora-muted);
    line-height: 1.45;
}

/* The authenticated workspace behaves like an application, not a product page. */
.st-key-workspace-shell {
    max-width: 1420px;
    margin: 0 auto;
}

.st-key-workspace-shell .metrora-workspace-topbar {
    margin-bottom: 1.75rem;
    padding-bottom: 1.25rem;
}

.st-key-workspace-shell .metrora-workspace-topbar h1 {
    font-size: clamp(1.85rem, 2.5vw, 2.25rem);
    letter-spacing: -.045em;
}

.st-key-workspace-shell [data-testid="stMetric"] {
    min-height: 98px;
    padding: 1rem .2rem .85rem;
    border: 0;
    border-top: 2px solid #dbe3ef;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
}

.st-key-workspace-shell [data-testid="stMetricValue"] {
    overflow-wrap: anywhere;
    font-size: clamp(1.35rem, 2vw, 1.85rem);
    line-height: 1.12;
}

.st-key-workspace-shell [data-testid="stMetricDelta"] {
    font-size: .8rem;
}

.metrora-subsection-label {
    margin: 2rem 0 .65rem;
    color: var(--metrora-muted);
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.metrora-attention-item {
    display: grid;
    grid-template-columns: .55rem minmax(0, 1fr);
    gap: .75rem;
    padding: .9rem 0;
    border-top: 1px solid var(--metrora-line);
}

.metrora-attention-item > span {
    width: .48rem;
    height: .48rem;
    margin-top: .35rem;
    border-radius: 50%;
    background: #8a96a8;
}

.metrora-attention-item.attention > span {
    background: #d96c58;
}

.metrora-attention-item.positive > span {
    background: #2f9f83;
}

.metrora-attention-item strong {
    color: var(--metrora-ink);
    font-size: .94rem;
}

.metrora-attention-item p {
    margin: .18rem 0 0;
    color: var(--metrora-muted);
    font-size: .83rem !important;
    line-height: 1.45 !important;
}

.metrora-advanced-note {
    display: grid;
    grid-template-columns: 9rem minmax(0, 1fr);
    gap: 1.25rem;
    margin: 0 0 1.6rem;
    padding: .9rem 0 .9rem 1rem;
    border-left: 3px solid #6d8ca6;
}

.metrora-advanced-note strong {
    color: var(--metrora-ink);
}

.metrora-advanced-note span {
    color: var(--metrora-muted);
    line-height: 1.5;
}

[data-testid="stSidebar"] .st-key-workspace_nav_advanced {
    margin-top: .45rem;
    padding-top: .45rem;
    border-top: 1px solid #e5eaf1;
}

/* Keep native Streamlit content readable when the host theme is dark. */
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6 {
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p {
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--metrora-muted) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stAlert"],
[data-testid="stAppViewContainer"] [data-testid="stAlert"] p {
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] .metrora-hero h1 {
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] .metrora-hero p {
    color: #52627a !important;
}

[data-testid="stAppViewContainer"] .metrora-feature-card h3 {
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] .metrora-feature-card p,
[data-testid="stAppViewContainer"] .metrora-workspace-heading p,
[data-testid="stAppViewContainer"] .metrora-empty-state p {
    color: var(--metrora-muted) !important;
}

[data-testid="stAppViewContainer"] .metrora-empty-state h3 {
    color: var(--metrora-ink) !important;
}

@media (max-width: 800px) {
    .block-container { padding: 1.2rem 1rem 3rem; }
    .metrora-hero { padding: 2rem 1.35rem; border-radius: 1.35rem; }
    .metrora-hero h1 { font-size: 2.65rem; }
    .metrora-workspace-topbar { flex-direction: column; }
    .metrora-source-strip { grid-template-columns: 1fr 1fr; }
    .metrora-report-kpis { grid-template-columns: 1fr 1fr; }
    .metrora-report-kpi:nth-child(3) { border-left: 0; }
    .metrora-report-kpi:nth-child(n+3) { border-top: 1px solid var(--metrora-line); }
    .metrora-report-action { grid-template-columns: 1fr; gap: .55rem; }
    .metrora-advanced-note { grid-template-columns: 1fr; gap: .3rem; }
}
</style>
"""


METRORA_DARK_CSS = """
<style>
:root {
    color-scheme: dark;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 92% 2%, rgba(217,243,107,.09), transparent 22rem),
        radial-gradient(circle at 4% 24%, rgba(91,213,181,.07), transparent 26rem),
        #0c1220;
    color: #edf3fb;
}

[data-testid="stMain"] {
    color: #edf3fb;
}

[data-testid="stSidebar"] {
    background: #111a2b;
    border-right: 0;
}

[data-testid="stSidebar"] * {
    color: #e7edf7;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
    color: #b9c6d8;
}

.metrora-sidebar-status {
    border-color: rgba(255,255,255,.10);
    background: rgba(255,255,255,.05);
    color: #dbe5f3;
}

.metrora-sidebar-status strong {
    color: var(--metrora-lime);
}

.metrora-hero {
    border-color: rgba(255,255,255,.45);
    background:
        radial-gradient(circle at 86% 18%, rgba(217,243,107,.28), transparent 14rem),
        radial-gradient(circle at 16% 118%, rgba(91,213,181,.24), transparent 17rem),
        linear-gradient(120deg, #17223a 0%, #1c2b4a 58%, #29366a 100%);
    box-shadow: 0 24px 50px rgba(31, 48, 86, .16);
}

.metrora-hero h1 {
    color: #fff !important;
}

.metrora-kicker {
    color: var(--metrora-lime);
}

.metrora-hero p {
    color: #c7d2e4 !important;
}

.metrora-hero-meta span {
    border-color: rgba(255,255,255,.14);
    background: rgba(255,255,255,.08);
    color: #e4ecf7;
}

body,
h1, h2, h3, h4, h5, h6,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
[data-testid="stAlert"],
[data-testid="stAlert"] p {
    color: #edf3fb;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stAlert"],
[data-testid="stAppViewContainer"] [data-testid="stAlert"] p {
    color: #edf3fb !important;
}

[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: #b2bfd1 !important;
}

[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p,
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] label {
    color: #dce5f1 !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button,
[data-testid="stSidebar"] [data-testid="stButton"] button {
    border-color: #2a3850 !important;
    background: #162338 !important;
    color: #edf3fb !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button p,
[data-testid="stAppViewContainer"] [data-testid="stButton"] button span,
[data-testid="stAppViewContainer"] [data-testid="stButton"] button div,
[data-testid="stSidebar"] [data-testid="stButton"] button p,
[data-testid="stSidebar"] [data-testid="stButton"] button span,
[data-testid="stSidebar"] [data-testid="stButton"] button div {
    color: inherit !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    border-color: #53627a !important;
    background: #1d2d47 !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"] {
    border-color: #7d73ef !important;
    background: #6658e8 !important;
    color: #ffffff !important;
}

[data-testid="stButton"] button:disabled,
[data-testid="stDownloadButton"] button:disabled {
    border-color: #26344a !important;
    background: #111a2b !important;
    color: #75849a !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

[data-testid="stButton"] button:disabled *,
[data-testid="stDownloadButton"] button:disabled * {
    color: #75849a !important;
}

[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea,
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div,
[data-testid="stAppViewContainer"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] input {
    border-color: #2a3850 !important;
    background: #162338 !important;
    color: #edf3fb !important;
}

[data-testid="stAppViewContainer"] input::placeholder,
[data-testid="stAppViewContainer"] textarea::placeholder,
[data-testid="stAppViewContainer"] [data-baseweb="select"] * {
    color: #b2bfd1 !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    border-color: #2a3850 !important;
    background: #162338 !important;
    color: #edf3fb !important;
}

[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="option"] {
    background: #162338 !important;
    color: #edf3fb !important;
}

[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #21324b !important;
    color: #ffffff !important;
}

[data-baseweb="calendar"],
[data-baseweb="calendar"] > div {
    background: #162338 !important;
    color: #edf3fb !important;
}

[data-baseweb="calendar"] button,
[data-baseweb="calendar"] [role="gridcell"],
[data-baseweb="calendar"] [role="columnheader"] {
    color: #edf3fb !important;
}

[data-baseweb="calendar"] button[aria-selected="true"] {
    background: #6658e8 !important;
    color: #ffffff !important;
}

[data-baseweb="tag"] {
    background: #2b285f !important;
    color: #e4e0ff !important;
}

[data-testid="stAlert"] {
    border-color: #294365;
    background: #112346;
}

[data-testid="stAppViewContainer"] .metrora-hero h1 {
    color: #fff !important;
}

[data-testid="stAppViewContainer"] .metrora-hero p {
    color: #c7d2e4 !important;
}

[data-testid="stAppViewContainer"] .metrora-feature-card h3,
[data-testid="stAppViewContainer"] .metrora-empty-state h3,
[data-testid="stAppViewContainer"] [data-testid="stMetricValue"] {
    color: #f4f7fb !important;
}

[data-testid="stAppViewContainer"] .metrora-feature-card p,
[data-testid="stAppViewContainer"] .metrora-workspace-heading p,
[data-testid="stAppViewContainer"] .metrora-empty-state p {
    color: #b2bfd1 !important;
}

.metrora-workspace-heading h2,
.metrora-feature-card h3,
.metrora-empty-state h3,
[data-testid="stMetricValue"] {
    color: #f4f7fb;
}

.metrora-workspace-heading p,
.metrora-feature-card p,
.metrora-empty-state p,
[data-testid="stCaptionContainer"] {
    color: #b2bfd1;
}

.metrora-feature-card,
.metrora-empty-state,
[data-testid="stMetric"] {
    border-color: #2a3850;
    background: rgba(24, 36, 56, .86);
    box-shadow: 0 14px 34px rgba(0, 0, 0, .18);
}

.metrora-feature-card .icon,
.metrora-empty-icon {
    background: rgba(102,88,232,.22);
    color: #b8b1ff;
}

.metrora-step {
    border-color: #2a3850;
    background: rgba(24,36,56,.82);
    color: #9baac0;
}

.metrora-step.is-ready {
    border-color: rgba(91,213,181,.4);
    background: rgba(91,213,181,.12);
    color: #8ae7d0;
}

[data-testid="stFileUploaderDropzone"] {
    border-color: #53627a;
    background: rgba(24,36,56,.72);
}

[data-testid="stFileUploaderDropzone"] button {
    background: #6658e8 !important;
}

[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: #b2bfd1 !important;
}

[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button * {
    color: #ffffff !important;
}

.stExpander,
div[data-testid="stDataFrame"] {
    border-color: #2a3850;
    background: rgba(17, 27, 44, .7);
}

/* Keep Streamlit's native evidence widgets readable in the dark workspace. */
[data-testid="stExpander"] {
    border-color: #2a3850 !important;
    background: #111a2b !important;
}

[data-testid="stExpander"] > details > summary,
[data-testid="stExpander"] [data-testid="stExpanderToggleDetails"],
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    color: #edf3fb !important;
}

[data-testid="stExpander"] > details > summary,
[data-testid="stExpander"] [data-testid="stExpanderToggleDetails"] {
    background: #162338 !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    border-color: #2a3850 !important;
    background: #111a2b !important;
}

[data-testid="stExpander"] > details > summary *,
[data-testid="stExpander"] [data-testid="stExpanderToggleDetails"] * {
    color: #edf3fb !important;
}

div[data-testid="stDataFrame"] {
    background: #111a2b !important;
}

div[data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
    --gdg-accent-color: #8c82ff !important;
    --gdg-accent-fg: #ffffff !important;
    --gdg-bg-cell: #111a2b !important;
    --gdg-bg-cell-medium: #162338 !important;
    --gdg-bg-header: #162338 !important;
    --gdg-bg-header-has-focus: #21324b !important;
    --gdg-bg-header-hovered: #21324b !important;
    --gdg-bg-group-header: #162338 !important;
    --gdg-bg-group-header-hovered: #21324b !important;
    --gdg-bg-bubble: #21324b !important;
    --gdg-bg-bubble-selected: #2a3850 !important;
    --gdg-text-dark: #edf3fb !important;
    --gdg-text-medium: #b9c6d8 !important;
    --gdg-text-light: #7e8ba1 !important;
    --gdg-text-header: #c7d2e4 !important;
    --gdg-text-group-header: #c7d2e4 !important;
    --gdg-text-header-selected: #ffffff !important;
    --gdg-bg-icon-header: rgba(237, 243, 251, .6) !important;
    --gdg-fg-icon-header: #edf3fb !important;
    --gdg-border-color: #2a3850 !important;
    --gdg-horizontal-border-color: #2a3850 !important;
    --gdg-drilldown-border: #53627a !important;
    --gdg-link-color: #9abaff !important;
    --gdg-resize-indicator-color: #8c82ff !important;
}

[data-testid="stJson"] .react-json-view {
    background: #111a2b !important;
    color: #dce5f1 !important;
}

[data-testid="stJson"] .react-json-view .object-key,
[data-testid="stJson"] .react-json-view .object-key-val > span,
[data-testid="stJson"] .react-json-view .variable-row > span {
    color: #dce5f1 !important;
}

[data-testid="stJson"] .react-json-view .variable-row,
[data-testid="stJson"] .react-json-view .object-content {
    border-color: #2a3850 !important;
    background: transparent !important;
}

[data-testid="stJson"] .react-json-view .variable-value > div {
    color: #a9d7ff !important;
}

[data-testid="stFormSubmitButton"] button,
[data-testid="stBaseButton-secondaryFormSubmit"] {
    border-color: #7d73ef !important;
    background: #6658e8 !important;
    color: #ffffff !important;
}

[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
    border-color: #aaa3ff !important;
    background: #7569f0 !important;
}

[data-testid="stFormSubmitButton"] button *,
[data-testid="stBaseButton-secondaryFormSubmit"] * {
    color: #ffffff !important;
}

.metrora-workspace-topbar {
    border-color: #2a3850;
}

.metrora-workspace-topbar h1,
.metrora-automation-note strong,
.metrora-source-strip strong {
    color: #f4f7fb !important;
}

.metrora-workspace-topbar p,
.metrora-automation-note,
.metrora-source-strip small {
    color: #b2bfd1 !important;
}

.metrora-workspace-state {
    border-color: rgba(91,213,181,.32);
    background: rgba(91,213,181,.11);
    color: #8ae7d0;
}

.metrora-automation-note,
.metrora-source-strip,
.metrora-table-shell {
    border-color: #2a3850;
    background: rgba(17,27,44,.72);
}

.metrora-data-table {
    color: #edf3fb;
}

.metrora-data-table th {
    border-color: #2a3850;
    background: #162338;
    color: #9eabc0;
}

.metrora-data-table td {
    border-color: #2a3850;
    color: #e6edf7;
}

.metrora-data-table tbody tr:hover {
    background: #18263d;
}

.metrora-driver-list,
.metrora-driver-row {
    border-color: #2a3850;
}

.metrora-driver-head strong,
.metrora-driver-head b,
.metrora-driver-body strong,
.metrora-driver-why p {
    color: #edf3fb !important;
}

.metrora-driver-head span {
    background: rgba(102,88,232,.2);
    color: #c4bdff;
}

.metrora-driver-body small {
    color: #9eabc0;
}

.metrora-report-kpis,
.metrora-report-kpi + .metrora-report-kpi,
.metrora-report-action {
    border-color: #2a3850;
}

.metrora-report-kpi span,
.metrora-report-kpi small,
.metrora-report-action small {
    color: #a8b5c8;
}

.metrora-report-kpi strong,
.metrora-report-bottom-line p,
.metrora-report-action h4,
.metrora-report-action p {
    color: #edf3fb !important;
}

.metrora-report-kpi.risk strong {
    color: #ff9c89 !important;
}

.metrora-report-kpi.positive strong {
    color: #7fe0c8 !important;
}

.metrora-report-bottom-line {
    border-left-color: #72a8ff;
}

.metrora-report-bottom-line span {
    color: #91b9f4;
}

.metrora-report-priority {
    background: #202c40;
    color: #c2cddd;
}

.metrora-report-priority.high {
    background: rgba(255,129,107,.14);
    color: #ffab9c;
}

.metrora-report-priority.medium {
    background: rgba(217,164,65,.14);
    color: #e9c36e;
}

.st-key-workspace-shell [data-testid="stMetric"] {
    border-top-color: #2a3850;
    background: transparent;
    box-shadow: none;
}

.metrora-attention-item {
    border-color: #2a3850;
}

.metrora-attention-item strong,
.metrora-advanced-note strong {
    color: #edf3fb !important;
}

.metrora-attention-item p,
.metrora-advanced-note span,
.metrora-subsection-label {
    color: #a8b5c8 !important;
}

[data-testid="stSidebar"] .st-key-workspace_nav_advanced {
    border-top-color: #253249;
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button {
    border: 0 !important;
    border-left: 3px solid transparent !important;
    background: transparent !important;
    color: #b9c6d8 !important;
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_reports button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button[kind="primary"] {
    border-left-color: #8c82ff !important;
    background: rgba(102,88,232,.13) !important;
    color: #f4f2ff !important;
}

.stTabs [data-baseweb="tab-list"] {
    border-color: #2a3850;
}

.stTabs [data-baseweb="tab"] {
    color: #a8b5c8;
}

.stTabs [aria-selected="true"] {
    color: #c4bdff;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: #dce5f1;
}

button[aria-label^="Help for"] {
    color: #9eabc0 !important;
}
</style>
"""


METRORA_REFINED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&family=Outfit:wght@500;600;700;800&display=swap');

:root {
    color-scheme: dark;
    --metrora-ink: #f2f5fb;
    --metrora-muted: #9eaabd;
    --metrora-line: #273347;
    --metrora-paper: #080c13;
    --metrora-white: #101722;
    --metrora-violet: #8faeff;
    --metrora-blue: #9bb8ff;
    --metrora-mint: #7ee0d0;
    --metrora-lime: #b9cbff;
    --metrora-coral: #f2c58e;
}

html, body, [class*="css"] {
    background: var(--metrora-paper);
    color: var(--metrora-ink);
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 84% -8%, rgba(95, 125, 190, .15), transparent 33rem),
        radial-gradient(circle at 8% 15%, rgba(74, 193, 180, .06), transparent 28rem),
        #080c13 !important;
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] *,
[data-testid="stSidebar"] * {
    scrollbar-color: #34425a transparent;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stAlert"],
[data-testid="stAppViewContainer"] [data-testid="stAlert"] p {
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p,
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] label {
    color: var(--metrora-muted) !important;
}

[data-testid="stSidebar"] {
    background: #0c111a !important;
    border-right: 1px solid var(--metrora-line) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--metrora-muted) !important;
}

.metrora-sidebar-status,
.metrora-automation-note,
.metrora-source-strip,
.metrora-table-shell,
.metrora-empty-state,
[data-testid="stMetric"] {
    border-color: var(--metrora-line) !important;
    background: rgba(16, 23, 34, .78) !important;
    box-shadow: none !important;
}

.metrora-sidebar-status strong,
.metrora-workspace-state,
.metrora-step.is-ready {
    color: var(--metrora-mint) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button,
[data-testid="stSidebar"] [data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {
    min-height: 2.55rem;
    border: 1px solid var(--metrora-line) !important;
    border-radius: .58rem !important;
    background: #111927 !important;
    color: var(--metrora-ink) !important;
    box-shadow: none !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: #52647e !important;
    background: #172237 !important;
    color: #ffffff !important;
}

[data-testid="stMain"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button,
[data-testid="stFileUploaderDropzone"] button {
    border-color: #9bb8ff !important;
    background: #9bb8ff !important;
    color: #08101d !important;
    box-shadow: 0 9px 24px rgba(117, 150, 223, .18) !important;
}

[data-testid="stMain"] [data-testid="stButton"] button[kind="primary"] *,
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button *,
[data-testid="stFileUploaderDropzone"] button * {
    color: #08101d !important;
}

[data-testid="stButton"] button:disabled,
[data-testid="stDownloadButton"] button:disabled {
    border-color: #202a3a !important;
    background: #0e141e !important;
    color: #68748a !important;
}

[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea,
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div,
[data-testid="stAppViewContainer"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] input {
    border-color: var(--metrora-line) !important;
    background: #101722 !important;
    color: var(--metrora-ink) !important;
}

[data-testid="stAppViewContainer"] input::placeholder,
[data-testid="stAppViewContainer"] textarea::placeholder,
[data-testid="stAppViewContainer"] [data-baseweb="select"] * {
    color: var(--metrora-muted) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[data-baseweb="calendar"],
[data-baseweb="calendar"] > div {
    border-color: var(--metrora-line) !important;
    background: #101722 !important;
    color: var(--metrora-ink) !important;
}

[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="option"],
[data-baseweb="calendar"] button,
[data-baseweb="calendar"] [role="gridcell"],
[data-baseweb="calendar"] [role="columnheader"] {
    background: #101722 !important;
    color: var(--metrora-ink) !important;
}

[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"],
[data-baseweb="calendar"] button[aria-selected="true"] {
    background: #1b2940 !important;
    color: #ffffff !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--metrora-line) !important;
    border-radius: .75rem !important;
    background: #101722 !important;
}

[data-testid="stExpander"] > details > summary,
[data-testid="stExpander"] [data-testid="stExpanderToggleDetails"],
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] > details > summary * {
    background: #101722 !important;
    color: var(--metrora-ink) !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--metrora-line) !important;
    border-radius: .75rem !important;
    background: #101722 !important;
}

div[data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
    --gdg-accent-color: #9bb8ff !important;
    --gdg-accent-fg: #08101d !important;
    --gdg-bg-cell: #101722 !important;
    --gdg-bg-cell-medium: #141e2d !important;
    --gdg-bg-header: #141e2d !important;
    --gdg-bg-header-has-focus: #1b2940 !important;
    --gdg-bg-header-hovered: #1b2940 !important;
    --gdg-bg-group-header: #141e2d !important;
    --gdg-bg-group-header-hovered: #1b2940 !important;
    --gdg-bg-bubble: #1b2940 !important;
    --gdg-bg-bubble-selected: #26354e !important;
    --gdg-text-dark: #f2f5fb !important;
    --gdg-text-medium: #c3cede !important;
    --gdg-text-light: #8996aa !important;
    --gdg-text-header: #cbd6e7 !important;
    --gdg-text-group-header: #cbd6e7 !important;
    --gdg-text-header-selected: #ffffff !important;
    --gdg-border-color: #273347 !important;
    --gdg-horizontal-border-color: #273347 !important;
    --gdg-drilldown-border: #52647e !important;
    --gdg-link-color: #a9c1ff !important;
    --gdg-resize-indicator-color: #9bb8ff !important;
}

[data-testid="stJson"] .react-json-view {
    background: #101722 !important;
    color: #dce5f2 !important;
}

[data-testid="stJson"] .react-json-view .object-key,
[data-testid="stJson"] .react-json-view .object-key-val > span,
[data-testid="stJson"] .react-json-view .variable-row > span {
    color: #dce5f2 !important;
}

.metrora-data-table { color: var(--metrora-ink) !important; }
.metrora-data-table th { background: #141e2d !important; color: #cbd6e7 !important; }
.metrora-data-table td, .metrora-data-table th { border-color: var(--metrora-line) !important; }
.metrora-data-table td { color: #e4eaf4 !important; }
.metrora-data-table tbody tr:hover { background: #172237 !important; }

[data-testid="stFileUploaderDropzone"] {
    border-color: #52647e !important;
    background: #101722 !important;
}

[data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: var(--metrora-muted) !important;
}

.stTabs [data-baseweb="tab-list"] { border-color: var(--metrora-line) !important; }
.stTabs [data-baseweb="tab"] { color: var(--metrora-muted) !important; }
.stTabs [aria-selected="true"] { color: var(--metrora-ink) !important; }

[data-testid="stSidebar"] .st-key-workspace_nav_home button,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button {
    background: transparent !important;
    color: #aeb9ca !important;
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_reports button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button[kind="primary"] {
    border-left-color: #9bb8ff !important;
    background: rgba(155, 184, 255, .1) !important;
    color: #f2f5fb !important;
}

/* Active workspace navigation uses a soft surface, not the generic blue CTA.
   Explicitly carry its light label into Streamlit's nested text elements. */
[data-testid="stSidebar"] .st-key-workspace_nav_home button[kind="primary"] *,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button[kind="primary"] *,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button[kind="primary"] *,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button[kind="primary"] *,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button[kind="primary"] * {
    color: #f2f5fb !important;
}

[data-testid="stSidebar"] [data-testid="stButton"].st-key-workspace_nav_home button[kind="primary"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stButton"].st-key-workspace_nav_cost_explorer button[kind="primary"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stButton"].st-key-workspace_nav_plans_alerts button[kind="primary"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stButton"].st-key-workspace_nav_reports button[kind="primary"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stButton"].st-key-workspace_nav_advanced button[kind="primary"] [data-testid="stMarkdownContainer"] p {
    color: #f2f5fb !important;
}

/* Keep the operating area rich in context without turning it into a wall of cards. */
.metrora-workspace-command-meta {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: .95rem;
}

.metrora-workspace-context-item {
    display: grid;
    gap: .16rem;
    min-width: 4.8rem;
    padding-left: .95rem;
    border-left: 1px solid #273347;
}

.metrora-workspace-context-item small,
.metrora-decision-snapshot span {
    color: #8e9bb0 !important;
    font-size: .64rem !important;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}

.metrora-workspace-context-item strong {
    max-width: 12rem;
    overflow: hidden;
    color: #e9eef7 !important;
    font-size: .78rem;
    font-weight: 650;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.metrora-decision-snapshot {
    display: grid;
    grid-template-columns: minmax(14rem, 1.45fr) repeat(3, minmax(9.5rem, 1fr));
    margin: 1.45rem 0 2.65rem;
    border-top: 1px solid #32425b;
    border-bottom: 1px solid #273347;
    background: linear-gradient(100deg, rgba(145, 168, 255, .085), rgba(16, 23, 34, 0) 44%);
}

.metrora-snapshot-lead,
.metrora-snapshot-signal {
    min-height: 8.5rem;
    padding: 1.3rem 1.15rem 1.2rem 0;
}

.metrora-snapshot-signal {
    padding-left: 1.15rem;
    border-left: 1px solid #273347;
}

.metrora-decision-snapshot strong {
    display: block;
    margin: .5rem 0 .45rem;
    color: #f1f5fb !important;
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
    font-weight: 650;
    letter-spacing: -.025em;
    line-height: 1.18;
}

.metrora-decision-snapshot p {
    margin: 0 !important;
    color: #aeb9c9 !important;
    font-size: .78rem !important;
    line-height: 1.52 !important;
}

@media (max-width: 980px) {
    .metrora-workspace-command-meta { justify-content: flex-start; }
    .metrora-decision-snapshot { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metrora-snapshot-signal:nth-child(3) { border-left: 0; }
    .metrora-snapshot-signal:nth-child(-n+3) { border-bottom: 1px solid #273347; }
}

@media (max-width: 640px) {
    .metrora-workspace-context-item { padding-left: .7rem; }
    .metrora-decision-snapshot { grid-template-columns: 1fr; }
    .metrora-snapshot-lead,
    .metrora-snapshot-signal {
        min-height: auto;
        padding: 1rem 0;
        border-left: 0;
        border-bottom: 1px solid #273347;
    }
    .metrora-snapshot-signal:last-child { border-bottom: 0; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}
</style>
"""


METRORA_WORKSPACE_V2_CSS = """
<style>
/* Workspace v2: a focused operating canvas with quiet navigation and visible flow. */
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700&display=swap');

:root {
    color-scheme: dark;
    --metrora-ink: #f2f5f8;
    --metrora-muted: #96a2b1;
    --metrora-line: #232e3a;
    --metrora-paper: #080b10;
    --metrora-white: #0e141c;
    --metrora-violet: #7da7ff;
    --metrora-blue: #7da7ff;
    --metrora-mint: #55d6c7;
    --metrora-lime: #a8c5ff;
    --metrora-coral: #efbd7f;
}

html, body, [class*="css"] {
    background: var(--metrora-paper);
    color: var(--metrora-ink);
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(255,255,255,.012) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.012) 1px, transparent 1px),
        radial-gradient(circle at 88% -8%, rgba(85, 214, 199, .075), transparent 31rem),
        #080b10 !important;
    background-size: 48px 48px, 48px 48px, auto, auto !important;
}

.block-container {
    max-width: 1540px !important;
    padding: 1.25rem 2.35rem 6rem !important;
}

[data-testid="stSidebar"] {
    min-width: 17rem !important;
    max-width: 17rem !important;
    border-right: 1px solid #202a35 !important;
    background: #0a0e14 !important;
}

[data-testid="stSidebar"] > div:first-child { width: 17rem !important; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1.35rem 1rem 1rem !important; }

.metrora-sidebar-brand {
    margin: .1rem .3rem 2rem;
    padding: 0;
}
.metrora-sidebar-mark,
.metrora-sidebar-mark .metrora-logo { width: 2.55rem; height: 2.55rem; }
.metrora-sidebar-name {
    color: #f4f7f9 !important;
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: 1.02rem;
    letter-spacing: -.035em;
}
.metrora-sidebar-subtitle { color: #778495 !important; font-size: .58rem; letter-spacing: .11em; }

.metrora-sidebar-label {
    margin: 1.4rem .55rem .65rem;
    color: #657284 !important;
    font-size: .58rem;
    letter-spacing: .14em;
}

.metrora-sidebar-status {
    margin: 0 .2rem .75rem;
    padding: .9rem .85rem .8rem;
    border: 1px solid #222d39 !important;
    border-radius: .78rem !important;
    background: linear-gradient(145deg, rgba(17, 24, 33, .94), rgba(12, 17, 24, .94)) !important;
}
.metrora-sidebar-status-line { display: grid; gap: .25rem; }
.metrora-sidebar-status-line strong {
    overflow: hidden;
    color: #e9eef4 !important;
    font-size: .79rem;
    font-weight: 650;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.metrora-sidebar-status-line span { color: #79dbd0; font-size: .68rem; font-weight: 700; }
.metrora-sidebar-status small { color: #667487 !important; font-size: .61rem; }
.metrora-sidebar-progress {
    height: 3px;
    margin: .8rem 0 .6rem;
    overflow: hidden;
    border-radius: 999px;
    background: #222c37;
}
.metrora-sidebar-progress i {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #7da7ff, #55d6c7);
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button {
    display: flex !important;
    justify-content: flex-start !important;
    min-height: 2.65rem !important;
    margin: .08rem 0;
    padding: 0 .72rem !important;
    border: 0 !important;
    border-radius: .58rem !important;
    background: transparent !important;
    color: #8f9baa !important;
    font-size: .82rem !important;
    font-weight: 550 !important;
    text-align: left !important;
}
[data-testid="stSidebar"] .st-key-workspace_nav_home button::before,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button::before,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button::before,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button::before,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button::before {
    width: 1.45rem;
    margin-right: .25rem;
    color: #596779;
    font-family: 'Manrope', sans-serif;
    font-size: .58rem;
    font-weight: 700;
    letter-spacing: .04em;
}
[data-testid="stSidebar"] .st-key-workspace_nav_home button::before { content: '01'; }
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button::before { content: '02'; }
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button::before { content: '03'; }
[data-testid="stSidebar"] .st-key-workspace_nav_reports button::before { content: '04'; }
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button::before { content: '05'; }

[data-testid="stSidebar"] .st-key-workspace_nav_home button:hover,
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button:hover,
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button:hover,
[data-testid="stSidebar"] .st-key-workspace_nav_reports button:hover,
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button:hover {
    background: #111821 !important;
    color: #dfe5ec !important;
}

[data-testid="stSidebar"] .st-key-workspace_nav_home button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_cost_explorer button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_plans_alerts button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_reports button[kind="primary"],
[data-testid="stSidebar"] .st-key-workspace_nav_advanced button[kind="primary"] {
    border: 1px solid #252f3b !important;
    background: linear-gradient(90deg, rgba(125, 167, 255, .11), rgba(85, 214, 199, .045)) !important;
    color: #f2f5f8 !important;
}

.metrora-sidebar-guidance {
    margin: 1rem .25rem .5rem;
    padding: .9rem .75rem 0;
    border: 0 !important;
    border-top: 1px solid #202a35 !important;
    border-radius: 0 !important;
    background: transparent !important;
    color: #6f7c8d !important;
    font-size: .67rem;
    line-height: 1.55;
}
.metrora-sidebar-guidance strong { display: block; margin-bottom: .28rem; color: #9eabb9 !important; }

.metrora-workspace-topbar {
    display: block;
    margin: .45rem 0 2rem;
    padding: .65rem 0 1.6rem;
    border: 0;
    border-bottom: 1px solid #202a35;
    background: transparent;
}
.metrora-workspace-location {
    display: flex;
    align-items: center;
    gap: .52rem;
    min-height: 1.8rem;
    color: #657385;
    font-size: .67rem;
}
.metrora-workspace-location i { color: #394656; font-style: normal; }
.metrora-workspace-location strong { color: #a1adbb; font-weight: 600; }
.metrora-workspace-state {
    display: inline-flex;
    align-items: center;
    gap: .38rem;
    margin-left: auto;
    padding: .35rem .58rem;
    border: 1px solid rgba(85, 214, 199, .18) !important;
    border-radius: 999px;
    background: rgba(85, 214, 199, .055) !important;
    color: #76dacf !important;
    font-size: .61rem;
    font-weight: 700;
    letter-spacing: .04em;
}
.metrora-workspace-state::before {
    width: .36rem;
    height: .36rem;
    border-radius: 50%;
    background: #55d6c7;
    content: '';
}
.metrora-workspace-title-row {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 2.6rem;
    padding-top: 1.05rem;
}
.metrora-workspace-title-copy { min-width: 0; }
.metrora-workspace-topbar h1 {
    margin: 0;
    color: #f3f6f8 !important;
    font-family: 'Manrope', 'Outfit', sans-serif;
    font-size: clamp(1.8rem, 2.7vw, 2.7rem) !important;
    font-weight: 650;
    letter-spacing: -.055em;
    line-height: 1.08;
}
.metrora-workspace-topbar p {
    max-width: 46rem;
    margin: .72rem 0 0 !important;
    color: #8794a4 !important;
    font-size: .84rem !important;
}
.metrora-workspace-command-meta { gap: .25rem; flex-wrap: nowrap; }
.metrora-workspace-context-item {
    min-width: 5.8rem;
    padding: .18rem 1rem;
    border-left: 1px solid #222d39;
}
.metrora-workspace-context-item small { color: #647284 !important; font-size: .55rem !important; }
.metrora-workspace-context-item strong { color: #cfd7e1 !important; font-size: .7rem; }

.metrora-analysis-flow {
    display: grid;
    grid-template-columns: 9rem minmax(0, 1fr);
    align-items: center;
    gap: 1.15rem;
    margin: 0 0 1.6rem;
    padding: 1rem 1.1rem;
    border: 1px solid #222d39;
    border-radius: .9rem;
    background: rgba(13, 19, 27, .88);
    box-shadow: 0 18px 48px rgba(0,0,0,.12);
}
.metrora-flow-heading { display: grid; gap: .2rem; }
.metrora-flow-heading span { color: #dce3eb; font-size: .72rem; font-weight: 700; }
.metrora-flow-heading small { color: #657385; font-size: .57rem; letter-spacing: .08em; text-transform: uppercase; }
.metrora-flow-track {
    display: grid;
    grid-template-columns: minmax(7rem, 1fr) 2rem minmax(7rem, 1fr) 2rem minmax(7rem, 1fr) 2rem minmax(7rem, 1fr);
    align-items: center;
}
.metrora-flow-node { display: flex; align-items: center; gap: .62rem; min-width: 0; }
.metrora-flow-node > span {
    display: grid;
    flex: 0 0 1.65rem;
    width: 1.65rem;
    height: 1.65rem;
    place-items: center;
    border: 1px solid #2a3542;
    border-radius: .5rem;
    background: #101720;
    color: #677487;
    font-size: .56rem;
    font-weight: 800;
}
.metrora-flow-node > div { min-width: 0; }
.metrora-flow-node strong,
.metrora-flow-node small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.metrora-flow-node strong { color: #b7c1cc; font-size: .69rem; }
.metrora-flow-node small { margin-top: .16rem; color: #687587; font-size: .57rem; }
.metrora-flow-node.is-ready > span {
    border-color: rgba(85, 214, 199, .24);
    background: rgba(85, 214, 199, .09);
    color: #79ddd2;
}
.metrora-flow-node.is-ready strong { color: #e0e6ec; }
.metrora-flow-link { position: relative; height: 1px; background: #2a3541; }
.metrora-flow-link i {
    position: absolute;
    top: -2px;
    left: 0;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #55d6c7;
    opacity: .65;
    animation: metrora-workspace-flow 5s ease-in-out infinite;
}

.st-key-workspace-kpi-strip,
.st-key-explorer-kpi-strip {
    margin: .2rem 0 0;
    padding: .2rem;
    overflow: hidden;
    border: 1px solid #222d39;
    border-radius: .92rem;
    background: rgba(13, 19, 27, .92);
}
.st-key-workspace-kpi-strip [data-testid="stHorizontalBlock"],
.st-key-explorer-kpi-strip [data-testid="stHorizontalBlock"] { gap: 0 !important; }
.st-key-workspace-kpi-strip [data-testid="stColumn"],
.st-key-explorer-kpi-strip [data-testid="stColumn"] { min-width: 0; }
.st-key-workspace-kpi-strip [data-testid="stMetric"],
.st-key-explorer-kpi-strip [data-testid="stMetric"] {
    min-height: 7.2rem;
    padding: 1rem 1.05rem !important;
    border: 0 !important;
    border-right: 1px solid #222d39 !important;
    border-radius: 0 !important;
    background: transparent !important;
}
.st-key-workspace-kpi-strip [data-testid="stColumn"]:last-child [data-testid="stMetric"],
.st-key-explorer-kpi-strip [data-testid="stColumn"]:last-child [data-testid="stMetric"] { border-right: 0 !important; }
[data-testid="stMetricLabel"] { color: #7f8c9c !important; font-size: .69rem !important; }
[data-testid="stMetricValue"] {
    max-width: 100%;
    overflow: visible !important;
    color: #f1f4f7 !important;
    font-family: 'Manrope', 'Outfit', sans-serif !important;
    font-size: clamp(1.25rem, 1.9vw, 1.9rem) !important;
    letter-spacing: -.045em !important;
    line-height: 1.15 !important;
    white-space: normal !important;
}
[data-testid="stMetricDelta"] { font-size: .68rem !important; }

.st-key-forecast_summary_metrics {
    margin: 1.35rem 0 2rem;
    padding: .2rem;
    overflow: hidden;
    border: 1px solid #222d39;
    border-radius: .9rem;
    background: rgba(12, 18, 26, .88);
}
.st-key-forecast_summary_metrics [data-testid="stHorizontalBlock"] { gap: 0 !important; }
.st-key-forecast_summary_metrics [data-testid="stMetric"] {
    min-height: 6.7rem;
    padding: 1.1rem 1.2rem !important;
    border-right: 1px solid #222d39;
}
.st-key-forecast_summary_metrics [data-testid="stColumn"]:last-child [data-testid="stMetric"] { border-right: 0; }

.st-key-anomaly_summary_metric {
    margin: 1.35rem 0 2rem;
    padding: 1.15rem 1.3rem;
    border: 1px solid #26384d;
    border-radius: .85rem;
    background: linear-gradient(90deg, rgba(125, 167, 255, .09), rgba(13, 19, 27, .84));
}
.st-key-anomaly_summary_metric [data-testid="stMetric"] { min-height: 4.4rem; }
.st-key-anomaly_summary_metric [data-testid="stMetricLabel"] { margin-bottom: .5rem; }

.metrora-period-context {
    display: flex;
    align-items: center;
    gap: .62rem;
    margin: .7rem .2rem 0;
    color: #687587;
    font-size: .65rem;
}
.metrora-period-context span { color: #8d9aaa; }
.metrora-period-context strong { color: #c1cad4; font-weight: 600; }
.metrora-period-context small { color: #657285; }

.metrora-planning-strip {
    display: grid;
    grid-template-columns: repeat(3, minmax(9rem, 1fr)) minmax(12rem, 1.35fr);
    align-items: center;
    gap: .8rem;
    margin: .55rem 0 1.85rem;
    padding: 1.15rem 1.3rem;
    border: 1px solid #222d39;
    border-radius: .82rem;
    background: rgba(13, 19, 27, .82);
}
.metrora-planning-strip > div { display: grid; gap: .3rem; padding-right: 1.2rem; border-right: 1px solid #222d39; }
.metrora-planning-strip span { color: #687587; font-size: .56rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.metrora-planning-strip strong { color: #d7dee6; font-size: .7rem; font-weight: 650; }
.metrora-planning-strip small { padding-left: 1.2rem; color: #697688; font-size: .64rem; line-height: 1.5; }

.metrora-decision-snapshot {
    grid-template-columns: minmax(15rem, 1.45fr) repeat(3, minmax(10rem, 1fr));
    margin: 1.45rem 0 2rem;
    overflow: hidden;
    border: 1px solid #222d39;
    border-radius: .92rem;
    background: rgba(12, 18, 26, .88);
    box-shadow: 0 22px 54px rgba(0,0,0,.12);
    animation: metrora-workspace-enter .55s ease both;
}
.metrora-snapshot-lead,
.metrora-snapshot-signal { min-height: 8.4rem; padding: 1.15rem; }
.metrora-snapshot-lead { background: linear-gradient(135deg, rgba(125,167,255,.09), rgba(85,214,199,.035)); }
.metrora-snapshot-signal { border-left-color: #222d39; }
.metrora-decision-snapshot span { color: #6e7b8d !important; font-size: .56rem !important; }
.metrora-decision-snapshot strong { color: #e8edf2 !important; font-family: 'Manrope', sans-serif; font-size: .95rem; }
.metrora-decision-snapshot p { color: #8794a4 !important; font-size: .72rem !important; }

.metrora-subsection-label {
    margin: 2.3rem 0 .8rem;
    color: #6d7a8b !important;
    font-size: .59rem;
    letter-spacing: .14em;
}

.st-key-home-trend-surface,
.st-key-home-attention-surface,
.st-key-explorer-trend-surface,
.st-key-explorer-breakdown-surface,
.st-key-explorer-control-bar {
    min-width: 0;
    padding: 1.05rem 1.05rem .85rem;
    border: 1px solid #222d39;
    border-radius: .92rem;
    background: rgba(12, 18, 26, .88);
}
.st-key-home-trend-surface,
.st-key-explorer-trend-surface,
.st-key-explorer-breakdown-surface { overflow: hidden; }
.st-key-home-attention-surface { min-height: 100%; }
.st-key-explorer-control-bar { margin-bottom: 1rem; padding: 1rem 1.15rem 1.15rem; }
.metrora-panel-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: .05rem .1rem .65rem;
}
.metrora-panel-heading span { color: #dce3ea; font-family: 'Manrope', sans-serif; font-size: .78rem; font-weight: 700; }
.metrora-panel-heading small { color: #657284; font-size: .6rem; }
.stPlotlyChart, .js-plotly-plot, .plot-container { min-width: 0 !important; max-width: 100% !important; }

.metrora-attention-item {
    margin: 0;
    padding: .9rem .1rem;
    border: 0;
    border-bottom: 1px solid #222d39;
    border-radius: 0;
    background: transparent;
}
.metrora-attention-item > span { width: .42rem; height: .42rem; margin-top: .26rem; }
.metrora-attention-item strong { color: #dfe5eb !important; font-size: .75rem; }
.metrora-attention-item p { color: #7f8c9c !important; font-size: .68rem !important; }
.st-key-home_open_explorer button,
.st-key-home_open_anomalies button,
.st-key-home_open_budget button {
    min-height: 2.15rem !important;
    margin: .45rem 0 .25rem;
    border: 0 !important;
    background: #151d27 !important;
    color: #bec8d3 !important;
    font-size: .69rem !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button,
[data-testid="stFileUploaderDropzone"] button {
    border-color: #86acff !important;
    background: #86acff !important;
    color: #08101a !important;
    box-shadow: 0 10px 28px rgba(90, 131, 220, .17) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"] *,
[data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button *,
[data-testid="stFileUploaderDropzone"] button * { color: #08101a !important; }

.metrora-driver-list { overflow: hidden; border: 1px solid #222d39; border-radius: .9rem; background: rgba(12,18,26,.72); }
.metrora-driver-row { padding: 1.15rem 1.2rem; border-bottom-color: #222d39; }
.metrora-driver-head span { background: rgba(125,167,255,.1); color: #a9c1ee; }

.metrora-report-decision {
    margin: 1rem 0 1.25rem;
    padding: 1.45rem 1.55rem 1.35rem;
    border-left: 3px solid #7da7ff;
    background: linear-gradient(90deg, rgba(125,167,255,.09), rgba(125,167,255,.015));
}
.metrora-report-decision.positive {
    border-left-color: #55d6c7;
    background: linear-gradient(90deg, rgba(85,214,199,.09), rgba(85,214,199,.012));
}
.metrora-report-decision.risk {
    border-left-color: #ef927f;
    background: linear-gradient(90deg, rgba(239,146,127,.10), rgba(239,146,127,.012));
}
.metrora-report-decision > span {
    display: inline-flex;
    margin-bottom: .9rem;
    color: #9cbcff;
    font-size: .61rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.metrora-report-decision.positive > span { color: #79ddd2; }
.metrora-report-decision.risk > span { color: #f3a697; }
.metrora-report-decision h2 {
    max-width: 55rem;
    margin: 0;
    color: #f2f5f8 !important;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(1.45rem, 2.4vw, 2.25rem) !important;
    line-height: 1.18;
    letter-spacing: -.045em;
}
.metrora-report-decision p {
    max-width: 48rem;
    margin: .75rem 0 0 !important;
    color: #91a0b0 !important;
    font-size: .78rem !important;
    line-height: 1.6;
}
.metrora-report-answers {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(14rem, 100%), 1fr));
    margin-bottom: 2.6rem;
    border-top: 1px solid #26313e;
    border-bottom: 1px solid #26313e;
}
.metrora-report-answers article {
    min-width: 0;
    padding: 1.35rem 1.4rem 1.5rem 0;
}
.metrora-report-answers article + article {
    padding-left: 1.4rem;
    border-left: 1px solid #26313e;
}
.metrora-report-answers small {
    display: block;
    margin-bottom: .8rem;
    color: #6f96e7;
    font-size: .6rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.metrora-report-answers p {
    margin: 0 !important;
    color: #c5ced8 !important;
    font-size: .78rem !important;
    line-height: 1.66;
}
.metrora-report-action { padding: 1.25rem 1.3rem !important; }
.metrora-report-action > div { min-width: 0; }
.metrora-report-action small { margin-top: .48rem; line-height: 1.55; }

.metrora-automation-note,
.metrora-source-strip,
.metrora-advanced-note {
    padding: 1rem 1.1rem !important;
}

[data-testid="stExpander"] > details > summary {
    min-height: 3rem;
    padding: .75rem 1rem !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: .35rem 1rem 1rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    width: fit-content;
    gap: .2rem !important;
    margin: 0 0 1.55rem;
    padding: .24rem !important;
    border: 1px solid #222d39 !important;
    border-radius: .7rem;
    background: #0c1219;
}
.stTabs [data-baseweb="tab"] {
    min-height: 2.45rem;
    padding: 0 1rem;
    border-radius: .5rem;
    color: #7d8998 !important;
    font-size: .72rem;
}
.stTabs [aria-selected="true"] { background: #18212c !important; color: #e7ecf1 !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

[data-testid="stExpander"] {
    overflow: hidden;
    border-color: #222d39 !important;
    border-radius: .78rem !important;
    background: #0d131b !important;
}
[data-testid="stExpander"] > details > summary,
[data-testid="stExpander"] [data-testid="stExpanderToggleDetails"],
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] > details > summary * { background: #0d131b !important; }

[data-testid="stDataFrame"],
.metrora-table-shell { border-color: #222d39 !important; background: #0d131b !important; }

@keyframes metrora-workspace-flow {
    0%, 15% { left: 0; opacity: 0; }
    35%, 70% { opacity: .75; }
    88%, 100% { left: calc(100% - 5px); opacity: 0; }
}
@keyframes metrora-workspace-enter {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1120px) {
    .metrora-workspace-title-row { align-items: flex-start; flex-direction: column; }
    .metrora-workspace-command-meta { flex-wrap: wrap; }
    .metrora-analysis-flow { grid-template-columns: 1fr; }
    .metrora-decision-snapshot { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metrora-planning-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .metrora-planning-strip small { grid-column: 1 / -1; margin-top: .75rem; padding: .7rem 0 0; border-top: 1px solid #222d39; }
}

@media (max-width: 760px) {
    .block-container { padding: 1rem 1rem 4rem !important; }
    .metrora-flow-track { grid-template-columns: 1fr; gap: .55rem; }
    .metrora-flow-link { display: none; }
    .metrora-period-context { align-items: flex-start; flex-direction: column; }
    .metrora-planning-strip { grid-template-columns: 1fr; }
    .metrora-planning-strip > div { padding: .65rem 0; border-right: 0; border-bottom: 1px solid #222d39; }
    .metrora-decision-snapshot { grid-template-columns: 1fr; }
    .metrora-snapshot-signal { border-left: 0; border-top: 1px solid #222d39; }
    .st-key-workspace-kpi-strip [data-testid="stHorizontalBlock"],
    .st-key-explorer-kpi-strip [data-testid="stHorizontalBlock"] { gap: .35rem !important; }
    .st-key-workspace-kpi-strip [data-testid="stMetric"],
    .st-key-explorer-kpi-strip [data-testid="stMetric"] { border-right: 0 !important; border-bottom: 1px solid #222d39 !important; }
    .metrora-report-answers { grid-template-columns: 1fr; }
    .metrora-report-answers article,
    .metrora-report-answers article + article {
        padding: 1.15rem .2rem !important;
        border-left: 0;
        border-bottom: 1px solid #26313e;
    }
    .metrora-report-answers article:last-child { border-bottom: 0; }
}

@media (prefers-reduced-motion: reduce) {
    .metrora-flow-link i,
    .metrora-decision-snapshot { animation: none !important; }
}
</style>
"""


def inject_styles() -> None:
    """Inject Metrora's single dark application theme."""
    import streamlit as st

    # A style-only st.html block takes up no layout space. Keeping the theme in one
    # block also avoids the empty Streamlit wrappers that used to add a large blank
    # area before the first visible control, especially on narrow screens.
    st.html(
        "".join(
            (
                METRORA_CSS,
                METRORA_DARK_CSS,
                METRORA_REFINED_CSS,
                METRORA_WORKSPACE_V2_CSS,
                METRORA_SCROLL_REVEAL_CSS,
            )
        )
    )


METRORA_SCROLL_REVEAL_CSS = """
<style>
/* Content is visible by default. Scroll animation is progressive enhancement, so a
   slow phone, embedded browser, or blocked script can never leave a blank page. */
.metrora-scroll-reveal {
    opacity: 1;
    visibility: visible;
    transform: none;
}

@keyframes metrora-safe-scroll-enter {
    from { opacity: .58; transform: translate3d(0, 16px, 0); }
    to { opacity: 1; transform: translate3d(0, 0, 0); }
}

@supports (animation-timeline: view()) {
    @media (min-width: 721px) and (prefers-reduced-motion: no-preference) {
        .metrora-scroll-reveal {
            animation: metrora-safe-scroll-enter both linear;
            animation-timeline: view();
            animation-range: entry 0% entry 34%;
        }
    }
}

@media (max-width: 720px), (prefers-reduced-motion: reduce) {
    .metrora-scroll-reveal {
        opacity: 1 !important;
        visibility: visible !important;
        transform: none !important;
        animation: none !important;
        transition: none !important;
    }
}
</style>
"""


def enable_scroll_reveals() -> None:
    """Retain the app-shell hook; reveal effects now use safe CSS enhancement."""


TOP_NAVIGATION_CSS = """
<style>
/* The application uses a single full-width canvas. Navigation lives above the work,
   so content never competes with a persistent side rail. */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

.metrora-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.25rem;
    padding: .2rem 0 1rem;
    border-bottom: 1px solid #202b38;
}

.metrora-topbar-brand {
    display: inline-flex;
    align-items: center;
    gap: .7rem;
    min-width: 0;
}

.metrora-topbar-mark {
    display: inline-flex;
    width: 2.1rem;
    height: 2.1rem;
    flex: 0 0 2.1rem;
}

.metrora-topbar-mark .metrora-logo { width: 100%; height: 100%; }

.metrora-topbar-name {
    color: #f4f7fb;
    font-family: 'Outfit', 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -.025em;
}

.metrora-topbar-subtitle,
.metrora-topbar-context {
    color: #8290a2;
    font-size: .69rem;
    font-weight: 650;
    letter-spacing: .055em;
    line-height: 1.35;
    text-transform: uppercase;
}

.metrora-topbar-context {
    display: inline-flex;
    align-items: center;
    justify-content: flex-end;
    gap: .45rem;
    text-align: right;
}

.metrora-topbar-context i {
    width: .42rem;
    height: .42rem;
    border-radius: 50%;
    background: #55d6c7;
    box-shadow: 0 0 0 4px rgba(85, 214, 199, .1);
}

.st-key-metrora_top_nav {
    margin: .7rem 0 1.8rem;
}

.st-key-metrora_top_nav [data-testid="stHorizontalBlock"] {
    align-items: stretch;
    gap: .45rem !important;
}

.st-key-metrora_top_nav [data-testid="stButton"] button {
    min-height: 2.45rem;
    padding: .48rem .68rem;
    border: 1px solid transparent;
    border-radius: .58rem;
    background: transparent;
    color: #9aa7b8;
    font-size: .78rem;
    font-weight: 650;
    line-height: 1.2;
    box-shadow: none;
    transition: color .16s ease, background .16s ease, border-color .16s ease;
}

.st-key-metrora_top_nav [data-testid="stButton"] button:hover {
    color: #eef4fb;
    background: #121d2a;
    border-color: #2a3a4d;
}

.st-key-metrora_top_nav [data-testid="stButton"] button[kind="primary"] {
    color: #eaf5ff;
    background: #162a3d;
    border-color: #31516d;
}

.st-key-metrora_top_nav .st-key-top_workspace_new_analysis button,
.st-key-metrora_top_nav .st-key-top_workspace_back_to_product button {
    color: #b8c7d8;
    background: #101a27;
    border-color: #27384b;
}

.metrora-product-top-links {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: .25rem;
    margin: .75rem 0 2.1rem;
    padding-bottom: .85rem;
    border-bottom: 1px solid #202b38;
}

.metrora-product-top-links a {
    padding: .52rem .72rem;
    border: 1px solid transparent;
    border-radius: .48rem;
    color: #9aa7b8 !important;
    font-size: .78rem;
    font-weight: 650;
    line-height: 1.2;
    text-decoration: none !important;
    transition: color .16s ease, background .16s ease, border-color .16s ease, transform .16s ease;
}

.metrora-product-top-links a:hover {
    border-color: #2a3a4d;
    background: #121d2a;
    color: #edf4fb !important;
    transform: translateY(-1px);
}

.metrora-product-top-links .metrora-product-demo-link {
    margin-left: .35rem;
    border-color: #31516d;
    background: #162a3d;
    color: #eaf5ff !important;
}

.metrora-connection-row {
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
    gap: 2rem;
    padding: 1.15rem 1.25rem;
    margin-top: .85rem;
    border-top: 1px solid #253242;
    border-bottom: 1px solid #182331;
    background: linear-gradient(90deg, rgba(18,29,42,.72), rgba(11,18,27,.25));
}

.metrora-connection-row > div {
    display: grid;
    gap: .32rem;
    min-width: 0;
}

.metrora-connection-row span {
    color: #55d6c7;
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.metrora-connection-row strong {
    color: #eef3f8;
    font-size: .98rem;
    overflow-wrap: anywhere;
}

.metrora-connection-row small {
    color: #8794a4;
    font-size: .78rem;
    line-height: 1.55;
    overflow-wrap: anywhere;
}

.metrora-governance-list {
    display: grid;
    gap: 0;
    margin-top: 1.15rem;
    border-top: 1px solid #263545;
}

.metrora-governance-row {
    display: grid;
    grid-template-columns: minmax(12rem, .7fr) minmax(18rem, 1.2fr) minmax(18rem, 1fr);
    gap: 1.5rem;
    align-items: center;
    padding: 1.15rem .25rem;
    border-bottom: 1px solid #1d2936;
}

.metrora-governance-row > div {
    display: grid;
    gap: .32rem;
}

.metrora-governance-row span {
    width: fit-content;
    padding: .2rem .46rem;
    border-radius: 999px;
    color: #99a7b8;
    background: #151f2b;
    font-size: .63rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metrora-governance-row.met span {
    color: #6fe2d3;
    background: rgba(85,214,199,.1);
}

.metrora-governance-row.attention span {
    color: #ff9c8d;
    background: rgba(255,124,107,.11);
}

.metrora-governance-row strong {
    color: #eef3f8;
    font-size: .94rem;
}

.metrora-governance-row p,
.metrora-governance-row small {
    margin: 0;
    color: #9aa7b8;
    font-size: .8rem;
    line-height: 1.55;
}

.metrora-governance-row small { color: #c4ced9; }

.metrora-decision-list {
    display: grid;
    gap: .7rem;
    margin: 1.2rem 0 1.8rem;
}

.metrora-decision-row {
    display: grid;
    grid-template-columns: 4.6rem minmax(18rem, 1.2fr) minmax(30rem, 1fr);
    gap: 1.35rem;
    align-items: center;
    padding: 1.15rem 1.25rem;
    border: 1px solid #243243;
    border-radius: .85rem;
    background: linear-gradient(110deg, rgba(18, 29, 42, .88), rgba(10, 16, 24, .72));
}

.metrora-decision-score {
    display: grid;
    min-height: 3.7rem;
    align-content: center;
    justify-items: center;
    border-right: 1px solid #283647;
}

.metrora-decision-score span {
    color: #8ae2d7;
    font-family: 'Manrope', 'DM Sans', sans-serif;
    font-size: 1.35rem;
    font-weight: 750;
}

.metrora-decision-score small,
.metrora-decision-meta small {
    color: #718095;
    font-size: .58rem;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}

.metrora-decision-main {
    display: grid;
    gap: .38rem;
    min-width: 0;
}

.metrora-decision-main > span {
    color: #6fd9cc;
    font-size: .63rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metrora-decision-main strong {
    color: #eff4fa;
    font-size: 1rem;
}

.metrora-decision-main p {
    display: -webkit-box;
    margin: 0;
    overflow: hidden;
    color: #96a3b3 !important;
    font-size: .78rem !important;
    line-height: 1.5 !important;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
}

.metrora-decision-meta {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .9rem;
    min-width: 0;
}

.metrora-decision-meta > div {
    display: grid;
    gap: .24rem;
    min-width: 0;
    padding-left: .8rem;
    border-left: 1px solid #253343;
}

.metrora-decision-meta strong,
.metrora-decision-meta span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.metrora-decision-meta strong { color: #d8e1eb; font-size: .75rem; }
.metrora-decision-meta span { color: #8795a7; font-size: .7rem; }

@media (max-width: 760px) {
    .metrora-topbar {
        align-items: flex-start;
        gap: .8rem;
        padding-bottom: .8rem;
    }
    .metrora-topbar-context {
        max-width: 11.5rem;
        font-size: .61rem;
        line-height: 1.45;
    }
    .st-key-metrora_top_nav [data-testid="stHorizontalBlock"] { gap: .25rem !important; }
    .st-key-metrora_top_nav [data-testid="stButton"] button { font-size: .69rem; padding: .42rem .25rem; }
    .metrora-product-top-links {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .35rem;
        margin: .75rem 0 1.35rem;
        padding-bottom: .75rem;
    }
    .metrora-product-top-links a {
        display: flex;
        min-width: 0;
        min-height: 2.45rem;
        align-items: center;
        justify-content: center;
        padding: .55rem .35rem;
        text-align: center;
    }
    .metrora-product-top-links .metrora-product-demo-link { margin-left: 0; }
    .metrora-connection-row { grid-template-columns: 1fr; gap: 1rem; }
    .metrora-governance-row { grid-template-columns: 1fr; gap: .65rem; }
    .metrora-decision-row { grid-template-columns: 3.5rem 1fr; }
    .metrora-decision-meta { grid-column: 1 / -1; }
}
</style>
"""


def render_top_navigation(settings: Settings) -> None:
    """Render the full-width navigation shared by product and workspace views."""
    import streamlit as st

    from .navigation import set_product_route, set_workspace_route

    is_workspace = bool(st.session_state.get("demo_authenticated", False))
    has_source = st.session_state.get("loaded_table") is not None
    has_model = st.session_state.get("normalized_table") is not None
    report = st.session_state.get("quality_report")
    analysis_ready = bool(has_model and report is not None and report.ready_for_analysis)

    if is_workspace:
        workspace_label = st.session_state.get(
            "demo_workspace", f"{settings.app_env.title()} workspace"
        )
        status_label = "Analysis ready" if analysis_ready else "Review needed"
        context = f"<i></i>{escape(str(workspace_label))} / {status_label}"
    else:
        context = "Local product preview / no sign-in required"

    st.html(TOP_NAVIGATION_CSS)
    st.markdown(
        f"""
        <header class="metrora-topbar">
            <div class="metrora-topbar-brand">
                <span class="metrora-topbar-mark">{METRORA_LOGO_SVG}</span>
                <div>
                    <div class="metrora-topbar-name">Metrora</div>
                    <div class="metrora-topbar-subtitle">Cloud FinOps intelligence</div>
                </div>
            </div>
            <div class="metrora-topbar-context">{context}</div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    if not is_workspace:
        if st.session_state.get("product_page", "Product") == "Demo":
            st.markdown(
                """
                <nav class="metrora-product-top-links" aria-label="Product navigation">
                    <a class="metrora-product-demo-link" href="?surface=product&amp;page=Product" target="_self">Back to product</a>
                </nav>
                """,
                unsafe_allow_html=True,
            )
            return
        st.markdown(
            """
            <nav class="metrora-product-top-links" aria-label="Product sections">
                <a href="#metrora-overview">Overview</a>
                <a href="#metrora-workflow">How it works</a>
                <a href="#metrora-evidence">Trust &amp; evidence</a>
                <a class="metrora-product-demo-link" href="?surface=product&amp;page=Demo" target="_self">Explore demos</a>
            </nav>
            """,
            unsafe_allow_html=True,
        )
        return

    pages = (
        ("Overview", "Home", "home"),
        ("Explore spend", "Cost explorer", "cost_explorer"),
        ("Forecast & alerts", "Plans & alerts", "plans_alerts"),
        ("Decisions", "Decisions", "decisions"),
        ("Reports & exports", "Reports", "reports"),
        ("Data sources", "Connections", "connections"),
        ("Data settings", "Advanced", "advanced"),
    )
    legacy_pages = {
        "Overview": "Home",
        "Spend explorer": "Cost explorer",
        "Forecast & alerts": "Plans & alerts",
        "Reports & exports": "Reports",
        "Data sources": "Connections",
        "Data settings": "Advanced",
        "Data & quality": "Advanced",
        "Investigate": "Plans & alerts",
    }
    current_page = legacy_pages.get(
        st.session_state.get("workspace_page", "Home"),
        st.session_state.get("workspace_page", "Home"),
    )
    st.session_state["workspace_page"] = current_page

    desktop_mode = bool(st.session_state.get("desktop_mode", False))
    with st.container(key="metrora_top_nav"):
        weights = [1, 1.1, 1.25, .9, 1.2, 1, .95, 1]
        if not desktop_mode:
            weights.append(1)
        columns = st.columns(weights, gap="small")
        for column, (label, destination, slug) in zip(columns[:7], pages, strict=True):
            with column:
                if st.button(
                    label,
                    key=f"top_workspace_nav_{slug}",
                    type="primary" if destination == current_page else "tertiary",
                    width="stretch",
                ):
                    set_workspace_route(destination)
                    st.rerun()
        with columns[7]:
            if st.button(
                "New analysis",
                key="top_workspace_new_analysis",
                disabled=not (has_source or has_model),
                width="stretch",
                help="Clear the current data and start a new analysis.",
            ):
                reset_workspace_state()
                for key in ("demo_mode", "demo_scenario", "demo_workspace"):
                    st.session_state.pop(key, None)
                set_workspace_route("Home", scenario_id=None)
                st.rerun()
        if not desktop_mode:
            with columns[8]:
                if st.button(
                    "Exit demo",
                    key="top_workspace_back_to_product",
                    width="stretch",
                    help="Return to the Metrora demo scenarios.",
                ):
                    reset_workspace_state()
                    for key in (
                        "demo_authenticated",
                        "demo_mode",
                        "demo_scenario",
                        "demo_user_email",
                        "demo_workspace",
                    ):
                        st.session_state.pop(key, None)
                    set_product_route("Demo")
                    st.rerun()


def apply_plotly_theme(figure):
    """Apply Metrora's fixed dark chart palette."""
    text = "#edf2f7"
    muted = "#8794a4"
    grid = "rgba(135,148,164,.14)"
    line = "#222d39"
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": text, "family": "DM Sans"},
        title_font={"color": text, "family": "Manrope"},
        legend={"font": {"color": muted}},
        hoverlabel={
            "bgcolor": "#111821",
            "bordercolor": "#2b3744",
            "font": {"color": text, "family": "DM Sans"},
        },
        xaxis={
            "gridcolor": grid,
            "linecolor": line,
            "tickfont": {"color": muted},
            "title_font": {"color": muted},
            "automargin": True,
            "zeroline": False,
        },
        yaxis={
            "gridcolor": grid,
            "linecolor": line,
            "tickfont": {"color": muted},
            "title_font": {"color": muted},
            "automargin": True,
            "zeroline": False,
        },
    )
    return figure


def render_compact_table(dataframe, *, max_rows: int = 20) -> None:
    """Render a bounded, theme-safe HTML table for operational detail views."""
    import streamlit as st

    if dataframe.empty:
        st.info("No rows are available for this view.")
        return
    bounded = dataframe.head(max_rows)
    table_html = bounded.to_html(
        index=False,
        border=0,
        classes="metrora-data-table",
        escape=True,
        na_rep="-",
    )
    st.markdown(
        f'<div class="metrora-table-shell">{table_html}</div>',
        unsafe_allow_html=True,
    )
    if len(dataframe) > max_rows:
        st.caption(f"Showing the first {max_rows:,} of {len(dataframe):,} rows.")


def render_brand_header() -> None:
    """Render the product hero and high-level capability cards."""
    import streamlit as st

    st.markdown(
        """
        <section class="metrora-hero">
            <div class="metrora-kicker">Metrora · cloud FinOps intelligence</div>
            <h1>Turn cloud spend into decisions.</h1>
            <p>
                Validate the data, find the signal, and give finance and engineering teams
                a shared view of cost, risk, and what to do next.
            </p>
            <div class="metrora-hero-meta">
                <span>Local-first workflow</span>
                <span>Evidence before AI</span>
                <span>Built for FinOps teams</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="metrora-section-kicker">The Metrora loop</div>',
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    cards = [
        (
            "01",
            "See the signal",
            "Profile billing exports, map their meaning, and surface the services "
            "and owners moving spend.",
        ),
        (
            "02",
            "Prove the number",
            "Reconcile totals, expose data-quality caveats, and keep every metric "
            "traceable to source rows.",
        ),
        (
            "03",
            "Act with context",
            "Connect budgets and business metrics to forecasts, anomalies, and "
            "evidence-backed next steps.",
        ),
    ]
    for column, (number, title, copy) in zip(columns, cards, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="metrora-feature-card">
                    <div class="icon">{number}</div>
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_product_sidebar() -> None:
    """Render the public-product navigation in the same persistent left rail."""
    import streamlit as st

    from .navigation import set_product_route

    pages = (
        ("Product overview", "Product", "product"),
        ("How it works", "Workflow", "workflow"),
        ("Trust & evidence", "Evidence", "evidence"),
        ("Demo scenarios", "Demo", "demo"),
    )
    current_page = st.session_state.get("product_page", "Product")
    destinations = {destination for _, destination, _ in pages}
    if current_page not in destinations:
        current_page = "Product"
        st.session_state["product_page"] = current_page

    with st.sidebar:
        st.markdown(
            f"""
            <div class="metrora-sidebar-brand">
                <span class="metrora-sidebar-mark">{METRORA_LOGO_SVG}</span>
                <div>
                    <div class="metrora-sidebar-name">Metrora</div>
                    <div class="metrora-sidebar-subtitle">Cloud FinOps intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="metrora-sidebar-label">Explore Metrora</div>', unsafe_allow_html=True
        )
        for label, destination, slug in pages:
            if st.button(
                label,
                key=f"product_nav_{slug}",
                type="primary" if current_page == destination else "tertiary",
                width="stretch",
            ):
                set_product_route(destination)
                st.rerun()
        st.divider()
        st.markdown(
            """
            <div class="metrora-sidebar-guidance">
                <strong>Start with a scenario</strong>
                Choose a ready-to-share baseline, a data-quality issue, or a future-risk case.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Choose a demo scenario", key="product_nav_demo_cta", width="stretch"):
            set_product_route("Demo")
            st.rerun()
        st.caption("Synthetic local data · no sign-in required")


def render_sidebar(settings: Settings) -> None:
    """Render simple workspace navigation and current-source context."""
    import streamlit as st

    from .navigation import set_product_route, set_workspace_route

    with st.sidebar:
        st.markdown(
            f"""
            <div class="metrora-sidebar-brand">
                <span class="metrora-sidebar-mark">{METRORA_LOGO_SVG}</span>
                <div>
                    <div class="metrora-sidebar-name">Metrora</div>
                    <div class="metrora-sidebar-subtitle">Cloud FinOps intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        has_source = st.session_state.get("loaded_table") is not None
        has_model = st.session_state.get("normalized_table") is not None
        quality_report = st.session_state.get("quality_report")
        analysis_ready = bool(
            has_model and quality_report is not None and quality_report.ready_for_analysis
        )
        status_label = (
            "Analysis ready"
            if analysis_ready
            else "Review needed"
            if has_model
            else "Source loaded"
            if has_source
            else "Add billing data"
        )
        workspace_label = st.session_state.get(
            "demo_workspace",
            f"{settings.app_env.title()} workspace",
        )
        if st.session_state.get("demo_mode"):
            workspace_label = "Guided demo workspace"
        progress = 100 if analysis_ready else 66 if has_model else 33 if has_source else 8
        st.markdown(
            '<div class="metrora-sidebar-label">Current workspace</div>'
            '<div class="metrora-sidebar-status">'
            f'<div class="metrora-sidebar-status-line"><strong>{escape(workspace_label)}</strong>'
            f"<span>{escape(status_label)}</span></div>"
            '<div class="metrora-sidebar-progress" aria-hidden="true">'
            f'<i style="width:{progress}%"></i></div>'
            "<small>Local analytical session</small></div>",
            unsafe_allow_html=True,
        )

        pages = (
            ("Overview", "Home", "home"),
            ("Spend explorer", "Cost explorer", "cost_explorer"),
            ("Forecast & alerts", "Plans & alerts", "plans_alerts"),
            ("Decision register", "Decisions", "decisions"),
            ("Reports & exports", "Reports", "reports"),
            ("Data settings", "Advanced", "advanced"),
        )
        legacy_pages = {
            "Overview": "Home",
            "Spend explorer": "Cost explorer",
            "Forecast & alerts": "Plans & alerts",
            "Reports & exports": "Reports",
            "Data settings": "Advanced",
            "Data & quality": "Advanced",
            "Investigate": "Plans & alerts",
        }
        current_page = legacy_pages.get(
            st.session_state.get("workspace_page", "Home"),
            st.session_state.get("workspace_page", "Home"),
        )
        st.session_state["workspace_page"] = current_page
        st.markdown('<div class="metrora-sidebar-label">Workspace</div>', unsafe_allow_html=True)
        for label, destination, slug in pages:
            if st.button(
                label,
                key=f"workspace_nav_{slug}",
                type="primary" if current_page == destination else "tertiary",
                width="stretch",
            ):
                set_workspace_route(destination)
                st.rerun()
        st.markdown(
            """
            <div class="metrora-sidebar-guidance">
                <strong>Automated by default</strong>
                Overview handles the standard workflow. Open Data settings only for mapping
                exceptions, reconciliation detail, or model tuning.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        if st.button(
            "New analysis",
            key="new_analysis",
            disabled=not (has_source or has_model),
            width="stretch",
            help="Clear the current data and begin a new analysis.",
        ):
            reset_workspace_state()
            for key in ("demo_mode", "demo_scenario", "demo_workspace"):
                st.session_state.pop(key, None)
            set_workspace_route("Home", scenario_id=None)
            st.rerun()
        if st.button(
            "Back to product page",
            key="back_to_product_page",
            width="stretch",
            help="Return to the Metrora product page and access options.",
        ):
            reset_workspace_state()
            st.session_state.pop("demo_authenticated", None)
            st.session_state.pop("demo_mode", None)
            st.session_state.pop("demo_scenario", None)
            st.session_state.pop("demo_user_email", None)
            st.session_state.pop("demo_workspace", None)
            set_product_route("Demo")
            st.rerun()
        st.caption(f"Local calculations · AI: {settings.ai_provider}")


def reset_workspace_state() -> None:
    """Clear data and widget state while preserving app preferences."""
    import streamlit as st

    exact_keys = {
        "loaded_table",
        "data_profile",
        "column_mapping",
        "normalized_table",
        "normalized_source_key",
        "mapping_source_key",
        "quality_report",
        "quality_source_key",
        "warehouse_summary",
        "warehouse_source_key",
        "fact_pack",
        "summary_result",
        "decision_register",
        "analytics_filtered_table",
        "analytics_source_key",
        "budget_table",
        "budget_upload_key",
        "business_metrics_table",
        "business_upload_key",
        "workspace_page",
        "auto_attempted_source_key",
        "auto_analysis_message",
        "auto_analysis_error",
        "mapping_edit_mode",
        "summary_source_key",
        "billing_upload",
    }
    prefixes = (
        "mapping_",
        "analysis_",
        "breakdown_",
        "forecast_",
        "anomaly_",
        "allocation_",
        "business_metric_",
        "budget_",
        "business_upload_",
        "s3_upload_",
        "summary_button_",
        "download_",
    )
    for key in list(st.session_state):
        if key in exact_keys or key.startswith(prefixes):
            st.session_state.pop(key, None)
