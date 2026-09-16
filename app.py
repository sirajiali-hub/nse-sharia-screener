"""
NSE Sharia Stock Screener: Streamlit app.

Interactive front-end for screener.py. Lets a user explore the
three-layer AAOIFI screen applied to the NSE 20, adjust the ratio
thresholds to see how sensitive the results are, and view both the
Fully Compliant and Rating A tiers separately.

Run locally with:  streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import screener

st.set_page_config(
    page_title="NSE Sharia Stock Screener",
    page_icon="\U0001F54C",
    layout="wide",
)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "sans-serif",
})


# ---------------------------------------------------------------------------
# Sidebar: adjustable thresholds
# ---------------------------------------------------------------------------
st.sidebar.title("Screening thresholds")
st.sidebar.caption(
    "AAOIFI standard defaults are pre-set below. Adjust to test how "
    "sensitive the results are to the cutoff chosen."
)

threshold_debt = st.sidebar.slider(
    "Debt / Total Assets must be below", 0.0, 1.0, screener.DEFAULT_THRESHOLD_DEBT, 0.01,
    help="AAOIFI default: 33%",
)
threshold_interest = st.sidebar.slider(
    "Interest Income / Revenue must be below", 0.0, 0.30, screener.DEFAULT_THRESHOLD_INTEREST, 0.01,
    help="AAOIFI default: 5%",
)
threshold_liquid = st.sidebar.slider(
    "(Cash + Receivables) / Total Assets must be below", 0.0, 1.0, screener.DEFAULT_THRESHOLD_LIQUID, 0.01,
    help="AAOIFI default: 33%",
)

st.sidebar.divider()
st.sidebar.caption(
    "Data source: individual NSE-listed company annual reports, "
    "FY2024/25, manually extracted. Not a live feed, figures should "
    "be re-verified against the latest filings before use in an "
    "actual investment decision."
)


# ---------------------------------------------------------------------------
# Run the screen
# ---------------------------------------------------------------------------
try:
    df = screener.run_screen(
        threshold_debt=threshold_debt,
        threshold_interest=threshold_interest,
        threshold_liquid=threshold_liquid,
    )
except Exception as exc:  # pragma: no cover - defensive UI guard
    st.error(f"The screen could not be run: {exc}")
    st.stop()

tier1 = screener.get_fully_compliant(df)
tier2 = screener.get_rating_a(df)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("NSE Sharia Stock Screener")
st.caption(
    "A three-layer Sharia compliance screen applied to the NSE 20, "
    "following AAOIFI (Accounting and Auditing Organisation for "
    "Islamic Financial Institutions) methodology. Built by Siraji Ali."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies screened", len(df))
col2.metric("Excluded at sector screen", int((~df["L1_Pass"]).sum()))
col3.metric("Fully compliant (Score = 100)", len(tier1))
col4.metric("Rating A (Score 80-99)", len(tier2))

st.info(
    "**Two compliance tiers are shown, deliberately kept separate.** "
    "*Fully compliant* companies clear every AAOIFI ratio threshold "
    "outright. *Rating A* companies pass the sector screen and are "
    "broadly within AAOIFI norms, but narrowly miss one ratio on the "
    "strict cutoff. Treat these as different risk tiers, not "
    "interchangeable. An investor wanting zero ratio exceptions "
    "should use the Fully Compliant tier only.",
    icon="\u2139\ufe0f",
)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Layer 1: Sector Screen",
    "Layer 2: Financial Ratios",
    "Compliant Companies",
    "Full Results Table",
    "About the Methodology",
])

# --- Tab 1: Sector screen ---
with tab1:
    st.subheader("Business Activity Screen")
    l1_pass = df[df["L1_Pass"]]
    l1_fail = df[~df["L1_Pass"]]

    c1, c2 = st.columns(2)
    with c1:
        st.success(f"Passed sector screen: {len(l1_pass)} companies")
        st.dataframe(
            l1_pass[["Ticker", "Company", "Sector"]].reset_index(drop=True),
            use_container_width=True,
        )
    with c2:
        st.error(f"Excluded by sector screen: {len(l1_fail)} companies")
        st.dataframe(
            l1_fail[["Ticker", "Company", "Sector", "L1_Reason"]].reset_index(drop=True),
            use_container_width=True,
        )

# --- Tab 2: Ratio screen ---
with tab2:
    st.subheader("Financial Ratio Screen")
    st.caption(
        "Applied only to companies that passed the sector screen. "
        "Banking-sector companies show no ratios here since they were "
        "already excluded at Layer 1."
    )
    l1 = df[df["L1_Pass"]].copy()
    display = l1[["Company", "Ticker", "Debt_Ratio", "Interest_Ratio", "Liquid_Ratio", "L2_Pass"]].copy()
    display["Debt_Ratio"] = display["Debt_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    display["Interest_Ratio"] = display["Interest_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    display["Liquid_Ratio"] = display["Liquid_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    display["Result"] = display["L2_Pass"].apply(lambda x: "Pass" if x else "Fail")
    display = display.drop(columns=["L2_Pass"]).rename(columns={
        "Debt_Ratio": f"Debt/Assets (< {threshold_debt:.0%})",
        "Interest_Ratio": f"Interest/Revenue (< {threshold_interest:.0%})",
        "Liquid_Ratio": f"Liquid/Assets (< {threshold_liquid:.0%})",
    })
    st.dataframe(display.reset_index(drop=True), use_container_width=True)

    # Funnel chart
    fig, ax = plt.subplots(figsize=(6, 4))
    total = len(df)
    l1_n = len(l1)
    l2_n = len(l1[l1["L2_Pass"]])
    labels = ["NSE 20\nUniverse", "Pass Layer 1\n(Sector)", "Pass Layer 2\n(Ratios)"]
    vals = [total, l1_n, l2_n]
    bars = ax.bar(labels, vals, color=["#4472C4", "#70AD47", "#FFC000"], edgecolor="white")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3, str(v),
                ha="center", fontweight="bold")
    ax.set_title("Screening Funnel")
    ax.set_ylabel("No. of companies")
    st.pyplot(fig)

# --- Tab 3: Compliant companies (two tiers) ---
with tab3:
    st.subheader("Tier 1: Fully Compliant (Score = 100)")
    if len(tier1) == 0:
        st.warning("No companies are fully compliant at these thresholds.")
    else:
        for _, r in tier1.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([2, 1])
                c1.markdown(f"**{r['Ticker']}: {r['Company']}**  |  {r['Sector']}")
                c2.markdown(f"Portfolio weight: **{r['Weight']:.1%}**")
                st.caption(
                    f"Debt/Assets {r['Debt_Ratio']:.1%}  |  "
                    f"Interest/Rev {r['Interest_Ratio']:.1%}  |  "
                    f"Liq/Assets {r['Liquid_Ratio']:.1%}"
                )

        fig, ax = plt.subplots(figsize=(6, 5))
        colors_pie = ["#2E75B6", "#375623", "#70AD47", "#FFC000", "#4472C4"]
        ax.pie(
            tier1["Weight"], labels=tier1["Ticker"], autopct="%1.1f%%",
            colors=colors_pie[: len(tier1)], startangle=140, pctdistance=0.75,
            wedgeprops=dict(edgecolor="white", linewidth=2),
        )
        ax.set_title("Fully Compliant Portfolio (Asset-weighted)", fontweight="bold")
        st.pyplot(fig)

    st.divider()
    st.subheader("Tier 2: Rating A, Not Fully Compliant (Score 80-99)")
    st.caption(
        "Passes the sector screen and is broadly within AAOIFI norms, "
        "but narrowly misses one ratio on the strict threshold."
    )
    if len(tier2) == 0:
        st.info("No companies fall into this tier at these thresholds.")
    else:
        st.dataframe(
            tier2[["Ticker", "Company", "Sector", "Score", "Debt_Ratio", "Interest_Ratio", "Liquid_Ratio"]]
            .assign(
                Debt_Ratio=lambda d: d["Debt_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"),
                Interest_Ratio=lambda d: d["Interest_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"),
                Liquid_Ratio=lambda d: d["Liquid_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"),
            )
            .reset_index(drop=True),
            use_container_width=True,
        )

    st.divider()
    st.subheader("Excluded or marked down: reasons")
    excluded = df[df["Score"] < 80].sort_values("Score", ascending=False)
    for _, r in excluded.iterrows():
        st.markdown(f"- **{r['Ticker']} {r['Company']}**: {screener.exclusion_reason(r)}")

# --- Tab 4: Full results table ---
with tab4:
    st.subheader("Full NSE 20 Screening Results")
    results = df[["Company", "Ticker", "Sector", "Score", "Rating"]].copy()
    results["Status"] = results["Score"].apply(
        lambda s: "Fully Compliant" if s == 100 else ("Rating A" if s >= 80 else "Non-compliant")
    )
    results["Debt/Assets"] = df["Debt_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    results["Interest/Rev"] = df["Interest_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    results["Liq/Assets"] = df["Liquid_Ratio"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    results = results.sort_values("Score", ascending=False).reset_index(drop=True)
    results.index += 1

    st.dataframe(
        results[["Company", "Ticker", "Sector", "Debt/Assets", "Interest/Rev",
                  "Liq/Assets", "Score", "Rating", "Status"]],
        use_container_width=True,
    )

    csv = results.to_csv().encode("utf-8")
    st.download_button(
        "Download full results as CSV", csv, "nse_sharia_screen_results.csv", "text/csv"
    )

# --- Tab 5: Methodology ---
with tab5:
    st.subheader("About This Screen")
    st.markdown(
        """
**Layer 1: Business Activity Screen**
Companies in sectors considered impermissible under Islamic finance
(banking, alcohol, tobacco, weapons, pork, gambling, pornography) are
excluded outright, regardless of their financial ratios.

**Layer 2: Financial Ratio Screen**
For companies that pass Layer 1, three balance-sheet ratios are
checked against AAOIFI thresholds:
- Debt / Total Assets < 33%
- Interest Income / Revenue < 5%
- (Cash + Receivables) / Total Assets < 33%

**Layer 3: Compliance Score**
Each company earns 40 points for passing the sector screen, plus up
to 20 points per ratio (10 points if it narrowly misses the strict
threshold but clears a looser secondary bound). This produces a
0-100 score and an A-D rating, letting companies be ranked rather
than only pass/fail.

**Data source and limitations**
Figures are manually extracted from individual company annual
reports (FY2024/25), not a live data feed. Banking-sector companies
show no ratio data because they are excluded at Layer 1 before
ratios would be calculated. This is a portfolio/research project and
should not be treated as investment advice; verify all figures
against the latest filings before making any investment decision.
        """
    )
