import yfinance as yf
import talib as ta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 주식 데이터 가져오기 (삼성전자 예시)
ticker = '005930.KS'
data = yf.download(ticker, start="2023-01-01", end="2023-12-31")

sma = ta.SMA(data["Close"], timeperiod=20)

# Plot the stock data and SMA
plt.figure(figsize=(15, 5))
plt.plot(data["Close"])
plt.plot(sma, label="20-day SMA")
plt.legend()
plt.show()

