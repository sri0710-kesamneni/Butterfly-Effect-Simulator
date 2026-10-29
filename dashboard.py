from pathlib import Path
import json
import urllib.request
import urllib.error

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from real_data import (
    load_workbook, prepare_data, data_quality, duration_summary,
    duration_sensitivity, correlation_summary, theoretical_capacity_experiment
)

# ─────────────────────────────────────────────────────────────────────────────
# Page setup + visual system
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Butterfly Effect | Research Studio",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAPER = "#F6F3EA"
CARD = "#FFFEFA"
INK = "#24352F"
MUTED = "#69766D"
GREEN = "#456D5C"
GREEN_DARK = "#2E4F41"
LILAC = "#DCD4ED"
CORAL = "#D67F69"
MINT = "#DDE8DE"
LINE = "#DCDDD2"
GOLD = "#C5A46D"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root {{
 --paper:{PAPER}; --card:{CARD}; --ink:{INK}; --muted:{MUTED};
 --green:{GREEN}; --green-dark:{GREEN_DARK}; --lilac:{LILAC};
 --coral:{CORAL}; --mint:{MINT}; --line:{LINE}; --gold:{GOLD};
}}
.stApp {{
 background:
 radial-gradient(ellipse at 100% 0%, rgba(220,212,237,.45) 0, transparent 28%),
 radial-gradient(ellipse at 0% 38%, rgba(221,232,222,.45) 0, transparent 25%),
 var(--paper);
 color:var(--ink); font-family:'DM Sans',sans-serif;
}}
[data-testid="stHeader"] {{background:rgba(246,243,234,.9);}}
.block-container {{max-width:1500px;padding-top:1.6rem;padding-bottom:3rem;}}
h1,h2,h3 {{font-family:'Playfair Display',Georgia,serif!important;color:var(--ink)!important;letter-spacing:-.025em;}}
p,li,label,.stMarkdown {{color:var(--ink);}}
[data-testid="stSidebar"] {{background:#ECEDE3;border-right:1px solid var(--line);}}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {{font-family:'DM Sans',sans-serif!important;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{padding:.35rem .2rem;}}
div[data-testid="stTabs"] button {{font-weight:600;color:var(--muted);}}
div[data-testid="stTabs"] button[aria-selected="true"] {{color:var(--green-dark);border-bottom-color:var(--coral);}}
.stButton>button,.stDownloadButton>button {{
 border-radius:11px;background:var(--green);color:white;border:1px solid var(--green);
 font-weight:600;padding:.52rem 1rem;transition:all .16s ease;
}}
.stButton>button:hover,.stDownloadButton>button:hover {{background:var(--green-dark);border-color:var(--green-dark);color:white;transform:translateY(-1px);}}
div[data-testid="stDataFrame"] {{border:1px solid var(--line);border-radius:12px;overflow:hidden;}}
div[data-testid="stAlert"] {{border-radius:12px;}}
.metric-card {{background:rgba(255,254,250,.88);border:1px solid var(--line);border-radius:17px;padding:1rem 1.05rem;min-height:120px;box-shadow:0 5px 18px rgba(36,53,47,.035);}}
.metric-label {{font-size:.7rem;letter-spacing:.12em;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:.55rem;}}
.metric-value {{font-size:1.85rem;line-height:1.12;font-weight:700;letter-spacing:-.045em;color:var(--green-dark);}}
.metric-note {{font-size:.75rem;color:var(--muted);margin-top:.45rem;}}
.eyebrow {{font-size:.7rem;letter-spacing:.17em;font-weight:700;text-transform:uppercase;color:var(--green);}}
.hero {{border:1px solid rgba(69,109,92,.2);border-radius:25px;background:linear-gradient(110deg,rgba(255,254,250,.96),rgba(239,237,229,.94));padding:2rem 2.15rem;margin-bottom:1.2rem;position:relative;overflow:hidden;box-shadow:0 12px 34px rgba(36,53,47,.045);}}
.hero:after {{content:"❋";position:absolute;right:2.2rem;top:-2.4rem;font-size:11rem;color:rgba(214,127,105,.14);transform:rotate(15deg);pointer-events:none;}}
.hero h1 {{font-size:clamp(2.2rem,4vw,3.55rem);line-height:1.02;margin:.55rem 0 .75rem;max-width:800px;}}
.hero p {{color:var(--muted);max-width:760px;line-height:1.7;margin-bottom:1rem;}}
.pill {{display:inline-block;border-radius:999px;background:var(--lilac);color:#51476A;padding:.38rem .7rem;font-size:.72rem;font-weight:700;letter-spacing:.04em;}}
.page-head {{padding:.4rem 0 .9rem;border-bottom:1px solid var(--line);margin-bottom:1.2rem;}}
.page-head h2 {{font-size:2.05rem;margin:.35rem 0 .25rem;}}
.page-head p {{color:var(--muted);max-width:900px;margin-bottom:.4rem;}}
.info-card {{background:rgba(255,254,250,.78);border:1px solid var(--line);border-radius:15px;padding:1rem 1.05rem;height:100%;}}
.info-card .label {{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:var(--muted);}}
.info-card .body {{margin-top:.45rem;line-height:1.55;color:var(--ink);}}
.note {{font-size:.78rem;color:var(--muted);line-height:1.55;padding:.8rem .9rem;border-radius:12px;border:1px solid var(--line);background:rgba(255,254,250,.72);}}
.footer {{border-top:1px solid var(--line);margin-top:2.5rem;padding-top:.8rem;font-size:.72rem;color:var(--muted);letter-spacing:.04em;}}
hr {{border-color:var(--line);}}
</style>
""", unsafe_allow_html=True)

# Matplotlib styling consistent with the app.
plt.rcParams.update({
    "figure.facecolor": CARD,
    "axes.facecolor": CARD,
    "axes.edgecolor": LINE,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": INK,
    "axes.titlecolor": INK,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": LINE,
    "grid.alpha": 0.5,
    "grid.linewidth": 0.7,
})

# ─────────────────────────────────────────────────────────────────────────────
# Navigation
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="eyebrow">FIELD STUDY · 01</div>', unsafe_allow_html=True)
    st.markdown("## 🦋 Butterfly Effect")
    st.caption("Human systems · Queue research studio")
    st.divider()
    page = st.radio(
        "WORKSPACE",
        [
            "Overview",
            "Data explorer",
            "Data quality",
            "Distribution analysis",
            "Relationships",
            "Sensitivity lab",
            "Counter capacity",
            "AI research notes",
        ],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("**Project settings**")
    st.caption("Source workbook is read from `data/data.xlsx`.")
    show_rows = st.slider("Preview rows", min_value=5, max_value=50, value=10, step=5)
    st.markdown(
        '<div class="note">Keep measured data, synthetic examples and modelled what-if scenarios clearly separated in reports.</div>',
        unsafe_allow_html=True
    )

DATA_PATH = Path(__file__).resolve().parent / "data.xlsx"

@st.cache_data(show_spinner=False)
def get_data(path_string, modified_time):
    sheet_name, raw_frame = load_workbook(Path(path_string))
    cleaned, duration_source = prepare_data(raw_frame)
    return sheet_name, raw_frame, cleaned, duration_source

if not DATA_PATH.exists():
    st.markdown("""
    <div class="hero"><div class="eyebrow">RESEARCH STUDIO</div>
    <h1>Small shifts.<br>Different queues.</h1>
    <p>Explore the effect of small changes in a human-facing service system.</p></div>
    """, unsafe_allow_html=True)
    st.error("Workbook not found. Place your Excel file at `data/data.xlsx`.")
    st.markdown("[Open the selected dataset source](https://data.mendeley.com/datasets/79zt3t734g/1)")
    st.stop()

try:
    sheet, raw, df, duration_source = get_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
except Exception as exc:
    st.error(f"Could not read the workbook: {exc}")
    st.info("Check that `data/data.xlsx` is the original Excel workbook, not a renamed ZIP archive or webpage.")
    st.stop()

valid_duration = df["actual_duration_min"].dropna()
valid_duration = valid_duration[valid_duration > 0]
summary = duration_summary(df).iloc[0]
is_synthetic = (
    "data_status" in df.columns
    and df["data_status"].astype(str).str.contains("SYNTHETIC", case=False, na=False).any()
)

# Keep a provenance warning visible across every page.
if is_synthetic:
    st.warning("SYNTHETIC DATA NOTICE · This workbook contains generated records. Use it for testing and demonstration, not as real-world observations.")
else:
    st.caption("Measurement note: order-to-delivery system time is not necessarily pure queue waiting time or service duration.")

def page_header(kicker, title, description):
    st.markdown(
        f'<div class="page-head"><div class="eyebrow">{kicker}</div><h2>{title}</h2><p>{description}</p></div>',
        unsafe_allow_html=True
    )

def metric(col, label, value, note):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True
        )

def chart_download(fig, filename):
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor=CARD)
    st.download_button("Download chart PNG", buf.getvalue(), filename, "image/png")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Overview
# ─────────────────────────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">HUMAN SYSTEMS · STOCHASTIC MODELLING</div>
      <h1>Small shifts.<br>Different queues.</h1>
      <p>A research workspace for exploring service duration, perceived waiting and the sensitivity of queue-capacity assumptions.</p>
      <span class="pill">🦋 BUTTERFLY EFFECT / QUEUE LAB</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"WORKBOOK / {sheet} · {len(df):,} rows · duration source: {duration_source}")
    a,b,c,d = st.columns(4, gap="medium")
    metric(a, "VALID RECORDS", f"{int(summary['n_valid']):,}", "positive duration values")
    metric(b, "MEAN DURATION", f"{summary['mean_min']:.2f} min", "average system duration")
    metric(c, "MEDIAN DURATION", f"{summary['median_min']:.2f} min", "middle observation")
    metric(d, "95TH PERCENTILE", f"{summary['p95_min']:.2f} min", "upper-tail duration")
    st.markdown("<br>", unsafe_allow_html=True)
    page_header("START HERE", "Your research at a glance", "Each workspace answers a different question. Choose a section from the sidebar to explore the dataset in detail.")
    cols = st.columns(3, gap="medium")
    cards = [
        ("01 · Data explorer", "Inspect the workbook, filter records and download the current view."),
        ("02 · Data quality", "Check missing values, duplicates, invalid durations and column types."),
        ("03 · Distribution analysis", "Study the shape, spread and tail of the measured duration."),
        ("04 · Relationships", "Explore correlations with numeric survey and satisfaction measures."),
        ("05 · Sensitivity lab", "Test hypothetical duration increases and compare summary metrics."),
        ("06 · Counter capacity", "Run a counterfactual capacity model with assumptions made explicit."),
    ]
    for i, (title, body) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div class="info-card"><div class="label">{title}</div><div class="body">{body}</div></div>', unsafe_allow_html=True)
            st.write("")
    st.markdown("### Duration snapshot")
    left, right = st.columns([1.35, 1])
    with left:
        fig, ax = plt.subplots(figsize=(8,3.8))
        ax.hist(valid_duration, bins=18, color=GREEN, edgecolor=CARD, linewidth=1.1)
        ax.axvline(valid_duration.median(), color=CORAL, linestyle="--", linewidth=2, label=f"Median {valid_duration.median():.1f} min")
        ax.set_xlabel("Order-to-delivery duration (minutes)")
        ax.set_ylabel("Records")
        ax.legend(frameon=False)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with right:
        st.markdown("#### Key interpretation")
        st.markdown(
            f"- **Mean:** {valid_duration.mean():.2f} minutes\n"
            f"- **Median:** {valid_duration.median():.2f} minutes\n"
            f"- **95th percentile:** {valid_duration.quantile(.95):.2f} minutes\n\n"
            "The mean being above the median can indicate a right-skewed duration distribution. Confirm the shape in Distribution analysis."
        )
        st.markdown('<div class="note">The butterfly effect is explored here as sensitivity to small parameter changes, not as proof that every small change causes a large effect.</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Data explorer
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Data explorer":
    page_header("WORKSPACE 01", "Data explorer", "Browse the source workbook, filter rows and export a clean slice for further analysis.")
    st.caption(f"Source sheet: {sheet} · Original columns: {len(raw.columns)}")
    search = st.text_input("Search across text values", placeholder="e.g. gender, timestamp, a value…")
    cols_to_show = st.multiselect("Columns to display", options=list(df.columns), default=list(df.columns[:min(10,len(df.columns))]))
    view = df.copy()
    if search.strip():
        mask = view.astype(str).apply(lambda s: s.str.contains(search.strip(), case=False, na=False)).any(axis=1)
        view = view.loc[mask]
    if cols_to_show:
        view = view[cols_to_show]
    st.markdown(f"**{len(view):,} rows** match the current view.")
    st.dataframe(view.head(500), use_container_width=True, hide_index=True)
    st.download_button("Download filtered view as CSV", view.to_csv(index=False), "filtered_data_view.csv", "text/csv")
    with st.expander("Column dictionary / detected data types"):
        dictionary = pd.DataFrame({
            "column": df.columns,
            "dtype": [str(df[c].dtype) for c in df.columns],
            "missing": [int(df[c].isna().sum()) for c in df.columns],
            "unique_values": [int(df[c].nunique(dropna=True)) for c in df.columns],
        })
        st.dataframe(dictionary, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Data quality
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Data quality":
    page_header("WORKSPACE 02", "Data quality", "Review missingness, duplicates, invalid durations and type consistency before interpreting results.")
    quality = data_quality(df)
    q1,q2,q3,q4 = st.columns(4)
    metric(q1, "ROWS", f"{len(df):,}", "records in workbook")
    metric(q2, "COLUMNS", f"{len(df.columns):,}", "fields available")
    metric(q3, "DUPLICATES", f"{int(df.duplicated().sum()):,}", "fully duplicated rows")
    metric(q4, "MISSING CELLS", f"{int(df.isna().sum().sum()):,}", "across all fields")
    st.markdown("### Quality checks")
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.markdown("### Missing values by column")
    missing = df.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if missing.empty:
        st.success("No missing cells detected.")
    else:
        fig, ax = plt.subplots(figsize=(9, max(3.2, .32*len(missing))))
        missing.sort_values().plot(kind="barh", ax=ax, color=CORAL)
        ax.set_xlabel("Missing cells")
        ax.set_ylabel("")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    st.markdown("### Column profile")
    profile = pd.DataFrame({
        "column": df.columns,
        "type": [str(df[c].dtype) for c in df.columns],
        "missing_count": [int(df[c].isna().sum()) for c in df.columns],
        "missing_pct": [100*df[c].isna().mean() for c in df.columns],
        "unique_count": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    st.dataframe(profile.round(2), use_container_width=True, hide_index=True)
    st.download_button("Download quality report", profile.to_csv(index=False), "data_quality_profile.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Distribution analysis
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Distribution analysis":
    page_header("WORKSPACE 03", "Distribution analysis", "Look beyond the average: compare spread, skew and high-duration observations.")
    values = valid_duration
    s1,s2,s3,s4 = st.columns(4)
    metric(s1, "MINIMUM", f"{values.min():.2f} min", "shortest valid duration")
    metric(s2, "MAXIMUM", f"{values.max():.2f} min", "longest valid duration")
    metric(s3, "STD. DEVIATION", f"{values.std():.2f} min", "typical spread around mean")
    metric(s4, "IQR", f"{values.quantile(.75)-values.quantile(.25):.2f} min", "middle 50% range")
    left, right = st.columns(2)
    with left:
        bins = st.slider("Histogram bins", 5, 50, 18)
        fig, ax = plt.subplots(figsize=(7,4))
        ax.hist(values, bins=bins, color=GREEN, edgecolor=CARD, linewidth=1)
        ax.axvline(values.mean(), color=CORAL, linestyle="--", linewidth=2, label="Mean")
        ax.axvline(values.median(), color=GOLD, linestyle=":", linewidth=2.4, label="Median")
        ax.set_xlabel("Duration (minutes)")
        ax.set_ylabel("Count")
        ax.legend(frameon=False)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        chart_download(fig, "duration_histogram.png")
        plt.close(fig)
    with right:
        fig, ax = plt.subplots(figsize=(7,4))
        ax.boxplot(values, vert=False, patch_artist=True,
                   boxprops=dict(facecolor=LILAC, color=GREEN),
                   medianprops=dict(color=CORAL, linewidth=2),
                   whiskerprops=dict(color=GREEN), capprops=dict(color=GREEN),
                   flierprops=dict(marker="o", markerfacecolor=CORAL, markeredgecolor="none", alpha=.35, markersize=3))
        ax.set_xlabel("Duration (minutes)")
        ax.set_yticks([])
        ax.set_title("Spread and potential extreme values")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        chart_download(fig, "duration_boxplot.png")
        plt.close(fig)
    st.markdown("### Percentile table")
    percentile_table = pd.DataFrame({
        "percentile": ["10th", "25th", "50th / median", "75th", "90th", "95th", "99th"],
        "duration_min": [values.quantile(q) for q in [.10,.25,.50,.75,.90,.95,.99]],
    })
    st.dataframe(percentile_table.round(3), use_container_width=True, hide_index=True)
    st.download_button("Download distribution statistics", duration_summary(df).to_csv(index=False), "duration_summary.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Relationships
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Relationships":
    page_header("WORKSPACE 04", "Relationships", "Explore whether duration moves with survey responses or other numeric variables. Correlation does not establish causation.")
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    selected = st.multiselect("Choose numeric variables", numeric, default=numeric[:min(8,len(numeric))])
    if len(selected) >= 2:
        corr = df[selected].corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(max(7,.75*len(selected)), max(5,.62*len(selected))))
        im = ax.imshow(corr, cmap="PiYG", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(selected)), selected, rotation=45, ha="right")
        ax.set_yticks(range(len(selected)), selected)
        for i in range(len(selected)):
            for j in range(len(selected)):
                if pd.notna(corr.iloc[i,j]):
                    ax.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=8, color=INK)
        fig.colorbar(im, ax=ax, fraction=.035, pad=.03, label="Pearson correlation")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        chart_download(fig, "correlation_heatmap.png")
        plt.close(fig)
        st.dataframe(corr.round(3), use_container_width=True)
        st.download_button("Download correlation matrix", corr.to_csv(), "correlation_matrix.csv", "text/csv")
    else:
        st.info("Choose at least two numeric variables to generate a correlation matrix.")
    # Focused scatterplot when duration and one other variable are selected.
    candidates = [c for c in numeric if c != "actual_duration_min"]
    if candidates:
        st.markdown("### Compare duration with one variable")
        xcol = st.selectbox("X variable", candidates)
        plot_df = df[[xcol, "actual_duration_min"]].apply(pd.to_numeric, errors="coerce").dropna()
        fig, ax = plt.subplots(figsize=(8,4))
        ax.scatter(plot_df[xcol], plot_df["actual_duration_min"], alpha=.35, s=20, color=GREEN, edgecolors="none")
        ax.set_xlabel(xcol)
        ax.set_ylabel("Order-to-delivery duration (minutes)")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        if len(plot_df) >= 3:
            st.caption(f"Pearson r = {plot_df[xcol].corr(plot_df['actual_duration_min']):.3f} · n = {len(plot_df):,}")

# ─────────────────────────────────────────────────────────────────────────────
# 6. Sensitivity lab
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Sensitivity lab":
    page_header("WORKSPACE 05", "Sensitivity lab", "Apply controlled percentage changes to measured durations and inspect how summary metrics move.")
    st.markdown('<div class="note">These are hypothetical perturbations of the existing duration values. They are not newly observed customers and do not prove a causal effect.</div>', unsafe_allow_html=True)
    increments = st.multiselect("Percentage changes to test", [0,1,3,5,10,15,20,25], default=[0,5,10,15])
    threshold = st.slider("Duration threshold for long-duration share (minutes)", 5, 30, 15)
    if increments:
        sens = duration_sensitivity(df, tuple(v/100 for v in sorted(set(increments))))
        sens["share_over_threshold"] = [
            (valid_duration*(1+v/100) > threshold).mean() for v in sorted(set(increments))
        ]
        sens["share_over_threshold_pct"] = sens["share_over_threshold"]*100
        st.markdown("### Scenario table")
        st.dataframe(sens.round(3), use_container_width=True, hide_index=True)
        left,right = st.columns(2)
        with left:
            fig, ax = plt.subplots(figsize=(7,4))
            ax.plot(sens["scenario"], sens["mean_duration_min"], marker="o", linewidth=2.4, color=GREEN, label="Mean")
            ax.plot(sens["scenario"], sens["p95_duration_min"], marker="o", linewidth=2.4, color=CORAL, label="95th percentile")
            ax.set_ylabel("Duration (minutes)")
            ax.tick_params(axis="x", rotation=20)
            ax.legend(frameon=False)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with right:
            ax2 = None
            fig2, ax2 = plt.subplots(figsize=(7,4))
            ax2.plot(sens["scenario"], sens["share_over_threshold_pct"], marker="o", linewidth=2.4, color="#8D79AE")
            ax2.set_ylabel(f"Records over {threshold} min (%)")
            ax2.tick_params(axis="x", rotation=20)
            fig2.tight_layout()
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)
        st.download_button("Download sensitivity results", sens.to_csv(index=False), "duration_sensitivity.csv", "text/csv")
    else:
        st.info("Choose at least one percentage change.")

# ─────────────────────────────────────────────────────────────────────────────
# 7. Counter capacity
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Counter capacity":
    page_header("WORKSPACE 06", "Counter capacity studio", "Compare assumed counter counts using repeated simulation runs.")
    st.markdown('<div class="note">IMPORTANT MODEL LIMITATION · The source duration is order-to-delivery system time, not confirmed service time. This model uses it as a proxy and is counterfactual only, not a validated prediction of the real restaurant.</div>', unsafe_allow_html=True)
    left,right = st.columns(2)
    with left:
        max_counters = st.slider("Maximum assumed counters", 2, 8, 5)
        rep_count = st.select_slider("Monte Carlo repetitions", options=[50,100,200,300,500], value=200)
    with right:
        st.markdown("#### Experiment setup")
        st.markdown(f"- Counter range: 1 to **{max_counters}**\n- Repetitions per setting: **{rep_count}**\n- Duration proxy: **{valid_duration.mean():.2f} minutes mean**")
    if st.button("Run capacity experiment", type="primary"):
        with st.spinner("Running repeated queue scenarios…"):
            cap = theoretical_capacity_experiment(df, counters=tuple(range(1,max_counters+1)), repetitions=rep_count)
        st.session_state["capacity_results"] = cap
    if "capacity_results" in st.session_state:
        cap = st.session_state["capacity_results"]
        st.markdown("### Results")
        st.dataframe(cap.round(3), use_container_width=True, hide_index=True)
        left,right = st.columns(2)
        with left:
            fig, ax = plt.subplots(figsize=(7,4))
            ax.plot(cap["counters_assumed"], cap["mean_queue_wait_min"], marker="o", linewidth=2.5, color=GREEN)
            ax.set_xlabel("Assumed active counters")
            ax.set_ylabel("Mean simulated queue wait (minutes)")
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with right:
            fig, ax = plt.subplots(figsize=(7,4))
            ax.plot(cap["counters_assumed"], cap["prob_wait_over_5min"]*100, marker="o", linewidth=2.5, color=CORAL)
            ax.set_xlabel("Assumed active counters")
            ax.set_ylabel("Simulated probability wait > 5 min (%)")
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        st.download_button("Download capacity results", cap.to_csv(index=False), "counterfactual_capacity_scenarios.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# 8. AI research notes (optional local Ollama)
# ─────────────────────────────────────────────────────────────────────────────
elif page == "AI research notes":
    page_header("WORKSPACE 07", "AI research notes", "Use a local language model to help interpret computed results and propose experiments. Numerical calculations remain in Python.")
    st.markdown('<div class="note">AI output is hypothesis generation only. Verify every numerical statement against the tables and test recommendations in the simulator before including them in your report.</div>', unsafe_allow_html=True)
    model = st.text_input("Ollama model", value="llama3.2")
    task = st.selectbox("What should the assistant help with?", [
        "Interpret the observed duration profile",
        "Suggest follow-up sensitivity experiments",
        "Propose service interventions to test",
        "Draft a limitations section",
    ])
    if task == "Interpret the observed duration profile":
        prompt_task = "Interpret the provided summary. Identify patterns, avoid causal claims, and clearly distinguish observation from hypothesis."
    elif task == "Suggest follow-up sensitivity experiments":
        prompt_task = "Suggest 5 specific sensitivity experiments. For each, give the parameter, values to test, outcome metrics, and what result would support the hypothesis."
    elif task == "Propose service interventions to test":
        prompt_task = "Propose 4 possible service interventions as testable hypotheses. For each, name the simulation change and measurable success metric. Do not claim they will work without testing."
    else:
        prompt_task = "Draft a concise limitations section covering dataset provenance, measurement definition, proxy assumptions, stochastic variation, and external validity."
    if st.button("Generate research notes", type="primary"):
        payload = {
            "model": model,
            "stream": False,
            "prompt": (
                "You are a careful research assistant. Do not invent statistics or citations. "
                "State that the duration is order-to-delivery system time, not necessarily queue waiting time or service time. "
                "Clearly label assumptions and synthetic data if present.\n\n"
                f"Task: {prompt_task}\n\n"
                f"Data status: {'synthetic generated records' if is_synthetic else 'workbook provenance not independently verified here'}\n"
                f"Rows: {len(df)}\n"
                f"Mean duration minutes: {summary['mean_min']:.4f}\n"
                f"Median duration minutes: {summary['median_min']:.4f}\n"
                f"95th percentile minutes: {summary['p95_min']:.4f}\n"
                f"Standard deviation minutes: {valid_duration.std():.4f}\n"
            )
        }
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                answer = json.loads(response.read().decode("utf-8")).get("response", "")
            st.markdown("### Draft research notes")
            st.write(answer)
            st.download_button("Download notes", answer, "ai_research_notes.txt", "text/plain")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            st.error("Could not connect to Ollama. Start the Ollama app, ensure the model is downloaded, and try again.")
            st.caption(str(exc))
    st.markdown("### Reliable prompt checklist")
    st.markdown("- Give the model only aggregate metrics, not identifiable personal data.\n- Ask it to separate observed facts from hypotheses.\n- Recalculate all numbers in Python.\n- Test every suggested intervention before claiming an improvement.")

st.markdown('<div class="footer">BUTTERFLY EFFECT / RESEARCH STUDIO &nbsp; · &nbsp; Data quality → Patterns → Relationships → Sensitivity → Capacity</div>', unsafe_allow_html=True)
