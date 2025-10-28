
from model.base.BaseModelInteger import BaseModelInteger
from sqlalchemy import Column, String


class StockData(BaseModelInteger):
    """股票日线数据"""
    __tablename__ = 'stocks_data'
    # 日期
    date = Column(String(50), nullable=False)
    # 开盘价
    open = Column(String(50), nullable=False)
    # 收盘价
    close = Column(String(50), nullable=False)
    # 最高价
    high = Column(String(50), nullable=False)
    # 最低价
    low = Column(String(50), nullable=False)
    # 成交量
    volume = Column(String(50), nullable=False)
    # 成交额
    amount = Column(String(50), nullable=False)
    # 涨跌幅
    pct_chg = Column(String(50), nullable=False)
    # 涨跌额
    change = Column(String(50), nullable=False)
    # 换手率
    turnover_rate = Column(String(50), nullable=False)
    # 量比
    volume_ratio = Column(String(50), nullable=False)
    # 总市值
    total_mv = Column(String(50), nullable=False)
    # 流通市值
    circ_mv = Column(String(50), nullable=False)
    def __repr__(self):
        return f"StockData(id={self.id}, date='{self.date}', open='{self.open}', close='{self.close}', high='{self.high}', low='{self.low}', volume='{self.volume}', amount='{self.amount}', pct_chg='{self.pct_chg}', change='{self.change}', turnover_rate='{self.turnover_rate}')"
