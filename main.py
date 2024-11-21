

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import json
from pathlib import Path
from src.analyzer.stock_ranker import StockRanker
from src.analyzer.technical_analyzer import StockAnalyzer
from src.analyzer.src.predictor.predict import StockPredictor
import sys
import os
from fastapi.middleware.cors import CORSMiddleware
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Analysis App")
# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web" / "static")), name="static")

ranker = StockRanker()
predictors = {}  # 종목별 예측기 저장


def load_stock_data():
    json_file_path = r"C:\Users\asdp8\React\pythonProject1\src\data_collector\data\stock_data_20241121.json"
    with open(json_file_path, 'r', encoding='utf-8') as f:
        stock_data = json.load(f)
    return stock_data

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/main")
async def home(request: Request):
    try:
        logger.info("홈 라우트 접근")
        stocks_data = load_stock_data()

        if not stocks_data:
            logger.warning("수집된 데이터가 없습니다")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error_message": "주식 데이터를 가져올 수 없습니다."}
            )

        ranked_stocks = ranker.calculate_ranking(stocks_data)
        ranked_stocks_dict = ranked_stocks.to_dict(orient='records')

        debug_info = {
            "collected_stocks": len(stocks_data),
            "ranked_stocks": len(ranked_stocks)
        }

        return templates.TemplateResponse(
            "main.html",
            {
                "request": request,
                "stocks": ranked_stocks_dict,
                "debug_info": debug_info
            }
        )
    except Exception as e:
        logger.exception("홈 라우트 에러 발생")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": str(e)}
        )

@app.get("/predict/{stock_code}")
async def show_prediction(request: Request, stock_code: str):
    try:
        if stock_code not in predictors:
            predictors[stock_code] = StockPredictor(f"{stock_code}.KS")

        predictor = predictors[stock_code]
        results = await asyncio.get_event_loop().run_in_executor(None, predictor.train_model)

        if results is None:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error_message": "예측 실패"}
            )

        prediction_data = {
            "request": request,
            "stock_name": "종목명",  # 종목명을 가져오는 로직 필요
            "current_price": format(int(results['y_test_actual'][-1]), ','),
            "direction": "상승" if results['test_predict'][-1] > results['y_test_actual'][-1] else "하락",
            "accuracy": round(results['metrics']['prediction_accuracy']),
            "rmse": format(int(results['metrics']['test_rmse']), ','),
            "recent_predictions": [
                {
                    "date": date,
                    "actual": format(int(actual), ','),
                    "predicted": format(int(pred), ',')
                }
                for date, actual, pred in zip(
                    results['test_dates'][-10:],
                    results['y_test_actual'][-10:],
                    results['test_predict'][-10:]
                )
            ],
            "chart_data": {
                "dates": results['test_dates'][-10:],
                "actual_prices": results['y_test_actual'][-10:].tolist(),
                "predicted_prices": results['test_predict'][-10:].tolist(),
                "future_predictions": predictor.predict_next_days(results['model'], days=7).tolist()
            }
        }

        return templates.TemplateResponse("prediction.html", prediction_data)

    except Exception as e:
        logger.error(f"예측 페이지 에러: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": str(e)}
        )
@app.get("/api/predict/{stock_code}")
async def predict_stock(stock_code: str):
    """주식 예측 API 엔드포인트"""
    try:
        # 종목별 예측기 초기화
        if stock_code not in predictors:
            predictors[stock_code] = StockPredictor(f"{stock_code}.KS")

        predictor = predictors[stock_code]

        # 모델 학습을 비동기로 실행
        results = await asyncio.get_event_loop().run_in_executor(
            None, predictor.train_model
        )

        if results is None:
            logger.error("예측 결과가 없습니다.")
            return JSONResponse(
                content={"error": "예측 실패"},
                status_code=500
            )

        try:
            # 최근 실제 가격과 예측 가격 데이터 준비
            test_dates = results['test_dates'][-10:]  # 최근 10일 날짜
            actual_prices = results['y_test_actual'][-10:].tolist()  # 최근 10일 실제 가격
            predicted_prices = results['test_predict'][-10:].tolist()  # 최근 10일 예측 가격

            # 다음 7일 예측을 비동기로 실행
            future_predictions = await asyncio.get_event_loop().run_in_executor(
                None,
                predictor.predict_next_days,
                results['model'],
                7
            )

            # 최근 예측 결과를 테이블 형식으로 준비
            recent_predictions = [
                {
                    "date": date,
                    "actual": float(actual),
                    "predicted": float(pred)
                }
                for date, actual, pred in zip(test_dates, actual_prices, predicted_prices)
            ]

            # 반환 데이터 구성
            prediction_data = {
                "current_price": float(results['y_test_actual'][-1]),
                "direction": "상승" if results['test_predict'][-1] > results['y_test_actual'][-1] else "하락",
                "accuracy": float(results['metrics']['prediction_accuracy']),
                "dates": test_dates,
                "actual_prices": actual_prices,
                "predicted_prices": predicted_prices,
                "future_predictions": future_predictions.tolist(),
                "recent_predictions": recent_predictions,
                "metrics": {
                    "rmse": float(results['metrics'].get('test_rmse', 0)),
                    "r2": float(results['metrics'].get('test_r2', 0))
                }
            }

            logger.info(f"예측 성공: {stock_code}")
            return JSONResponse(content=prediction_data)

        except Exception as data_error:
            logger.error(f"데이터 처리 중 오류: {str(data_error)}")
            return JSONResponse(
                content={"error": "데이터 처리 중 오류가 발생했습니다"},
                status_code=500
            )

    except Exception as e:
        logger.error(f"예측 API 오류: {str(e)}")
        return JSONResponse(
            content={"error": "예측 처리 중 오류가 발생했습니다"},
            status_code=500
        )


if __name__ == "__main__":
    logger.info("서버 시작")
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)

