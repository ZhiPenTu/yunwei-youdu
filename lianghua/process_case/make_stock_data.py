from tqdm import tqdm
import pandas as pd
import threading
import akshare as ak
from pathlib import Path

class Test:
    def __init__(self):
        """
        初始化，获取股票代码和名称的映射。
        """
        self.load_stock_data_from_csv()



    def clear_data(self):

        """
        从 CSV 文件加载所有股票数据。
        """

        stock_data_dir = Path('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/stock_data')
        if stock_data_dir.exists():
            csv_files = list(stock_data_dir.glob('*.csv'))
            num_threads = 10
            chunk_size = (len(csv_files) + num_threads - 1) // num_threads
            chunks = [csv_files[i:i + chunk_size] for i in range(0, len(csv_files), chunk_size)]

            def load_stocks(codes):
                with tqdm(total=len(codes), desc="加载本地历史股票数据") as pbar:
                    for file in codes:
                        code = file.stem
                        df = pd.read_csv(file)
                        df = df.drop(columns=['ma5', 'ma20', 'ma60', 'ma100', 'ma120', 'is_head'])
                        # 保存到csv
                        df.to_csv(f'/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/source_data/{code}.csv', index=False)
                        pbar.update(1)

            threads = [threading.Thread(target=load_stocks, args=(chunk,)) for chunk in chunks]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

    def load_stock_data_from_csv(self):
        """
        从 CSV 文件加载所有股票数据。
        """
        stock_data_dir = Path('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/source_data')
        if stock_data_dir.exists():
            csv_files = list(stock_data_dir.glob('*.csv'))
            num_threads = 10
            chunk_size = (len(csv_files) + num_threads - 1) // num_threads
            chunks = [csv_files[i:i + chunk_size] for i in range(0, len(csv_files), chunk_size)]

            def load_stocks(codes):
                with tqdm(total=len(codes), desc="加载本地历史股票数据") as pbar:
                    for file in codes:
                        code = file.stem
                        df = pd.read_csv(file)
                        
                        # 计算5日线 保留小数点后两位
                        df['ma5'] = df['close'].rolling(5).mean().round(2)
                        # 计算20日均线
                        df['ma20'] = df['close'].rolling(20).mean().round(2)
                        # 计算60日均线
                        df['ma60'] = df['close'].rolling(60).mean().round(2)
                         # 计算100日均线
                        df['ma100'] = df['close'].rolling(100).mean().round(2)
                         # 计算120日均线
                        df['ma120'] = df['close'].rolling(120).mean().round(2)
                        # 是否多头行情
                        df['is_head'] = (df['ma20'] > df['ma60']) & (df['ma60'] > df['ma120'])
                        # 获取120日内的最大值
                        df['max_120'] = df['high'].rolling(120).max()
                        # 获取120日内的最小值
                        df['min_120'] = df['low'].rolling(120).min()
                        # 换手率 先乘以 100 在保留小数点后两位
                        df['turnover'] = df['turnover'].apply(lambda x: x * 100).round(2)
                        # 保存到csv
                        df.to_csv(f'/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/stock_data/{code}.csv', index=False)
                        pbar.update(1)

            threads = [threading.Thread(target=load_stocks, args=(chunk,)) for chunk in chunks]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
                            
            



if __name__ == '__main__':
    test = Test()

    # for code, df in test.all_stocks_data.items():
    #     print(code)

    