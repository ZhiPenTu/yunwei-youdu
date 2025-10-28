import akshare as ak
import pandas as pd
    
def get_data():
    stock_info_sh = ak.stock_info_sh_name_code()  # 上海交易所
    stock_info_sz = ak.stock_info_sz_name_code()  # 深圳交易所
    stock_info_sh.to_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/上海交易所.csv', index=False, encoding='utf-8-sig')
    stock_info_sz.to_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/深圳交易所.csv', index=False, encoding='utf-8-sig')
    print(f"上海交易所已保存到 /Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/上海交易所.csv")
    print(f"深圳交易所已保存到 /Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/深圳交易所.csv")
if __name__ == '__main__':
    get_data()