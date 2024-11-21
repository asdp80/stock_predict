# src/analyzer/stock_list.py

from pykrx import stock
from datetime import datetime, timedelta

# Calculate the previous trading day
def get_previous_trading_day():
    today = datetime.now()
    while True:
        today -= timedelta(days=1)
        # Check if there is market cap data for the day (valid trading day)
        try:
            data = stock.get_market_cap_by_ticker(today.strftime("%Y%m%d"), market="KOSPI")
            if not data.empty:
                break
        except:
            continue
    return today.strftime("%Y%m%d")

# Get the previous trading day
today = get_previous_trading_day()

# Fetch KOSPI market cap data
kospi_stocks = stock.get_market_cap_by_ticker(today, market="KOSPI")

# Extract the top 50 by market cap
top_50_stocks = kospi_stocks.nlargest(50, '시가총액')

# List of stock codes and names
top_50_companies = [(ticker, stock.get_market_ticker_name(ticker)) for ticker in top_50_stocks.index]

# Display the results
print(f"코스피 시가총액 상위 50 종목 (기준일: {today}):")
for ticker, name in top_50_companies:
    print(f"{ticker}: {name}")