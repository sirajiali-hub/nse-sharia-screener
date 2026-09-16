"""
NSE Sharia Stock Screener: core screening logic.

Implements a three-layer AAOIFI-based Sharia compliance screen for
NSE-listed companies:

  Layer 1 (Business Activity): excludes companies in prohibited
    ("haram") sectors outright (banking, alcohol, tobacco, etc.).
  Layer 2 (Financial Ratios): for companies that pass Layer 1, checks
    three balance-sheet ratios against AAOIFI thresholds.
  Layer 3 (Compliance Score): converts the Layer 1/2 results into a
    0-100 score and an A-D rating, so companies can be ranked rather
    than only pass/fail.

This module contains no UI code. It is imported by app.py (the
Streamlit interface) and can also be imported directly for testing
or reuse in a notebook.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_HARAM_SECTORS = [
    "Banking", "Alcohol", "Tobacco", "Weapons", "Pork",
    "Gambling", "Pornography",
]

DEFAULT_THRESHOLD_DEBT = 0.33       # Debt / Total Assets
DEFAULT_THRESHOLD_INTEREST = 0.05   # Interest Income / Revenue
DEFAULT_THRESHOLD_LIQUID = 0.33     # (Cash + Receivables) / Total Assets


def load_nse20_data() -> pd.DataFrame:
    """Return the hardcoded NSE 20 dataset (FY2024/25 annual reports).

    All monetary figures are in KShs Millions. Banking-sector rows are
    intentionally left with NaN financials, since they are excluded at
    Layer 1 (sector screen) before ratios would ever be calculated,
    this mirrors how the screen is actually applied, not a data gap.
    """
    data = {
        "Company": [
            "Safaricom", "Bamburi Cement", "Kenya Airways", "Nation Media",
            "Centum Invest.", "Jubilee Hold.", "Britam Hold.", "CIC Insurance",
            "Kenya Power", "Equity Group", "KCB Group", "Cooperative Bk",
            "Std Chartered", "ABSA Bank", "Diamond Trust", "NCBA Group",
            "I&M Group", "Stanbic Hold.", "EA Breweries", "BAT Kenya",
        ],
        "Ticker": [
            "SCOM", "BAMB", "KQ", "NMG", "CTUM", "JUB", "BRIT", "CIC", "KPLC",
            "EQTY", "KCB", "COOP", "SCBK", "ABSA", "DTK", "NCBA", "IMH",
            "CFC", "EABL", "BAT",
        ],
        "Sector": [
            "Telecom", "Manufacturing", "Aviation", "Media", "Investment",
            "Insurance", "Insurance", "Insurance", "Utility",
            "Banking", "Banking", "Banking", "Banking", "Banking",
            "Banking", "Banking", "Banking", "Banking", "Alcohol", "Tobacco",
        ],
        "Total_Assets": [
            641164.3, 33006, 179104, 10700.5, 76171.9, 251082.9, 208531.8,
            61937.7, 389039,
            np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
            np.nan, np.nan, np.nan,
        ],
        "Total_Debt": [
            108146.8, 0, 148085, 0, 1614.4, 0, 1100.6, 5271.4, 87640,
            np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
            np.nan, np.nan, np.nan,
        ],
        "Revenue": [
            349447.2, 41381, 188495, 6229.6, 6332.4, 29920.9, 37556.7,
            26348.8, 219285,
            np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
            np.nan, np.nan, np.nan,
        ],
        "Interest_Income": [
            5459.6, 310, 69, 270.6, 607.4, 22572.2, 19408.4, 6046.4, 625,
            np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
            np.nan, np.nan, np.nan,
        ],
        "Cash_Receivables": [
            70987.2, 7121, 26142, 4568.2, 9659.5, 11144.5, 9224.8, 1751.8,
            98370,
            np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
            np.nan, np.nan, np.nan,
        ],
        "FY": [
            "2024", "2024", "2024", "2024", "Mar-2024", "2025", "2024",
            "2024", "Jun-2025",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
            "N/A", "N/A",
        ],
    }
    return pd.DataFrame(data)


def apply_layer1(
    df: pd.DataFrame, haram_sectors: list[str] | None = None
) -> pd.DataFrame:
    """Business activity screen: exclude companies in prohibited sectors.

    Adds L1_Pass (bool) and L1_Reason (str) columns. Does not mutate
    the input DataFrame.
    """
    if haram_sectors is None:
        haram_sectors = DEFAULT_HARAM_SECTORS

    out = df.copy()
    out["L1_Pass"] = ~out["Sector"].isin(haram_sectors)
    out["L1_Reason"] = out.apply(
        lambda r: "PASS" if r["L1_Pass"] else f"FAIL: {r['Sector']} is prohibited",
        axis=1,
    )
    return out


def apply_layer2(
    df: pd.DataFrame,
    threshold_debt: float = DEFAULT_THRESHOLD_DEBT,
    threshold_interest: float = DEFAULT_THRESHOLD_INTEREST,
    threshold_liquid: float = DEFAULT_THRESHOLD_LIQUID,
) -> pd.DataFrame:
    """Financial ratio screen, applied only to rows with L1_Pass == True.

    Expects the DataFrame to already have an L1_Pass column (i.e. run
    apply_layer1 first). Rows that fail Layer 1 are left with NaN
    ratios and L2_Pass = False, rather than being dropped, so the full
    universe can still be displayed together.
    """
    if "L1_Pass" not in df.columns:
        raise ValueError("apply_layer2 requires L1_Pass. Run apply_layer1 first.")

    out = df.copy()
    out["Debt_Ratio"] = out["Total_Debt"] / out["Total_Assets"]
    out["Interest_Ratio"] = out["Interest_Income"] / out["Revenue"]
    out["Liquid_Ratio"] = out["Cash_Receivables"] / out["Total_Assets"]

    out["L2a_Pass"] = out["Debt_Ratio"] < threshold_debt
    out["L2b_Pass"] = out["Interest_Ratio"] < threshold_interest
    out["L2c_Pass"] = out["Liquid_Ratio"] < threshold_liquid

    ratio_cols = ["L2a_Pass", "L2b_Pass", "L2c_Pass"]
    out["L2_Pass"] = out["L1_Pass"] & out[ratio_cols].all(axis=1)
    # Companies that failed Layer 1 (or have no ratio data) can't pass Layer 2
    out.loc[~out["L1_Pass"], "L2_Pass"] = False

    return out


def _score_row(row: pd.Series) -> tuple[int, str]:
    """Score a single company 0-100 and assign an A-D rating.

    40 points for passing the sector screen, up to 20 points each for
    the three financial ratios (10 points if the ratio narrowly
    misses the AAOIFI threshold but is under a looser secondary
    bound, 0 otherwise). Companies that fail Layer 1 outright score 0.
    """
    if not row.get("L1_Pass", False):
        return 0, "D"
    if pd.isna(row.get("Debt_Ratio", np.nan)):
        # Passed the sector screen but has no financial data to score
        return 0, "D"

    score = 40
    score += 20 if row["Debt_Ratio"] < 0.33 else (10 if row["Debt_Ratio"] < 0.50 else 0)
    score += 20 if row["Interest_Ratio"] < 0.05 else (10 if row["Interest_Ratio"] < 0.10 else 0)
    score += 20 if row["Liquid_Ratio"] < 0.33 else (10 if row["Liquid_Ratio"] < 0.50 else 0)

    rating = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
    return score, rating


def apply_layer3(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Score (0-100) and Rating (A-D) for every company.

    Expects L1_Pass and the ratio columns from apply_layer2 to
    already be present.
    """
    out = df.copy()
    scores, ratings = [], []
    for _, row in out.iterrows():
        s, g = _score_row(row)
        scores.append(s)
        ratings.append(g)
    out["Score"] = scores
    out["Rating"] = ratings
    return out


def run_screen(
    df: pd.DataFrame | None = None,
    haram_sectors: list[str] | None = None,
    threshold_debt: float = DEFAULT_THRESHOLD_DEBT,
    threshold_interest: float = DEFAULT_THRESHOLD_INTEREST,
    threshold_liquid: float = DEFAULT_THRESHOLD_LIQUID,
) -> pd.DataFrame:
    """Run the full three-layer screen and return the enriched DataFrame.

    If df is None, loads the built-in NSE 20 dataset. Thresholds can
    be overridden to test sensitivity of the results to the AAOIFI
    cutoffs used.
    """
    if df is None:
        df = load_nse20_data()

    df = apply_layer1(df, haram_sectors=haram_sectors)
    df = apply_layer2(
        df,
        threshold_debt=threshold_debt,
        threshold_interest=threshold_interest,
        threshold_liquid=threshold_liquid,
    )
    df = apply_layer3(df)
    return df


def _weighted(subset: pd.DataFrame) -> pd.DataFrame:
    """Add an asset-weighted portfolio Weight column to a subset of
    companies. Returns the subset unchanged if it's empty.
    """
    subset = subset.copy()
    if len(subset) == 0:
        return subset
    subset["Weight"] = subset["Total_Assets"] / subset["Total_Assets"].sum()
    return subset


def get_fully_compliant(df: pd.DataFrame) -> pd.DataFrame:
    """Tier 1: fully compliant companies (Score == 100). Pass the
    sector screen and clear all three AAOIFI ratio thresholds
    outright, with no reliance on the looser secondary bound.
    """
    return _weighted(df[df["Score"] == 100])


def get_rating_a(df: pd.DataFrame) -> pd.DataFrame:
    """Tier 2: Rating A companies that are NOT fully compliant
    (80 <= Score < 100): pass the sector screen and are broadly
    within AAOIFI norms, but narrowly miss one ratio on the strict
    threshold (while still clearing the looser secondary bound).
    Investors who want a wider but still high-quality universe may
    consider this tier; investors who want zero ratio exceptions
    should use get_fully_compliant instead.
    """
    return _weighted(df[(df["Score"] >= 80) & (df["Score"] < 100)])


def get_compliant(df: pd.DataFrame) -> pd.DataFrame:
    """Deprecated alias for get_fully_compliant. Kept so any existing
    callers using the old name continue to work. New code should call
    get_fully_compliant or get_rating_a explicitly, since "compliant"
    on its own is ambiguous between the two tiers.
    """
    return get_fully_compliant(df)


def exclusion_reason(row: pd.Series) -> str:
    """Human-readable reason a company was excluded or marked down."""
    if not row.get("L1_Pass", False):
        return f"Haram sector: {row['Sector']}"
    reasons = []
    if pd.notna(row.get("L2a_Pass")) and not row["L2a_Pass"]:
        reasons.append(f"Debt/Assets {row['Debt_Ratio']:.1%} > 33%")
    if pd.notna(row.get("L2b_Pass")) and not row["L2b_Pass"]:
        reasons.append(f"Interest/Rev {row['Interest_Ratio']:.1%} > 5%")
    if pd.notna(row.get("L2c_Pass")) and not row["L2c_Pass"]:
        reasons.append(f"Liq/Assets {row['Liquid_Ratio']:.1%} > 33%")
    return "; ".join(reasons) if reasons else "No financial data available"
