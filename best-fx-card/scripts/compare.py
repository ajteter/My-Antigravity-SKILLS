import urllib.request
import ssl
import sys
from datetime import datetime
from html.parser import HTMLParser

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

def get_best_cards(currency, amount):
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.kylc.com/huilv/whichcard.html?ccy={currency.lower()}&amt={amount}&date={today}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=context) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching data for {currency}: {e}")
        return []
        
    parser = KylcParser()
    parser.feed(html)
    
    # row format example: ['1', 'direct-multi-currency', '华夏Visa美元卡', '不需要', '不需要', '0', '6.9253', '100', 'USD', '≈', '692.53', 'RMB']
    results = []
    # Skip header row (which is usually the first row with '#', '卡种', etc)
    for row in parser.rows:
        if len(row) > 10 and row[0] != '#':
            try:
                # The total RMB is typically near the end of the row
                rmb_amount = float(row[-2].replace(',', ''))
                results.append(row)
            except ValueError:
                pass
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compare.py \"usd 100\" \"jpy 15000\"")
        sys.exit(1)
        
    inputs = sys.argv[1:]
    best_overall_rmb = float('inf')
    best_overall_option = None
    
    all_results = {}
    
    for item in inputs:
        parts = item.split()
        if len(parts) != 2:
            print(f"Invalid format: {item}. Use \"currency amount\"")
            continue
        currency = parts[0].lower()
        amount = parts[1]
        
        print(f"\\n--- Querying best cards for {currency.upper()} {amount} ---")
        rows = get_best_cards(currency, amount)
        if not rows:
            print("No data found or parsing error.")
            continue
            
        # The first valid row is usually the cheapest
        cheapest_rmb = float(rows[0][-2].replace(',', ''))
        all_results[item] = {
            'currency': currency,
            'amount': amount,
            'cheapest_rmb': cheapest_rmb,
            'top20': rows[:20]
        }
        
        if cheapest_rmb < best_overall_rmb:
            best_overall_rmb = cheapest_rmb
            best_overall_option = item
            
    print("\\n=======================================================")
    print("                      SUMMARY                          ")
    print("=======================================================")
    for item, data in all_results.items():
        print(f"{data['currency'].upper()} {data['amount']} -> Minimum {data['cheapest_rmb']} RMB")
    
    if best_overall_option:
        print(f"\\n🏆 THE BEST DEAL IS: {best_overall_option.upper()} (Estimated: {best_overall_rmb} RMB) 🏆\\n")
        print(f"Here are the top 20 most suitable bank cards for {best_overall_option.upper()}:")
        for i, row in enumerate(all_results[best_overall_option]['top20']):
            card_name = row[2]
            rmb_cost = row[-2]
            print(f"{i+1}. {card_name} -> {rmb_cost} RMB")
    else:
        print("\\nNo valid deals found.")

if __name__ == "__main__":
    main()
