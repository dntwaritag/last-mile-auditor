"""
Veridi Logistics · Last Mile Auditor
Streamlit dashboard backed by pre-aggregated master_dataset.csv from the notebook.
"""
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veridi Logistics · Last Mile Auditor",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME / GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
PALETTE = {
    "bg":      "#0D1117",
    "surface": "#161B22",
    "border":  "#21262D",
    "accent":  "#F78166",
    "accent2": "#58A6FF",
    "ok":      "#3FB950",
    "warn":    "#D29922",
    "danger":  "#F85149",
    "text":    "#E6EDF3",
    "muted":   "#8B949E",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {PALETTE['bg']};
    color: {PALETTE['text']};
}}

section[data-testid="stSidebar"] {{
    background-color: {PALETTE['surface']};
    border-right: 1px solid {PALETTE['border']};
}}
section[data-testid="stSidebar"] * {{ color: {PALETTE['text']} !important; }}
header[data-testid="stHeader"] {{ display: none; }}

.kpi-grid  {{ display: flex; gap: 16px; margin-bottom: 8px; }}
.kpi-card  {{
    flex: 1; background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']}; border-radius: 8px;
    padding: 20px 24px; position: relative; overflow: hidden;
}}
.kpi-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}}
.kpi-card.danger::before {{ background: {PALETTE['danger']}; }}
.kpi-card.warn::before   {{ background: {PALETTE['warn']}; }}
.kpi-card.ok::before     {{ background: {PALETTE['ok']}; }}
.kpi-card.info::before   {{ background: {PALETTE['accent2']}; }}

.kpi-label {{
    font-size: 11px; font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: {PALETTE['muted']}; margin-bottom: 8px;
}}
.kpi-value {{
    font-size: 36px; font-weight: 700;
    font-family: 'IBM Plex Mono', monospace; line-height: 1;
}}
.kpi-sub {{ font-size: 12px; color: {PALETTE['muted']}; margin-top: 6px; }}

.section-header {{
    margin: 32px 0 16px; padding-bottom: 8px;
    border-bottom: 1px solid {PALETTE['border']};
}}
.section-title {{
    font-size: 13px; font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 2px; text-transform: uppercase; color: {PALETTE['muted']};
}}

.dash-title {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; margin: 0; }}
.dash-sub   {{
    font-size: 13px; color: {PALETTE['muted']};
    font-family: 'IBM Plex Mono', monospace; margin-top: 4px;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MATPLOTLIB STYLE
# ─────────────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  PALETTE["bg"],
    "axes.facecolor":    PALETTE["surface"],
    "axes.edgecolor":    PALETTE["border"],
    "axes.labelcolor":   PALETTE["muted"],
    "axes.titlecolor":   PALETTE["text"],
    "xtick.color":       PALETTE["muted"],
    "ytick.color":       PALETTE["muted"],
    "text.color":        PALETTE["text"],
    "grid.color":        PALETTE["border"],
    "grid.linewidth":    0.6,
    "font.family":       "monospace",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING — reads pre-aggregated master_dataset.csv from the notebook
# ─────────────────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "master_dataset.csv")


@st.cache_data(show_spinner="Loading dataset...")
def load_master() -> pd.DataFrame:
    """
    Load the pre-cleaned master dataset built by the analysis notebook.
    Required columns are validated; missing optional columns are tolerated.
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"'{DATA_PATH}' not found. Run the notebook's data-export cell to "
            f"generate it, then place it at this path before launching the app."
        )

    df = pd.read_csv(DATA_PATH, parse_dates=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ])

    required = {"customer_state", "Delay_Days", "Delivery_Status", "review_score"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"master_dataset.csv is missing columns: {missing}")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fig_late_by_state(df: pd.DataFrame) -> plt.Figure:
    """% Late by state, vectorized (no groupby.apply)."""
    work = df.assign(is_late=df["Delivery_Status"].isin(["Late", "Super Late"]))
    state_stats = (
        work.groupby("customer_state")["is_late"]
            .mean()
            .mul(100)
            .reset_index(name="late_pct")
            .sort_values("late_pct", ascending=True)
    )

    n = len(state_stats)
    fig, ax = plt.subplots(figsize=(7, max(4, n * 0.32)))

    colors = [
        PALETTE["danger"] if v >= 15 else
        PALETTE["warn"]   if v >= 10 else
        PALETTE["ok"]
        for v in state_stats["late_pct"]
    ]
    bars = ax.barh(state_stats["customer_state"], state_stats["late_pct"],
                   color=colors, height=0.65, zorder=3)

    for bar, val in zip(bars, state_stats["late_pct"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=8, color=PALETTE["muted"])

    nat_avg = state_stats["late_pct"].mean()
    ax.axvline(nat_avg, color=PALETTE["accent2"], lw=1.2, ls="--",
               label=f"Avg {nat_avg:.1f}%")
    ax.set_xlabel("% Late Deliveries", fontsize=9)
    ax.set_xlim(0, state_stats["late_pct"].max() * 1.18)
    ax.legend(fontsize=8, framealpha=0)
    ax.grid(axis="x", zorder=0)
    ax.set_title("Late Delivery % by State", fontsize=11, pad=12)
    fig.tight_layout()
    return fig


def fig_status_distribution(df: pd.DataFrame) -> plt.Figure:
    """Horizontal bar instead of pie — readable at any proportion."""
    order = ["On Time", "Late", "Super Late"]
    counts = (df["Delivery_Status"].value_counts()
                .reindex(order).fillna(0).astype(int))
    pct = (counts / counts.sum() * 100) if counts.sum() else counts

    colors = [PALETTE["ok"], PALETTE["warn"], PALETTE["danger"]]
    fig, ax = plt.subplots(figsize=(5, 3.8))
    bars = ax.barh(order, counts.values, color=colors, height=0.6, zorder=3)

    for bar, n_orders, share in zip(bars, counts.values, pct.values):
        ax.text(bar.get_width() + counts.max() * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{n_orders:,}  ({share:.1f}%)",
                va="center", fontsize=9, color=PALETTE["text"])

    ax.set_xlim(0, counts.max() * 1.25 if counts.max() else 1)
    ax.set_xlabel("Orders", fontsize=9)
    ax.set_title("Delivery Status Distribution", fontsize=11, pad=12)
    ax.grid(axis="x", zorder=0)
    fig.tight_layout()
    return fig


def fig_scatter(df: pd.DataFrame) -> plt.Figure:
    """Scatter of delay vs. review score with regression line."""
    sample = df.dropna(subset=["Delay_Days", "review_score"]).copy()
    sample = sample[sample["Delay_Days"].between(-30, 60)]
    if len(sample) > 3000:
        sample = sample.sample(3000, random_state=42)

    color_map = {
        "On Time":    PALETTE["ok"],
        "Late":       PALETTE["warn"],
        "Super Late": PALETTE["danger"],
    }
    c = sample["Delivery_Status"].map(color_map).fillna(PALETTE["muted"])

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.scatter(sample["Delay_Days"], sample["review_score"],
               c=c, alpha=0.35, s=12, zorder=3)

    # Regression line on the full filtered sample
    if len(sample) > 1:
        z = np.polyfit(sample["Delay_Days"], sample["review_score"], 1)
        xs = np.linspace(sample["Delay_Days"].min(),
                         sample["Delay_Days"].max(), 200)
        ax.plot(xs, np.poly1d(z)(xs), color=PALETTE["accent"], lw=1.8, zorder=4)

    ax.axvline(0, color=PALETTE["border"], lw=1, ls="--")
    ax.set_xlabel("Delay Days (negative = early)", fontsize=9)
    ax.set_ylabel("Review Score (1-5)", fontsize=9)
    ax.set_ylim(0.5, 5.5)
    ax.set_title("Delay vs Review Score", fontsize=11, pad=12)
    ax.grid(zorder=0)

    patches = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
    ax.legend(handles=patches, fontsize=8, framealpha=0, loc="lower right")
    fig.tight_layout()
    return fig


def fig_avg_score_by_status(df: pd.DataFrame) -> plt.Figure:
    """Average review score per delivery status."""
    order = ["On Time", "Late", "Super Late"]
    avg = (df[df["Delivery_Status"].isin(order)]
             .groupby("Delivery_Status")["review_score"].mean()
             .reindex(order))

    colors = [PALETTE["ok"], PALETTE["warn"], PALETTE["danger"]]
    fig, ax = plt.subplots(figsize=(5, 3.8))
    bars = ax.bar(avg.index, avg.values, color=colors, width=0.5, zorder=3)

    for bar, val in zip(bars, avg.values):
        if pd.notna(val):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.04,
                    f"{val:.2f}", ha="center", fontsize=10, fontweight="600")

    overall = df["review_score"].mean()
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Avg Review Score", fontsize=9)
    ax.set_title("Avg Review Score by Delivery Status", fontsize=11, pad=12)
    if pd.notna(overall):
        ax.axhline(overall, color=PALETTE["accent2"], lw=1.2, ls="--",
                   label=f"Overall avg {overall:.2f}")
        ax.legend(fontsize=8, framealpha=0)
    ax.grid(axis="y", zorder=0)
    fig.tight_layout()
    return fig


def fig_promise_gap(df: pd.DataFrame) -> plt.Figure:
    """
    Candidate's Choice — Promise Gap by State.
    Median actual delivery time vs late rate, bubble = order volume.
    Top-right quadrant = priority intervention.
    """
    if "Actual_Time_Days" not in df.columns:
        return _empty_chart("Promise Gap: requires Actual_Time_Days column")

    work = df.assign(is_late=df["Delivery_Status"].isin(["Late", "Super Late"]))
    gap = (work.groupby("customer_state")
                .agg(median_actual=("Actual_Time_Days", "median"),
                     pct_late=("is_late", lambda s: s.mean() * 100),
                     n_orders=("is_late", "count"))
                .reset_index())

    fig, ax = plt.subplots(figsize=(7, 4.5))
    sizes = (gap["n_orders"] / gap["n_orders"].max() * 600) + 30
    ax.scatter(gap["median_actual"], gap["pct_late"], s=sizes,
               alpha=0.55, color=PALETTE["accent"],
               edgecolor=PALETTE["text"], linewidth=0.5, zorder=3)

    for _, row in gap.iterrows():
        ax.annotate(row["customer_state"],
                    (row["median_actual"], row["pct_late"]),
                    fontsize=7.5, color=PALETTE["text"],
                    xytext=(4, 2), textcoords="offset points")

    ax.set_xlabel("Median Actual Delivery Time (days from purchase)", fontsize=9)
    ax.set_ylabel("% Late", fontsize=9)
    ax.set_title("Promise Gap by State - bubble = order volume",
                 fontsize=11, pad=12)
    ax.grid(zorder=0)
    fig.tight_layout()
    return fig


def fig_late_by_category(df: pd.DataFrame, top_n: int = 12) -> plt.Figure:
    """Top product categories by late-delivery rate (English-translated)."""
    if "product_category" not in df.columns:
        return _empty_chart("Category breakdown: product_category column missing")

    work = (df.dropna(subset=["product_category"])
              .assign(is_late=df["Delivery_Status"].isin(["Late", "Super Late"])))
    if work.empty:
        return _empty_chart("Category breakdown: no data after filters")

    cat = (work.groupby("product_category")
                .agg(pct_late=("is_late", lambda s: s.mean() * 100),
                     n=("is_late", "count"))
                .reset_index())
    # Stability filter: at least 100 orders to avoid noisy small-N categories
    cat = cat[cat["n"] >= 100].sort_values("pct_late", ascending=False).head(top_n)
    cat = cat.sort_values("pct_late", ascending=True)

    if cat.empty:
        return _empty_chart("No categories with >=100 orders for current filter")

    colors = [
        PALETTE["danger"] if v >= 15 else
        PALETTE["warn"]   if v >= 10 else
        PALETTE["ok"]
        for v in cat["pct_late"]
    ]

    fig, ax = plt.subplots(figsize=(7, max(3.5, len(cat) * 0.32)))
    bars = ax.barh(cat["product_category"], cat["pct_late"],
                   color=colors, height=0.65, zorder=3)
    for bar, val, n in zip(bars, cat["pct_late"], cat["n"]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}% (n={n:,})", va="center", fontsize=8,
                color=PALETTE["muted"])
    ax.set_xlabel("% Late Deliveries", fontsize=9)
    ax.set_xlim(0, cat["pct_late"].max() * 1.30)
    ax.set_title(f"Top {len(cat)} Product Categories by Late Rate (n>=100)",
                 fontsize=11, pad=12)
    ax.grid(axis="x", zorder=0)
    fig.tight_layout()
    return fig


def _empty_chart(message: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.text(0.5, 0.5, message, ha="center", va="center",
            fontsize=10, color=PALETTE["muted"])
    ax.axis("off")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
try:
    df_full = load_master()
except (FileNotFoundError, ValueError) as e:
    st.error(str(e))
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📦 Veridi Logistics")
    st.markdown(
        f"<span style='color:{PALETTE['muted']};font-size:11px;"
        f"font-family:monospace'>LAST MILE AUDITOR v1.0</span>",
        unsafe_allow_html=True,
    )
    st.divider()

    all_states = sorted(df_full["customer_state"].dropna().unique())
    sel_states = st.multiselect("Filter by State", all_states,
                                default=all_states,
                                help="Brazilian state of the customer")

    st.markdown("---")
    all_statuses = ["On Time", "Late", "Super Late"]
    sel_statuses = st.multiselect("Filter by Delivery Status",
                                  all_statuses, default=all_statuses)

    st.markdown("---")
    st.markdown(
        f"<span style='color:{PALETTE['muted']};font-size:10px'>"
        f"Source: Olist Brazilian E-Commerce Dataset · {len(df_full):,} orders"
        f"</span>",
        unsafe_allow_html=True,
    )

# Apply filters
df = df_full[
    df_full["customer_state"].isin(sel_states)
    & df_full["Delivery_Status"].isin(sel_statuses)
].copy()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding: 24px 0 8px'>
  <p class='dash-title'>Last Mile Delivery Audit</p>
  <p class='dash-sub'>VERIDI LOGISTICS · OPERATIONAL INTELLIGENCE DASHBOARD</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KPI METRICS — thresholds calibrated for real Olist baseline (8.11% national)
# ─────────────────────────────────────────────────────────────────────────────
late_mask = df["Delivery_Status"].isin(["Late", "Super Late"])
pct_late  = late_mask.mean() * 100 if len(df) else 0
avg_delay = df.loc[late_mask, "Delay_Days"].mean() if late_mask.sum() else 0
avg_score = df["review_score"].mean() if len(df) else 0
total_ord = len(df)


def color_for(val: float, lo: float, hi: float) -> str:
    """Return CSS class — ok below lo, warn between, danger above hi."""
    if val >= hi:
        return "danger"
    if val >= lo:
        return "warn"
    return "ok"


# Calibrated to actual data:
#   - National late rate ≈ 8%, worst states 15-24%
#   - Avg delay among late orders ≈ 10-15 days
#   - Review score: 4+ healthy, 3-4 warning, <3 danger
late_cls  = color_for(pct_late, 9, 15)
delay_cls = color_for(avg_delay, 5, 10)
score_cls = "ok" if avg_score >= 4 else "warn" if avg_score >= 3 else "danger"

color_for_class = {
    "danger": PALETTE["danger"],
    "warn":   PALETTE["warn"],
    "ok":     PALETTE["ok"],
}

st.markdown(f"""
<div class='kpi-grid'>
  <div class='kpi-card {late_cls}'>
    <div class='kpi-label'>% Late Deliveries</div>
    <div class='kpi-value' style='color:{color_for_class[late_cls]}'>{pct_late:.1f}%</div>
    <div class='kpi-sub'>{late_mask.sum():,} of {total_ord:,} orders</div>
  </div>
  <div class='kpi-card {delay_cls}'>
    <div class='kpi-label'>Avg Delay (late orders)</div>
    <div class='kpi-value' style='color:{color_for_class[delay_cls]}'>{avg_delay:.1f}d</div>
    <div class='kpi-sub'>days past estimated date</div>
  </div>
  <div class='kpi-card {score_cls}'>
    <div class='kpi-label'>Avg Review Score</div>
    <div class='kpi-value' style='color:{color_for_class[score_cls]}'>{avg_score:.2f}<span style='font-size:16px'>/5</span></div>
    <div class='kpi-sub'>customer satisfaction index</div>
  </div>
  <div class='kpi-card info'>
    <div class='kpi-label'>Total Orders (filtered)</div>
    <div class='kpi-value' style='color:{PALETTE["accent2"]}'>{total_ord:,}</div>
    <div class='kpi-sub'>{len(sel_states)} state(s) selected</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ROW 1 — State bar + Status distribution
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'><span class='section-title'>"
    "Geographic & Status Breakdown</span></div>",
    unsafe_allow_html=True,
)
col1, col2 = st.columns([2, 1], gap="large")
with col1:
    if len(df) > 0:
        st.pyplot(fig_late_by_state(df), use_container_width=True)
    else:
        st.info("No data for current filters.")
with col2:
    if len(df) > 0:
        st.pyplot(fig_status_distribution(df), use_container_width=True)
    else:
        st.info("No data.")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 2 — Sentiment correlation
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'><span class='section-title'>"
    "Sentiment Correlation</span></div>",
    unsafe_allow_html=True,
)
col3, col4 = st.columns([3, 2], gap="large")
with col3:
    if len(df) > 0:
        st.pyplot(fig_scatter(df), use_container_width=True)
    else:
        st.info("No data.")
with col4:
    if len(df) > 0:
        st.pyplot(fig_avg_score_by_status(df), use_container_width=True)
    else:
        st.info("No data.")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 3 — Candidate's Choice (Promise Gap) + Product Categories (Bonus)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'><span class='section-title'>"
    "Promise Gap & Category Drilldown</span></div>",
    unsafe_allow_html=True,
)
col5, col6 = st.columns([3, 2], gap="large")
with col5:
    if len(df) > 0:
        st.pyplot(fig_promise_gap(df), use_container_width=True)
        st.markdown(
            f"<div style='color:{PALETTE['muted']};font-size:11px;"
            f"font-family:monospace;margin-top:4px'>"
            f"Top-right quadrant = states where customers wait longest "
            f"AND packages still arrive late. Priority for carrier renegotiation "
            f"or estimator recalibration."
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No data.")
with col6:
    if len(df) > 0:
        st.pyplot(fig_late_by_category(df), use_container_width=True)
    else:
        st.info("No data.")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-top:40px; padding-top:16px;
            border-top:1px solid {PALETTE["border"]};
            text-align:center; color:{PALETTE["muted"]};
            font-size:11px; font-family:monospace'>
  Veridi Logistics · Last Mile Auditor · Built with Streamlit + Matplotlib
</div>
""", unsafe_allow_html=True)
