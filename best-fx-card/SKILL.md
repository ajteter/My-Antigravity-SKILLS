---
name: best-fx-card
description: Compare overseas product prices in different currencies to find the best deal and the top 20 most suitable bank cards using kylc.com. Use when the user wants to compare multiple foreign currency prices and find out which currency and bank card is cheapest in RMB. 自动查询和比较外币价格，找出最划算的支付币种及推荐的前20张信用卡。
---

# Best FX Card (出国刷哪张卡)

This skill helps you find the cheapest way to pay for overseas products when prices are offered in multiple foreign currencies. It queries https://www.kylc.com/huilv/whichcard.html to calculate the exact RMB cost for each currency and card, and identifies the absolute best deal and the top 20 bank cards to use.

这个能力能够帮您自动计算境外消费时，多个外币标价中哪一个换算成人民币最便宜。它会通过实时拉取汇率数据，直接给出最优货币选项以及省钱对应的前20张信用卡排名。

## Usage / 用法

### 1. Agentic Activation / AI 助手激活
当需要进行比价时，可以直接向 AI 助手下达类似指令：
- "帮我算一下 $100, 15000 JPY, 95 EUR 哪个最划算？"
- "去美国买一个 500 刀的东西，刷哪张卡最省钱？"
- "计算一下 800 欧换算成人民币的具体支出。"

AI 将提取其中的币种和金额，并自动调用 `scripts/compare.py` 脚本：

```bash
python3 scripts/compare.py "usd 100" "jpy 15000" "eur 95"
```

The script will:
1. Fetch live exchange rates and card fees from kylc.com for every currency.
2. Output a summary comparing the cheapest RMB price for each currency.
3. Show the absolute best option and the top 20 most suitable bank cards for that currency.

## Data Source / 数据来源
The prices and rates are sourced from fast and free services: https://www.kylc.com/huilv/whichcard.html. The script automatically handles parsing the HTML table directly from the site without needing third-party dependencies outside of Python's standard library. 数据直接来源于快易理财网，内置原生 Python 解析器，无冗余依赖。
