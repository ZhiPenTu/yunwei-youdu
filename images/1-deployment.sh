#!/bin/bash
set -e

# 配置Harbor参数
HARBOR_HOST="dockerhub.kubekey.local"
HARBOR_PROJECT="htcfproject"
HARBOR_USER="admin"
HARBOR_PASS="Harbor12345"
IMAGE_DIR="./offline-images"

# 检测 jq 是否安装
if ! command -v jq &> /dev/null; then
    echo "[Warning] jq 未安装，正在尝试安装..."
    # 尝试安装 xargs
    if ! sudo apt-get update || ! sudo apt-get install -y jq; then
        echo "[Error] 安装 jq 失败，请手动安装 jq"
        exit 1
    fi
    echo "[Success] jq 安装成功"
fi

# 登录Harbor
echo "[Deployment] 登录Harbor仓库 $HARBOR_HOST"
docker login "$HARBOR_HOST" -u "$HARBOR_USER" -p "$HARBOR_PASS"

# 加载并推送镜像
for tar_file in "$IMAGE_DIR"/*.tar; do
    echo "[Deployment] 加载镜像文件: $tar_file"
    docker load -i "$tar_file"
    
    original_image=$(tar xfO "$tar_file" manifest.json | jq -r '.[0].RepoTags[0]')
    new_image="$HARBOR_HOST/$HARBOR_PROJECT/$(basename "${original_image%%:*}"):${original_image##*:}"
    
    echo "[Deployment] 重新标记镜像: $new_image"
    docker tag "$original_image" "$new_image"
    
    echo "[Deployment] 推送镜像到Harbor"
    docker push "$new_image"
done

echo "[Deployment] 完成！"
