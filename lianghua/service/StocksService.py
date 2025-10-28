
from db.database import PostgresDB
from model.Stock import Stock
import akshare as ak



class StocksService:
    def __init__(self):
        # 初始化数据库连接
        self.db = PostgresDB()
        self.stock_info_sh = ak.stock_info_sh_name_code()  # 上海交易所
        self.stock_info_sz = ak.stock_info_sz_name_code()  # 深圳交易所

    # 定义批量插入股票数据
    @staticmethod
    def insert_stock_data(self,stocks):
        """
        插入股票数据
        :param stock_data: 股票数据
        :return:
        """
        try:
            # 使用上下文管理器示例
            with self.db.get_session() as session:
                # 批量更新 根据 id 更新该对象其他字段
                for item in stocks:
                    stock = Stock()
                    stock.id = item.id
                    stock.name = item.name
                    stock.industry = item.industry
                    stock.list_date = item.list_date
                    stock.exchange = item.exchange
                    session.merge(stock)
                    # session.add(stock)
                session.commit()
                print("数据插入成功")
                # 关闭会话
                session.commit()
        except Exception as e:
            print(f"插入失败详情: {str(e)}")
            # 回滚事务
            session.rollback()
        finally:
            print("关闭数据库连接")
            session.close()




        
    def get_data(self):
        stocks = []
        # 处理上海交易所数据
        for index, row in self.stock_info_sh.iterrows():
            stock = Stock()
            stock.id = row['证券代码']
            stock.name = row['证券简称']
            stock.industry = '未知'
            stock.list_date = row['上市日期']
            stock.exchange = 'SH'
            stocks.append(stock)
        
        # # 处理深圳交易所数据
        for index, row in self.stock_info_sz.iterrows():    
            # 假设 Stock 类有对应的属性可以赋值,这里以证券代码和证券简称为例
            stock = Stock()
            stock.id = row['A股代码']
            stock.name = row['A股简称']
            stock.industry = row['所属行业']
            stock.list_date = row['A股上市日期']
            stock.exchange = 'SZ'
            stocks.append(stock)

        self.insert_stock_data(self,stocks)

if __name__ == '__main__':
    get_data()
