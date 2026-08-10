"""Shared Metrora visual identity and Streamlit presentation helpers."""

# ruff: noqa: E501

from __future__ import annotations

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

[data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button,
[data-testid="stFileUploaderDropzone"] button {
    border-color: #9bb8ff !important;
    background: #9bb8ff !important;
    color: #08101d !important;
    box-shadow: 0 9px 24px rgba(117, 150, 223, .18) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stButton"] button[kind="primary"] *,
[data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button *,
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

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}
</style>
"""


def inject_styles() -> None:
    """Inject Metrora's single dark application theme."""
    import streamlit as st

    st.markdown(METRORA_CSS, unsafe_allow_html=True)
    st.markdown(METRORA_DARK_CSS, unsafe_allow_html=True)
    st.markdown(METRORA_REFINED_CSS, unsafe_allow_html=True)


def apply_plotly_theme(figure):
    """Apply Metrora's fixed dark chart palette."""
    text = "#f2f5fb"
    muted = "#9eaabd"
    grid = "rgba(158,170,189,.16)"
    line = "#273347"
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": text, "family": "DM Sans"},
        title_font={"color": text, "family": "Outfit"},
        legend={"font": {"color": muted}},
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


def render_sidebar(settings: Settings) -> None:
    """Render simple workspace navigation and current-source context."""
    import streamlit as st

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
        st.markdown(
            '<div class="metrora-sidebar-label">Current workspace</div>'
            f'<div class="metrora-sidebar-status"><strong>● {status_label}</strong><br>'
            f"{workspace_label}</div>",
            unsafe_allow_html=True,
        )

        pages = (
            ("Home", "home"),
            ("Cost explorer", "cost_explorer"),
            ("Plans & alerts", "plans_alerts"),
            ("Reports", "reports"),
            ("Advanced", "advanced"),
        )
        legacy_pages = {
            "Overview": "Home",
            "Data & quality": "Advanced",
            "Investigate": "Plans & alerts",
            "Reports & exports": "Reports",
        }
        current_page = legacy_pages.get(
            st.session_state.get("workspace_page", "Home"),
            st.session_state.get("workspace_page", "Home"),
        )
        st.session_state["workspace_page"] = current_page
        st.markdown('<div class="metrora-sidebar-label">Workspace</div>', unsafe_allow_html=True)
        for label, slug in pages:
            if st.button(
                label,
                key=f"workspace_nav_{slug}",
                type="primary" if current_page == label else "tertiary",
                width="stretch",
            ):
                st.session_state["workspace_page"] = label
                st.rerun()
        st.markdown(
            """
            <div class="metrora-sidebar-guidance">
                Home handles the standard workflow automatically. Open Advanced only for
                mapping exceptions, reconciliation detail, or model tuning.
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
            st.session_state["workspace_page"] = "Home"
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
            st.session_state.pop("demo_user_email", None)
            st.session_state.pop("demo_workspace", None)
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
