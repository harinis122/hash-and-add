import html
from typing import Dict, List

import streamlit as st

from sample_data import POP_PRODUCTS
from scoring import score_sample_trends

st.set_page_config(
    page_title="POP Strategy Engine",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -- Brand palette -------------------------------------------------------------
P = dict(
    pop="#2E6B90",
    pop_dark="#1a4a66",
    pop_light="#4A90B8",
    pop_xlight="#e8f3f9",
    pop_xxlight="#f4f9fd",
    ink="#1a2e3d",
    muted="#5a7a8a",
    line="#d0e4ef",
    surface="#ffffff",
    bg="#f0f7fc",
    sweet_dark="#b8714a",
    sweet_bg="#fdf5f0",
    salty_dark="#3d6b38",
    salty_bg="#f2f8f1",
    good="#2e7d5e",
    warn="#b87a2a",
    danger="#a03030",
)

PERIODS = ["Q1", "Q2", "Q3", "Q4", "Q5"]
PAGE_GUTTER = "clamp(1.25rem, 3vw, 2.75rem)"
CONTENT_MAX_WIDTH = "1320px"

RANKING_META = {
    "score": {"label": "Overall Score", "field": "final_score", "unit": "/ 100", "color": P["pop"]},
    "momentum": {
        "label": "Momentum",
        "field": "trend_momentum_score",
        "unit": "/ 100",
        "color": P["good"],
    },
    "opportunity": {
        "label": "Opportunity",
        "field": "gap_opportunity_score",
        "unit": "/ 100",
        "color": P["warn"],
    },
}

GLOBAL_Y_MIN = 0
GLOBAL_Y_MAX = None


@st.cache_data
def load_trends() -> List[Dict]:
    return score_sample_trends()


def _compute_global_scale(trends: List[Dict]):
    global GLOBAL_Y_MAX
    if GLOBAL_Y_MAX is None:
        all_vals = [float(v) for t in trends for v in t["growth"]]
        GLOBAL_Y_MAX = max(all_vals) * 1.10


def _init_state():
    defaults = dict(
        page="home",
        category="sweet",
        selected_trend=None,
        sort_by="score",
        ranking_metric="score",
        page_history=[],
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _route_snapshot():
    return {
        "page": st.session_state.page,
        "category": st.session_state.category,
        "selected_trend": st.session_state.selected_trend,
        "sort_by": st.session_state.sort_by,
        "ranking_metric": st.session_state.ranking_metric,
    }


def _restore_route(snapshot: Dict):
    for k, v in snapshot.items():
        st.session_state[k] = v


def _go(page: str, **kwargs):
    if st.session_state.page != page:
        history = list(st.session_state.page_history)
        history.append(_route_snapshot())
        st.session_state.page_history = history

    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


def _back(default_page: str, **default_kwargs):
    history = list(st.session_state.page_history)
    if history:
        snapshot = history.pop()
        st.session_state.page_history = history
        _restore_route(snapshot)
        st.rerun()
    _go(default_page, **default_kwargs)


def _esc(s):
    return html.escape(str(s))


def _score_color(s) -> str:
    s = int(s) if s else 0
    if s >= 75:
        return P["good"]
    if s >= 55:
        return P["warn"]
    return P["danger"]


def _score_bg(s) -> str:
    s = int(s) if s else 0
    if s >= 75:
        return "#e8f5ef"
    if s >= 55:
        return "#fef3e2"
    return "#fdeaea"


def _cat_color(cat):
    return P["sweet_dark"] if cat == "sweet" else P["salty_dark"]


def _cat_bg(cat):
    return P["sweet_bg"] if cat == "sweet" else P["salty_bg"]


def _sorted_trends(trends, cat, sort_by):
    filtered = [t for t in trends if t["category"] == cat]
    if sort_by == "score":
        return sorted(filtered, key=lambda t: t["final_score"], reverse=True)
    if sort_by == "momentum":
        return sorted(filtered, key=lambda t: t["trend_momentum_score"], reverse=True)
    if sort_by == "opportunity":
        order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(filtered, key=lambda t: order.get(t["opportunity_level"], 2))
    return filtered


def _build_chart(trend: Dict, w: int = 480, h: int = 180, color: str = "#2E6B90") -> str:
    vals = [float(v) for v in trend["growth"]]
    lo = GLOBAL_Y_MIN
    hi = GLOBAL_Y_MAX or (max(vals) * 1.10)
    rng = max(hi - lo, 1.0)

    pl, pr, pt, pb = 42, 12, 16, 32
    uw, uh = w - pl - pr, h - pt - pb
    n = len(vals)

    pts = []
    for i, v in enumerate(vals):
        x = pl + uw * i / max(n - 1, 1)
        y = pt + uh - (v - lo) / rng * uh
        pts.append((round(x, 1), round(y, 1)))

    poly = " ".join(f"{x},{y}" for x, y in pts)
    area = f"{pl},{h - pb} " + " ".join(f"{x},{y}" for x, y in pts) + f" {pts[-1][0]},{h - pb}"

    grid = ""
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        gy = pt + uh * (1 - frac)
        val = int(lo + rng * frac)
        grid += (
            f"<line x1='{pl}' y1='{gy}' x2='{w - pr}' y2='{gy}' "
            f"stroke='#e8f0f6' stroke-width='1'/>"
            f"<text x='{pl - 5}' y='{gy + 4}' text-anchor='end' "
            f"fill='#aac0cc' font-size='10' font-family='DM Sans,sans-serif'>{val}</text>"
        )

    xlabels = ""
    for i, p in enumerate(pts):
        label = PERIODS[i] if i < len(PERIODS) else ""
        xlabels += (
            f"<text x='{p[0]}' y='{h - 6}' text-anchor='middle' "
            f"fill='#8aabbc' font-size='10' font-family='DM Sans,sans-serif'>{label}</text>"
        )

    dots = ""
    for i, p in enumerate(pts):
        r = 4 if i == n - 1 else 2.5
        op = 1.0 if i == n - 1 else 0.5
        dots += f"<circle cx='{p[0]}' cy='{p[1]}' r='{r}' fill='{color}' opacity='{op}'/>"

    return (
        f"<svg viewBox='0 0 {w} {h}' width='100%' height='{h}' "
        f"xmlns='http://www.w3.org/2000/svg'>"
        f"{grid}"
        f"<polygon points='{area}' fill='{color}' opacity='0.12'/>"
        f"<polyline points='{poly}' fill='none' stroke='{color}' "
        f"stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>"
        f"{dots}{xlabels}</svg>"
    )


def _inject_css():
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Serif+Display:ital@0;1&display=swap');

:root {{
  --pop:{P["pop"]};--pop-dark:{P["pop_dark"]};--pop-light:{P["pop_light"]};
  --pop-xlight:{P["pop_xlight"]};--pop-xxlight:{P["pop_xxlight"]};
  --ink:{P["ink"]};--muted:{P["muted"]};--line:{P["line"]};
  --bg:{P["bg"]};--content-max:{CONTENT_MAX_WIDTH};
  --sweet-dark:{P["sweet_dark"]};--sweet-bg:{P["sweet_bg"]};
  --salty-dark:{P["salty_dark"]};--salty-bg:{P["salty_bg"]};
  --good:{P["good"]};--warn:{P["warn"]};--danger:{P["danger"]};
}}

html,body,.stApp {{
  font-family:'DM Sans',sans-serif !important;
  background:var(--bg) !important;
  color:var(--ink) !important;
}}

#MainMenu,footer,header {{visibility:hidden;}}
.block-container {{
  padding:0 {PAGE_GUTTER} 2.25rem !important;
  max-width:var(--content-max) !important;
  margin:0 auto !important;
}}
section[data-testid="stSidebar"] {{display:none;}}

div[data-testid="stButton"] > button {{
  border-radius:999px !important;
  border:1.5px solid var(--line) !important;
  background:white !important;
  color:var(--ink) !important;
  font-family:'DM Sans',sans-serif !important;
  font-weight:500 !important;
  font-size:0.88rem !important;
  padding:0.45rem 1.1rem !important;
  height:38px !important;
  line-height:1 !important;
  box-shadow:none !important;
  transition:all .18s !important;
}}
div[data-testid="stButton"] > button:hover {{
  border-color:var(--pop-light) !important;
  color:var(--pop) !important;
  background:var(--pop-xxlight) !important;
}}

.tab-active div[data-testid="stButton"] > button {{
  background:var(--pop) !important;
  color:white !important;
  border-color:var(--pop) !important;
}}

.pill-base div[data-testid="stButton"] > button {{
  font-size:0.82rem !important;
  height:38px !important;
  color:var(--muted) !important;
}}
.pill-active div[data-testid="stButton"] > button {{
  background:var(--pop) !important;
  color:white !important;
  border-color:var(--pop) !important;
  font-size:0.82rem !important;
  height:38px !important;
}}

.btn-sweet div[data-testid="stButton"] > button {{
  background:var(--sweet-bg) !important;
  color:var(--sweet-dark) !important;
  border-color:var(--sweet-dark) !important;
}}
.btn-salty div[data-testid="stButton"] > button {{
  background:var(--salty-bg) !important;
  color:var(--salty-dark) !important;
  border-color:var(--salty-dark) !important;
}}

h1,h2,h3,h4 {{
  font-family:'DM Serif Display',serif !important;
  color:var(--ink) !important;
}}
hr {{ border:none; border-top:1px solid var(--line); margin:0; }}
[data-testid="column"] {{ padding:0 0.4rem; }}

#nav-button-row {{
  margin-top:10px;
  padding:0 {PAGE_GUTTER};
  margin-bottom:9px;
  position:relative;
  z-index:20;
}}
#nav-button-row [data-testid="column"] {{
  padding:0 0.2rem !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def _render_nav():
    page = st.session_state.page

    st.markdown(
        f"""
<div style="
  background:rgba(255,255,255,0.97);
  border-bottom:1px solid {P['line']};
  backdrop-filter:blur(12px);
  display:flex;align-items:center;justify-content:space-between;
  padding:0 {PAGE_GUTTER};height:58px;
  font-family:'DM Sans',sans-serif;
  position:relative;z-index:10;
">
  <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:{P['pop_dark']};
              display:flex;align-items:center;gap:8px;flex-shrink:0;">
    <div style="width:10px;height:10px;border-radius:50%;background:{P['pop']};"></div>
    POP Strategy Engine
  </div>
  <div style="display:flex;align-items:center;gap:8px;">
    <div style="width:250px;"></div>
    <div style="
      background:{P['pop_xlight']};color:{P['pop_dark']};border-radius:999px;
      padding:4px 14px;font-size:0.78rem;font-weight:600;white-space:nowrap;">
      Strategic Intel
    </div>
  </div>
</div>
<div id="nav-button-row">
""",
        unsafe_allow_html=True,
    )

    btn_cols = st.columns([7.6, 1.15, 1.15, 1.35])
    with btn_cols[1]:
        cls = "tab-active" if page == "home" else ""
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Home", key="nav_home_btn", use_container_width=True):
            _go("home")
        st.markdown("</div>", unsafe_allow_html=True)
    with btn_cols[2]:
        cls = "tab-active" if page in ("snacks", "detail") else ""
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Snacks", key="nav_snacks_btn", use_container_width=True):
            _go("snacks")
        st.markdown("</div>", unsafe_allow_html=True)
    with btn_cols[3]:
        cls = "tab-active" if page == "ranking" else ""
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Rankings", key="nav_rankings_btn", use_container_width=True):
            _go("ranking", ranking_metric=st.session_state.ranking_metric)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def page_home(trends: List[Dict]):
    top_score = max(t["final_score"] for t in trends) if trends else "—"
    n_trends = len(trends)

    st.markdown(
        f"""
<div style="
  background:radial-gradient(ellipse at 50% -10%,rgba(46,107,144,0.10) 0%,transparent 55%),{P['bg']};
  padding:5rem {PAGE_GUTTER} 2.5rem;text-align:center;
  font-family:'DM Sans',sans-serif;
">
  <div style="
    font-size:0.74rem;letter-spacing:0.24em;text-transform:uppercase;
    color:{P['pop']};font-weight:600;margin-bottom:1.5rem;
    display:flex;align-items:center;justify-content:center;gap:12px;
  ">
    <span style="width:36px;height:1px;background:{P['pop_light']};opacity:0.5;display:inline-block;"></span>
    POP Flavor Gap Detector
    <span style="width:36px;height:1px;background:{P['pop_light']};opacity:0.5;display:inline-block;"></span>
  </div>
  <h1 style="
    font-family:'DM Serif Display',serif;
    font-size:clamp(3rem,6vw,5rem);line-height:1.05;
    color:{P['ink']};margin:0 auto 1rem;max-width:700px;
  ">
    Ask me about a<br><em style="color:{P['pop']};">snack trend.</em>
  </h1>
  <p style="
    font-size:1rem;color:{P['muted']};
    max-width:480px;margin:0 auto 3rem;line-height:1.75;
  ">
    Discover which shelf-stable opportunities are growing, where POP has
    whitespace, and whether there's still time to act.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    card_l, card_r = st.columns(2, gap="medium")

    with card_l:
        st.markdown(
            f"""
<div style="
  padding:1.4rem 1.6rem;border-radius:16px;
  border:1.5px solid {P['sweet_dark']};background:{P['sweet_bg']};
  margin:0 0 0.75rem {PAGE_GUTTER};
">
  <div style="font-weight:700;font-size:1rem;color:{P['sweet_dark']};margin-bottom:4px;">
    🍫 Sweet Snacks
  </div>
  <div style="font-size:0.82rem;color:{P['muted']};">Chocolate, candy, baked goods</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="btn-sweet" style="padding:0 0 0 {PAGE_GUTTER};">', unsafe_allow_html=True)
        if st.button("→ Explore Sweet Snacks", key="home_sweet", use_container_width=True):
            _go("snacks", category="sweet")
        st.markdown("</div>", unsafe_allow_html=True)

    with card_r:
        st.markdown(
            f"""
<div style="
  padding:1.4rem 1.6rem;border-radius:16px;
  border:1.5px solid {P['salty_dark']};background:{P['salty_bg']};
  margin:0 {PAGE_GUTTER} 0.75rem 0;
">
  <div style="font-weight:700;font-size:1rem;color:{P['salty_dark']};margin-bottom:4px;">
    🥨 Salty Snacks
  </div>
  <div style="font-size:0.82rem;color:{P['muted']};">Chips, crackers, pretzels</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="btn-salty" style="padding:0 {PAGE_GUTTER} 0 0;">', unsafe_allow_html=True)
        if st.button("→ Explore Salty Snacks", key="home_salty", use_container_width=True):
            _go("snacks", category="salty")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    for col, num, label in [
        (s1, n_trends, "Trends Tracked"),
        (s2, f"{top_score}/100", "Top Score"),
        (s3, "2", "Categories"),
    ]:
        with col:
            st.markdown(
                f"""
<div style="text-align:center;padding:1rem;">
  <div style="font-family:'DM Serif Display',serif;font-size:2.4rem;
              color:{P['pop']};line-height:1;">{num}</div>
  <div style="font-size:0.72rem;color:{P['muted']};text-transform:uppercase;
              letter-spacing:0.12em;margin-top:6px;">{label}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def page_snacks(trends: List[Dict]):
    cat = st.session_state.category
    sort_by = st.session_state.sort_by
    is_sweet = cat == "sweet"
    cat_color = _cat_color(cat)
    chart_color = P["sweet_dark"] if is_sweet else P["salty_dark"]
    cat_label = "Sweet Snacks" if is_sweet else "Salty Snacks"

    st.markdown(
        f"""
<div style="
  background:white;border-bottom:1px solid {P['line']};
  padding:1.6rem {PAGE_GUTTER} 1.4rem;font-family:'DM Sans',sans-serif;
">
  <div style="font-size:0.8rem;color:{P['muted']};margin-bottom:0.7rem;">
    <span style="color:{P['pop']};">Home</span>
    <span style="margin:0 6px;color:{P['line']};">›</span>
    <span>{cat_label}</span>
  </div>
  <h2 style="font-family:'DM Serif Display',serif;font-size:2rem;color:{P['ink']};margin:0;">
    {cat_label}
  </h2>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div style="background:{P['bg']};padding:0.65rem {PAGE_GUTTER};border-bottom:1px solid {P['line']};">
""",
        unsafe_allow_html=True,
    )

    bar = st.columns([1, 1, 0.5, 0.45, 1, 1, 1])

    with bar[0]:
        cls = "tab-active" if is_sweet else ""
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Sweet", key="tab_sweet", use_container_width=True):
            _go("snacks", category="sweet", sort_by=sort_by)
        st.markdown("</div>", unsafe_allow_html=True)

    with bar[1]:
        cls = "tab-active" if not is_sweet else ""
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Salty", key="tab_salty", use_container_width=True):
            _go("snacks", category="salty", sort_by=sort_by)
        st.markdown("</div>", unsafe_allow_html=True)

    with bar[2]:
        st.markdown(
            f"<div style='width:1px;height:28px;background:{P['line']};margin:5px auto;'></div>",
            unsafe_allow_html=True,
        )

    with bar[3]:
        st.markdown(
            f"<div style='font-size:0.78rem;color:{P['muted']};font-weight:500;"
            f"white-space:nowrap;padding-top:9px;'>Sort by:</div>",
            unsafe_allow_html=True,
        )

    for col, (skey, slabel) in zip(
        bar[4:],
        [("score", "Score"), ("momentum", "Momentum"), ("opportunity", "Opportunity")],
    ):
        with col:
            cls = "pill-active" if sort_by == skey else "pill-base"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(slabel, key=f"sort_{skey}", use_container_width=True):
                _go("ranking", ranking_metric=skey)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    sorted_trends = _sorted_trends(trends, cat, sort_by)
    st.markdown(
        f"<div style='padding:1.5rem {PAGE_GUTTER} 0.5rem;font-size:0.82rem;color:{P['muted']};'>"
        f"{len(sorted_trends)} trend{'s' if len(sorted_trends) != 1 else ''} found</div>",
        unsafe_allow_html=True,
    )

    st.markdown(f"<div style='padding:0 {PAGE_GUTTER};'>", unsafe_allow_html=True)
    for row_start in range(0, len(sorted_trends), 2):
        cols = st.columns(2, gap="medium")
        for col_idx, trend in enumerate(sorted_trends[row_start : row_start + 2]):
            with cols[col_idx]:
                _render_trend_card(trend, cat_color, chart_color, cat)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='padding:0 {PAGE_GUTTER} 2rem;'>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="snacks_back"):
        _back("home")
    st.markdown("</div>", unsafe_allow_html=True)


def _render_trend_card(trend: Dict, cat_color: str, chart_color: str, cat: str):
    sc = trend["final_score"]
    sc_color = _score_color(sc)
    sc_bg = _score_bg(sc)
    action = trend["recommended_action"]
    action_bg = "#e8f5ef" if action == "build" else "#fef3e2"
    action_fg = P["good"] if action == "build" else P["warn"]
    desc_short = trend["description"][:120] + ("…" if len(trend["description"]) > 120 else "")

    st.markdown(
        f"""
<div style="
  background:white;border:1px solid {P['line']};border-radius:20px;
  overflow:hidden;margin-bottom:1rem;font-family:'DM Sans',sans-serif;
">
  <div style="padding:1.1rem 1.1rem 0;">
    {_build_chart(trend, w=380, h=130, color=chart_color)}
  </div>
  <div style="padding:0.85rem 1.2rem 1.1rem;">
    <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.14em;
                text-transform:uppercase;color:{cat_color};margin-bottom:0.35rem;">{cat.title()}</div>
    <div style="font-family:'DM Serif Display',serif;font-size:1.35rem;
                color:{P['ink']};margin-bottom:0.3rem;line-height:1.2;">{_esc(trend['name'])}</div>
    <div style="font-size:0.83rem;color:{P['muted']};line-height:1.55;margin-bottom:0.85rem;">
      {_esc(desc_short)}</div>
    <div style="display:flex;align-items:center;justify-content:space-between;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:40px;height:40px;border-radius:50%;
                    background:{sc_bg};color:{sc_color};
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.85rem;font-weight:700;flex-shrink:0;">{sc}</div>
        <div>
          <div style="font-size:0.8rem;font-weight:600;color:{P['ink']};">{trend['opportunity_level']} Opportunity</div>
          <div style="font-size:0.72rem;color:{P['muted']};">{trend['timing_stage']} stage</div>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px;">
        <span style="padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:500;
                     background:{action_bg};color:{action_fg};border:1px solid {P['line']};">
          {action.title()}
        </span>
        <span style="color:{P['pop']};font-size:0.9rem;">→</span>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button(f"Open → {trend['name']}", key=f"open_{trend['name']}", use_container_width=True):
        _go("detail", selected_trend=trend["name"])


def page_ranking(trends: List[Dict]):
    metric = st.session_state.ranking_metric
    meta = RANKING_META.get(metric, RANKING_META["score"])
    field = meta["field"]
    color = meta["color"]
    label = meta["label"]
    unit = meta["unit"]

    if metric == "opportunity":
        opp_order = {"High": 3, "Medium": 2, "Low": 1}
        sorted_all = sorted(trends, key=lambda t: opp_order.get(t["opportunity_level"], 0), reverse=True)

        def _val(t):
            return t["opportunity_level"]

        def _bar_frac(t):
            return opp_order.get(t["opportunity_level"], 0) / 3
    else:
        sorted_all = sorted(trends, key=lambda t: float(t.get(field, 0)), reverse=True)
        max_val = max((float(t.get(field, 0)) for t in sorted_all), default=1)

        def _val(t):
            return t.get(field, 0)

        def _bar_frac(t):
            return float(t.get(field, 0)) / max(max_val, 1)

    st.markdown(
        f"""
<div style="background:white;border-bottom:1px solid {P['line']};
            padding:1.6rem {PAGE_GUTTER} 1.4rem;font-family:'DM Sans',sans-serif;">
  <div style="font-size:0.8rem;color:{P['muted']};margin-bottom:0.7rem;">
    <span style="color:{P['pop']};">Home</span>
    <span style="margin:0 6px;color:{P['line']};">›</span>
    <span>{label} Rankings</span>
  </div>
  <h2 style="font-family:'DM Serif Display',serif;font-size:2rem;color:{P['ink']};margin:0 0 0.3rem;">
    {label} Rankings
  </h2>
  <p style="font-size:0.9rem;color:{P['muted']};margin:0;">
    All {len(sorted_all)} trends ranked by {label.lower()}
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div style='background:{P['bg']};padding:0.65rem {PAGE_GUTTER};border-bottom:1px solid {P['line']};'>",
        unsafe_allow_html=True,
    )
    sw = st.columns([0.5, 1, 1, 1, 3])
    for col, (mkey, mlabel) in zip(
        sw[1:4],
        [("score", "Score"), ("momentum", "Momentum"), ("opportunity", "Opportunity")],
    ):
        with col:
            cls = "pill-active" if metric == mkey else "pill-base"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(mlabel, key=f"rank_{mkey}", use_container_width=True):
                _go("ranking", ranking_metric=mkey)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='padding:1.5rem {PAGE_GUTTER};'>", unsafe_allow_html=True)
    for rank, trend in enumerate(sorted_all, 1):
        cat = trend["category"]
        cat_color = _cat_color(cat)
        cat_bg = _cat_bg(cat)
        val = _val(trend)
        frac = _bar_frac(trend)
        sc = trend["final_score"]
        sc_color = _score_color(sc)
        sc_bg = _score_bg(sc)
        rank_color = P["pop"] if rank == 1 else (P["warn"] if rank == 2 else (P["good"] if rank == 3 else P["muted"]))
        bar_w = int(frac * 100)
        val_display = f"{val} {unit}" if metric != "opportunity" else val

        st.markdown(
            f"""
<div style="background:white;border:1px solid {P['line']};border-radius:16px;
            padding:1rem 1.25rem;margin-bottom:0.75rem;font-family:'DM Sans',sans-serif;
            display:flex;align-items:center;gap:1rem;">
  <div style="width:36px;height:36px;border-radius:50%;background:{P['pop_xlight']};color:{rank_color};
              display:flex;align-items:center;justify-content:center;
              font-weight:700;font-size:0.92rem;flex-shrink:0;">#{rank}</div>
  <div style="flex:1;min-width:0;">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <span style="font-family:'DM Serif Display',serif;font-size:1.05rem;color:{P['ink']};">
        {_esc(trend['name'])}</span>
      <span style="padding:1px 8px;border-radius:999px;font-size:0.7rem;font-weight:600;
                   background:{cat_bg};color:{cat_color};border:1px solid {cat_color};">
        {cat.title()}</span>
    </div>
    <div style="height:6px;border-radius:999px;background:{P['line']};overflow:hidden;">
      <div style="height:100%;width:{bar_w}%;background:{color};border-radius:999px;"></div>
    </div>
  </div>
  <div style="text-align:right;flex-shrink:0;">
    <div style="font-size:1.25rem;font-weight:700;color:{color};">{val_display}</div>
    <div style="font-size:0.7rem;color:{P['muted']};">{trend['timing_stage']} stage</div>
  </div>
  <div style="width:38px;height:38px;border-radius:50%;background:{sc_bg};color:{sc_color};
              display:flex;flex-direction:column;align-items:center;justify-content:center;
              font-size:0.8rem;font-weight:700;flex-shrink:0;">{sc}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button(f"View {trend['name']}", key=f"rank_open_{rank}_{trend['name']}"):
            _go("detail", selected_trend=trend["name"])

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='padding:0 {PAGE_GUTTER} 2rem;'>", unsafe_allow_html=True)
    if st.button("← Back", key="ranking_back"):
        _back("snacks")
    st.markdown("</div>", unsafe_allow_html=True)


def page_detail(trends: List[Dict]):
    name = st.session_state.selected_trend
    trend = next((t for t in trends if t["name"] == name), None)
    if trend is None:
        st.error("Trend not found.")
        if st.button("← Back"):
            _back("snacks")
        return

    cat = trend["category"]
    is_sweet = cat == "sweet"
    cat_color = _cat_color(cat)
    chart_color = P["sweet_dark"] if is_sweet else P["salty_dark"]
    cat_label = "Sweet Snacks" if is_sweet else "Salty Snacks"
    sc = trend["final_score"]
    sc_color = _score_color(sc)
    sc_bg = _score_bg(sc)
    action = trend["recommended_action"]
    matched = ", ".join(p["name"] for p in trend.get("matched_pop_products", [])[:3]) or "No current adjacency"
    ws_tags = trend.get("whitespace_tags", [])
    fit_tags = trend.get("strategic_fit_tags", [])
    constraints = trend.get("constraint_flags", [])

    st.markdown(
        f"""
<div style="background:white;border-bottom:1px solid {P['line']};
            padding:1.6rem {PAGE_GUTTER} 1.4rem;font-family:'DM Sans',sans-serif;">
  <div style="font-size:0.8rem;color:{P['muted']};margin-bottom:0.9rem;">
    <span style="color:{P['pop']};">Home</span>
    <span style="margin:0 6px;color:{P['line']};">›</span>
    <span style="color:{P['pop']};">{cat_label}</span>
    <span style="margin:0 6px;color:{P['line']};">›</span>
    <span>{_esc(trend['name'])}</span>
  </div>
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;">
    <div style="flex:1;min-width:260px;">
      <div style="font-size:0.76rem;font-weight:600;letter-spacing:0.14em;
                  text-transform:uppercase;color:{cat_color};margin-bottom:0.5rem;">{cat.title()} Snack</div>
      <h1 style="font-family:'DM Serif Display',serif;font-size:2.4rem;
                 color:{P['ink']};line-height:1.1;margin:0 0 0.6rem;">{_esc(trend['name'])}</h1>
      <p style="font-size:0.95rem;color:{P['muted']};line-height:1.65;max-width:580px;margin:0;">
        {_esc(trend['description'])}</p>
    </div>
    <div style="text-align:center;flex-shrink:0;">
      <div style="width:76px;height:76px;border-radius:50%;background:{sc_bg};color:{sc_color};
                  display:flex;flex-direction:column;align-items:center;justify-content:center;
                  font-size:1.6rem;font-weight:700;line-height:1;margin:0 auto 6px;">
        {sc}
        <span style="font-size:0.62rem;font-weight:500;opacity:0.7;margin-top:2px;">/ 100</span>
      </div>
      <div style="font-size:0.75rem;color:{P['muted']};">{trend['opportunity_level']} Opportunity</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(f"<div style='padding:1rem {PAGE_GUTTER} 0;'>", unsafe_allow_html=True)
    if st.button("← Back", key="detail_back"):
        _back("snacks")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='padding:0 {PAGE_GUTTER} 2rem;'>", unsafe_allow_html=True)
    left, right = st.columns([1.6, 1], gap="medium")

    with left:
        st.markdown(
            f"""
<div style="background:white;border:1px solid {P['line']};border-radius:20px;
            overflow:hidden;margin:1rem 0 0;font-family:'DM Sans',sans-serif;">
  <div style="padding:1rem 1.25rem 0.5rem;border-bottom:1px solid {P['line']};
              font-size:0.76rem;font-weight:600;letter-spacing:0.12em;
              text-transform:uppercase;color:{P['muted']};">Growth Trajectory</div>
  <div style="padding:1.25rem 1.5rem 1rem;">
    {_build_chart(trend, w=560, h=230, color=chart_color)}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        metrics = [
            ("Trend Strength", trend["trend_strength_score"], "/ 100", P["ink"]),
            ("Momentum", trend["trend_momentum_score"], "/ 100", P["ink"]),
            ("Gap Score", trend["gap_opportunity_score"], "/ 100", P["good"]),
            ("Sat. Penalty", f"-{trend['saturation_penalty']}", "pts", P["danger"]),
        ]
        m_cols = st.columns(4)
        for mcol, (mlabel, mval, munit, mcolor) in zip(m_cols, metrics):
            with mcol:
                st.markdown(
                    f"""
<div style="background:{P['bg']};border:1px solid {P['line']};border-radius:14px;
            padding:1rem 0.75rem;text-align:center;margin:0.75rem 0 1.25rem;
            font-family:'DM Sans',sans-serif;">
  <div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;
              letter-spacing:0.1em;color:{P['muted']};margin-bottom:8px;line-height:1.3;">
    {mlabel}
  </div>
  <div style="font-size:1.6rem;font-weight:700;color:{mcolor};line-height:1;">{mval}</div>
  <div style="font-size:0.68rem;color:{P['muted']};margin-top:4px;">{munit}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

        st.markdown(
            f"""
<div style="background:white;border:1px solid {P['line']};border-radius:20px;
            overflow:hidden;margin:0 0 1.25rem;font-family:'DM Sans',sans-serif;">
  <div style="padding:1rem 1.25rem 0.75rem;border-bottom:1px solid {P['line']};
              font-size:0.76rem;font-weight:600;letter-spacing:0.12em;
              text-transform:uppercase;color:{P['muted']};">Trend Analysis</div>
  <div style="padding:1.1rem 1.25rem;">
    <div style="padding-bottom:0.9rem;border-bottom:1px solid {P['line']};margin-bottom:0.9rem;">
      <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.1em;color:{P['pop']};margin-bottom:0.35rem;">Forecast</div>
      <div style="font-size:0.9rem;color:{P['ink']};line-height:1.6;">{_esc(trend['forecast_summary'])}</div>
    </div>
    <div style="padding-bottom:0.9rem;border-bottom:1px solid {P['line']};margin-bottom:0.9rem;">
      <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.1em;color:{P['pop']};margin-bottom:0.35rem;">Feasibility</div>
      <div style="font-size:0.9rem;color:{P['ink']};line-height:1.6;">
        {_esc(trend['feasibility_summary'])}
        <strong> Score: {trend['feasibility_score']}/100</strong>
      </div>
    </div>
    <div>
      <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.1em;color:{P['pop']};margin-bottom:0.35rem;">Timing</div>
      <div style="font-size:0.9rem;color:{P['ink']};line-height:1.6;">
        <strong>{_esc(trend['timing_window'])}</strong> - {_esc(trend['timing_guidance'])}
      </div>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        def _tags(tags, bg, fg, border):
            return "".join(
                f"<span style='padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:500;"
                f"background:{bg};color:{fg};border:1px solid {border};margin:2px;display:inline-block;'>"
                f"{_esc(t)}</span>"
                for t in tags
            )

        ws_html = _tags(ws_tags, P["pop_xlight"], P["pop_dark"], P["line"])
        fit_html = _tags(fit_tags, P["pop_xlight"], P["pop_dark"], P["line"])
        con_html = _tags(constraints, "#fdeaea", P["danger"], "#f5c5c5")

        st.markdown(
            f"""
<div style="background:white;border:1px solid {P['line']};border-radius:20px;
            overflow:hidden;margin:1rem 0 1.25rem;font-family:'DM Sans',sans-serif;">
  <div style="padding:1rem 1.25rem 0.75rem;border-bottom:1px solid {P['line']};
              font-size:0.76rem;font-weight:600;letter-spacing:0.12em;
              text-transform:uppercase;color:{P['muted']};">POP Landscape</div>
  <div style="padding:1.1rem 1.25rem;">
    <div style="margin-bottom:0.85rem;">
      <div style="font-size:0.78rem;color:{P['muted']};margin-bottom:4px;">POP Presence</div>
      <div style="font-weight:600;font-size:0.92rem;">{trend['pop_presence']}</div>
      <div style="font-size:0.82rem;color:{P['muted']};margin-top:2px;">{matched}</div>
    </div>
    <div style="margin-bottom:0.85rem;">
      <div style="font-size:0.78rem;color:{P['muted']};margin-bottom:6px;">Whitespace</div>
      <div style="display:flex;flex-wrap:wrap;gap:4px;">{ws_html}</div>
    </div>
    <div style="margin-bottom:0.85rem;">
      <div style="font-size:0.78rem;color:{P['muted']};margin-bottom:6px;">Ingredient Fit</div>
      <div style="display:flex;flex-wrap:wrap;gap:4px;">{fit_html}</div>
    </div>
    <div>
      <div style="font-size:0.78rem;color:{P['muted']};margin-bottom:6px;">Constraints</div>
      <div style="display:flex;flex-wrap:wrap;gap:4px;">{con_html}</div>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        facts = [
            f"POP adjacency: {matched}.",
            f"Timing: {trend['timing_stage']}-stage with {trend['timing_window'].lower()}.",
            f"Top whitespace: {', '.join(ws_tags[:2]) if ws_tags else 'limited'}.",
        ]
        if fit_tags:
            facts.append(f"Ingredient overlap: {', '.join(fit_tags[:3])}.")
        facts_html = "".join(
            f"<li style='margin-bottom:6px;font-size:0.88rem;'>{_esc(f)}</li>" for f in facts
        )

        st.markdown(
            f"""
<div style="background:white;border:1px solid {P['line']};border-radius:20px;
            overflow:hidden;margin:0 0 1.25rem;font-family:'DM Sans',sans-serif;">
  <div style="padding:1rem 1.25rem 0.75rem;border-bottom:1px solid {P['line']};
              font-size:0.76rem;font-weight:600;letter-spacing:0.12em;
              text-transform:uppercase;color:{P['muted']};">Quick Snapshot</div>
  <div style="padding:1.1rem 1.25rem;">
    <ul style="padding-left:1.1rem;margin:0;color:{P['ink']};line-height:1.65;">
      {facts_html}
    </ul>
    <div style="margin-top:0.85rem;font-size:0.85rem;color:{P['muted']};line-height:1.6;">
      <strong style="color:{P['ink']};">Details:</strong> {_esc(trend.get('scoring_summary', ''))}
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div style="
  background:linear-gradient(135deg,{P['pop_dark']},{P['pop']});
  color:white;border-radius:20px;padding:1.75rem 2rem;
  margin:0.5rem {PAGE_GUTTER} 2rem;font-family:'DM Sans',sans-serif;
">
  <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.18em;
              text-transform:uppercase;opacity:0.65;margin-bottom:0.5rem;">
    Strategic Recommendation
  </div>
  <div style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.5rem;">
    {action.title()} It
  </div>
  <div style="font-size:0.95rem;opacity:0.88;line-height:1.65;max-width:680px;margin-bottom:1rem;">
    {_esc(trend['reasoning'])}
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">
    <span style="background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);
                 border-radius:999px;padding:4px 14px;font-size:0.8rem;">{trend['timing_stage']} stage</span>
    <span style="background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);
                 border-radius:999px;padding:4px 14px;font-size:0.8rem;">{_esc(trend['timing_window'])}</span>
    <span style="background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);
                 border-radius:999px;padding:4px 14px;font-size:0.8rem;">Feasibility {trend['feasibility_score']}/100</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def main():
    _init_state()
    _inject_css()

    trends = load_trends()
    _compute_global_scale(trends)

    _render_nav()

    page = st.session_state.page
    if page == "home":
        page_home(trends)
    elif page == "snacks":
        page_snacks(trends)
    elif page == "detail":
        page_detail(trends)
    elif page == "ranking":
        page_ranking(trends)
    else:
        page_home(trends)


if __name__ == "__main__":
    main()
