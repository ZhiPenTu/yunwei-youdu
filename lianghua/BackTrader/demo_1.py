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
 # 配置数据库连接参数（根据实际数据库修改）
DB_CONFIG = {
    'db_type': 'mysql',      # 可选: mysql, postgresql, sqlite
    'username': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': '3306',
    'database': 'your_database',
    'table_name': 'your_table',  # 要读取的表名
    'sqlite_path': '/path/to/database.db'  # SQLite 专用
}
def read_db_to_dataframe(config):       
    """从数据库读取数据到Pandas DataFrame"""
    db_type = config['db_type']
    config['password'] = quote_plus(config['password'])  # 处理密码中的特殊字符
    try:
        # 创建数据库连接引擎
        if db_type == 'mysql':
            conn_str = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        elif db_type == 'postgresql':
            conn_str = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        elif db_type == 'sqlite':
            conn_str = f"sqlite:///{config['sqlite_path']}"
        else:
            raise ValueError("不支持的数据库类型！请选择: mysql, postgresql, sqlite")
        
        engine = create_engine(conn_str)
        
        # 方法1：直接读取整张表
        # df = pd.read_sql_table(config['table_name'], engine)
        
        # 方法2：通过SQL查询读取（更灵活）
        query = "SELECT * FROM t_iot_device LIMIT 1000"  # 示例查询
        df = pd.read_sql_query(query, engine)
        print(f"成功读取 {len(df)} 行数据")
        engine.dispose()
        return df
    
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None
def get_data():
    # 读取数据
    df = pd.read_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/stock_data/000017.csv', )
    # 设置日期为索引
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    # 选择需要的列
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df['openinterest'] = 0
    print(f"df: {df}")
    return df
# 创建策略类
class MyStrategy(bt.Strategy):
    # 定义参数
    params = (
        ("period", 20),  # 快速移动平均期数
        )  # 慢速移动平均期数
    
    def __init__(self):
        self.order = None  # 跟踪挂起的订单
        self.sma = bt.talib.SMA(self.data, timeperiod=self.params.period)
        print(f"sma: {self.sma}")
    def next(self):
        if self.order:  # 检查是否有订单等待执行
            return  # 如果有，退出
        # 检查是否有持仓    
        if not self.position:  # 还没有仓位
            # 判断股价是否上穿均线
            if self.sma > 0:  # 如果fast线上穿slow线
                self.order = self.buy(size=2000)  # 买入
        else:
            if self.sma < 0:  # 如果fast线下穿slow线
                self.order = self.sell(size=2000)  # 卖出

def run_backtest():
    # 初始化cerebro回测系统设置
    cerebro = bt.Cerebro()  
    # 设置初始资金
    cerebro.broker.setcash(1000000.0)        
    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.002)
    # 添加策略
    cerebro.addstrategy(MyStrategy)
    # 调整回测时间范围至数据存在的时间段
    start_date = datetime(2001,8,27)  # 数据起始日期
    end_date = datetime(2024, 12, 31)  # 尽量设置较晚日期
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
    print(f'Final Portfolio Value: {cerebro.broker.getvalue()} ')
    # print(f"Annual Return: {cerebro.broker.get_annual_return()}")
    # print(f"Max Drawdown: {cerebro.broker.get_max_drawdown()}")
    # 绘制回测结果
    cerebro.plot(style='candlestick')  # 将figure对象传递给plot函数

if __name__ == '__main__':    
         
    run_backtest()
    # # 替换为你的实际配置
    # DB_CONFIG.update({
    #     'db_type': 'mysql',
    #     'host': '35.46.5.37',
    #     'port': '8066',
    #     'username': 'root',
    #     'password': 'HTcf2022!@#',
    #     'database': 'cvis_iot',
    #     'table_name': 't_iot_device'
    # })
    
    # # 读取数据
    # df = read_db_to_dataframe(DB_CONFIG)
    # print(df.head()) 
