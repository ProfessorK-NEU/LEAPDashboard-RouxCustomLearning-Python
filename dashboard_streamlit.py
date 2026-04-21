# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICAL LEAP — Learner Experience Executive Dashboard (Streamlit)
# Run with: streamlit run dashboard_streamlit.py
# Required: pip install streamlit plotly pandas scipy numpy
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io, base64

# ── Global chart font size ─────────────────────────────────────────────────────
pio.templates["roux"] = go.layout.Template(
    layout=go.Layout(font=dict(size=15))
)
pio.templates.default = "plotly+roux"

st.set_page_config(
    page_title="Roux Institute Custom Learning Feedback Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {
    background: white; border-radius: 10px; padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07); border-left: 4px solid #A4804A;
    margin-bottom: 12px;
  }
  .metric-val  { font-size: 2rem; font-weight: 700; color: #7A5C2E; }
  .metric-lbl  { font-size: 0.85rem; color: #555; margin-top: 2px; }
  .section-hdr { font-size: 1.1rem; font-weight: 600; color: #7A5C2E;
                 border-bottom: 2px solid #F0E2C8; padding-bottom: 4px; margin-bottom: 12px; }
  [data-testid="stSidebar"] { background: #A6192E; }
  [data-testid="stSidebar"] label, [data-testid="stSidebar"] .st-emotion-cache-16idsys p
    { color: #fce; }
  .partner-banner {
    background: linear-gradient(135deg, #7A5C2E 0%, #A4804A 60%, #D4A568 100%);
    border-radius: 12px; padding: 28px 36px; margin-bottom: 24px; color: white;
  }
  .partner-banner h1 { font-size: 1.9rem; font-weight: 800; margin: 0 0 4px 0; color: white; }
  .partner-banner p  { font-size: 0.95rem; margin: 0; opacity: 0.85; }
  .partner-kpi {
    background: white; border-radius: 10px; padding: 20px 18px; text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,.08); border-top: 4px solid #A4804A;
  }
  .partner-kpi-val { font-size: 2.1rem; font-weight: 800; color: #7A5C2E; }
  .partner-kpi-lbl { font-size: 0.8rem; color: #777; text-transform: uppercase;
                     letter-spacing: 0.05em; margin-top: 4px; }
  .highlight-box {
    background: #fdf6ed; border-left: 4px solid #A4804A; border-radius: 6px;
    padding: 14px 18px; margin-bottom: 10px;
  }
  .highlight-box b { color: #7A5C2E; }
  .benchmark-better { color: #2D6A3F; font-weight: 700; }
  .benchmark-worse  { color: #C8102E; font-weight: 700; }
  .spark-table {
    width: 100%; border-collapse: collapse; font-family: 'Calibri', sans-serif;
    font-size: 13px;
  }
  .spark-table th {
    background: #7A5C2E; color: white; padding: 8px 12px;
    text-align: center; font-weight: 600; white-space: nowrap;
    border: 1px solid #5a4020;
  }
  .spark-table th.left { text-align: left; }
  .spark-table td {
    padding: 5px 10px; border: 1px solid #EEE5D8;
    vertical-align: middle; background: white;
  }
  .spark-table tr:nth-child(even) td { background: #FDF6ED; }
  .spark-table tr:hover td { background: #F5EAD8; }
  .spark-table td.group-label {
    font-weight: 600; color: #7A5C2E; white-space: nowrap;
    border-left: 3px solid #A4804A;
  }
  .spark-table td.num { text-align: center; color: #555; font-size: 12px; }
  .spark-table td.spark { text-align: center; padding: 4px 8px; }
  .spark-table td.score-val {
    text-align: center; font-weight: 700; font-size: 13px;
  }
  .spark-table td.score-hi { color: #1A7A3C; }
  .spark-table td.score-lo { color: #C0392B; }
  .spark-legend {
    display: flex; gap: 18px; align-items: center;
    font-size: 12px; color: #666; margin-bottom: 10px;
  }
  .spark-legend span { display: inline-flex; align-items: center; gap: 5px; }
  .dot-hi { width:9px; height:9px; border-radius:50%;
            background:#27AE60; display:inline-block; }
  .dot-lo { width:9px; height:9px; border-radius:50%;
            background:#E74C3C; display:inline-block; }
  .line-ref { width:22px; height:2px; background:#BBBBBB;
              display:inline-block; border-top: 2px dashed #BBBBBB; }
  .spark-section-label {
    font-size: 1rem; font-weight: 700; color: #7A5C2E;
    background: #FDF6ED; padding: 6px 14px; border-radius: 6px;
    margin: 16px 0 8px 0; display: inline-block;
  }
</style>
""", unsafe_allow_html=True)

# ── Palette ───────────────────────────────────────────────────────────────────
PAL = ["#A4804A",  # 0: NU Gold (primary)
       "#D4A568",  # 1: Medium Gold
       "#7A5C2E",  # 2: Dark Gold / Walnut
       "#F0E2C8",  # 3: Pale Gold (light fill)
       "#C8A882",  # 4: Warm Tan / Sand
       "#545454",  # 5: Dark Gray
       "#C8102E",  # 6: NU Red (accent only)
       "#9E9E9E"]  # 7: Mid Gray

# ── Metric config ─────────────────────────────────────────────────────────────
METRICS = {
    "Recommend":              "id_recommend_this_course_to_others_numeric_mean",
    "Instructor Effectiveness":"my_instructor_was_an_effective_and_engaging_facilitator_of_learning_numeric_mean",
    "Skill Acquisition":       "the_course_materials_and_assignments_helped_me_acquire_new_knowledge_and_skills_numeric_mean",
    "Job Relevance":           "taking_this_course_will_improve_my_job_performance_numeric_mean",
}
METRIC_COLS = list(METRICS.values())

# ── Helpers ───────────────────────────────────────────────────────────────────
def wtd_mean(values, weights):
    mask = values.notna() & weights.notna() & (weights > 0)
    if mask.sum() == 0:
        return np.nan
    return np.average(values[mask], weights=weights[mask])

def metric_card(label, value):
    return f"""
    <div class="metric-card">
      <div class="metric-val">{value}</div>
      <div class="metric-lbl">{label}</div>
    </div>"""

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("feedback_anonymized.csv")
    for c in METRIC_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["response_pct"]   = pd.to_numeric(df["response_pct"], errors="coerce")
    df["total_learners"] = pd.to_numeric(df["total_learners"], errors="coerce")
    df["responses"]      = pd.to_numeric(df["responses"], errors="coerce")
    df["first_run_label"] = df["first_run_section"].map({1:"First Run", 0:"Repeat Run"})
    df["calendar_month_dt"] = pd.to_datetime(df["calendar_month"])
    return df

df_raw = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("The Roux Institute_RGB_Monogram_RGB_NURed+B.png", width=140)
    st.markdown("## Roux Institute Custom Learning Feedback Dashboard")
    st.markdown("### Filters")

    metric_label = st.selectbox("Primary Metric", list(METRICS.keys()), key="metric_sel")
    metric_col   = METRICS[metric_label]

    # Date range slider
    months_all = sorted(df_raw["calendar_month"].dropna().unique())
    date_start, date_end = st.select_slider(
        "Date Range",
        options=months_all,
        value=(months_all[0], months_all[-1]),
        key="date_range"
    )

    # Cascading multiselects — each selection narrows the options below it
    pool = df_raw[(df_raw["calendar_month"] >= date_start) &
                  (df_raw["calendar_month"] <= date_end)].copy()

    persona  = st.multiselect("Persona",      sorted(pool["persona"].dropna().unique()),        placeholder="All", key="ms_persona")
    if persona:  pool = pool[pool["persona"].isin(persona)]

    level    = st.multiselect("Level",        sorted(pool["level"].dropna().unique()),           placeholder="All", key="ms_level")
    if level:    pool = pool[pool["level"].isin(level)]

    vertical = st.multiselect("Org Vertical", sorted(pool["org_vertical"].dropna().unique()),    placeholder="All", key="ms_vertical")
    if vertical: pool = pool[pool["org_vertical"].isin(vertical)]

    run_type = st.multiselect("Run Type",     sorted(pool["first_run_label"].dropna().unique()), placeholder="All", key="ms_run_type")
    if run_type: pool = pool[pool["first_run_label"].isin(run_type)]

    org      = st.multiselect("Organization", sorted(pool["organization"].dropna().unique()),    placeholder="All", key="ms_org")
    if org:      pool = pool[pool["organization"].isin(org)]

    course   = st.multiselect("Course",       sorted(pool["course_title"].dropna().unique()),    placeholder="All", key="ms_course")
    if course:   pool = pool[pool["course_title"].isin(course)]

    st.divider()
    if st.button("🔄 Reset All Filters", use_container_width=True):
        for k in ["metric_sel", "date_range", "ms_persona", "ms_level",
                  "ms_vertical", "ms_run_type", "ms_org", "ms_course"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── Apply filters ─────────────────────────────────────────────────────────────
df = pool

# ── Guard: empty filtered dataset ─────────────────────────────────────────────
if df.empty:
    st.warning("No data matches the current filters. Adjust the sidebar selections to continue.")
    st.stop()

# ── Navigation tabs ───────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Overview",
    "📚 Course Comparison",
    "🔍 Segment Analysis",
    "📬 Response Rates",
    "📈 Trends",
    "🔬 Statistical Tests",
    "✦ Sparklines",
    "📋 Raw Data",
    "🤝 Partner Report",
])

# ════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-hdr">Key Performance Indicators</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Sections", f"{len(df):,}"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Total Learners",
                                f"{int(df['total_learners'].sum()):,}"), unsafe_allow_html=True)
    with c3:
        rr = wtd_mean(df["response_pct"], df["total_learners"])
        st.markdown(metric_card("Avg Response Rate", f"{rr*100:.1f}%"), unsafe_allow_html=True)
    with c4:
        mv = wtd_mean(df[metric_col], df["responses"])
        st.markdown(metric_card(f"{metric_label} (wtd)", f"{mv:.2f} / 5"), unsafe_allow_html=True)

    st.divider()

    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown('<div class="section-hdr">All Four Metrics — Weighted Mean</div>',
                    unsafe_allow_html=True)
        means = {lbl: wtd_mean(df[col], df["responses"])
                 for lbl, col in METRICS.items()}
        fig = go.Figure(go.Bar(
            x=list(means.keys()), y=list(means.values()),
            marker_color=PAL[:4],
            text=[f"{v:.2f}" for v in means.values()],
            textposition="outside"
        ))
        fig.update_layout(yaxis=dict(range=[1, 5.5], title="Weighted Mean (1–5)"),
                          height=350, margin=dict(t=20, b=30))
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.markdown('<div class="section-hdr">Score Distribution</div>',
                    unsafe_allow_html=True)
        melt = df[METRIC_COLS].melt(var_name="metric", value_name="score").dropna()
        melt["metric"] = melt["metric"].map({v:k for k,v in METRICS.items()})
        fig2 = px.box(melt, x="metric", y="score", color="metric",
                      color_discrete_sequence=PAL,
                      range_y=[1, 5.5])
        fig2.update_layout(showlegend=False, height=350,
                           margin=dict(t=20, b=30),
                           xaxis_title="", yaxis_title="Score")
        st.plotly_chart(fig2, use_container_width=True)

    c3a, c3b = st.columns(2)
    with c3a:
        st.markdown('<div class="section-hdr">Sections by Vertical</div>',
                    unsafe_allow_html=True)
        vc = df["org_vertical"].value_counts().reset_index()
        vc.columns = ["vertical","count"]
        fig3 = px.bar(vc, x="count", y="vertical", orientation="h",
                      color_discrete_sequence=[PAL[1]])
        fig3.update_layout(height=280, margin=dict(t=10, b=10),
                           xaxis_title="Sections", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

    with c3b:
        st.markdown('<div class="section-hdr">Sections by Persona</div>',
                    unsafe_allow_html=True)
        pc = df["persona"].value_counts().reset_index()
        pc.columns = ["persona","count"]
        fig4 = px.pie(pc, values="count", names="persona",
                      color_discrete_sequence=PAL)
        fig4.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 2: COURSE COMPARISON
# ════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown(f'<div class="section-hdr">{metric_label} by Course</div>',
                unsafe_allow_html=True)

    d_course = (df.groupby("course_title")
                  .apply(lambda g: pd.Series({
                      "val": wtd_mean(g[metric_col], g["responses"]),
                      "n":   g["responses"].sum()
                  }))
                  .reset_index()
                  .dropna(subset=["val"])
                  .sort_values("val", ascending=True))

    fig = go.Figure(go.Bar(
        x=d_course["val"], y=d_course["course_title"],
        orientation="h",
        text=[f"{v:.2f} (n={int(n)})" for v, n in zip(d_course["val"], d_course["n"])],
        textposition="outside",
        marker_color=PAL[0]
    ))
    fig.update_layout(height=max(400, len(d_course)*30),
                      xaxis=dict(range=[1, 5.8], title=metric_label),
                      yaxis_title="",
                      margin=dict(l=320, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown('<div class="section-hdr">Heatmap — All Metrics × All Courses</div>',
                unsafe_allow_html=True)

    heat = (df.groupby("course_title")
              .apply(lambda g: pd.Series({
                  lbl: wtd_mean(g[col], g["responses"])
                  for lbl, col in METRICS.items()
              }))
              .reset_index())

    z_vals = heat[list(METRICS.keys())].values.round(2)
    fig5 = go.Figure(go.Heatmap(
        x=list(METRICS.keys()),
        y=heat["course_title"],
        z=z_vals,
        colorscale=[[0,"#F0E2C8"],[0.5,"#A4804A"],[1,"#7A5C2E"]],
        zmin=1, zmax=5,
        text=z_vals, texttemplate="%{text}"
    ))
    fig5.update_layout(height=max(350, len(heat)*28),
                       margin=dict(l=320, t=20, b=80))
    st.plotly_chart(fig5, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 3: SEGMENT ANALYSIS
# ════════════════════════════════════════════════════════════════════════
with tabs[2]:

    def seg_bar(group_col, title, color):
        d = (df.groupby(group_col)
               .apply(lambda g: pd.Series({
                   "val": wtd_mean(g[metric_col], g["responses"]),
                   "n":   len(g)
               }))
               .reset_index()
               .dropna(subset=["val"])
               .sort_values("val", ascending=False))
        fig = go.Figure(go.Bar(
            x=d[group_col], y=d["val"],
            text=[f"{v:.2f}\n(n={int(n)})" for v,n in zip(d["val"],d["n"])],
            textposition="outside",
            marker_color=color
        ))
        fig.update_layout(
            title=title, height=300,
            yaxis=dict(range=[1, 5.5], title=metric_label),
            xaxis_title="", margin=dict(t=40, b=10)
        )
        return fig

    c1, c2, c3 = st.columns(3)
    with c1: st.plotly_chart(seg_bar("level",       "By Level",    PAL[0]), use_container_width=True)
    with c2: st.plotly_chart(seg_bar("persona",     "By Persona",  PAL[4]), use_container_width=True)
    with c3: st.plotly_chart(seg_bar("org_vertical","By Vertical", PAL[2]), use_container_width=True)

    c4, c5 = st.columns(2)
    with c4:
        st.markdown('<div class="section-hdr">First Run vs Repeat — All Metrics</div>',
                    unsafe_allow_html=True)
        fr = (df.groupby("first_run_label")
                .apply(lambda g: pd.Series({
                    lbl: wtd_mean(g[col], g["responses"])
                    for lbl, col in METRICS.items()
                }))
                .reset_index()
                .melt(id_vars="first_run_label", var_name="metric", value_name="val"))
        fig6 = px.bar(fr, x="metric", y="val", color="first_run_label",
                      barmode="group", color_discrete_sequence=[PAL[0], PAL[4]],
                      range_y=[1, 5.5])
        fig6.update_layout(height=320, margin=dict(t=20))
        st.plotly_chart(fig6, use_container_width=True)

    with c5:
        st.plotly_chart(seg_bar("organization", "By Organization", PAL[1]),
                        use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 4: RESPONSE RATES
# ════════════════════════════════════════════════════════════════════════
with tabs[3]:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-hdr">Response Rate by Course</div>',
                    unsafe_allow_html=True)
        d = (df.groupby("course_title")
               .apply(lambda g: wtd_mean(g["response_pct"], g["total_learners"]))
               .reset_index(name="rr")
               .dropna()
               .sort_values("rr", ascending=True))
        fig = go.Figure(go.Bar(
            x=d["rr"], y=d["course_title"], orientation="h",
            text=[f"{v*100:.1f}%" for v in d["rr"]],
            textposition="outside", marker_color=PAL[2]
        ))
        fig.update_layout(height=max(350, len(d)*28),
                          xaxis=dict(range=[0, 1.2], tickformat=".0%"),
                          margin=dict(l=320, t=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-hdr">Response Rate by Vertical</div>',
                    unsafe_allow_html=True)
        d2 = (df.groupby("org_vertical")
                .apply(lambda g: wtd_mean(g["response_pct"], g["total_learners"]))
                .reset_index(name="rr")
                .dropna()
                .sort_values("rr", ascending=True))
        fig2 = go.Figure(go.Bar(
            x=d2["rr"], y=d2["org_vertical"], orientation="h",
            text=[f"{v*100:.1f}%" for v in d2["rr"]],
            textposition="outside", marker_color=PAL[4]
        ))
        fig2.update_layout(height=350, xaxis=dict(range=[0,1.2], tickformat=".0%"),
                           margin=dict(l=160, t=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-hdr">Response Rate vs Satisfaction</div>',
                    unsafe_allow_html=True)
        sc = df[["response_pct", metric_col, "course_title",
                 "organization", "persona", "level"]].dropna()
        r, p = stats.pearsonr(sc["response_pct"], sc[metric_col])
        fig3 = px.scatter(sc, x="response_pct", y=metric_col,
                          color="persona", color_discrete_sequence=PAL,
                          hover_data=["course_title","organization"],
                          trendline="ols",
                          range_y=[1, 5.5],
                          labels={"response_pct":"Response Rate", metric_col: metric_label})
        fig3.update_layout(height=340,
                           title=f"Pearson r={r:.3f}, p={p:.3f}",
                           margin=dict(t=40))
        fig3.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown('<div class="section-hdr">Response Rate: First Run vs Repeat</div>',
                    unsafe_allow_html=True)
        d4 = (df.groupby("first_run_label")
                .apply(lambda g: wtd_mean(g["response_pct"], g["total_learners"]))
                .reset_index(name="rr"))
        fig4 = go.Figure(go.Bar(
            x=d4["first_run_label"], y=d4["rr"],
            text=[f"{v*100:.1f}%" for v in d4["rr"]],
            textposition="outside",
            marker_color=[PAL[0], PAL[4]]
        ))
        fig4.update_layout(height=340, yaxis=dict(range=[0, 1.2], tickformat=".0%"),
                           xaxis_title="", margin=dict(t=10))
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 5: TRENDS
# ════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(f'<div class="section-hdr">{metric_label} — Monthly Trend</div>',
                unsafe_allow_html=True)

    trend = (df.groupby("calendar_month_dt")
               .apply(lambda g: pd.Series({
                   "val": wtd_mean(g[metric_col], g["responses"]),
                   "n":   len(g)
               }))
               .reset_index()
               .dropna(subset=["val"]))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["calendar_month_dt"], y=trend["val"],
        mode="lines+markers",
        line=dict(color=PAL[0], width=2.5),
        marker=dict(size=8),
        name=metric_label
    ))
    fig.update_layout(height=380, yaxis=dict(range=[1,5.5], title=metric_label),
                      xaxis_title="Month", margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        rrt = (df.groupby("calendar_month_dt")
                 .apply(lambda g: wtd_mean(g["response_pct"], g["total_learners"]))
                 .reset_index(name="rr")
                 .dropna())
        fig2 = px.line(rrt, x="calendar_month_dt", y="rr",
                       markers=True, color_discrete_sequence=[PAL[4]])
        fig2.update_layout(title="Response Rate — Monthly",
                           height=300, yaxis=dict(tickformat=".0%"),
                           xaxis_title="Month", yaxis_title="Response Rate")
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        vol = df.groupby("calendar_month_dt").size().reset_index(name="sections")
        fig3 = px.bar(vol, x="calendar_month_dt", y="sections",
                      color_discrete_sequence=[PAL[2]])
        fig3.update_layout(title="Section Volume — Monthly",
                           height=300, xaxis_title="Month", yaxis_title="Sections")
        st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 6: STATISTICAL TESTS
# ════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-hdr">One-Way ANOVA</div>', unsafe_allow_html=True)
    st.caption("Tests whether mean scores differ significantly across groups. "
               "p < 0.05 = statistically significant variation.")

    group_col = st.selectbox("Group By",
                             ["persona","level","org_vertical","first_run_label"])

    clean = df[[metric_col, group_col, "responses"]].dropna()

    if clean[group_col].nunique() >= 2:
        groups = [grp[metric_col].values
                  for _, grp in clean.groupby(group_col)
                  if len(grp) >= 2]
        f_stat, p_val = stats.f_oneway(*groups)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**ANOVA Result**")
            result_df = pd.DataFrame({
                "Statistic": ["F-statistic", "p-value", "Significant"],
                "Value":     [f"{f_stat:.3f}", f"{p_val:.4f}",
                              "✓ Yes (p < 0.05)" if p_val < 0.05 else "✗ No"]
            })
            st.dataframe(result_df, use_container_width=True, hide_index=True)

        with c2:
            st.markdown("**Group Means**")
            gm = (clean.groupby(group_col)
                       .apply(lambda g: pd.Series({
                           "N":          len(g),
                           "Wtd Mean":   round(wtd_mean(g[metric_col], g["responses"]), 3),
                           "Std Dev":    round(g[metric_col].std(), 3)
                       }))
                       .reset_index()
                       .sort_values("Wtd Mean", ascending=False))
            st.dataframe(gm, use_container_width=True, hide_index=True)
    else:
        st.warning("Need at least 2 groups in the filtered data for ANOVA.")

    st.divider()
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-hdr">Correlation Matrix — All Metrics + Response Rate</div>',
                    unsafe_allow_html=True)
        corr_df = df[METRIC_COLS + ["response_pct"]].copy()
        corr_df.columns = list(METRICS.keys()) + ["Response Rate"]
        cm = corr_df.corr(numeric_only=True).round(2)
        fig = go.Figure(go.Heatmap(
            x=cm.columns, y=cm.index, z=cm.values,
            colorscale=[[0,"#7A5C2E"],[0.5,"white"],[1,"#A4804A"]],
            zmin=-1, zmax=1,
            text=cm.values.round(2), texttemplate="%{text}"
        ))
        fig.update_layout(height=380, margin=dict(l=150, b=120, t=10))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown('<div class="section-hdr">OLS Regression — Metric Predictors</div>',
                    unsafe_allow_html=True)
        st.caption(f"Dependent variable: {metric_label}")

        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import OneHotEncoder
            import warnings
            warnings.filterwarnings("ignore")

            reg_df = df[[metric_col,"response_pct","first_run_section",
                        "level","persona"]].dropna()
            dummies = pd.get_dummies(
                reg_df[["level","persona"]], drop_first=True)
            X = pd.concat([
                reg_df[["response_pct","first_run_section"]].reset_index(drop=True),
                dummies.reset_index(drop=True)
            ], axis=1).astype(float)
            y = reg_df[metric_col].values

            # Manual OLS with p-values using scipy
            from numpy.linalg import lstsq
            X_c = np.column_stack([np.ones(len(X)), X])
            coef, _, _, _ = lstsq(X_c, y, rcond=None)
            y_hat = X_c @ coef
            residuals = y - y_hat
            dof = len(y) - X_c.shape[1]
            mse = np.sum(residuals**2) / dof
            cov = mse * np.linalg.inv(X_c.T @ X_c)
            se = np.sqrt(np.diag(cov))
            t_stats = coef / se
            p_vals = 2 * stats.t.sf(np.abs(t_stats), dof)

            reg_result = pd.DataFrame({
                "Term":    ["Intercept"] + list(X.columns),
                "Coef":    coef.round(4),
                "Std Err": se.round(4),
                "t-stat":  t_stats.round(3),
                "p-value": p_vals.round(4),
                "Sig":     ["✓" if p < 0.05 else "" for p in p_vals]
            })
            st.dataframe(reg_result, use_container_width=True, hide_index=True,
                         column_config={"Sig": st.column_config.TextColumn("Sig")})
        except Exception as e:
            st.error(f"Regression error: {e}")

# ════════════════════════════════════════════════════════════════════════
# TAB 7: SPARKLINES
# ════════════════════════════════════════════════════════════════════════
with tabs[6]:

    # ── Sparkline rendering helpers ───────────────────────────────────────
    ALL_SPARK_METRICS = {
        "Recommend":  "id_recommend_this_course_to_others_numeric_mean",
        "Instructor": "my_instructor_was_an_effective_and_engaging_facilitator_of_learning_numeric_mean",
        "Skills":     "the_course_materials_and_assignments_helped_me_acquire_new_knowledge_and_skills_numeric_mean",
        "Job Rel.":   "taking_this_course_will_improve_my_job_performance_numeric_mean",
        "Response %": "response_pct",
    }

    def wtd_mean_spark(g, col):
        """Weighted mean for sparkline computation."""
        w_col = "total_learners" if col == "response_pct" else "responses"
        mask = g[col].notna() & g[w_col].notna() & (g[w_col] > 0)
        if mask.sum() == 0:
            return np.nan
        return np.average(g[col][mask], weights=g[w_col][mask])

    def build_monthly_series(source_df, group_col, metric_col):
        """Monthly weighted mean series per group value, sorted chronologically."""
        result = {}
        for grp, gdf in source_df.groupby(group_col):
            monthly = (
                gdf.groupby("calendar_month_dt")
                   .apply(lambda g: wtd_mean_spark(g, metric_col))
                   .sort_index()
                   .dropna()
            )
            result[grp] = monthly
        return result

    def build_crosssection_series(source_df, group_col, metric_col):
        """Per-course weighted mean per group (for orgs with sparse temporal data)."""
        result = {}
        for grp, gdf in source_df.groupby(group_col):
            by_course = (
                gdf.groupby("course_title")
                   .apply(lambda g: wtd_mean_spark(g, metric_col))
                   .dropna()
                   .sort_values()
            )
            result[grp] = by_course
        return result

    def make_sparkline_img(values, overall_mean, is_pct=False,
                           px_w=160, px_h=34, dpi=96):
        """
        Render a sparkline as a transparent-background base64 PNG.
        - Temporal line with fill above/below overall mean
        - Single dot for 1-observation groups
        - Dashed reference line at overall mean
        - Terminal dot colored green/red vs mean
        """
        fig, ax = plt.subplots(figsize=(px_w / dpi, px_h / dpi), dpi=dpi)
        ax.set_facecolor("none")
        fig.patch.set_alpha(0.0)

        scale = (0.0, 1.05) if is_pct else (1.0, 5.2)

        if len(values) == 0:
            ax.axis("off")

        elif len(values) == 1:
            v = float(values.iloc[0])
            color = "#27AE60" if v >= overall_mean else "#E74C3C"
            ax.axhline(overall_mean, color="#BBBBBB", linewidth=0.9,
                       linestyle="--", zorder=1)
            ax.scatter([0.5], [v], color=color, s=36, zorder=5, clip_on=False)
            ax.set_xlim(0, 1)
            ax.set_ylim(*scale)
            ax.axis("off")

        else:
            xs = np.arange(len(values), dtype=float)
            ys = np.array(values.values, dtype=float)

            # Dashed reference at overall mean
            ax.axhline(overall_mean, color="#BBBBBB", linewidth=0.85,
                       linestyle="--", zorder=1)

            # Fill above / below mean
            ax.fill_between(xs, ys, overall_mean,
                            where=(ys >= overall_mean),
                            color="#2E86C1", alpha=0.22, interpolate=True)
            ax.fill_between(xs, ys, overall_mean,
                            where=(ys < overall_mean),
                            color="#E74C3C", alpha=0.18, interpolate=True)

            # Line
            ax.plot(xs, ys, color="#1B4F72", linewidth=1.3, zorder=3,
                    solid_capstyle="round")

            # Intermediate dots for very short series
            if len(ys) <= 5:
                ax.scatter(xs[:-1], ys[:-1], color="#1B4F72",
                           s=12, zorder=4, alpha=0.6)

            # Terminal dot colored vs mean
            end_color = "#27AE60" if ys[-1] >= overall_mean else "#E74C3C"
            ax.scatter([xs[-1]], [ys[-1]], color=end_color,
                       s=28, zorder=6, clip_on=False)

            ax.set_xlim(xs[0] - 0.3, xs[-1] + 0.3)
            ax.set_ylim(*scale)
            ax.axis("off")

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight",
                    pad_inches=0.01, transparent=True)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    def score_cell(val, overall_mean, is_pct=False):
        """Format the summary value cell with color class."""
        if np.isnan(val):
            return '<td class="num">—</td>'
        cls = "score-hi" if val >= overall_mean else "score-lo"
        fmt = f"{val*100:.1f}%" if is_pct else f"{val:.2f}"
        return f'<td class="score-val {cls}">{fmt}</td>'

    def build_spark_table(source_df, group_col, series_mode="monthly"):
        """
        Build the full HTML sparkline table for a given grouping dimension.
        series_mode: 'monthly' (temporal) or 'crosssection' (per-course)
        """
        # Overall benchmark values
        overall = {}
        for lbl, col in ALL_SPARK_METRICS.items():
            w_col = "total_learners" if col == "response_pct" else "responses"
            mask = source_df[col].notna() & source_df[w_col].notna()
            if mask.sum() > 0:
                overall[lbl] = np.average(
                    source_df[col][mask], weights=source_df[w_col][mask])
            else:
                overall[lbl] = np.nan

        # Group-level summary stats
        group_stats = {}
        for grp, gdf in source_df.groupby(group_col):
            group_stats[grp] = {
                "n_sections": len(gdf),
                "n_learners": int(gdf["total_learners"].sum()),
                "means": {lbl: wtd_mean_spark(gdf, col)
                          for lbl, col in ALL_SPARK_METRICS.items()}
            }

        # Pre-render all sparklines
        spark_imgs = {}
        for lbl, col in ALL_SPARK_METRICS.items():
            is_pct = (col == "response_pct")
            if series_mode == "monthly":
                series_map = build_monthly_series(source_df, group_col, col)
            else:
                series_map = build_crosssection_series(source_df, group_col, col)

            for grp, vals in series_map.items():
                key = (grp, lbl)
                om = overall.get(lbl, np.nan)
                if np.isnan(om):
                    spark_imgs[key] = ""
                else:
                    spark_imgs[key] = make_sparkline_img(
                        vals, om, is_pct=is_pct)

        # Metric header labels
        metric_labels = list(ALL_SPARK_METRICS.keys())
        n_pts_label = "Months" if series_mode == "monthly" else "Courses"

        # ── Overall reference row ─────────────────────────────────────────
        ref_cells = ""
        for lbl, col in ALL_SPARK_METRICS.items():
            is_pct = (col == "response_pct")
            v = overall[lbl]
            fmt = f"{v*100:.1f}%" if is_pct else f"{v:.2f}"
            ref_cells += (f'<td class="score-val" '
                          f'style="color:#1B4F72;font-size:12px;">{fmt}</td>')

        # ── Group rows ────────────────────────────────────────────────────
        rows_html = ""
        for grp in sorted(group_stats.keys()):
            st_info  = group_stats[grp]
            row_html = (f'<td class="group-label">{grp}</td>'
                        f'<td class="num">{st_info["n_sections"]}</td>'
                        f'<td class="num">{st_info["n_learners"]:,}</td>')

            for lbl, col in ALL_SPARK_METRICS.items():
                is_pct = (col == "response_pct")
                img_b64 = spark_imgs.get((grp, lbl), "")
                grp_mean = st_info["means"][lbl]
                om = overall[lbl]

                if img_b64:
                    img_tag = (f'<img src="data:image/png;base64,{img_b64}" '
                               f'style="display:block;margin:auto;" />')
                else:
                    img_tag = '<span style="color:#ccc;font-size:10px;">n/a</span>'

                # Color-code the sparkline cell border-bottom
                if not np.isnan(grp_mean) and not np.isnan(om):
                    border_col = "#27AE60" if grp_mean >= om else "#E74C3C"
                    cell_style = f"border-bottom: 2px solid {border_col};"
                else:
                    cell_style = ""

                row_html += (f'<td class="spark" style="{cell_style}">'
                             f'{img_tag}</td>')
                row_html += score_cell(grp_mean, om, is_pct=is_pct)

            rows_html += f"<tr>{row_html}</tr>\n"

        # ── Assemble headers ──────────────────────────────────────────────
        metric_headers = ""
        for lbl in metric_labels:
            metric_headers += (f'<th colspan="2" style="background:#2E86C1;">'
                               f'{lbl}</th>')

        html = f"""
        <table class="spark-table">
          <thead>
            <tr>
              <th class="left" rowspan="2">{group_col.replace('_',' ').title()}</th>
              <th rowspan="2">Sections</th>
              <th rowspan="2">Learners</th>
              {metric_headers}
            </tr>
            <tr>
              {"".join(f'<th style="background:#144060;font-size:11px;">Trend<br>({n_pts_label})</th>'
                       f'<th style="background:#144060;font-size:11px;">Wtd<br>Mean</th>'
                       for _ in metric_labels)}
            </tr>
          </thead>
          <tbody>
            <tr style="border-top:2px solid #A4804A;">
              <td class="group-label" style="color:#888;font-weight:400;
                  font-style:italic;border-left:3px solid #BBBBBB;">
                ◈ Overall Benchmark
              </td>
              <td class="num">{len(source_df)}</td>
              <td class="num">{int(source_df['total_learners'].sum()):,}</td>
              {ref_cells}
            </tr>
            {rows_html}
          </tbody>
        </table>
        """
        return html.strip()

    # ── Tab UI ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-hdr">KPI Sparklines — Trend vs. Overall Benchmark</div>',
        unsafe_allow_html=True)

    st.markdown("""
    <div class="spark-legend">
      <span>Each sparkline shows the weighted mean trend over time (or across courses for organizations).</span>
      &nbsp;|&nbsp;
      <span><span class="line-ref"></span> Overall benchmark (all sections)</span>
      <span><span class="dot-hi"></span> At or above benchmark</span>
      <span><span class="dot-lo"></span> Below benchmark</span>
      <span style="font-style:italic;color:#999;">Fill: blue = above avg · red = below avg</span>
    </div>
    """, unsafe_allow_html=True)

    dim_choice = st.radio(
        "Group By",
        ["Analytical LEAP Persona", "Org Vertical", "Customer (Organization)"],
        horizontal=True
    )

    dim_map = {
        "Analytical LEAP Persona":   ("persona",       "monthly"),
        "Org Vertical":              ("org_vertical",   "monthly"),
        "Customer (Organization)":   ("organization",   "crosssection"),
    }
    group_col, series_mode = dim_map[dim_choice]

    if dim_choice == "Customer (Organization)":
        st.caption(
            "Organizations have limited temporal data, so sparklines here show "
            "the score distribution across individual course deliveries "
            "(sorted ascending), rather than a monthly trend.")

    with st.spinner("Rendering sparklines…"):
        table_html = build_spark_table(df, group_col, series_mode)

    st.markdown(table_html, unsafe_allow_html=True)
    st.caption(
        "Terminal dot = most recent value (monthly) or highest-scoring course "
        "(cross-sectional). Weighted means weight each section by its "
        "number of survey responses.")


# ════════════════════════════════════════════════════════════════════════
# TAB 8: RAW DATA
# ════════════════════════════════════════════════════════════════════════
with tabs[7]:
    display_cols = [
        "course_title","organization","org_vertical","calendar_month",
        "persona","level","first_run_section","responses","total_learners",
        "response_pct"
    ] + METRIC_COLS

    show = df[[c for c in display_cols if c in df.columns]].copy()
    show.columns = [
        "Course","Organization","Vertical","Month",
        "Persona","Level","First Run","Responses","Total Learners",
        "Response %", "Recommend","Instructor","Skills","Job Relevance"
    ][:len(show.columns)]
    show = show.round(3)

    st.dataframe(show, use_container_width=True, height=500)
    st.download_button(
        "⬇️ Download Filtered Data",
        data=show.to_csv(index=False).encode(),
        file_name="leap_filtered.csv",
        mime="text/csv"
    )

# ════════════════════════════════════════════════════════════════════════
# TAB 9: PARTNER REPORT
# ════════════════════════════════════════════════════════════════════════
with tabs[8]:

    all_orgs = sorted(df_raw["organization"].dropna().unique())
    selected_partner = st.selectbox(
        "Select Partner Organization", all_orgs, key="partner_org"
    )

    p_df = df_raw[
        (df_raw["organization"] == selected_partner) &
        (df_raw["calendar_month"] >= date_start) &
        (df_raw["calendar_month"] <= date_end)
    ].copy()

    bench_df = df_raw[
        (df_raw["calendar_month"] >= date_start) &
        (df_raw["calendar_month"] <= date_end)
    ].copy()

    if p_df.empty:
        st.warning(f"No data found for {selected_partner} in the selected date range.")
    else:
        n_courses   = p_df["course_title"].nunique()
        n_learners  = int(p_df["total_learners"].sum())
        n_sections  = len(p_df)
        p_rr        = wtd_mean(p_df["response_pct"], p_df["total_learners"])
        overall_sat = {lbl: wtd_mean(p_df[col], p_df["responses"])
                       for lbl, col in METRICS.items()}
        avg_sat     = np.nanmean([v for v in overall_sat.values() if not np.isnan(v)])
        date_range_label = f"{date_start} – {date_end}"

        st.markdown(f"""
        <div class="partner-banner">
          <h1>{selected_partner}</h1>
          <p>Roux Custom Learning &nbsp;|&nbsp; Learner Experience Report &nbsp;|&nbsp; {date_range_label}</p>
        </div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4, k5 = st.columns(5)
        kpis = [
            (f"{n_courses}",       "Courses Delivered"),
            (f"{n_sections}",      "Sections Completed"),
            (f"{n_learners:,}",    "Learners Reached"),
            (f"{avg_sat:.2f} / 5", "Avg Satisfaction"),
            (f"{p_rr*100:.1f}%",   "Feedback Response Rate"),
        ]
        for col, (val, lbl) in zip([k1, k2, k3, k4, k5], kpis):
            with col:
                st.markdown(
                    f'<div class="partner-kpi">'
                    f'<div class="partner-kpi-val">{val}</div>'
                    f'<div class="partner-kpi-lbl">{lbl}</div>'
                    f'</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">How You Compare — vs. Roux Portfolio Benchmark</div>',
                    unsafe_allow_html=True)

        bench_vals = {lbl: wtd_mean(bench_df[col], bench_df["responses"])
                      for lbl, col in METRICS.items()}

        bm_rows = []
        for lbl in METRICS:
            pv, bv = overall_sat[lbl], bench_vals[lbl]
            if not (np.isnan(pv) or np.isnan(bv)):
                diff  = pv - bv
                arrow = "▲" if diff >= 0 else "▼"
                css   = "benchmark-better" if diff >= 0 else "benchmark-worse"
                bm_rows.append({"Metric": lbl, "Your Score": f"{pv:.2f}",
                                 "Portfolio Avg": f"{bv:.2f}",
                                 "Difference": f'<span class="{css}">{arrow} {abs(diff):.2f}</span>'})

        bc1, bc2 = st.columns([1, 2])
        with bc1:
            html_rows = "".join(
                f"<tr><td>{r['Metric']}</td><td>{r['Your Score']}</td>"
                f"<td>{r['Portfolio Avg']}</td><td>{r['Difference']}</td></tr>"
                for _, r in pd.DataFrame(bm_rows).iterrows()
            )
            st.markdown(f"""<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">
  <thead><tr style="background:#7A5C2E;color:white;">
    <th style="padding:8px;text-align:left">Metric</th>
    <th style="padding:8px;text-align:center">Your Score</th>
    <th style="padding:8px;text-align:center">Portfolio Avg</th>
    <th style="padding:8px;text-align:center">vs. Benchmark</th>
  </tr></thead>
  <tbody>{html_rows}</tbody>
</table>""", unsafe_allow_html=True)

        with bc2:
            fig_bm = go.Figure()
            fig_bm.add_trace(go.Bar(
                name="Portfolio Avg", x=list(METRICS.keys()),
                y=[bench_vals[l] for l in METRICS],
                marker_color=PAL[3], opacity=0.85))
            fig_bm.add_trace(go.Bar(
                name=selected_partner, x=list(METRICS.keys()),
                y=[overall_sat[l] for l in METRICS],
                marker_color=PAL[0]))
            fig_bm.update_layout(
                barmode="group", height=260,
                yaxis=dict(range=[1, 5.5], title="Score (1–5)"),
                xaxis_title="", margin=dict(t=10, b=10),
                legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig_bm, use_container_width=True)

        st.divider()
        st.markdown('<div class="section-hdr">Course Performance Summary</div>',
                    unsafe_allow_html=True)

        course_summary = (
            p_df.groupby("course_title")
              .apply(lambda g: pd.Series({
                  "Sections":          len(g),
                  "Learners":          int(g["total_learners"].sum()),
                  "Response Rate":     wtd_mean(g["response_pct"], g["total_learners"]),
                  "Recommend":         wtd_mean(g[METRICS["Recommend"]], g["responses"]),
                  "Instructor":        wtd_mean(g[METRICS["Instructor Effectiveness"]], g["responses"]),
                  "Skill Acquisition": wtd_mean(g[METRICS["Skill Acquisition"]], g["responses"]),
                  "Job Relevance":     wtd_mean(g[METRICS["Job Relevance"]], g["responses"]),
              }))
              .reset_index().rename(columns={"course_title": "Course"})
        )
        course_summary["Avg Score"] = course_summary[
            ["Recommend","Instructor","Skill Acquisition","Job Relevance"]].mean(axis=1)
        course_summary = course_summary.sort_values("Avg Score", ascending=False)
        for c in ["Response Rate","Recommend","Instructor","Skill Acquisition","Job Relevance","Avg Score"]:
            course_summary[c] = course_summary[c].round(2)
        course_summary["Response Rate"] = course_summary["Response Rate"].apply(
            lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—")

        st.dataframe(
            course_summary.set_index("Course"), use_container_width=True,
            column_config={
                "Avg Score":         st.column_config.ProgressColumn("Avg Score", min_value=1, max_value=5, format="%.2f"),
                "Recommend":         st.column_config.NumberColumn(format="%.2f"),
                "Instructor":        st.column_config.NumberColumn(format="%.2f"),
                "Skill Acquisition": st.column_config.NumberColumn(format="%.2f"),
                "Job Relevance":     st.column_config.NumberColumn(format="%.2f"),
            })

        st.divider()
        cl, cr = st.columns([3, 2])
        with cl:
            st.markdown('<div class="section-hdr">Satisfaction Heatmap</div>', unsafe_allow_html=True)
            heat_p = (p_df.groupby("course_title")
                          .apply(lambda g: pd.Series({
                              lbl: wtd_mean(g[col], g["responses"])
                              for lbl, col in METRICS.items()}))
                          .reset_index()
                          .dropna(how="all", subset=list(METRICS.keys())))
            z_p = heat_p[list(METRICS.keys())].values.round(2)
            fig_h = go.Figure(go.Heatmap(
                x=list(METRICS.keys()), y=heat_p["course_title"], z=z_p,
                colorscale=[[0,"#F0E2C8"],[0.5,"#A4804A"],[1,"#7A5C2E"]],
                zmin=1, zmax=5, text=z_p, texttemplate="%{text}"))
            fig_h.update_layout(height=max(250, len(heat_p)*34),
                                margin=dict(l=300, t=10, b=60))
            st.plotly_chart(fig_h, use_container_width=True)

        with cr:
            st.markdown('<div class="section-hdr">Satisfaction Over Time</div>', unsafe_allow_html=True)
            trend_p = (p_df.groupby("calendar_month_dt")
                           .apply(lambda g: pd.Series({
                               lbl: wtd_mean(g[col], g["responses"])
                               for lbl, col in METRICS.items()}))
                           .reset_index()
                           .dropna(how="all", subset=list(METRICS.keys())))
            fig_t = go.Figure()
            for i, lbl in enumerate(METRICS):
                fig_t.add_trace(go.Scatter(
                    x=trend_p["calendar_month_dt"], y=trend_p[lbl],
                    mode="lines+markers", name=lbl,
                    line=dict(color=PAL[i], width=2)))
            fig_t.update_layout(
                height=max(250, len(heat_p)*34),
                yaxis=dict(range=[1, 5.5], title="Score"),
                xaxis_title="Month",
                legend=dict(orientation="h", y=-0.3),
                margin=dict(t=10, b=60))
            st.plotly_chart(fig_t, use_container_width=True)

        st.divider()
        st.markdown('<div class="section-hdr">Highlights</div>', unsafe_allow_html=True)
        h1, h2, h3 = st.columns(3)
        with h1:
            top = course_summary.iloc[0]
            st.markdown(
                f'<div class="highlight-box"><b>Top Rated Course</b><br>{top["Course"]}<br>'
                f'<span style="font-size:1.4rem;font-weight:700;color:#7A5C2E">'
                f'{top["Avg Score"]:.2f} / 5</span></div>', unsafe_allow_html=True)
        with h2:
            best_m = max(overall_sat, key=lambda k: overall_sat[k] if not np.isnan(overall_sat[k]) else 0)
            st.markdown(
                f'<div class="highlight-box"><b>Strongest Dimension</b><br>{best_m}<br>'
                f'<span style="font-size:1.4rem;font-weight:700;color:#7A5C2E">'
                f'{overall_sat[best_m]:.2f} / 5</span></div>', unsafe_allow_html=True)
        with h3:
            st.markdown(
                f'<div class="highlight-box"><b>Learner Engagement</b><br>Feedback response rate<br>'
                f'<span style="font-size:1.4rem;font-weight:700;color:#7A5C2E">'
                f'{p_rr*100:.1f}%</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        dl_cols = ["course_title","calendar_month","persona","level",
                   "responses","total_learners","response_pct"] + METRIC_COLS
        dl_df = p_df[[c for c in dl_cols if c in p_df.columns]].copy().round(3)
        st.download_button(
            f"⬇️ Download {selected_partner} Data",
            data=dl_df.to_csv(index=False).encode(),
            file_name=f"leap_{selected_partner.replace(' ','_')}.csv",
            mime="text/csv"
        )
