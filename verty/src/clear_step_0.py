import os

def clear_files():
    # 清理旧文件
    res_file = os.path.join("/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty", "res.xlsx")
    if os.path.exists(res_file):
        os.remove(res_file)
        
    # 清理图片文件夹
    for img_dir in ["left_img", "right_img"]:
        img_path = os.path.join("/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty", img_dir)
        if os.path.exists(img_path):
            for filename in os.listdir(img_path):
                if filename.endswith(".jpg"):
                    os.remove(os.path.join(img_path, filename))

if __name__ == "__main__":
    clear_files()