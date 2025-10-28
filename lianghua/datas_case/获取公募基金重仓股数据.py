import akshare as ak



def get_fund_hold_stock_df():
    # 获取公募基金重仓股数据
    fund_hold_stock_df = ak.stock_institute_hold("20244")
    # 保存数据到 csv 文件
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/公募基金重仓股数据.csv'
    fund_hold_stock_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"公募基金重仓股数据已保存到 {file_path}")


if __name__ == "__main__":
    get_fund_hold_stock_df()    