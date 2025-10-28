import akshare as ak


def stock_board_industry_summary_ths():
    df = ak.stock_board_industry_summary_ths()
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/同花顺-同花顺行业一览表.csv'
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"同花顺-同花顺行业一览表 {file_path}")

if __name__ == '__main__':
    stock_board_industry_summary_ths()