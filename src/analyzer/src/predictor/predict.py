import os
import json
import self
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import (Sequential)
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from datetime import datetime
import tensorflow as tf  # TensorFlow import 추가

# 랜덤 시드 설정
seed_value = 42  # 시드값 고정해야 그대로 출력됨
np.random.seed(seed_value)
tf.random.set_seed(seed_value)  # TensorFlow의 랜덤 시드 설정


class StockPredictor:

    def __init__(self, ticker_symbol, prediction_days=30):
        self.ticker = ticker_symbol
        self.prediction_days = prediction_days
        self.scaler = MinMaxScaler()

    def train_model(self):
        """모델 학습 및 예측 수행"""
        try:
            # 데이터 준비
            df = self.prepare_data()
            if df is None:
                return None

            # 데이터 스케일링
            scaled_data = self.scaler.fit_transform(self.feature_data)

            # 시퀀스 데이터 생성
            X, y = self.create_sequences(scaled_data)

            # 훈련/테스트 데이터 분할
            split = int(0.8 * len(X))
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]

            # 모델 생성
            model = self.build_model(input_shape=(self.prediction_days, X.shape[2]))

            # 모델 학습
            history = model.fit(
                X_train, y_train,
                epochs=50,
                batch_size=32,
                validation_split=0.1,
                verbose=1
            )

            # 예측 수행
            train_predict = model.predict(X_train)
            test_predict = model.predict(X_test)

            # 예측값을 원래 스케일로 변환
            y_train_actual = self.inverse_transform_predictions(y_train.reshape(-1, 1))
            y_test_actual = self.inverse_transform_predictions(y_test.reshape(-1, 1))
            train_predict = self.inverse_transform_predictions(train_predict)
            test_predict = self.inverse_transform_predictions(test_predict)

            # 성능 지표 계산
            train_rmse = np.sqrt(mean_squared_error(y_train_actual, train_predict))
            test_rmse = np.sqrt(mean_squared_error(y_test_actual, test_predict))
            train_r2 = r2_score(y_train_actual, train_predict)
            test_r2 = r2_score(y_test_actual, test_predict)

            # 예측 정확도 계산
            prediction_accuracy = self.calculate_prediction_accuracy(y_test_actual, test_predict)

            # 테스트 기간 날짜 가져오기
            test_dates = self.df.index[split + self.prediction_days:].strftime('%Y-%m-%d').tolist()

            return {
                'model': model,
                'test_dates': test_dates,
                'y_test_actual': y_test_actual,
                'test_predict': test_predict,
                'metrics': {
                    'train_rmse': train_rmse,
                    'test_rmse': test_rmse,
                    'train_r2': train_r2,
                    'test_r2': test_r2,
                    'prediction_accuracy': prediction_accuracy
                }
            }

        except Exception as e:
            print(f"모델 학습 중 오류 발생: {str(e)}")
            return None
    def calculate_prediction_accuracy(self, actual, predicted):
        """주가 상승/하락 예측 정확도 계산"""
        actual_direction = np.sign(np.diff(actual))  # 상승: 1, 하락: -1
        predicted_direction = np.sign(np.diff(predicted))  # 상승: 1, 하락: -1

        # 정확도 계산
        correct_predictions = np.sum(actual_direction == predicted_direction)
        total_predictions = len(actual_direction)

        # 정확도를 퍼센트로 계산
        accuracy = (correct_predictions / total_predictions) * 100
        return accuracy


    def prepare_data(self, start_date='2020-01-01'):
        """데이터 수집 및 전처리"""
        try:
            stock = yf.Ticker(self.ticker)
            self.df = stock.history(start=start_date)

            # N/A 값 처리
            self.df = self.df.replace('N/A', np.nan)
            self.df = self.df.fillna(method='ffill')  # 앞의 값으로 채우기
            self.df = self.df.fillna(method='bfill')  # 뒤의 값으로 채우기

            # 기술적 지표 추가
            self.df['MA5'] = self.df['Close'].rolling(window=5).mean()
            self.df['MA20'] = self.df['Close'].rolling(window=20).mean()
            self.df['MA60'] = self.df['Close'].rolling(window=60).mean()

            # RSI 계산
            delta = self.df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            self.df['RSI'] = 100 - (100 / (1 + rs))

            # MACD 계산
            exp1 = self.df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = self.df['Close'].ewm(span=26, adjust=False).mean()
            self.df['MACD'] = exp1 - exp2
            self.df['Signal_Line'] = self.df['MACD'].ewm(span=9, adjust=False).mean()

            self.df.dropna(inplace=True)
            features = ['Close', 'Volume', 'MA5', 'MA20', 'MA60', 'RSI', 'MACD', 'Signal_Line']
            self.feature_data = self.df[features]
            return self.df

        except Exception as e:
            print(f"데이터 준비 중 오류 발생: {e}")
            return None

    def create_sequences(self, data):
        """시계열 데이터를 시퀀스로 변환"""
        X, y = [], []
        for i in range(len(data) - self.prediction_days):
            X.append(data[i:(i + self.prediction_days)])
            y.append(data[i + self.prediction_days, 0])  # Close 가격만 예측
        return np.array(X), np.array(y)

    def build_model(self, input_shape):
        """LSTM 모델 구축"""
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model



    def inverse_transform_predictions(self, predictions):
        """예측값을 원래 스케일로 변환"""
        dummy = np.zeros((predictions.shape[0], self.feature_data.shape[1]))
        dummy[:, 0] = predictions[:, 0]
        return self.scaler.inverse_transform(dummy)[:, 0]

    def predict_next_days(self, model, days=7):
        """향후 n일 예측"""
        try:
            # 최근 데이터 준비
            df = self.prepare_data()
            scaled_data = self.scaler.transform(self.feature_data)
            last_sequence = scaled_data[-self.prediction_days:]

            predictions = []
            current_sequence = last_sequence.copy()

            # n일 동안 예측 수행
            for _ in range(days):
                next_day = model.predict(current_sequence.reshape(1, self.prediction_days,
                                                                  scaled_data.shape[1]))
                predictions.append(next_day[0, 0])

                # 시퀀스 업데이트
                current_sequence = np.roll(current_sequence, -1, axis=0)
                current_sequence[-1] = next_day

            # 예측값을 원래 스케일로 변환
            predictions = np.array(predictions).reshape(-1, 1)
            return self.inverse_transform_predictions(predictions)

        except Exception as e:
            print(f"예측 중 오류 발생: {str(e)}")
            return None


if __name__ == "__main__":
    # JSON에서 종목 코드 불러오기
    json_file = "/src/data_collector/data/stock_data_20241121.json"  # 절대 경로로 수정

    # JSON 파일이 존재하는지 확인
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            stock_data = json.load(f)

        # 종목 코드 리스트 추출
        tickers = list(stock_data.keys())
        tickers = [ticker + '.KS' for ticker in tickers]
        # 각 종목에 대해 예측 수행
        for ticker in tickers:
            print(f"\n=== {ticker} 주가 분석 시작 ===")

            predictor = StockPredictor(ticker)
            results = predictor.train_model()

            if results is not None:
                model = results['model']
                metrics = results['metrics']
                test_dates = results['test_dates']

                print("\n=== 모델 성능 ===")
                print(f"학습 데이터 RMSE: {metrics['train_rmse']:,.0f}원")
                print(f"테스트 데이터 RMSE: {metrics['test_rmse']:,.0f}원")
                print(f"학습 데이터 R²: {metrics['train_r2']:.4f}")
                print(f"테스트 데이터 R²: {metrics['test_r2']:.4f}")
                print(f"주가 상승/하락 예측 정확도: {metrics['prediction_accuracy']:.2f}%")

                print("\n=== 실제 주가와 예측 주가 비교 ===")

                # 최근 10일간의 데이터 출력
                last_10_days = -10
                for date, actual, pred in zip(test_dates[last_10_days:],
                                              results['y_test_actual'][last_10_days:],
                                              results['test_predict'][last_10_days:]):
                    print(f"날짜: {date} | 실제 주가: {actual:,.0f}원 | 예측 주가: {pred:,.0f}원")

                # 상승/하락 예측
                last_actual_direction = np.diff(results['y_test_actual'][-2:])[-1]
                last_predicted_direction = np.diff(results['test_predict'][-2:])[-1]

                direction = "상승" if last_predicted_direction > 0 else "하락"
                print(f"\n예측: 주가가 {direction}합니다. 예측 정확도: {metrics['prediction_accuracy']:.2f}%")
                print("\n*주가 예측은 참고용이며, 투자의 책임은 투자자 본인에게 있습니다*")
    else:
        print(f"파일 {json_file}이 존재하지 않습니다.")

