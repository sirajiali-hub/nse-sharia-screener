# NSE Sharia-Compliant Stock Screener

A data tool that screens Nairobi Securities Exchange (NSE) listed stocks 
for compliance with Islamic finance principles.

## What it does
Takes a list of NSE-listed companies and filters out those whose primary 
business violates Sharia principles — conventional banking, insurance, 
alcohol, tobacco, gambling, adult entertainment, and pork-related 
businesses.

## Why it matters
Islamic finance is a growing segment in East Africa, but there is no 
publicly available tool for screening NSE stocks against Sharia business 
standards. This project is a first step toward making halal investing 
more accessible in Kenya.

## Methodology
This version (v1) implements the **business activity screen** from AAOIFI 
(Accounting and Auditing Organization for Islamic Financial Institutions) 
standards. Companies in prohibited sectors are excluded.

A future version (v2) will add **financial ratio screens** — debt ratios, 
interest income ratios, and interest-bearing investment ratios.

## Limitations
- This is a data tool, not a religious ruling. Real Sharia compliance 
  requires review by qualified scholars.
- The business screen alone is insufficient — financial ratios matter too 
  and will be added in v2.
- Stock universe is limited to 20 manually selected NSE-listed companies.

## Tech stack
Python, pandas, matplotlib, seaborn, Jupyter.

## Author
Siraji Ali