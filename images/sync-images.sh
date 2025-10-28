#!/bin/bash
set -e

# docker push dockerhub.kubekey.htcf/htcf/REPOSITORY[:TAG]

# 配置Harbor参数
HARBOR_HOST="dockerhub.kubekey.htcf"
HARBOR_IP="35.46.5.92"
HARBOR_PROJECT="htcf"
HARBOR_USER="admin"
HARBOR_PASS="Harbor12345"
IMAGE_LIST_FILE="image-list.txt"

# 检查并配置hosts文件
if ! grep -q "$HARBOR_IP $HARBOR_HOST" /etc/hosts; then
    echo "[Config] 添加Harbor主机映射到/etc/hosts"
    echo "$HARBOR_IP $HARBOR_HOST" | sudo tee -a /etc/hosts > /dev/null
else
    echo "[Config] 检测到Harbor主机映射已存在"
fi

# 检查jq是否安装
if ! command -v jq &> /dev/null; then
    echo "[Warning] jq 未安装，正在尝试安装..."
    if ! sudo apt-get update || ! sudo apt-get install -y jq; then
        echo "[Error] 安装 jq 失败，请手动安装 jq"
        exit 1
    fi
    echo "[Success] jq 安装成功"
fi

# 登录Harbor
echo "[Deployment] 登录Harbor仓库 $HARBOR_HOST"
cat /etc/docker_passwd  | docker login "$HARBOR_HOST" -u "$HARBOR_USER" --password-stdin || {
    echo "[Error] 登录Harbor失败，请检查用户名和密码"
    exit 1
}


# 检查镜像列表文件是否存在
if [ ! -f "$IMAGE_LIST_FILE" ]; then
    echo "[Error] 镜像列表文件 $IMAGE_LIST_FILE 不存在"
    exit 1
fi

# 处理每个镜像
while IFS= read -r image_name; do
    # 跳过空行
    [ -z "$image_name" ] && continue
    
    echo "[Sync] 处理镜像: $image_name"
    
    # 检查本地是否存在镜像
    if docker image inspect "$image_name" &> /dev/null; then
        echo "[Sync] 镜像已存在于本地"
    else
        echo "[Sync] 本地不存在镜像，正在从网络拉取..."
        docker pull "$image_name" || {
            echo "[Error] 拉取镜像 $image_name 失败"
            continue
        }
    fi
    
    # 重新标记镜像为Harbor格式
    new_image="$HARBOR_HOST/$HARBOR_PROJECT/$(basename "${image_name%%:*}"):${image_name##*:}"
    echo "[Sync] 重新标记镜像: $new_image"
    docker tag "$image_name" "$new_image"
    
    # 推送镜像到Harbor
    echo "[Sync] 推送镜像到Harbor"
    docker push "$new_image" || echo "[Error] 推送镜像 $new_image 失败"
    
    echo "[Sync] 镜像 $image_name 处理完成"
done < "$IMAGE_LIST_FILE"

echo "[Sync] 所有镜像处理完成！"
