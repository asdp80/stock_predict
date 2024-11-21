import pandas as pd
import numpy as np

class StockRanker:
    def __init__(self):
        pass

    def calculate_score(self, series, is_higher_better=True):
        series = pd.to_numeric(series, errors='coerce')

        if is_higher_better:
            return ((series - series.min()) / (series.max() - series.min()) * 100)
        else:
            return ((series.max() - series) / (series.max() - series.min()) * 100)

    def calculate_per_and_pbr(self, stock_info):
        per = stock_info['투자지표']['PER']
        pbr = stock_info['투자지표']['PBR']

        if per is None:
            if stock_info['투자지표']['EPS'] is not None and stock_info['가격정보']['현재가'] is not None:
                per = stock_info['가격정보']['현재가'] / stock_info['투자지표']['EPS']
            else:
                per = 0

        if pbr is None:
            if stock_info['투자지표']['BPS'] is not None and stock_info['가격정보']['현재가'] is not None:
                pbr = stock_info['가격정보']['현재가'] / stock_info['투자지표']['BPS']
            else:
                pbr = 0

        return per, pbr

    def calculate_ranking(self, data):
        # 데이터를 DataFrame으로 변환하기 위한 리스트
        stocks_list = []

        for code, stock_info in data.items():
            per, pbr = self.calculate_per_and_pbr(stock_info)
            stock_dict = {

                '종목코드': code,
                '종목명': stock_info['기본정보']['종목명'],
                '섹터': stock_info['기본정보']['섹터'],
                '시가총액': stock_info['가격정보']['시가총액'],
                'PER': per,
                'PBR': pbr,
                'DIV': stock_info['투자지표']['DIV'],
                'ROE': stock_info['투자지표']['ROE'],
                'ROA': stock_info['투자지표']['ROA']
            }
            stocks_list.append(stock_dict)

        # DataFrame 생성
        df = pd.DataFrame(stocks_list)

        # 'N/A' 값을 NaN으로 변환
        df = df.replace('N/A', np.nan)

        # 지표별 점수 계산 (0-100점 스케일)
        df['PER_점수'] = self.calculate_score(df['PER'], False)  # Lower PER is better
        df['PBR_점수'] = self.calculate_score(df['PBR'], False)  # Lower PBR is better
        df['DIV_점수'] = self.calculate_score(df['DIV'], True)  # Higher DIV is better
        df['ROE_점수'] = self.calculate_score(df['ROE'], True)  # Higher ROE is better
        df['ROA_점수'] = self.calculate_score(df['ROA'], True)  # Higher ROA is better

        # 종합 점수 계산 (가중치 적용)
        weights = {
            'PER_점수': 0.25,
            'PBR_점수': 0.20,
            'DIV_점수': 0.15,
            'ROE_점수': 0.25,
            'ROA_점수': 0.15
        }

        df['종합점수'] = sum(df[score] * weight for score, weight in weights.items())

        # 순위 계산
        df['순위'] = df['종합점수'].rank(ascending=False, method='min')

        # NaN 또는 무한 값을 0 또는 다른 적절한 값으로 채우기
        df['순위'] = df['순위'].fillna(0).replace([np.inf, -np.inf], 0)

        # 소수점 제거: 순위를 정수로 변환
        df['순위'] = df['순위'].astype(int)
        # 결과 정렬 및 포맷팅

        result = df.sort_values('종합점수', ascending=False)

        # 점수들을 소수점 2자리까지 반올림
        score_columns = ['PER_점수', 'PBR_점수', 'DIV_점수', 'ROE_점수', 'ROA_점수', '종합점수']
        result[score_columns] = result[score_columns].round(2)

        # 시가총액을 조원 단위로 변환
        result['시가총액(조원)'] = (result['시가총액'] / 1e12).round(2)

        # 최종 출력을 위한 컬럼 선택 및 정렬
        final_columns = ['순위', '종목코드', '종목명', '섹터', '시가총액(조원)',
                         'PER', 'PBR', 'DIV', 'ROE', 'ROA', '종합점수']

        return result[final_columns]
