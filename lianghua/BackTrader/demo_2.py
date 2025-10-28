import backtrader as bt 
import backtrader.indicators as btind # 导入策略分析模块
import backtrader.feeds as btfeeds # 导入数据模块
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import pymysql
from sqlalchemy import create_engine
from urllib.parse import quote_plus



def get_data():
    # 读取数据
    df = pd.read_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/stock_data/600128.csv', )
    # 设置日期为索引
    df['datetime'] = pd.to_datetime(df['date'])
    df.set_index('datetime', inplace=True)
    # 选择需要的列
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df['openinterest'] = 0
    # 计算5日线
    # df['ma5'] = df['close'].rolling(5).mean()
    # # 计算20日均线
    # df['ma20'] = df['close'].rolling(20).mean()
    # # 计算60日均线
    # df['ma60'] = df['close'].rolling(60).mean()
    # # 计算120日均线
    df['ma100'] = df['close'].rolling(100).mean()
    # # 是否多头行情
    # df['is_head'] = (df['ma20'] > df['ma60']) & (df['ma60'] > df['ma120'])
    # print(f"{df}")
    return df



# 创建策略类
class MyStrategy(bt.Strategy):
    # 定义参数
    params = (
        ("period", 20),  # 快速移动平均期数
        )  # 慢速移动平均期数
    
    def __init__(self):
        self.order = None  # 跟踪挂起的订单
        self.sma5 = bt.talib.SMA(self.data, timeperiod=5)
        self.sma10 = bt.talib.SMA(self.data, timeperiod=10)
        self.sma20 = bt.talib.SMA(self.data, timeperiod=20)
        self.sma60 = bt.talib.SMA(self.data, timeperiod=60)
        self.sma120 = bt.talib.SMA(self.data, timeperiod=120)
        # 在 Backtrader 中,不能直接使用 pandas 的 pct_change 方法,需要手动计算收益率
        self.returns = bt.ind.PercentChange(self.data.close)

    def notify_order(self, order):
        '''打印订单信息'''
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return
        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"✅-买单执行:{order.executed.price}")  
                print(f"当前持仓数量: {self.position.size}")
                print(f"当前持仓成本: {self.position.price}")
                print(f"当前持仓收益率: {self.returns[0]}")

            elif order.issell():
                print(f"🅾️-卖单执行:{order.executed.price}" ) 
                print(f"当前持仓数量: {self.position.size}")
                print(f"当前持仓成本: {self.position.price}")
                print(f"当前持仓收益率: {self.returns[0]}") 
                
            self.bar_executed = len(self)   # 记录成交时的bar
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('订单取消/保证金不足/拒绝')    # 订单取消/保证金不足/拒绝
        # 其他状态记录为：无挂起订单
        self.order = None   

    def next(self):
        if self.order:  # 检查是否有订单等待执行
            return  # 如果有，退出
        # 检查是否有持仓   
        if not self.position:  # 还没有仓位
            if (self.sma20[0] > self.sma60[0]) & (self.sma60[0] > self.sma120[0]): 
                self.order = self.buy(size=100)  # 买入
        else:
            if self.position.size > 0: 
                if self.returns[0] > 0.1:
                    self.order = self.sell(size=100)

def run_backtest():
    # 初始化cerebro回测系统设置
    cerebro = bt.Cerebro()  
    # 设置初始资金
    cerebro.broker.setcash(100000.0)        
    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.002)
    # 添加策略
    cerebro.addstrategy(MyStrategy)
    # 调整回测时间范围至数据存在的时间段
    start_date = datetime(2001,8,27)  # 数据起始日期
    end_date = datetime(2025,3, 31)  # 尽量设置较晚日期
    new_df = get_data()
    # 原代码部分
    # start_date = datetime(2021, 9, 1)  # 回测开始时间
    # end_date = datetime(2021, 9, 30)  # 回测结束时间
    data = bt.feeds.PandasData(dataname=new_df, fromdate=start_date, todate=end_date, plot=False)
    cerebro.adddata(data)
    # 运行回测系统
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 在 cerebro.run() 前添加日志
    logging.info('数据长度: %d', len(new_df))


    cerebro.run()
    # 获取回测结果
    print(f'💰-账户余额: {cerebro.broker.getvalue()} ')
    # 绘制回测结果

if __name__ == '__main__':    
    run_backtest()
