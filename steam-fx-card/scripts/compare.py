import json
import re
import ssl
import sys
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple, Union


CARD_NAMES = (
    "中国银联信用卡",
    "广发Visa美元卡",
    "兴业Visa美元全币种卡",
    "招商JCB美元全币种卡",
)

CURRENCY_ALIASES = {
    "usd": "usd",
    "us$": "usd",
    "$": "usd",
    "dollar": "usd",
    "dollars": "usd",
    "美金": "usd",
    "美元": "usd",
    "jpy": "jpy",
    "yen": "jpy",
    "日元": "jpy",
    "円": "jpy",
    "eur": "eur",
    "euro": "eur",
    "euros": "eur",
    "欧元": "eur",
    "sgd": "sgd",
    "singapore dollar": "sgd",
    "singapore dollars": "sgd",
    "新加坡元": "sgd",
    "新币": "sgd",
    "gbp": "gbp",
    "pound": "gbp",
    "pounds": "gbp",
    "英镑": "gbp",
    "inr": "inr",
    "rupee": "inr",
    "rupees": "inr",
    "印度卢比": "inr",
    "卢比": "inr",
    "try": "try",
    "tl": "try",
    "里拉": "try",
    "土耳其里拉": "try",
    "ars": "ars",
    "比索": "ars",
    "阿根廷比索": "ars",
    "cny": "cny",
    "rmb": "cny",
    "人民币": "cny",
    "hkd": "hkd",
    "港币": "hkd",
}

SUPPORTED_CURRENCIES = tuple(sorted(set(CURRENCY_ALIASES.values())))


class FetchError(Exception):
    def __init__(self, message: str, used_insecure_fallback: bool = False, warning: Optional[str] = None):
        super().__init__(message)
        self.used_insecure_fallback = used_insecure_fallback
        self.warning = warning


class ParseError(Exception):
    pass

class KylcParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table': self.in_table = True
        elif self.in_table and tag == 'tr': self.in_tr = True
        elif self.in_tr and tag in ('td', 'th'): self.in_td = True

    def handle_endtag(self, tag):
        if tag == 'table': self.in_table = False
        elif self.in_table and tag == 'tr':
            self.in_tr = False
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = []
        elif self.in_tr and tag in ('td', 'th'): self.in_td = False

    def handle_data(self, data):
        data = data.strip()
        if self.in_td and data:
            self.current_row.append(data)


def normalize_currency(token: str) -> Optional[str]:
    cleaned = token.strip().lower().replace(",", "")
    return CURRENCY_ALIASES.get(cleaned)


def normalize_amount(token: str) -> Optional[str]:
    cleaned = token.strip().replace(",", "")
    if not cleaned:
        return None
    if cleaned.startswith("."):
        cleaned = f"0{cleaned}"
    try:
        value = float(cleaned)
    except ValueError:
        return None

    if value <= 0:
        return None

    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def extract_amount_fragment(text: str) -> Optional[str]:
    match = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    if not match:
        return None
    return normalize_amount(match.group(1))


def extract_currency_and_amount(raw_item: str) -> Tuple[str, str]:
    parts = raw_item.strip().split()
    if len(parts) == 2:
        left_currency = normalize_currency(parts[0])
        right_currency = normalize_currency(parts[1])
        left_amount = normalize_amount(parts[0])
        right_amount = normalize_amount(parts[1])

        if left_currency and right_amount:
            return left_currency, right_amount
        if right_currency and left_amount:
            return right_currency, left_amount
        if left_currency:
            amount = extract_amount_fragment(parts[1])
            if amount:
                return left_currency, amount
        if right_currency:
            amount = extract_amount_fragment(parts[0])
            if amount:
                return right_currency, amount

    compact = raw_item.strip().replace(",", "")
    lowered = compact.lower()

    for prefix, currency in sorted(CURRENCY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if lowered.startswith(prefix):
            amount = normalize_amount(compact[len(prefix):].strip()) or extract_amount_fragment(compact[len(prefix):].strip())
            if amount:
                return currency, amount
        if lowered.endswith(prefix):
            amount = normalize_amount(compact[:-len(prefix)].strip()) or extract_amount_fragment(compact[:-len(prefix)].strip())
            if amount:
                return currency, amount

    raise ParseError(
        f"Could not parse '{raw_item}'. Supported examples: usd 100, 100 usd, US$5.99, JPY 1500."
    )


def build_query_url(currency: str, amount: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return f"https://www.kylc.com/huilv/whichcard.html?ccy={currency.lower()}&amt={amount}&date={today}"


def fetch_html(url: str) -> Union[str, Tuple[str, str]]:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        message = str(e)
        tls_error_signals = (
            "CERTIFICATE_VERIFY_FAILED",
            "self-signed certificate",
            "certificate verify failed",
        )
        if any(signal in message for signal in tls_error_signals):
            try:
                with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=15) as response:
                    warning = (
                        "网站证书校验没有通过，这次按兼容方式抓取了结果，适合自己参考用；"
                        "如果你要特别严谨，建议换一个网络环境再查一次。"
                    )
                    return response.read().decode("utf-8"), warning
            except Exception as fallback_error:
                raise FetchError(
                    f"Failed to fetch live card comparison data after certificate fallback: {fallback_error}"
                ) from fallback_error
        raise FetchError(f"Failed to fetch live card comparison data: {e}") from e


def get_best_cards(currency: str, amount: str) -> Tuple[List[List[str]], Optional[str]]:
    url = build_query_url(currency, amount)
    fetch_result = fetch_html(url)
    warning: Optional[str] = None
    if isinstance(fetch_result, tuple):
        html, warning = fetch_result
    else:
        html = fetch_result

    parser = KylcParser()
    parser.feed(html)

    results = []
    for row in parser.rows:
        if len(row) <= 10 or row[0] == '#':
            continue

        card_name = row[2]
        if not any(name in card_name for name in CARD_NAMES):
            continue

        try:
            float(row[-2].replace(",", ""))
        except ValueError:
            continue

        results.append(row)

    if parser.rows and not results:
        raise ParseError(
            f"Fetched comparison page for {currency.upper()} {amount}, but no matching card rows were recognized. "
            "The upstream page structure may have changed."
        )

    results.sort(key=lambda x: float(x[-2].replace(",", "")))
    return results, warning


def format_rmb(value: float) -> str:
    return f"{value:.2f}"


def parse_cli_args(argv: List[str]) -> Tuple[bool, List[str]]:
    json_mode = False
    inputs: List[str] = []
    for arg in argv:
        if arg == "--json":
            json_mode = True
            continue
        inputs.append(arg)
    return json_mode, inputs


def build_json_card_rows(rows: List[List[str]]) -> List[Dict[str, str]]:
    return [
        {
            "rank": str(index),
            "card_name": row[2],
            "rmb_cost": row[-2],
        }
        for index, row in enumerate(rows, start=1)
    ]


def main() -> int:
    json_mode, inputs = parse_cli_args(sys.argv[1:])
    if not inputs:
        print("Usage: python3 compare.py [--json] \"usd 100\" \"jpy 15000\"")
        print(f"Supported currencies include: {', '.join(SUPPORTED_CURRENCIES)}")
        return 1

    best_overall_rmb = float('inf')
    best_overall_option = None
    all_results: Dict[str, Dict[str, object]] = {}
    had_errors = False
    json_results: List[Dict[str, Any]] = []
    run_warnings: List[str] = []

    for item in inputs:
        try:
            currency, amount = extract_currency_and_amount(item)
        except ParseError as e:
            had_errors = True
            if json_mode:
                json_results.append(
                    {
                        "input": item,
                        "status": "input_parse_error",
                        "error": str(e),
                    }
                )
            else:
                print(f"\n--- Skipping input: {item} ---")
                print(f"Input parse error: {e}")
            continue

        normalized_key = f"{currency} {amount}"
        if not json_mode:
            print(f"\n--- Querying your cards for {currency.upper()} {amount} ---")

        try:
            rows, warning = get_best_cards(currency, amount)
        except FetchError as e:
            had_errors = True
            if json_mode:
                json_results.append(
                    {
                        "input": item,
                        "normalized_input": normalized_key,
                        "currency": currency,
                        "amount": amount,
                        "status": "fetch_error",
                        "error": str(e),
                    }
                )
            else:
                print(f"Live fetch failed for {currency.upper()} {amount}: {e}")
            continue
        except ParseError as e:
            had_errors = True
            if json_mode:
                json_results.append(
                    {
                        "input": item,
                        "normalized_input": normalized_key,
                        "currency": currency,
                        "amount": amount,
                        "status": "page_parse_error",
                        "error": str(e),
                    }
                )
            else:
                print(f"Live page parse failed for {currency.upper()} {amount}: {e}")
            continue

        if not rows:
            had_errors = True
            if json_mode:
                json_results.append(
                    {
                        "input": item,
                        "normalized_input": normalized_key,
                        "currency": currency,
                        "amount": amount,
                        "status": "no_matching_cards",
                        "error": f"No matching hardcoded cards were found for {currency.upper()} {amount}.",
                    }
                )
            else:
                print(f"No matching hardcoded cards were found for {currency.upper()} {amount}.")
            continue

        cheapest_rmb = float(rows[0][-2].replace(',', ''))
        all_results[normalized_key] = {
            'currency': currency,
            'amount': amount,
            'cheapest_rmb': cheapest_rmb,
            'my_cards': rows,
            'warning': warning,
        }

        if warning and warning not in run_warnings:
            run_warnings.append(warning)

        json_results.append(
            {
                "input": item,
                "normalized_input": normalized_key,
                "currency": currency,
                "amount": amount,
                "status": "ok",
                "best_card": rows[0][2],
                "best_rmb_cost": format_rmb(cheapest_rmb),
                "card_rankings": build_json_card_rows(rows),
                "warning": warning,
            }
        )

        if not json_mode:
            print(f"Best card: {rows[0][2]} -> {format_rmb(cheapest_rmb)} RMB")
            if warning:
                print(f"Note: {warning}")
            print("Card rankings:")
            for i, row in enumerate(rows, start=1):
                print(f"{i}. {row[2]} -> {row[-2]} RMB")

        if cheapest_rmb < best_overall_rmb:
            best_overall_rmb = cheapest_rmb
            best_overall_option = normalized_key

    if json_mode:
        payload: Dict[str, Any] = {
            "status": "ok" if all_results else "no_valid_live_deals",
            "results": json_results,
            "overall_best": None,
            "warnings": run_warnings,
        }
        if best_overall_option:
            best_data = all_results[best_overall_option]
            payload["overall_best"] = {
                "normalized_input": best_overall_option,
                "currency": best_data["currency"],
                "amount": best_data["amount"],
                "best_card": best_data["my_cards"][0][2],
                "best_rmb_cost": format_rmb(best_overall_rmb),
                "warning": best_data["warning"],
            }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2 if had_errors and not all_results else 0

    print("\n=======================================================")
    print("                      SUMMARY                          ")
    print("=======================================================")
    for item, data in all_results.items():
        print(
            f"{data['currency'].upper()} {data['amount']} -> Minimum {format_rmb(data['cheapest_rmb'])} RMB "
            f"(using {data['my_cards'][0][2]})"
        )
        if data["warning"]:
            print(f"  提示: {data['warning']}")

    if best_overall_option:
        print(
            f"\nTHE BEST DEAL IS: {best_overall_option.upper()} "
            f"(Estimated: {format_rmb(best_overall_rmb)} RMB)"
        )
    else:
        print("\nNo valid live deals found among your hardcoded cards.")

    return 2 if had_errors and not all_results else 0


if __name__ == "__main__":
    sys.exit(main())
