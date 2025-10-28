import os
import base64
import requests
import openpyxl
from openpyxl import Workbook
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def process_image(filename, input_dir, ws):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        file_path = os.path.join(input_dir, filename)
        
        # 读取图片并转换为base64
        with open(file_path, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # 调用API
        api_url = "http://35.46.5.84:18000/check_accident"
        payload = {"image": img_base64}
        
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 根据文件夹确定图片类型
            folder_name = os.path.basename(input_dir)
            img_type = "正样本" if folder_name == "right_img" else "负样本"
            
            # 准备Excel行数据
            row_data = [
                img_type,
                "是" if result.get("accident", False) else "否",
                f"时间: {result.get('time', '')}, 地址: {result.get('address', '')}, 描述: {result.get('description', '')}",
                filename,
                folder_name
            ]
            
            return row_data
            
        except Exception as e:
            print(f"处理图片 {filename} 时出错: {str(e)}")
            return None


def process_images_to_excel(input_dirs, output_file):
    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    
    # 设置表头
    headers = ['样本类型', '是否识别成功', '识别结果', '图片名称', '图片来自的文件夹名称']
    ws.append(headers)
    
    with ThreadPoolExecutor() as executor:
        futures = []
        # 计算总图片数量
        total_images = sum([len([f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) 
                          for d in input_dirs])
        
        # 初始化进度条
        pbar = tqdm(total=total_images, desc="处理图片", unit="张")
        
        for input_dir in input_dirs:
            for filename in os.listdir(input_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    futures.append(executor.submit(process_image, filename, input_dir, ws))
        
        for future in futures:
            row_data = future.result()
            if row_data:
                ws.append(row_data)
            pbar.update(1)
        
        pbar.close()
    
    # 保存Excel文件
    wb.save(output_file)
    print(f"结果已保存到 {output_file}")

if __name__ == "__main__":
    # 示例用法
    input_directories = [
        "/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty/left_img",
        "/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty/right_img"
    ]
    output_excel = "/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty/res.xlsx"
    
    process_images_to_excel(input_directories, output_excel)