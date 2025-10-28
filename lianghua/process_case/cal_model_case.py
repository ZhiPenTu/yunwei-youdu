import pandas as pd

#  1.要求整理成表格， 表头为 “板块名称”， “涨幅”，“成交额(单位亿元)”， “主力净额”， “总流入”，并计算 "主力强度"，"散户强度"，
#  2.主力强度的计算公式为：(主力净额/成交额)*100
#  3.散户强度的计算公式为: (总流入-主力净额/成交额)*100
#  4.要求在表格中添加一个列，名为 “主力行为”，如果主力强度为 1～3标记建仓，-1～1为洗盘，大于等于 3为抢筹，小于等于-1 为出货
#  5.要求在表格中添加一个列，名为 “散户行为”，如果散户强度为 1～3标记建仓，-1～1为洗盘，大于等于 3为抢筹，小于等于-1 为出货
# 获取今日的日期 格式化为 2024-07-18
def get_today_date():
    import datetime
    today = datetime.date.today()
    # 判断当前时间是否是 15:00 之前 如果是 则获取前一天的日期
    if datetime.datetime.now().hour < 15:
        today = today - datetime.timedelta(days=1)
    return today.strftime('%Y-%m-%d')
 # 读取 CSV 文件 
def cal_res():
    # 表头为：序号,名称,今日涨跌幅,今日主力净流入-净额,今日主力净流入-净占比,今日超大单净流入-净额,今日超大单净流入-净占比,今日大单净流入-净额,今日大单净流入-净占比,今日中单净流入-净额,今日中单净流入-净占比,今日小单净流入-净额,今日小单净流入-净占比,今日主力净流入最大股
        
    # 读取两个CSV文件
    file1 = pd.read_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/同花顺-同花顺行业一览表.csv')
    file2 = pd.read_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/同花顺行业资金流.csv')
    file3 = pd.read_csv('/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/获取行业资金流数据.csv')
    # 重名命列名file1的 第二列的列名为“行业”，其他不变
    file1.rename(columns={file1.columns[1]: '行业'}, inplace=True)
    file3.rename(columns={file3.columns[1]: '行业'}, inplace=True)
    file2.drop(columns=[ '序号','公司家数','领涨股','领涨股-涨跌幅','当前价','行业-涨跌幅'], inplace=True)
    file1.drop(columns=['上涨家数', '下跌家数', '均价', '领涨股', '领涨股-最新价', '领涨股-涨跌幅'], inplace=True)
    file3.drop(columns=['序号','今日涨跌幅','今日主力净流入-净占比','今日超大单净流入-净额','今日超大单净流入-净占比','今日大单净流入-净额','今日大单净流入-净占比','今日中单净流入-净额','今日中单净流入-净占比','今日小单净流入-净额','今日小单净流入-净占比','今日主力净流入最大股'], inplace=True)
    # 按照第二列行业进行合并
    me1 = pd.merge(file1, file2, on=file1.columns[1], how='outer')
    merged_file = pd.merge(me1, file3, on=file1.columns[1], how='outer')
    # 删除主力净流入-净额列为空的行
    merged_file.dropna(subset=['今日主力净流入-净额'], inplace=True)
    merged_file['主力'] = divide_by_one_billion(merged_file['今日主力净流入-净额'])
    # 删除所有列值为空的行
    merged_file.dropna(subset=['序号'], inplace=True)

    # 重新按照第一列序号的大小进行排序
    merged_file.sort_values(by=file1.columns[0], inplace=True)
    # 序号重编号
    merged_file['序号'] = range(1, len(merged_file) + 1)

    # 创建新的表格
    new_df = pd.DataFrame(columns=['行业名称', '总流入', '成交额', '主力流入','散户流入','主力强度', '散户强度', '主力行为', '散户行为'])
    new_df['成交额'] = merged_file['总成交额']
    new_df['总流入'] = merged_file['净流入']
    new_df['主力流入'] = merged_file['主力']
    new_df['散户流入'] = round_to_two_decimal_places(merged_file['净流入'] - merged_file['主力'])
    new_df['主力强度'] =round_to_two_decimal_places(merged_file['主力'] / merged_file['总成交额'] * 100) 
    new_df['散户强度'] =round_to_two_decimal_places( (merged_file['净流入'] - merged_file['主力']) / merged_file['总成交额'] * 100) 
    new_df['行业名称'] = merged_file['行业']
    new_df['主力行为'] = new_df['主力强度'].apply(lambda x: '建仓' if x >= 1 and x <= 3 else '洗盘' if x >= -1 and x <= 1 else '抢筹' if x >= 3 else '出货')
    new_df['散户行为'] = new_df['散户强度'].apply(lambda x: '建仓' if x >= 1 and x <= 3 else '洗盘' if x >= -1 and x <= 1 else '抢筹' if x >= 3 else '出货')
    file_path =f"/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/板块强度/{get_today_date()}.csv"
    new_df.to_csv(file_path, index=False, encoding='utf-8-sig')

# 将数字除以一亿，把单位 元转换成亿元
def divide_by_one_billion(number):
    return round(number / 100000000,2)
# 保留两位小数
def round_to_two_decimal_places(number):
    return round(number, 2)


if __name__ == "__main__":
    cal_res()
