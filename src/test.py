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

# # 이동평균선(SMA) 및 RSI 지표 계산
# data['SMA20'] = ta.SMA(data['Close'].to_numpy().flatten(), timeperiod=20)  # 20일 단순 이동평균
# data['RSI'] = ta.RSI(data['Close'].to_numpy().flatten(), timeperiod=14)    # 14일 RSI
#
# # 볼린저 밴드 계산
# data['Upper'], data['Middle'], data['Lower'] = ta.BBANDS(
#     data['Close'].to_numpy().flatten(), timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
# )
#
# print(data[['Close', 'SMA20', 'RSI', 'Upper', 'Middle', 'Lower']].tail())
