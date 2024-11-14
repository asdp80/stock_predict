from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
from pathlib import Path

# 로컬 모듈 임포트
from src.data_collector.stock_collector import StockCollector
from src.analyzer.stock_ranker import StockRanker
from src.analyzer.technical_analyzer import *
from src.analyzer.technical_analyzer import StockAnalyzer  # StockAnalyzer 클래스가 이 파일에 있다고 가정

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="Stock Analysis App")

# 템플릿과 정적 파일 설정
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web" / "static")), name="static")

# 서비스 객체 초기화
collector = StockCollector()
analyzer = StockAnalyzer()
ranker = StockRanker()

@app.get("/")
async def home(request: Request):
    try:
        logger.info("홈 라우트 접근")

        # 데이터 수집 및 로깅
        stocks_data = collector.collect_all_stocks()
        logger.info(f"수집된 데이터: {stocks_data}")

        if not stocks_data:
            logger.warning("수집된 데이터가 없습니다")
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error_message": "주식 데이터를 가져올 수 없습니다."}
            )

        # 데이터 분석 및 로깅
        analyzed_stocks = analyzer.analyze_stocks(stocks_data)
        logger.info(f"분석된 데이터: {analyzed_stocks}")

        # 순위 계산 및 로깅
        ranked_stocks = ranker.rank_stocks(analyzed_stocks)
        logger.info(f"최종 데이터: {ranked_stocks}")

        # 디버그 정보 추가
        debug_info = {
            "collected_stocks": len(stocks_data),
            "analyzed_stocks": len(analyzed_stocks),
            "ranked_stocks": len(ranked_stocks)
        }

        # 템플릿 렌더링
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "stocks": ranked_stocks,
                "debug_info": debug_info,
                "analyzed_data": analyzed_stocks
            }
        )
    except Exception as e:
        logger.exception("홈 라우트 에러 발생")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": str(e)}
        )

@app.get("/api/stocks")
async def get_stocks():
    """
    주식 데이터를 JSON 형식으로 반환하는 API 엔드포인트
    """
    try:
        stocks_data = collector.collect_all_stocks()
        if not stocks_data:
            return JSONResponse(content={"error": "주식 데이터를 가져올 수 없습니다."}, status_code=404)

        analyzed_stocks = analyzer.analyze_stocks(stocks_data)
        ranked_stocks = ranker.rank_stocks(analyzed_stocks)
        return JSONResponse(content=ranked_stocks)
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error_message": str(exc)},
        status_code=500
    )

if __name__ == "__main__":
    logger.info("서버 시작")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8002,
        reload=True
    )