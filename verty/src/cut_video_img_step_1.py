import cv2
import os
from concurrent.futures import ThreadPoolExecutor

def extract_frames(video_path, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取视频文件名（不带扩展名）
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # 打开视频文件并处理错误
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"无法打开视频文件: {video_path}")
                
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # 计算9秒处的帧号（从0开始）
            start_frame = int(9 * fps)
            
            # 设置视频读取位置到9秒处
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            # 提取3帧，每秒1帧
            for i in range(10):
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # 保存帧为图片
                output_path = os.path.join(output_dir, f"{video_name}_{i+1:02d}.jpg")
                cv2.imwrite(output_path, frame)
                
                # 跳到下一秒的帧
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame + (i+1)*int(fps))
            
            cap.release()
            break
            
        except Exception as e:
            print(f"尝试 {attempt + 1}/{max_retries} 处理视频 {video_path} 时出错: {str(e)}")
            if cap and cap.isOpened():
                cap.release()
            
            if attempt == max_retries - 1:
                print(f"无法处理视频 {video_path}，已达到最大重试次数")
                raise

if __name__ == "__main__":
    # 定义输入输出文件夹映射
    folder_mapping = {
        "left_video": "left_img",
        "right_video": "right_img"
    }
    
    # 使用线程池并行处理
    with ThreadPoolExecutor() as executor:
        for video_subdir, img_subdir in folder_mapping.items():
            video_folder = os.path.join("/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty/video", video_subdir)
            output_folder = os.path.join("/Users/tuzhipeng/Desktop/航天长峰/运维有肚/verty", img_subdir)
            
            # 处理文件夹中的所有mp4文件
            for filename in os.listdir(video_folder):
                if filename.endswith(".mp4"):
                    video_path = os.path.join(video_folder, filename)
                    executor.submit(extract_frames, video_path, output_folder)