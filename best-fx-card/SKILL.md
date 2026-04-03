---
name: best-fx-card
description: Compares overseas prices across currencies and finds the lowest estimated RMB cost plus the top 20 bank-card recommendations using live data from kylc.com. Use when the user gives one or more foreign-currency amounts and wants to know which currency, price, or card is cheapest for general overseas spending, shopping, or travel. Don't use for Steam-only personal-card comparisons, exchange-rate news, or requests that do not include any parsable amount and currency.
---

# Best FX Card

Follow this procedure to compare general overseas prices across currencies.

## Step 1: Check that the request fits
1. Trigger only when the user wants a live card-based comparison for one or more concrete prices such as `100 USD`, `15000 JPY`, `€95`, or mixed lists of foreign-currency amounts.
2. Do not use this skill for Steam-only comparisons that should use the user's hardcoded personal cards. Do not use it for exchange-rate explanation, market news, or generic finance questions without a concrete price input.

## Step 2: Normalize inputs
1. Extract each recognizable `currency amount` pair from the user request.
2. Normalize each pair to the script format `currency amount`, for example `usd 100`, `jpy 15000`, `eur 95`.
3. Keep user-facing labels such as store, country, or region names only for the final explanation. Do not pass those labels to the script.
4. If no recognizable amount can be extracted, ask for the exact price and currency instead of guessing.

Accepted examples include:
- `US$5.99`
- `$100 USD`
- `15000 JPY`
- `JPY 15000`
- `95 欧元`

## Step 3: Run the script
1. Prefer JSON mode when summarizing results:
   `python3 scripts/compare.py --json "usd 100" "jpy 15000"`
2. Use plain-text mode only when the user explicitly wants the raw script output:
   `python3 scripts/compare.py "usd 100" "jpy 15000"`

## Step 4: Summarize results
1. Report the cheapest card and estimated RMB cost for each normalized input.
2. If multiple inputs were provided, identify the overall cheapest option across all successful results.
3. Mention that the ranking comes from live data on `kylc.com`.
4. If helpful, mention that the script returns the top 20 card rankings for each successful input.

## Error Handling
1. If the script returns `input_parse_error`, tell the user which input could not be parsed and ask for a clearer price.
2. If the script returns `fetch_error` or `page_parse_error`, say that the live comparison failed. Do not fabricate rates or fallback estimates.
3. If the script includes a TLS compatibility warning, say that the result is suitable for personal reference and that another network can be used for extra confidence.
