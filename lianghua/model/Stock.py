from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from model.base.BaseModelString import BaseModelString


class Stock(BaseModelString):
    """股票模型"""
    __tablename__ = 'stocks'
    #简称
    name = Column(String(50), nullable=False)
    # 上市时间
    list_date = Column(String(50))
    # 所属行业
    industry = Column(String(50))
    # 上市地点
    exchange = Column(String(50))
    # # 建立一对多关系
    # stock_data = relationship("StockData", back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Stock(id={self.id}, name='{self.name}', list_date='{self.list_date}', industry='{self.industry}', exchange='{self.exchange}', updated_at='{self.updated_at}', created_at='{self.created_at}')"


# class StockData(BaseModelInteger):
#     """股票日线数据"""
#     __tablename__ = 'stocks_data'
#     # 日期
#     date = Column(String(50), nullable=False)
#     # 开盘价
#     open = Column(String(50), nullable=False)
#     # 收盘价
#     close = Column(String(50), nullable=False)
#     # 最高价
#     high = Column(String(50), nullable=False)
#     # 最低价
#     low = Column(String(50), nullable=False)
#     # 成交量
#     volume = Column(String(50), nullable=False)
#     # 成交额
#     amount = Column(String(50), nullable=False)
#     # 振幅
#     pct_chg = Column(String(50), nullable=False)
#     # 涨跌幅
#     change = Column(String(50), nullable=False)
#     # 换手率
#     turnover_rate = Column(String(50), nullable=False)
#     # # 建立多对一关系
#     # stock = relationship("Stock", back_populates="stock_data")
#     def __repr__(self):
#         return f"StockData(stock_id={self.stock_id}, date='{self.date}', open='{self.open}', close='{self.close}', high='{self.high}', low='{self.low}', volume='{self.volume}', amount='{self.amount}', pct_chg='{self.pct_chg}', change='{self.change}', turnover_rate='{self.turnover_rate}')"
