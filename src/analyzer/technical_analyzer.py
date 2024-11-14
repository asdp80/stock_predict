# src/analyzer/technical_analyzer.py

import pandas as pd
import numpy as np
import talib


class StockAnalyzer:
    """
    주식의 건강상태를 체크하는 의사선생님이에요!
    """

    def __init__(self):
        self.indicators = {}  # 분석 결과를 저장할 거예요

    def analyze_stocks(self, stocks_data):
        analyzed_data = []  # 분석 결과를 저장할 리스트

        for stock in stocks_data:
            code = stock['code']
            prices = stock['prices']
            volumes = stock.get('volumes', [])
            financial_health = stock['financial_health']

            # 기술적 지표 계산
            technical_indicators = self.calculate_indicators(prices, volumes)

            # 재무 비율 분석
            per = financial_health.get('per')
            pbr = financial_health.get('pbr')
            roe = financial_health.get('roe')
            financial_ratios = self.analyze_financial_ratios(per, pbr, roe)

            # 'indicators' 필드에 통합하여 추가
            analyzed_data.append({
                'code': code,
                'indicators': {  # 여기에 통합된 지표 필드로 추가
                    'technical_indicators': technical_indicators,
                    'financial_ratios': financial_ratios
                },
                'current_price': stock['current_price'],
            })

        return analyzed_data

    def calculate_indicators(self, prices, volumes):
        indicators = {}

        # dtype을 float로 명시적으로 설정
        prices_array = np.array(prices, dtype=np.float64)
        volumes_array = np.array(volumes, dtype=np.float64)

        try:
            # RSI 계산
            rsi = talib.RSI(prices_array)
            if rsi is not None and len(rsi) > 0:
                indicators['RSI'] = float(rsi[-1])
            else:
                print("RSI 계산 실패: 데이터 부족")

            # MACD 계산
            macd, signal, hist = talib.MACD(prices_array)
            if macd is not None and len(macd) > 0:
                indicators['MACD'] = float(macd[-1])
                indicators['MACD_Signal'] = float(signal[-1])

            # 이동평균선 계산
            ma5 = talib.SMA(prices_array, timeperiod=5)
            ma20 = talib.SMA(prices_array, timeperiod=20)
            ma60 = talib.SMA(prices_array, timeperiod=60)

            if ma5 is not None and len(ma5) > 0:
                indicators['MA5'] = float(ma5[-1])
            if ma20 is not None and len(ma20) > 0:
                indicators['MA20'] = float(ma20[-1])
            if ma60 is not None and len(ma60) > 0:
                indicators['MA60'] = float(ma60[-1])

        except Exception as e:
            print(f"지표 계산 중 오류 발생: {e}")

        return indicators

    def analyze_financial_ratios(self, per, pbr, roe):
        """
        재무제표를 분석하는 함수예요 (주식의 혈액검사 같은 거예요!)
        """
        financial_health = {}

        # PER 분석 (주가수익비율: 얼마나 비싼지 확인)
        if per is not None:
            if per < 10:
                financial_health['PER_STATUS'] = "저평가 (싸요!)"
            elif per < 20:
                financial_health['PER_STATUS'] = "적정가치"
            else:
                financial_health['PER_STATUS'] = "고평가 (비싸요!)"

        # PBR 분석 (주가순자산비율: 회사의 가치 대비 주가 확인)
        if pbr is not None:
            if pbr < 1:
                financial_health['PBR_STATUS'] = "자산가치보다 저평가"
            elif pbr < 2:
                financial_health['PBR_STATUS'] = "적정가치"
            else:
                financial_health['PBR_STATUS'] = "자산가치보다 고평가"

        # ROE 분석 (자기자본이익률: 회사가 돈을 얼마나 잘 버는지)
        if roe is not None:
            if roe > 15:
                financial_health['ROE_STATUS'] = "수익성이 매우 좋아요!"
            elif roe > 10:
                financial_health['ROE_STATUS'] = "수익성이 괜찮아요"
            else:
                financial_health['ROE_STATUS'] = "수익성이 조금 아쉬워요"

        return financial_health


