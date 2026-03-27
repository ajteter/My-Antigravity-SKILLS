---
name: kylc-whichcard
description: Compare overseas product prices in different currencies to find the best deal and the top 10 most suitable bank cards using kylc.com. Use when the user wants to compare multiple foreign currency prices and find out which currency and bank card is cheapest in RMB.
---

# KYLC WhichCard (出国刷哪张卡)

This skill helps you find the cheapest way to pay for overseas products when prices are offered in multiple foreign currencies. It queries https://www.kylc.com/huilv/whichcard.html to calculate the exact RMB cost for each currency and card, and identifies the absolute best deal and the top 10 bank cards to use.

## Usage

When the user provides a list of prices in different currencies (e.g., "$100 USD, 15000 JPY, 95 EUR"), use the `scripts/compare.py` script to find the best deal.

Run the script by passing each currency and amount pair as a single string argument:
```bash
python3 scripts/compare.py "usd 100" "jpy 15000" "eur 95"
```

The script will:
1. Fetch live exchange rates and card fees from kylc.com for every currency.
2. Output a summary comparing the cheapest RMB price for each currency.
3. Show the absolute best option and the top 10 most suitable bank cards for that currency.

## Data Source
The prices and rates are sourced from fast and free services: https://www.kylc.com/huilv/whichcard.html. The script automatically handles parsing the HTML table directly from the site without needing third-party dependencies outside of Python's standard library.
