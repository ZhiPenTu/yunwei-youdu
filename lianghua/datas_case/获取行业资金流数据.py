import akshare as ak

def get_stock_sector_fund_flow_rank():
    """
    获取行业资金流数据
    :return: 行业资金流数据
    """
    df = ak.stock_sector_fund_flow_rank()
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/获取行业资金流数据.csv'
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"获取行业资金流数据已保存到 {file_path}")

if __name__ == "__main__":
    get_stock_sector_fund_flow_rank()