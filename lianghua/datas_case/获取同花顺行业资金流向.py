
import akshare as ak


def get_stock_fund_flow_industry_df():
    """
    同花顺行业资金流
    get_stock_hot_up_em():
    """
    # 同花顺行业资金流
    stock_fund_flow_industry_df = ak.stock_fund_flow_industry(symbol="即时")
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/同花顺行业资金流.csv'
    stock_fund_flow_industry_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"同花顺行业资金流 {file_path}")
    

if __name__ == '__main__':
    get_stock_fund_flow_industry_df()