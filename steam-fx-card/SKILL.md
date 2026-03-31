---
name: steam-fx-card
description: Compare Steam overseas prices in different currencies to find the lowest real RMB cost with the user's hardcoded personal cards. Use this whenever the user mentions Steam, cross-region pricing, overseas pricing, foreign-currency game prices, exchange-rate comparison, actual RMB cost, or region-price comparisons such as 阿区、土区、日区、美区, even if they do not explicitly ask for a "skill" or "汇率". DO NOT ask the user for their Steam region, game name, or which card they use; personal cards are already hardcoded. When the user gives one or more prices or asks which region/currency is cheaper, immediately normalize the amounts and run the scripts/compare.py script.
---

# Steam FX Card (Steam 专属汇率计算)

This skill helps you find the cheapest way to pay when Steam prices are offered in multiple foreign currencies. It only considers your personal credit cards and answers in terms of actual estimated RMB cost.

这个能力能够帮您自动计算、不同币种对应的实际人民币支出。它仅针对您自己持有的信用卡进行比价：中国银联、广发Visa美元卡、兴业Visa美元全币种卡、招商JCB美元全币种卡。

## Usage / 用法

When the user provides a price or list of prices, YOU MUST immediately use the `scripts/compare.py` script.
**CRITICAL:** DO NOT ask the user for their Steam account region, specific game name, or which credit card they want to use. The supported personal cards are already hardcoded in the script. Simply normalize the user input and execute the script directly.

Accepted user-style inputs include:
- `US$5.00`
- `$100 USD`
- `15000 JPY`
- `JPY 15000`
- `阿区 5 美元，日区 1200 日元`

Normalize each item to a `currency amount` pair before invoking the script. If the region name is mentioned alongside a recognizable currency amount, keep the region label in the final explanation, but still run the script only with normalized currency-and-amount values.

Run the script by passing each currency and amount pair:
```bash
python3 scripts/compare.py "usd 100" "jpy 15000"
```

If you need machine-readable output for downstream summarization, use:
```bash
python3 scripts/compare.py --json "usd 100" "jpy 15000"
```

The script will:
1. Fetch live card-based settlement results from kylc.com.
2. Try normal HTTPS verification first. If the current network environment causes certificate validation to fail, automatically retry in compatibility mode and show a plain-language warning.
3. Filter for your specific cards: 中国银联信用卡, 广发Visa美元卡, 兴业Visa美元全币种卡, 招商JCB美元全币种卡.
4. Show the best card for each queried currency amount.
5. Show the overall cheapest option across all queried inputs.

## Response Guidance / 响应要求

After running the script:
- Briefly summarize the best card for each input price.
- If multiple prices were provided, clearly point out the overall cheapest option.
- If the script reports a fetch or parsing failure, tell the user that live comparison failed instead of pretending there was "no suitable card".
- If the script had to use compatibility mode because certificate validation failed, explicitly mention that the result is suitable for personal reference and suggest rechecking on another network if the user needs extra confidence.
- Do not fabricate rates or fallback estimates.
- Prefer `--json` mode when you need stable structured output before writing the final answer.

## Data Source / 数据来源
The prices and rates are sourced from fast and free services: https://www.kylc.com/huilv/whichcard.html. 数据来源于快易理财网。
