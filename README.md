# NSE Sharia Stock Screener

An interactive three-layer Sharia compliance screen applied to the
NSE 20 (Nairobi Securities Exchange), following AAOIFI (Accounting
and Auditing Organisation for Islamic Financial Institutions)
methodology.

**Live app:** https://nse-sharia-screener-4qjv3c7sytjetz4jappxw5.streamlit.app/

## What it does

1. **Layer 1, Business Activity Screen.** Excludes companies in
   sectors considered impermissible under Islamic finance (banking,
   alcohol, tobacco, weapons, pork, gambling, pornography).
2. **Layer 2, Financial Ratio Screen.** For companies that pass
   Layer 1, checks three balance-sheet ratios against AAOIFI
   thresholds (Debt/Assets < 33%, Interest Income/Revenue < 5%,
   Liquid Assets/Total Assets < 33%).
3. **Layer 3, Compliance Score.** Converts the results into a 0-100
   score and A-D rating, so companies can be ranked rather than only
   pass/fail.

Results are split into two clearly labeled tiers:
- **Fully Compliant** (Score = 100), clears every threshold outright.
- **Rating A** (Score 80-99), broadly compliant, narrowly misses one
  ratio on the strict cutoff.

The Streamlit app lets you adjust the three AAOIFI thresholds live,
to see how sensitive the results are to the cutoffs chosen.

## Data

Figures are manually extracted from individual NSE-listed companies'
annual reports (FY2024/25), this is **not** a live data feed.
Banking-sector companies show no ratio data because they are
excluded at Layer 1 before ratios would be calculated. This is a
research/portfolio project, not investment advice, verify figures
against the latest filings before making any investment decision.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
screener.py   - core screening logic (no UI), reusable/testable
app.py        - Streamlit interface built on top of screener.py
requirements.txt
```

## Author

Siraji Ali · [GitHub](https://github.com/sirajiali-hub)
