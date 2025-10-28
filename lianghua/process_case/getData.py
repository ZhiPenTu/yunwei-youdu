from turtle import color
import akshare as ak
import pandas as pd
from datetime import datetime
import os
from tqdm import tqdm


class StockPriceMonitor:
    def __init__(self):
        """
        初始化，获取股票代码和名称的映射。
        """
        print("开始初始化，获取股票代码和名称的映射...")
        self.today = self.get_today_date()
        self.stock_info_sh = ak.stock_info_sh_name_code()  # 上海交易所
        self.stock_info_sz = ak.stock_info_sz_name_code()  # 深圳交易所
        if self.stock_info_sh.empty or self.stock_info_sz.empty:
            print("初始化失败，未能获取到完整股票代码和名称的映射信息，程序终止。")
            exit(1)
        self.code_name_map_sh = dict(zip(self.stock_info_sh['证券代码'], self.stock_info_sh['证券简称']))
        self.code_name_map_sz = dict(zip(self.stock_info_sz['A股代码'], self.stock_info_sz['A股简称']))
        self.all_stocks_data = {}  # 存储所有股票前复权数据的dict，key=股票代码，value=DataFrame
        self.load_source_data_from_csv()
        self.iterate_over_all_stocks()
        print("初始化完成。")

    @staticmethod
    def get_today_date():
        import datetime
        today = datetime.date.today()
        # 如果当前时间是当天的下午15:00以前，返回昨天的日期
        if datetime.datetime.now().time() < datetime.time(15, 0):
            today = today - datetime.timedelta(days=1)
        return today.strftime('%Y-%m-%d')

    def iterate_over_all_stocks(self):
        """
        遍历所有股票，获取或更新前复权日线数据。
        :return: 包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        print("开始遍历所有股票，获取前复权日线数据...")
        # 合并上海和深圳交易所的股票代码和名称映射
        all_code_name_map = {**self.code_name_map_sh, **self.code_name_map_sz}
        with tqdm(total=len(all_code_name_map), desc="获取股票数据", colour="#00ff00") as pbar:
            for stock_code, stock_name in all_code_name_map.items():
                if stock_code in self.all_stocks_data:
                    latest_date = self.all_stocks_data[stock_code]['date'].max()
                    if latest_date == self.today:
                        # 释放self.all_stocks_data[stock_code]的内存
                        del self.all_stocks_data[stock_code]
                        pbar.set_postfix_str(f"股票代码 {stock_code} 的前复权日线数据已是最新，无需更新。")
                        pbar.update(1)
                        continue
                    else:
                        pbar.set_postfix_str(f"股票代码 {stock_code} 历史数据已从本地加载，正在获取最新数据...")
                        start_date = (pd.to_datetime(latest_date) + pd.Timedelta(days=1)).strftime("%Y%m%d")
                        self.fetch_and_update_source_data(stock_code, pbar, start_date)
                        del self.all_stocks_data[stock_code]
                        pbar.update(1)
                else:
                    pbar.set_postfix_str(f"正在获取股票代码：{stock_code}，名称：{stock_name} 的日线数据...")
                    self.fetch_and_update_source_data(stock_code, pbar)
                    del self.all_stocks_data[stock_code]
                pbar.set_postfix_str(f"股票代码 {stock_code} 的前复权日线数据获取完成。")
                pbar.update(1)
        print("所有股票前复权日线数据获取完成。")

    def fetch_and_update_source_data(self, stock_code, pbar, start_date="19910101"):
        """
        获取单支股票的价格数据，计算其 KDJ 指标，更新内存中的数据并保存到 CSV 文件。

        :param stock_code: 股票代码
        :param pbar: 进度条对象，用于显示进度信息
        :param start_date: 股票数据获取的起始日期，默认为19910101
        """
        exchange_prefix = "sh" if stock_code in self.code_name_map_sh else "sz"
        df = self.fetch_price_data(exchange_prefix + stock_code, start_date=start_date)
        if (df is None) and (datetime.now().time() > datetime.strptime("15:00", "%H:%M").time()):
            pbar.set_postfix_str(f"股票代码 {stock_code} 不存在于数据集中。")
            return
        # 合并最新数据和历史数据
        if stock_code in self.all_stocks_data:
            combined_df = pd.concat([self.all_stocks_data[stock_code], df], ignore_index=True)
        else:
            combined_df = df
        # 更新内存中的数据
        self.all_stocks_data[stock_code] = combined_df
        # 保存数据到 CSV 文件
        self.save_single_source_data_to_csv(stock_code, self.all_stocks_data[stock_code])
        pbar.set_postfix_str(f"股票代码 {stock_code} 的前复权日线数据更新完成。")

    @staticmethod
    def fetch_price_data(stock_code, start_date, end_date=datetime.today().strftime("%Y%m%d")):
        """
        获取单支股票前复权日线数据。
        :param stock_code: 股票代码
        :param start_date: 开始日期
        :param end_date: 结束日期，默认为当前日期
        :return: 包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        df = ak.stock_zh_a_daily(symbol=stock_code,
                                 start_date=start_date,
                                 end_date=end_date,
                                 adjust="qfq")
        return df[["date", "open", "high", "low", "close", "volume", "amount", "turnover"]] if not df.empty else None

    def get_source_data(self, stock_code):
        """
        获取单支股票的前复权日线数据。
        :param stock_code: 股票代码
        :return: 包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        if stock_code not in self.all_stocks_data:
            print(f"股票代码 {stock_code} 不存在于数据集中。")
            return None
        return self.all_stocks_data.get(stock_code)

    def get_all_stocks_data(self):
        """
        获取所有股票的前复权日线数据。
        :return: key=股票代码，value=包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        return self.all_stocks_data

    def save_single_source_data_to_csv(self, code, df):
        """
        将单支股票数据保存到 CSV 文件。
        """
        if not os.path.exists('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/source_data'):
            os.makedirs('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/source_data')
        df.to_csv(f'/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/source_data/{code}.csv', index=False)

    def load_source_data_from_csv(self):
        """
        从 CSV 文件加载所有股票数据。
        """
        source_data_dir = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/data/source_data'
        if os.path.exists(source_data_dir):
            csv_files = [file for file in os.listdir(source_data_dir) if file.endswith('.csv')]
            with tqdm(total=len(csv_files), desc="加载本地历史股票数据", colour="#00ff00") as pbar:
                for file in csv_files:
                    code = file.replace('.csv', '')
                    self.all_stocks_data[code] = pd.read_csv(f'{source_data_dir}/{file}')
                    pbar.update(1)
                        


if __name__ == "__main__":
    # 初始化，获取所有个股的前复权日线数据
    monitor = StockPriceMonitor()

