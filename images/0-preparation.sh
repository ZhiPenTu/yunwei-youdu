#!/bin/bash
set -e

# 配置参数
IMAGES=("nginx:latest" "redis:alpine")  # 需要下载的镜像列表
OUTPUT_DIR="./offline-images"           # 镜像保存目录

echo "[Preparation] 创建输出目录 $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# 下载镜像并保存为tar文件
for image in "${IMAGES[@]}"; do
    echo "[Preparation] 下载镜像: $image"
    docker pull "$image"
    
    tar_file="${image//:/_}.tar"  # 替换冒号为下划线
    tar_path="$OUTPUT_DIR/$tar_file"
    
    echo "[Preparation] 保存镜像到 $tar_path"
    docker save -o "$tar_path" "$image"
done

echo "[Preparation] 完成！镜像已保存到 $OUTPUT_DIR"


