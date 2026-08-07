"""Shared SpendArc visual identity and Streamlit presentation helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Settings


PRODUCT_NAME = "SpendArc"
PRODUCT_SUBTITLE = "Cloud FinOps intelligence"
PRODUCT_DESCRIPTION = (
    "Turn messy cloud billing exports into trusted cost signals, forecasts, and decisions."
)


SPENDARC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --spendarc-ink: #142033;
    --spendarc-muted: #66758a;
    --spendarc-line: #e6ebf2;
    --spendarc-paper: #f7f9fc;
    --spendarc-white: #ffffff;
    --spendarc-violet: #6658e8;
    --spendarc-blue: #2878f0;
    --spendarc-mint: #5bd5b5;
    --spendarc-lime: #d9f36b;
    --spendarc-coral: #ff816b;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 92% 2%, rgba(217, 243, 107, .16), transparent 22rem),
        radial-gradient(circle at 4% 24%, rgba(91, 213, 181, .10), transparent 26rem),
        var(--spendarc-paper);
}

[data-testid="stHeader"] {
    background: transparent;
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

.spendarc-sidebar-brand {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: .4rem 0 1.3rem;
}

.spendarc-sidebar-mark,
.spendarc-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    width: 2.65rem;
    height: 2.65rem;
    border-radius: .85rem;
    color: #141c2d;
    background: linear-gradient(135deg, var(--spendarc-lime), var(--spendarc-mint));
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: -.06em;
    box-shadow: 0 10px 22px rgba(91, 213, 181, .18);
}

.spendarc-sidebar-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -.04em;
}

.spendarc-sidebar-subtitle {
    color: #8fa1b9;
    font-size: .76rem;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.spendarc-sidebar-label {
    color: #8394ac;
    font-size: .69rem;
    font-weight: 700;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.spendarc-sidebar-status {
    margin: .65rem 0 1.25rem;
    padding: .75rem .85rem;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: .9rem;
    background: rgba(255,255,255,.05);
    color: #dbe5f3;
    font-size: .86rem;
}

.spendarc-sidebar-status strong {
    color: var(--spendarc-lime);
    font-weight: 600;
}

.spendarc-hero {
    position: relative;
    overflow: hidden;
    margin-bottom: 1.25rem;
    padding: 2.8rem 3rem 2.65rem;
    border: 1px solid rgba(255,255,255,.45);
    border-radius: 2rem;
    background:
        radial-gradient(circle at 86% 18%, rgba(217,243,107,.28), transparent 14rem),
        radial-gradient(circle at 16% 118%, rgba(91,213,181,.24), transparent 17rem),
        linear-gradient(120deg, #17223a 0%, #1c2b4a 58%, #29366a 100%);
    box-shadow: 0 24px 50px rgba(31, 48, 86, .16);
}

.spendarc-hero::after {
    position: absolute;
    right: 3.2rem;
    bottom: -5.5rem;
    width: 15rem;
    height: 15rem;
    border: 1px solid rgba(217,243,107,.22);
    border-radius: 50%;
    content: '';
}

.spendarc-kicker,
.spendarc-section-kicker {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .16em;
    text-transform: uppercase;
}

.spendarc-kicker {
    color: var(--spendarc-lime);
}

.spendarc-hero h1 {
    position: relative;
    z-index: 1;
    max-width: 760px;
    margin: .55rem 0 .65rem;
    color: #fff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.2rem, 5vw, 4.55rem);
    line-height: .98;
    letter-spacing: -.075em;
}

.spendarc-hero p {
    position: relative;
    z-index: 1;
    max-width: 650px;
    margin: 0;
    color: #c7d2e4;
    font-size: 1.05rem;
    line-height: 1.6;
}

.spendarc-hero-meta {
    position: relative;
    z-index: 1;
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1.5rem;
}

.spendarc-hero-meta span {
    padding: .42rem .7rem;
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 999px;
    background: rgba(255,255,255,.08);
    color: #e4ecf7;
    font-size: .73rem;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
}

.spendarc-section-kicker {
    margin: 1.7rem 0 .65rem;
    color: var(--spendarc-violet);
}

.spendarc-feature-card {
    min-height: 148px;
    padding: 1.2rem 1.25rem;
    border: 1px solid var(--spendarc-line);
    border-radius: 1.25rem;
    background: rgba(255,255,255,.82);
    box-shadow: 0 12px 30px rgba(43, 59, 87, .05);
}

.spendarc-feature-card .icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: .7rem;
    background: #edf0ff;
    color: var(--spendarc-violet);
    font-size: 1rem;
    font-weight: 700;
}

.spendarc-feature-card h3 {
    margin: .8rem 0 .3rem;
    color: var(--spendarc-ink);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    letter-spacing: -.035em;
}

.spendarc-feature-card p {
    margin: 0;
    color: var(--spendarc-muted);
    font-size: .94rem;
    line-height: 1.45;
}

.spendarc-workspace-heading {
    margin: 2rem 0 .85rem;
}

.spendarc-workspace-heading span {
    color: var(--spendarc-violet);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .16em;
}

.spendarc-workspace-heading h2 {
    margin: .35rem 0 .2rem;
    color: var(--spendarc-ink);
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(1.65rem, 3vw, 2.45rem);
    letter-spacing: -.06em;
}

.spendarc-workspace-heading p {
    margin: 0;
    color: var(--spendarc-muted);
}

.spendarc-stepbar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: .45rem;
    margin: .55rem 0 1.35rem;
}

.spendarc-stepbar-label {
    margin-right: .35rem;
    color: #8a96a8;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .12em;
}

.spendarc-step {
    display: inline-flex;
    align-items: center;
    gap: .38rem;
    padding: .38rem .62rem;
    border: 1px solid var(--spendarc-line);
    border-radius: 999px;
    background: rgba(255,255,255,.68);
    color: #98a4b5;
    font-size: .74rem;
    font-weight: 600;
}

.spendarc-step b {
    color: #aeb8c7;
    font-size: .65rem;
}

.spendarc-step.is-ready {
    border-color: rgba(91,213,181,.35);
    background: rgba(91,213,181,.12);
    color: #277c6a;
}

.spendarc-step.is-ready b {
    color: #277c6a;
}

.spendarc-empty-state {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    max-width: 720px;
    margin: 2rem auto;
    padding: 1.5rem;
    border: 1px solid var(--spendarc-line);
    border-radius: 1.25rem;
    background: rgba(255,255,255,.8);
    box-shadow: 0 14px 34px rgba(43, 59, 87, .05);
}

.spendarc-empty-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    flex: 0 0 auto;
    border-radius: .8rem;
    background: #edf0ff;
    color: var(--spendarc-violet);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.35rem;
    font-weight: 600;
}

.spendarc-empty-state h3 {
    margin: 0 0 .3rem;
    color: var(--spendarc-ink);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    letter-spacing: -.035em;
}

.spendarc-empty-state p {
    margin: 0 0 .7rem;
    color: var(--spendarc-muted);
    font-size: .96rem;
    line-height: 1.5;
}

.spendarc-next-step {
    color: var(--spendarc-violet);
    font-size: .78rem;
    font-weight: 700;
}

[data-testid="stMetric"] {
    min-height: 110px;
    padding: 1rem 1.05rem;
    border: 1px solid var(--spendarc-line);
    border-radius: 1rem;
    background: rgba(255,255,255,.88);
    box-shadow: 0 10px 22px rgba(43, 59, 87, .04);
}

[data-testid="stMetricLabel"] {
    color: var(--spendarc-muted);
    font-size: .76rem;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--spendarc-ink);
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -.045em;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 2.65rem;
    border: 0;
    border-radius: .8rem;
    background: var(--spendarc-violet);
    color: #fff;
    font-weight: 600;
    box-shadow: 0 8px 18px rgba(102, 88, 232, .18);
    transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border: 0;
    background: #5649d1;
    color: #fff;
    box-shadow: 0 12px 22px rgba(102, 88, 232, .27);
    transform: translateY(-1px);
}

[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #b5c0d3;
    border-radius: 1.1rem;
    background: rgba(255,255,255,.74);
}

.stTabs [data-baseweb="tab-list"] {
    gap: .35rem;
    border-bottom: 1px solid var(--spendarc-line);
}

.stTabs [data-baseweb="tab"] {
    padding: .6rem .9rem;
    color: var(--spendarc-muted);
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: var(--spendarc-violet);
}

.stExpander {
    border: 1px solid var(--spendarc-line);
    border-radius: .95rem;
    background: rgba(255,255,255,.62);
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--spendarc-line);
    border-radius: .85rem;
    overflow: hidden;
}

@media (max-width: 800px) {
    .block-container { padding: 1.2rem 1rem 3rem; }
    .spendarc-hero { padding: 2rem 1.35rem; border-radius: 1.35rem; }
    .spendarc-hero h1 { font-size: 2.65rem; }
}
</style>
"""


SPENDARC_DARK_CSS = """
<style>
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

.spendarc-workspace-heading h2,
.spendarc-feature-card h3,
.spendarc-empty-state h3,
[data-testid="stMetricValue"] {
    color: #f4f7fb;
}

.spendarc-workspace-heading p,
.spendarc-feature-card p,
.spendarc-empty-state p,
[data-testid="stCaptionContainer"] {
    color: #b2bfd1;
}

.spendarc-feature-card,
.spendarc-empty-state,
[data-testid="stMetric"] {
    border-color: #2a3850;
    background: rgba(24, 36, 56, .86);
    box-shadow: 0 14px 34px rgba(0, 0, 0, .18);
}

.spendarc-feature-card .icon,
.spendarc-empty-icon {
    background: rgba(102,88,232,.22);
    color: #b8b1ff;
}

.spendarc-step {
    border-color: #2a3850;
    background: rgba(24,36,56,.82);
    color: #9baac0;
}

.spendarc-step.is-ready {
    border-color: rgba(91,213,181,.4);
    background: rgba(91,213,181,.12);
    color: #8ae7d0;
}

[data-testid="stFileUploaderDropzone"] {
    border-color: #53627a;
    background: rgba(24,36,56,.72);
}

.stExpander,
div[data-testid="stDataFrame"] {
    border-color: #2a3850;
    background: rgba(17, 27, 44, .7);
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
</style>
"""


def inject_styles(dark_mode: bool = False) -> None:
    """Inject the SpendArc theme and optional dark-mode overrides."""
    import streamlit as st

    st.markdown(SPENDARC_CSS, unsafe_allow_html=True)
    if dark_mode:
        st.markdown(SPENDARC_DARK_CSS, unsafe_allow_html=True)


def render_brand_header() -> None:
    """Render the product hero and high-level capability cards."""
    import streamlit as st

    st.markdown(
        """
        <section class="spendarc-hero">
            <div class="spendarc-kicker">SpendArc · cloud FinOps intelligence</div>
            <h1>Turn cloud spend into decisions.</h1>
            <p>
                Validate the data, find the signal, and give finance and engineering teams
                a shared view of cost, risk, and what to do next.
            </p>
            <div class="spendarc-hero-meta">
                <span>Local-first workflow</span>
                <span>Evidence before AI</span>
                <span>Built for FinOps teams</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="spendarc-section-kicker">The SpendArc loop</div>',
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
                <div class="spendarc-feature-card">
                    <div class="icon">{number}</div>
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar(settings: Settings) -> None:
    """Render product identity and workflow context in the sidebar."""
    import streamlit as st

    with st.sidebar:
        st.markdown(
            """
            <div class="spendarc-sidebar-brand">
                <span class="spendarc-sidebar-mark">SA</span>
                <div>
                    <div class="spendarc-sidebar-name">SpendArc</div>
                    <div class="spendarc-sidebar-subtitle">Cloud FinOps intelligence</div>
                </div>
            </div>
            <div class="spendarc-sidebar-label">Workspace</div>
            """,
            unsafe_allow_html=True,
        )
        has_source = st.session_state.get("loaded_table") is not None
        has_model = st.session_state.get("normalized_table") is not None
        status_label = "Analysis ready" if has_model else "Source loaded" if has_source else "Ready"
        status = (
            f'<div class="spendarc-sidebar-status"><strong>● {status_label}</strong><br>'
            f"{settings.app_env.title()} workspace<br>AI: {settings.ai_provider}</div>"
        )
        st.markdown(status, unsafe_allow_html=True)
        st.markdown('<div class="spendarc-sidebar-label">Workflow</div>', unsafe_allow_html=True)
        st.markdown(
            """
            1. **Load** a billing export
            2. **Map** its semantic fields
            3. **Validate** the financial data
            4. **Explore** spend and ownership
            5. **Plan** with budgets and forecasts
            6. **Share** an evidence-backed brief
            """
        )
        st.divider()
        st.toggle(
            "Dark mode",
            key="dark_mode",
            help="Use a lower-glare dark workspace while keeping the same data and filters.",
        )
        if st.button(
            "Reset workspace",
            disabled=not (has_source or has_model),
            width="stretch",
            help="Clear the current upload and analysis state without changing your settings.",
        ):
            reset_workspace_state()
            st.rerun()
        with st.expander("How to use SpendArc"):
            st.markdown(
                "Upload one billing file, confirm the suggested mapping, then use the tabs "
                "from left to right. Optional budgets and business metrics appear only after "
                "your spend view is ready."
            )
        st.caption(
            "SpendArc keeps deterministic calculations at the center. AI explains "
            "the evidence; it does not invent the numbers."
        )


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
