# NSE Sharia Compliant Stock Screener

**In one line:** Which of the top 20 companies on the Nairobi Securities Exchange can a Muslim investor own under Islamic finance rules?

## The question
Islamic investors avoid companies in banned businesses (such as interest based banking, alcohol and tobacco) and companies with too much debt or interest income. Which NSE 20 companies pass?

## What I did
1. Collected figures for the NSE 20 companies from their latest annual reports (FY2024 and FY2025).
2. **Step 1, business check:** removed banks, brewers and tobacco firms.
3. **Step 2, money check:** tested each remaining company on three limits used by AAOIFI, the main Islamic finance standards body:
   * Debt below 33% of total assets
   * Interest income below 5% of revenue
   * Cash plus money owed to it below 33% of total assets
4. Gave each company a compliance score and shared the results as a web app.

## What I found
* **Only 3 of 20 companies pass:** Safaricom, Bamburi Cement and Kenya Power.
* **11 fail the business check:** 9 banks, East African Breweries and BAT Kenya.
* **6 fail the money check:** Kenya Airways (debt 83% of assets), Nation Media (too much cash), Centum (interest income 9.6%), and the insurers Jubilee, Britam and CIC (interest income from their investments).

## Why it matters
Muslim investors in Kenya have very few listed options. This gives them a clear, rule based starting list.

## Limits 
* Covers the NSE 20 only, not all listed companies.
* Uses one year of annual report figures, so results can change each year.
* Scholars differ on some rules. This follows AAOIFI limits only.

## Files
* `nse_sharia_screener.ipynb`: the screening steps and charts


## How to run
1. Run `pip install pandas numpy matplotlib`
2. Open the notebook and run all cells from the top.

**Tools:** Python, Streamlit
