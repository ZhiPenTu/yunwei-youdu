import os
import csv
from datetime import datetime
import os
import subprocess
import sys


class UpateData:
    def __init__(self):
        self.data_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data'
        self.csv_header = ['文件名', '最后更新日期']
        self.run_all_py_files_in_folder("/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/datas_case")
    def get_file_info(self):
        file_info_list = []
        # 遍历 akshre_data 目录下的所有文件
        for root, dirs, files in os.walk(self.data_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 获取文件的最后修改时间
                last_modified_time = os.path.getmtime(file_path)
                # 将时间戳转换为日期时间格式
                last_modified_date = datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
                file_info_list.append([file, last_modified_date])
        return file_info_list

    def save_file_info(self, file_info_list, csv_file_path):
        # 创建并写入 csv 文件
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # 写入表头
            writer.writerow(self.csv_header)
            # 写入文件信息
            writer.writerows(file_info_list)
        print(f"文件信息已保存到 {csv_file_path}")
    

    def run_all_py_files_in_folder(sefle, folder_path):
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"错误: 文件夹 '{folder_path}' 不存在")
            return
        
        # 获取所有 .py 文件
        py_files = [f for f in os.listdir(folder_path) 
                if f.endswith('.py') and os.path.isfile(os.path.join(folder_path, f))]
        
        if not py_files:
            print(f"在 '{folder_path}' 中未找到 .py 文件")
            return
        
        # 按文件名排序后执行
        py_files.sort()
        for py_file in py_files:
            file_path = os.path.join(folder_path, py_file)
            print(f"\n{'=' * 50}")
            print(f"正在执行: {py_file}")
            print(f"{'=' * 50}")
            
            try:
                # 在独立进程中运行
                subprocess.run([sys.executable, file_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"执行失败 ({py_file}): 返回码 {e.returncode}")
            except Exception as e:
                print(f"发生未知错误 ({py_file}): {str(e)}")

    
    

           
if __name__ == '__main__':
    update_data = UpateData()
    file_info_list = update_data.get_file_info()
    csv_file_path = '/Users/tuzhipeng/Desktop/航天长峰/运维有肚/lianghua/akshare_data/akshre_data_file_info.csv'
    update_data.save_file_info(file_info_list, csv_file_path)
