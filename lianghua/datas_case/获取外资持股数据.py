import akshare as ak

def get_stock_foreign_holding():
    # 获取北向资金持股数据
    north_bound_holding = ak.stock_hsgt_hold_stock_em(market="北向")
    # 保存数据为 csv 文件
    file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/外资持股数据.csv'
    north_bound_holding.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f'北向资金持股数据已保存至 {file_path}')

if __name__ == '__main__':
    # 调用函数获取北向资金持股数据
    get_stock_foreign_holding()