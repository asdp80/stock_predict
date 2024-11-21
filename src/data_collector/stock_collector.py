import yfinance as yf
from pykrx import stock
from datetime import datetime, timedelta
import json
import os
import pandas as pd
import numpy as np
import time
from requests.exceptions import RequestException


def convert_numpy_types(obj):
    """NumPy 데이터 타입을 Python 기본 타입으로 변환"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif pd.isna(obj):
        return None
    return obj


def is_weekend_or_holiday(date):
    """주말 또는 공휴일인지 확인하는 함수"""
    if date.weekday() >= 5:
        return True
    return False


def get_previous_trading_day():
    """이전 거래일을 찾는 함수"""
    today = datetime.now()
    max_retries = 20
    for _ in range(max_retries):
        today -= timedelta(days=1)
        if not is_weekend_or_holiday(today):
            try:
                data = stock.get_market_cap_by_ticker(today.strftime("%Y%m%d"))
                if not data.empty:
                    return today.strftime("%Y%m%d")
            except Exception as e:
                print(f"데이터 조회 중 오류 발생: {e}")
            time.sleep(0.5)
    raise Exception("유효한 거래일을 찾을 수 없습니다.")


def get_top_100_stocks():
    """시가총액 상위 100개 종목을 가져오는 함수"""
    today = get_previous_trading_day()
    try:
        kospi_stocks = stock.get_market_cap_by_ticker(today, market='KOSPI')
        top_100_stocks = kospi_stocks.nlargest(100, '시가총액')
        return [(ticker, stock.get_market_ticker_name(ticker)) for ticker in top_100_stocks.index]
    except Exception as e:
        print(f"상위 100개 종목 조회 중 오류 발생: {e}")
        return []


def safe_convert(value):
    """값을 안전하게 변환하는 함수"""
    if pd.isna(value) or value is None:
        return 'N/A'
    try:
        float_value = float(value)
        return float_value if float_value != 0 else 'N/A'
    except:
        return 'N/A'


def save_stock_data(data, folder_path="data"):
    """주식 데이터를 JSON 파일로 저장"""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{folder_path}/stock_data_{timestamp}.json"

        converted_data = json.loads(
            json.dumps(data, default=convert_numpy_types)
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, ensure_ascii=False, indent=2)

        print(f"데이터가 {filename}에 저장되었습니다.")

    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")


def get_complete_stock_data(ticker_code):
    """yfinance와 pykrx를 결합하여 주식 데이터를 가져오는 함수"""
    today = get_previous_trading_day()
    yf_ticker = f"{ticker_code}.KS"

    try:
        kr_fundamentals = stock.get_market_fundamental_by_ticker(today)
        fundamental_data = kr_fundamentals.loc[ticker_code] if ticker_code in kr_fundamentals.index else None

        kr_cap = stock.get_market_cap(today, today, ticker_code)
        yf_stock = yf.Ticker(yf_ticker)
        yf_info = yf_stock.info
        hist = yf_stock.history(period="1y")

        current_price = 'N/A'
        if not hist.empty:
            current_price = safe_convert(hist['Close'].iloc[-1])
        elif 'currentPrice' in yf_info:
            current_price = safe_convert(yf_info['currentPrice'])

        # ROE와 ROA 계산을 함수 내부로 이동
        roe = round(safe_convert(yf_info.get('returnOnEquity')), 2) if safe_convert(
            yf_info.get('returnOnEquity')) != 'N/A' else 'N/A'
        roa = round(safe_convert(yf_info.get('returnOnAssets')), 2) if safe_convert(
            yf_info.get('returnOnAssets')) != 'N/A' else 'N/A'

        combined_data = {
            '기본정보': {
                '종목코드': ticker_code,
                '종목명': stock.get_market_ticker_name(ticker_code),
                '업종': yf_info.get('industry', 'N/A'),
                '섹터': yf_info.get('sector', 'N/A')
            },
            '가격정보': {
                '현재가': current_price,
                '시가총액': safe_convert(kr_cap['시가총액'].iloc[-1] if not kr_cap.empty else yf_info.get('marketCap')),
                '52주_최고': safe_convert(hist['High'].max() if not hist.empty else None),
                '52주_최저': safe_convert(hist['Low'].min() if not hist.empty else None),
                '거래량': safe_convert(yf_info.get('volume'))
            },
            '투자지표': {
                'PER': safe_convert(fundamental_data['PER'] if fundamental_data is not None else None),
                'PBR': safe_convert(fundamental_data['PBR'] if fundamental_data is not None else None),
                'EPS': safe_convert(fundamental_data['EPS'] if fundamental_data is not None else None),
                'BPS': safe_convert(fundamental_data['BPS'] if fundamental_data is not None else None),
                'DIV': safe_convert(fundamental_data['DIV'] if fundamental_data is not None else None),
                'ROE': roe,
                'ROA': roa
            },
            '실적정보': {
                '매출액': safe_convert(yf_info.get('totalRevenue')),
                '영업이익': safe_convert(yf_info.get('operatingMargins')),
                '당기순이익': safe_convert(yf_info.get('netIncomeToCommon'))
            }
        }

        return combined_data

    except Exception as e:
        print(f"데이터 수집 중 오류 발생 ({ticker_code}): {e}")
        return None


def main():
    try:
        top_100_companies = get_top_100_stocks()
        all_stock_data = {}

        if not top_100_companies:
            print("상위 100개 종목을 가져오는데 실패했습니다.")
            return

        print("코스피 시가총액 상위 100개 종목 데이터 수집 중...")

        for ticker, company_name in top_100_companies:
            print(f"{company_name} ({ticker}) 데이터 수집 중...")
            retry_count = 0
            max_retries = 3

            while retry_count < max_retries:
                try:
                    stock_data = get_complete_stock_data(ticker)
                    if stock_data:
                        all_stock_data[ticker] = stock_data
                        print(f"{company_name} 데이터 수집 완료")
                        break
                    else:
                        print(f"{company_name} 데이터 수집 실패")
                        retry_count += 1
                except RequestException:
                    print(f"{company_name} 데이터 수집 재시도 중... ({retry_count + 1}/{max_retries})")
                    retry_count += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"{company_name} 데이터 수집 중 예외 발생: {e}")
                    break

            time.sleep(1)

        save_stock_data(all_stock_data)

    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
        if all_stock_data:
            print("지금까지 수집된 데이터를 저장합니다...")
            save_stock_data(all_stock_data)
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")
        if all_stock_data:
            print("오류 발생 전까지 수집된 데이터를 저장합니다...")
            save_stock_data(all_stock_data)


if __name__ == "__main__":
    main()