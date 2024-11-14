# src/analyzer/stock_ranker.py

class StockRanker:
    """
    주식들의 시험 점수를 매기는 선생님이에요!
    """

    def __init__(self):
        self.scores = {}

    def calculate_technical_score(self, indicators):
        score = 0
        try:
            technical_indicators = indicators.get('technical_indicators', {})

            # RSI 점수 (30점 만점)
            rsi = technical_indicators.get('RSI', None)
            if rsi is not None:
                if 40 <= rsi <= 60:
                    score += 30
                elif (30 <= rsi < 40) or (60 < rsi <= 70):
                    score += 15

            # MACD 점수 (40점 만점)
            macd = technical_indicators.get('MACD', None)
            macd_signal = technical_indicators.get('MACD_Signal', None)
            if macd is not None and macd_signal is not None:
                if macd > macd_signal:
                    score += 40

            # 이동평균선 점수 (30점 만점)
            ma5 = technical_indicators.get('MA5', None)
            ma20 = technical_indicators.get('MA20', None)
            ma60 = technical_indicators.get('MA60', None)
            if all(x is not None for x in [ma5, ma20, ma60]):
                if ma5 > ma20 and ma20 > ma60:
                    score += 30
                elif ma5 > ma20:
                    score += 15

        except Exception as e:
            print(f"지표 계산 중 오류 발생: {e}")
            return 0

        return score

    def calculate_financial_score(self, financial_health):
        score = 0
        try:
            # PER 점수 (30점 만점)
            per_status = financial_health.get('PER_STATUS', '')
            if per_status == "저평가 (싸요!)":
                score += 30
            elif per_status == "적정가치":
                score += 15

            # PBR 점수 (30점 만점)
            pbr_status = financial_health.get('PBR_STATUS', '')
            if pbr_status == "자산가치보다 저평가":
                score += 30
            elif pbr_status == "적정가치":
                score += 15

            # ROE 점수 (40점 만점)
            roe_status = financial_health.get('ROE_STATUS', '')
            if roe_status == "수익성이 매우 좋아요!":
                score += 40
            elif roe_status == "수익성이 괜찮아요":
                score += 20

        except Exception as e:
            print(f"재무 점수 계산 중 오류 발생: {e}")
            return 0

        return score

    def rank_stocks(self, stocks_data):
        ranked_stocks = []

        for stock in stocks_data:
            try:
                if 'indicators' not in stock:
                    print(f"Warning: Stock data missing 'indicators' for {stock['code']}")
                    continue

                technical_score = self.calculate_technical_score(stock['indicators'])
                financial_score = self.calculate_financial_score(stock.get('financial_health', {}))
                total_score = technical_score + financial_score

                # 템플릿에 맞는 구조로 데이터 구성
                ranked_stock = {
                    'code': stock['code'],
                    'name': stock.get('company_info', {}).get('name', stock['code']),
                    'current_price': stock.get('current_price', 0),
                    'total_score': total_score,
                    'technical_score': technical_score,
                    'financial_score': financial_score,
                    'indicators': stock['indicators'],  # 원본 지표 데이터 유지
                    'financial_health': stock.get('financial_health', {}),  # 재무 데이터 유지
                    'rsi': stock['indicators'].get('technical_indicators', {}).get('RSI', 0),
                    'per_status': stock.get('financial_health', {}).get('PER_STATUS', 'N/A'),
                    'pbr_status': stock.get('financial_health', {}).get('PBR_STATUS', 'N/A'),
                    'roe_status': stock.get('financial_health', {}).get('ROE_STATUS', 'N/A')
                }
                ranked_stocks.append(ranked_stock)

            except Exception as e:
                print(f"Error processing stock {stock.get('code', 'unknown')}: {e}")
                continue

        ranked_stocks.sort(key=lambda x: x['total_score'], reverse=True)

        # 순위 추가
        for i, stock in enumerate(ranked_stocks, 1):
            stock['rank'] = i

        return ranked_stocks


