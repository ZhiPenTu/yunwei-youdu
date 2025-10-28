
import akshare as ak
import sys
import os
from utils.fileUtils import *
from config.index import *


FILE_NAME  = "两市股票飙升榜.csv"

def get_stock_hot_up_em():
    """
    股票数据-股票飙升榜-A股
    """
    # 股票数据-股票飙升榜-A股
    stock_hot_up_em_df = ak.stock_hot_up_em()
    file_path = CASE_CSV_FILE_PATH + FILE_NAME
    stock_hot_up_em_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"股票数据-两市股票飙升榜 {file_path}")
    name = get_current_filename()
    print(f"{name}1111")

if __name__ == '__main__':
    get_stock_hot_up_em()