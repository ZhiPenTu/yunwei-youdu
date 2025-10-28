import akshare as ak

def get_stock_basic_info():
    # 获取全市场股票基本信息
    # 使用 akshare 获取全市场股票基本信息 stock_info = ak.stock_zh_a_spot_em()
    stock_basic_info = ak.stock_zh_a_spot_em()
    # 保存到 csv 文件
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/两市股票基本信息.csv'
    stock_basic_info.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"两市股票基本信息已保存到 {file_path}")

if __name__ == "__main__":
    get_stock_basic_info()    