import urllib.request
import ssl
from html.parser import HTMLParser

url = "https://www.kylc.com/huilv/whichcard.html?ccy=usd&amt=1000"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
context = ssl._create_unverified_context()
with urllib.request.urlopen(req, context=context) as response:
    html = response.read().decode('utf-8')

class MyHTMLParser(HTMLParser):
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

parser = MyHTMLParser()
parser.feed(html)
for row in parser.rows[:50]:
    print(row)
