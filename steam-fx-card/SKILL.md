---
name: steam-fx-card
description: Compares Steam prices across currencies and returns the lowest estimated RMB cost using only the user's hardcoded personal cards. Use when the user mentions Steam, cross-region pricing, foreign-currency game prices, actual RMB cost, or region comparisons such as 阿区、土区、日区、美区 and provides one or more recognizable currency amounts. Don't use for general overseas spending, full-market card rankings across all banks, exchange-rate news, or requests that contain no parsable amount and currency.
---

# Steam FX Card

Follow this procedure to compare Steam prices with the user's hardcoded personal cards.

## Step 1: Check that the request fits
1. Trigger when the user asks about Steam or cross-region game pricing and provides one or more recognizable currency amounts.
2. Do not use this skill for non-Steam overseas spending or when the user wants recommendations across all available bank cards. Use the general card-comparison skill in those cases.
3. Do not ask the user for their Steam region, game name, or which card to use. The supported personal cards are already hardcoded in `scripts/compare.py`.

## Step 2: Normalize inputs
1. Extract each recognizable `currency amount` pair from the request.
2. Normalize each pair to the script format `currency amount`, for example `usd 5.99`, `jpy 980`, `try 149`.
3. Keep labels such as `美区`, `日区`, `阿区`, or `土区` only for the final explanation. Do not pass region labels to the script.
4. If the request mentions regions but no parsable amount and currency, ask for the exact prices instead of inferring them.

Accepted examples include:
- `US$5.00`
- `$100 USD`
- `15000 JPY`
- `JPY 15000`
- `阿区 5 美元，日区 1200 日元`

## Step 3: Run the script
1. Prefer JSON mode when summarizing results:
   `python3 scripts/compare.py --json "usd 5.99" "jpy 980"`
2. Use plain-text mode only when the user explicitly wants the raw script output:
   `python3 scripts/compare.py "usd 5.99" "jpy 980"`

## Step 4: Summarize results
1. Report the best personal card and estimated RMB cost for each successful input.
2. If multiple inputs were provided, identify the overall cheapest option across all successful results.
3. Preserve any user-facing region labels in the explanation so the user can map the result back to each Steam region.
4. Keep the answer focused on the supported personal cards only.

## Error Handling
1. If the script returns `input_parse_error`, tell the user which input could not be parsed and ask for a clearer Steam price.
2. If the script returns `fetch_error` or `page_parse_error`, say that the live comparison failed. Do not fabricate rates or fallback estimates.
3. If the script reports that no matching hardcoded cards were found, say so plainly instead of implying that the price itself is invalid.
4. If the script includes a TLS compatibility warning, say that the result is suitable for personal reference and that another network can be used for extra confidence.
