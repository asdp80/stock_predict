# src/database/database_manager.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 데이터베이스의 설계도를 만들어요
Base = declarative_base()


class StockPrice(Base):
    """
    주식 가격 정보를 저장하는 테이블이에요
    마치 책장의 한 칸이라고 생각하면 돼요!
    """
    __tablename__ = 'stock_prices'

    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    current_price = Column(Float)
    volume = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)
    per = Column(Float)
    pbr = Column(Float)
    roe = Column(Float)


class DatabaseManager:
    """
    데이터베이스를 관리하는 도서관 사서라고 생각하면 돼요!
    """

    def __init__(self):
        # 데이터베이스에 연결해요
        # 실제로는 비밀번호를 안전하게 보관해야 해요!
        self.engine = create_engine('mysql+mysqlconnector://root:root@localhost/stock_db')

        # 책장(테이블)을 만들어요
        Base.metadata.create_all(self.engine)

        # 세션을 만들어요 (도서관에서 일하는 시간이라고 생각하면 돼요!)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_stock_data(self, stock_data):
        """
        주식 정보를 데이터베이스에 저장하는 함수예요
        마치 책을 책장에 꽂는 것과 같아요!
        """
        try:
            # 새로운 가격 정보를 만들어요
            new_price = StockPrice(
                code=stock_data['code'],
                current_price=stock_data['current_price'],
                volume=stock_data['volumes'][-1],
                per=stock_data['per'],
                pbr=stock_data['pbr'],
                roe=stock_data['roe']
            )

            # 데이터베이스에 저장해요
            self.session.add(new_price)
            self.session.commit()

            print(f"{stock_data['code']} 정보를 잘 저장했어요!")

        except Exception as e:
            print(f"앗! 저장하다가 실수했어요: {str(e)}")
            self.session.rollback()


