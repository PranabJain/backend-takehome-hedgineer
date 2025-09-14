import requests

url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1mo&interval=1d"
resp = requests.get(url)
print(resp.status_code)
print(resp.text[:200])
