import streamlit as st
from typing import Dict, List
import html

'''
### Purpose:
This is the **front-end of the system**, built using Streamlit.

### Responsibilities:
- Display:
  - category selector (sweet / salty)
  - ranked trend cards
  - detail view for each trend
- Show:
  - trend score
  - opportunity level (early / saturated)
  - POP presence
  - final recommendation (build vs distribute)

### What it should NOT do:
- No heavy logic
- No scoring calculations
- No data processing

### Why it matters:
POP stakeholders need a **clear, visual decision tool**, not raw data.
'''

from sample_data import POP_PRODUCTS
from scoring import score_sample_trends


st.set_page_config(
    page_title="POP Snack Strategy Engine",
    page_icon="🍬",
    layout="wide",
)


PALETTE = {
    "ink": "#314967",
    "muted": "#7E90AA",
    "line": "#D6DEEA",
    "soft": "#F4F7FB",
    "panel": "#FFFFFF",
    "accent": "#86AFCF",
    "accent_dark": "#628CAF",
    "sand": "#F7F3EE",
    "sweet": "#F2C9B8",
    "salty": "#C8D7C4",
    "good": "#5E8E74",
    "warn": "#B58A4B",
}

PERIOD_LABELS = ["Q1", "Q2", "Q3", "Q4", "Q5"]


@st.cache_data
def load_trend_data() -> List[Dict]:
    return score_sample_trends()


def initialize_state() -> None:
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = "sweet"

    if "selected_trend_name" not in st.session_state:
        trends = load_trend_data()
        default_trend = next(
            (trend["name"] for trend in trends if trend["category"] == st.session_state.selected_category),
            trends[0]["name"],
        )
        st.session_state.selected_trend_name = default_trend


def set_category(category: str) -> None:
    st.session_state.selected_category = category
    category_trends = get_category_trends(category)
    if category_trends:
        st.session_state.selected_trend_name = category_trends[0]["name"]


def select_trend(trend_name: str) -> None:
    st.session_state.selected_trend_name = trend_name


def get_category_trends(category: str) -> List[Dict]:
    trends = [trend for trend in load_trend_data() if trend["category"] == category]
    return sorted(trends, key=lambda item: item["final_score"], reverse=True)


def get_selected_trend(category_trends: List[Dict]) -> Dict:
    selected_name = st.session_state.selected_trend_name
    return next(
        (trend for trend in category_trends if trend["name"] == selected_name),
        category_trends[0],
    )


def build_chart_svg(trend: Dict, height: int = 240) -> str:
    width = 700
    padding_left = 56
    padding_right = 18
    padding_top = 20
    padding_bottom = 44
    values = [float(value) for value in trend["growth"]]
    min_value = min(values)
    max_value = max(values)
    range_value = max(max_value - min_value, 1.0)
    usable_width = width - padding_left - padding_right
    usable_height = height - padding_top - padding_bottom

    points = []
    for index, value in enumerate(values):
        x = padding_left + (usable_width * index / max(len(values) - 1, 1))
        normalized = (value - min_value) / range_value
        y = padding_top + usable_height - (normalized * usable_height)
        points.append((round(x, 2), round(y, 2)))

    polyline_points = " ".join(f"{x},{y}" for x, y in points)
    area_points = " ".join(
        [f"{padding_left},{height - padding_bottom}"]
        + [f"{x},{y}" for x, y in points]
        + [f"{points[-1][0]},{height - padding_bottom}"]
    )

    vertical_lines = []
    horizontal_lines = []
    for tick in range(len(values)):
        x = padding_left + (usable_width * tick / max(len(values) - 1, 1))
        vertical_lines.append(
            f"<line x1='{x}' y1='{padding_top}' x2='{x}' y2='{height - padding_bottom}' "
            f"stroke='#E6EDF6' stroke-width='1' />"
        )

    for tick in range(5):
        y = padding_top + (usable_height * tick / 4)
        horizontal_lines.append(
            f"<line x1='{padding_left}' y1='{y}' x2='{width - padding_right}' y2='{y}' "
            f"stroke='#E6EDF6' stroke-width='1' />"
        )

    labels = []
    for index, period in enumerate(PERIOD_LABELS[: len(values)]):
        x = padding_left + (usable_width * index / max(len(values) - 1, 1))
        labels.append(
            f"<text x='{x}' y='{height - 16}' text-anchor='middle' fill='{PALETTE['muted']}' "
            f"font-size='12' font-family='sans-serif'>{html.escape(period)}</text>"
        )

    return f"""
    <div class="svg-chart-wrap">
        <svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img"
             aria-label="{html.escape(trend['name'])} trend chart">
            <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="white" />
            {''.join(vertical_lines)}
            {''.join(horizontal_lines)}
            <text x="10" y="24" fill="{PALETTE['muted']}" font-size="12" font-weight="700"
                  font-family="sans-serif">BETTER</text>
            <text x="6" y="{height - 48}" fill="{PALETTE['muted']}" font-size="12" font-weight="700"
                  font-family="sans-serif">RISKIER</text>
            <polygon points="{area_points}" fill="{PALETTE['accent']}" opacity="0.22"></polygon>
            <polyline points="{polyline_points}" fill="none" stroke="{PALETTE['accent_dark']}"
                      stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
            {''.join(labels)}
        </svg>
    </div>
    """


def build_fun_facts(trend: Dict) -> List[str]:
    matching_products = trend.get("matched_pop_products", [])
    matched_names = ", ".join(product["name"] for product in matching_products[:2]) or "none yet"
    whitespace_tags = trend.get("whitespace_tags", [])
    whitespace = ", ".join(whitespace_tags[:3]) if whitespace_tags else "limited whitespace"

    facts = [
        f"POP already has adjacency through {matched_names}.",
        f"This trend is currently {trend['timing_stage'].lower()}-stage, which gives it a {trend['timing_window'].lower()}.",
        f"The biggest whitespace signals are {whitespace}.",
    ]

    if trend.get("strategic_fit_tags"):
        facts.append(
            "It overlaps with POP-friendly ingredients such as "
            + ", ".join(trend["strategic_fit_tags"][:3])
            + "."
        )

    return facts


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(134,175,207,0.16), transparent 25%),
                linear-gradient(180deg, {PALETTE["sand"]} 0%, #FCFDFF 22%, #F6F9FC 100%);
        }}
        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 4rem;
            max-width: 1180px;
        }}
        h1, h2, h3 {{
            color: {PALETTE["ink"]};
            letter-spacing: 0.02em;
        }}
        p, li, label, div {{
            color: {PALETTE["ink"]};
        }}
        .browser-shell {{
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(118, 140, 171, 0.28);
            border-radius: 26px;
            box-shadow: 0 20px 50px rgba(74, 100, 132, 0.08);
            overflow: hidden;
            backdrop-filter: blur(12px);
        }}
        .browser-top {{
            padding: 0.85rem 1.15rem;
            border-bottom: 1px solid {PALETTE["line"]};
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(180deg, rgba(244,247,251,0.96), rgba(255,255,255,0.96));
        }}
        .browser-dots {{
            display: flex;
            gap: 0.45rem;
        }}
        .browser-dots span {{
            width: 12px;
            height: 12px;
            display: inline-block;
            border-radius: 999px;
            background: #c8d0dc;
        }}
        .browser-title {{
            font-size: 0.76rem;
            letter-spacing: 0.24em;
            color: {PALETTE["muted"]};
            text-transform: uppercase;
            font-weight: 700;
        }}
        .browser-pill {{
            border: 1px solid {PALETTE["line"]};
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.72rem;
            color: {PALETTE["ink"]};
            background: rgba(255,255,255,0.9);
        }}
        .hero-wrap {{
            padding: 3.2rem 2rem 2.4rem 2rem;
            text-align: center;
        }}
        .eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.22em;
            color: {PALETTE["muted"]};
            font-size: 0.74rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }}
        .hero-title {{
            font-size: clamp(2.2rem, 4vw, 4rem);
            font-weight: 700;
            line-height: 1.05;
            margin-bottom: 0.6rem;
        }}
        .hero-copy {{
            max-width: 780px;
            margin: 0 auto;
            color: {PALETTE["muted"]};
            font-size: 1.05rem;
            line-height: 1.7;
        }}
        .hero-note {{
            margin-top: 1.4rem;
            font-size: 0.98rem;
            color: {PALETTE["ink"]};
        }}
        .section-shell {{
            margin-top: 1.3rem;
            padding: 1.4rem;
        }}
        .section-title {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }}
        .section-copy {{
            color: {PALETTE["muted"]};
            margin-bottom: 1.2rem;
        }}
        .metric-strip {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1rem 0 1.4rem 0;
        }}
        .metric-card {{
            background: {PALETTE["soft"]};
            border: 1px solid {PALETTE["line"]};
            border-radius: 20px;
            padding: 1rem;
        }}
        .metric-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: {PALETTE["muted"]};
            margin-bottom: 0.55rem;
        }}
        .metric-value {{
            font-size: 1.7rem;
            font-weight: 700;
            color: {PALETTE["ink"]};
        }}
        .metric-sub {{
            margin-top: 0.3rem;
            font-size: 0.92rem;
            color: {PALETTE["muted"]};
        }}
        .trend-card {{
            background: rgba(255,255,255,0.92);
            border: 1px solid {PALETTE["line"]};
            border-radius: 24px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .trend-title {{
            font-size: 1.55rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }}
        .trend-meta {{
            color: {PALETTE["muted"]};
            line-height: 1.65;
        }}
        .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.85rem;
        }}
        .chip {{
            padding: 0.34rem 0.7rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            border: 1px solid {PALETTE["line"]};
            background: {PALETTE["soft"]};
            color: {PALETTE["ink"]};
        }}
        .detail-panel {{
            background: rgba(255,255,255,0.9);
            border: 1px solid {PALETTE["line"]};
            border-radius: 24px;
            padding: 1.1rem 1.2rem;
            height: 100%;
        }}
        .detail-subtitle {{
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: {PALETTE["muted"]};
            font-size: 0.76rem;
            margin-bottom: 0.55rem;
            font-weight: 700;
        }}
        .detail-title {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.65rem;
        }}
        .decision-card {{
            background: linear-gradient(180deg, rgba(134,175,207,0.12), rgba(255,255,255,0.88));
            border: 1px solid {PALETTE["line"]};
            border-radius: 24px;
            padding: 1.2rem;
            margin-top: 1.1rem;
        }}
        .decision-question {{
            font-weight: 700;
            margin-bottom: 0.3rem;
        }}
        .small-note {{
            color: {PALETTE["muted"]};
            font-size: 0.92rem;
        }}
        div[data-testid="stButton"] > button {{
            border-radius: 999px;
            border: 1px solid {PALETTE["line"]};
            background: white;
            color: {PALETTE["ink"]};
            font-weight: 600;
            padding: 0.65rem 1rem;
            box-shadow: none;
        }}
        div[data-testid="stButton"] > button:hover {{
            border-color: {PALETTE["accent_dark"]};
            color: {PALETTE["accent_dark"]};
        }}
        @media (max-width: 900px) {{
            .metric-strip {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="browser-shell">
            <div class="browser-top">
                <div class="browser-dots"><span></span><span></span><span></span></div>
                <div class="browser-title">Navigation Menu</div>
                <div class="browser-pill">Snack</div>
            </div>
            <div class="hero-wrap">
                <div class="eyebrow">POP Flavor Gap Detector</div>
                <div class="hero-title">Ask me about a trend.</div>
                <div class="hero-copy">
                    Pick sweet or salty to see which shelf-stable snack opportunities are growing,
                    where POP has whitespace, and whether the company still has enough time to act.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1.4, 2.6, 1.4])
    with center:
        sweet_col, salty_col = st.columns(2)
        with sweet_col:
            if st.button("Option 1: sweet", use_container_width=True):
                set_category("sweet")
                st.rerun()
        with salty_col:
            if st.button("Option 2: salty", use_container_width=True):
                set_category("salty")
                st.rerun()

    current = st.session_state.selected_category.title()
    st.markdown(
        f"<p class='hero-note' style='text-align:center;'>Currently viewing <strong>{current}</strong> snacks.</p>",
        unsafe_allow_html=True,
    )


def render_graph_section(category_trends: List[Dict]) -> None:
    category_label = st.session_state.selected_category.title()
    st.markdown(
        f"""
        <div class="browser-shell section-shell">
            <div class="section-title">{category_label} Trend Graphs</div>
            <div class="section-copy">
                Every row shows a POP-relevant snack trend in this category, how strongly it is growing,
                and the strategic score that balances momentum, feasibility, whitespace, and timing risk.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for trend in category_trends:
        chart_col, detail_col = st.columns([1.4, 1], gap="large")

        with chart_col:
            st.markdown("<div class='trend-card'>", unsafe_allow_html=True)
            st.markdown(build_chart_svg(trend, height=220), unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="small-note">
                    Better for POP when the curve is rising while the timing window is still open.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with detail_col:
            st.markdown(
                f"""
                <div class="trend-card">
                    <div class="detail-subtitle">{category_label} Snack</div>
                    <div class="trend-title">{trend["name"]}</div>
                    <div class="trend-meta">
                        {trend["description"]}<br><br>
                        Final score: <strong>{trend["final_score"]}/100</strong><br>
                        Opportunity: <strong>{trend["opportunity_level"]}</strong><br>
                        Action: <strong>{trend["recommended_action"].title()}</strong>
                    </div>
                    <div class="chip-row">
                        <span class="chip">Timing {trend["timing_stage"]}</span>
                        <span class="chip">Feasibility {trend["feasibility_score"]}/100</span>
                        <span class="chip">POP Presence {trend["pop_presence"]}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(f"Open {trend['name']}", key=f"open-{trend['name']}", use_container_width=True):
                select_trend(trend["name"])
                st.rerun()


def render_detail_section(selected_trend: Dict) -> None:
    fun_facts = build_fun_facts(selected_trend)
    promising = "Yes" if selected_trend["opportunity_level"] in {"High", "Medium"} else "Not yet"
    blocking_constraint = (
        ", ".join(selected_trend["constraint_flags"][:2]) if selected_trend["constraint_flags"] else "No major blocker"
    )

    st.markdown(
        f"""
        <div class="browser-shell section-shell">
            <div class="browser-top">
                <div class="browser-dots"><span></span><span></span><span></span></div>
                <div class="browser-title">{selected_trend["name"]}</div>
                <div class="browser-pill">{selected_trend["category"].title()}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col, detail_col = st.columns([1.6, 1], gap="large")

    with chart_col:
        st.markdown("<div class='detail-panel'>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="detail-subtitle">Close Up</div>
            <div class="detail-title">{selected_trend["name"]}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(build_chart_svg(selected_trend, height=300), unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="chip-row">
                <span class="chip">Trend Strength {selected_trend["trend_strength_score"]}</span>
                <span class="chip">Momentum {selected_trend["trend_momentum_score"]}</span>
                <span class="chip">Gap {selected_trend["gap_opportunity_score"]}</span>
                <span class="chip">Penalty {selected_trend["saturation_penalty"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with detail_col:
        st.markdown(
            f"""
            <div class="detail-panel">
                <div class="detail-subtitle">Trend Snapshot</div>
                <div class="detail-title">{selected_trend["name"]}</div>
                <ul>
                    {''.join(f"<li>{fact}</li>" for fact in fun_facts)}
                </ul>
                <p><strong>Description:</strong> {selected_trend["description"]}</p>
                <p><strong>Details:</strong> {selected_trend["forecast_summary"]}</p>
                <p><strong>Constraints:</strong> {selected_trend["feasibility_summary"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="decision-card">
            <div class="detail-title" style="font-size:1.35rem;">{selected_trend["name"]} Clicked On</div>
            <p class="decision-question">Is this trend growth promising for POP?</p>
            <p>{promising}. {selected_trend["scoring_summary"]}</p>
            <p class="decision-question">Should POP distribute an existing product or develop its own?</p>
            <p>{selected_trend["recommended_action"].title()}. {selected_trend["reasoning"]}</p>
            <p class="decision-question">What constraint is blocking it?</p>
            <p>{blocking_constraint}.</p>
            <p class="decision-question">Why now?</p>
            <p>{selected_trend["timing_guidance"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pop_products(category: str) -> None:
    category_products = [product["name"] for product in POP_PRODUCTS if product["category"] == category]
    if not category_products:
        return

    st.markdown(
        f"""
        <div class="small-note" style="margin-top:0.75rem;">
            Current POP products in this lane: {", ".join(category_products)}.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    initialize_state()
    inject_styles()

    category = st.session_state.selected_category
    category_trends = get_category_trends(category)
    selected_trend = get_selected_trend(category_trends)

    render_hero()
    render_pop_products(category)

    metric_columns = st.columns(4)
    metrics = [
        ("Viewing", category.title(), "Current snack lane"),
        ("Tracked Trends", str(len(category_trends)), "Ranked opportunities"),
        ("Best Score", f"{category_trends[0]['final_score']}/100", category_trends[0]["name"]),
        ("Selected", selected_trend["timing_stage"], "Timing stage"),
    ]
    for column, (label, value, sub) in zip(metric_columns, metrics):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_graph_section(category_trends)
    render_detail_section(selected_trend)


if __name__ == "__main__":
    main()









