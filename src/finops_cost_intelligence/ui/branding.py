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
    font-size: .88rem;
    line-height: 1.45;
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


def inject_styles() -> None:
    """Inject the SpendArc theme once at the top of the Streamlit app."""
    import streamlit as st

    st.markdown(SPENDARC_CSS, unsafe_allow_html=True)


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
        status = (
            f'<div class="spendarc-sidebar-status"><strong>● Ready</strong><br>'
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
        st.caption(
            "SpendArc keeps deterministic calculations at the center. AI explains "
            "the evidence; it does not invent the numbers."
        )
