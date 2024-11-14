import logging
import yfinance as yf
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class StockCollector:
    def __init__(self, stock_codes=None):
        if stock_codes is None:
            stock_codes = ['005930.KS', '000660.KS']  # 기본값을 설정하거나 적절한 기본값을 제공
        self.stock_codes = stock_codes
        self.data = []  # 데이터 리스트 초기화

    def collect_all_stocks(self):
        for stock_code in self.stock_codes:
            data = self.fetch_stock_data(stock_code)
            if data:
                self.data.append(data)  # 수집된 데이터를 리스트에 추가
            else:
                logger.warning(f"{stock_code} 데이터 수집 실패")
        return self.data

    def fetch_stock_data(self, stock_code):
        logger.info(f"{stock_code} 데이터 수집을 시작합니다.")

        stock = yf.Ticker(stock_code)

        # 주식 데이터 가져오기
        stock_info = stock.history(period="1mo")

        if stock_info.empty:
            logger.warning(f"{stock_code} 데이터가 비어 있습니다.")
            return None

        # 최신 주가 가져오기
        current_price = stock_info['Close'].iloc[-1]

        # RSI, MACD, MA 등 계산
        rsi = self.calculate_rsi(stock_info)
        macd, macd_signal = self.calculate_macd(stock_info)
        ma5 = stock_info['Close'].rolling(window=5).mean().iloc[-1]
        ma20 = stock_info['Close'].rolling(window=20).mean().iloc[-1]
        ma60 = stock_info['Close'].rolling(window=60).mean().iloc[-1] if len(stock_info) > 60 else np.nan

        # PBR 값 (필요시 다른 방법으로 계산)
        pbr = self.get_pbr(stock_code)

        # 재무 상태 분석
        financial_health = self.analyze_financial_health(stock_code)

        # 회사 정보
        company_info = self.get_company_info(stock_code)

        # 결과 출력
        logger.info(f"{stock_code} 데이터 수집이 완료되었습니다.")

        data = {
            'code': stock_code,
            'current_price': current_price,
            'prices': stock_info['Close'].tolist(),
            'indicators': {
                'RSI': rsi,
                'MACD': macd,
                'MACD_Signal': macd_signal,
                'MA5': ma5,
                'MA20': ma20,
                'MA60': ma60,
            },
            'financial_health': financial_health,
            'company_info': company_info
        }

        logger.info(f"{stock_code} 수집된 데이터: {data}")
        return data

    def calculate_rsi(self, stock_data):
        # RSI 계산 (기본 14일)
        delta = stock_data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else np.nan

    def calculate_macd(self, stock_data):
        # MACD 계산
        macd = stock_data['Close'].ewm(span=12, adjust=False).mean() - stock_data['Close'].ewm(span=26, adjust=False).mean()
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1], macd_signal.iloc[-1]

    def get_pbr(self, stock_code):
        # PBR 가져오기 (임시로 None 반환, 실제 PBR 값을 가져오는 방법 필요)
        try:
            stock = yf.Ticker(stock_code)
            info = stock.info
            pbr = info.get('priceToBook', None)
            if pbr is not None:
                return pbr
            else:
                return "PBR 정보 없음"
        except Exception as e:
            logger.error(f"PBR 정보를 가져오는 중 오류 발생: {e}")
            return "PBR 정보 없음"

    def analyze_financial_health(self, stock_code):
        # 재무 상태 분석 (임시로 예시 데이터 반환)
        return {
            'PER_STATUS': '자산가치보다 고평가',
            'PBR_STATUS': 'PBR 정보 없음',
            'ROE_STATUS': '자산가치보다 저평가'
        }

    def get_company_info(self, stock_code):
        # 회사 정보 가져오기 (예시)
        return {
            'name': 'SK hynix Inc.',
            'sector': 'Technology',
            'description': 'SK hynix Inc., a global leader in semiconductors, manufactures and sells memory chips and related products.'
        }


def main():
    """
    메인 실행 함수입니다.
    """
    # 수집할 주식 종목 목록 (예시로 삼성전자와 SK hynix의 종목 코드 사용)
    stocks = ['005930.KS', '000660.KS']  # 삼성전자, SK hynix

    # StockCollector 객체 생성 시 stock_codes 인자 전달
    collector = StockCollector(stocks)  # stock_codes 인자로 stocks를 전달

    # 모든 주식 데이터 수집
    data = collector.collect_all_stocks()
    print(f"수집된 데이터 수: {len(data)}개")

    # 간단한 결과 출력
    for stock in data:
        print(f"\n{stock['company_info']['name']}({stock['code']}):")
        print(f"현재가: {stock['current_price']:,.0f}원")
        print(f"PBR 상태: {stock['financial_health']['PBR_STATUS']}")

if __name__ == "__main__":
    main()
