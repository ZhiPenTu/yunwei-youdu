import akshare as ak


def get_stock_fund_flow_concept():
    """
    获取概念资金流数据
    :return: 概念资金流数据
    """
    stock_fund_flow_concept_df = ak.stock_fund_flow_concept(symbol="即时")
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/概念资金流数据.csv'
    stock_fund_flow_concept_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"概念资金流数据 {file_path}")

if __name__ == '__main__':
    get_stock_fund_flow_concept()