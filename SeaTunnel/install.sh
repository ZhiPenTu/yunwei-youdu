#!/bin/bash
set -e

# 配置参数
SEATUNNEL_IMAGE="apache/seatunnel:latest"
OFFLINE_PACKAGE="./seatunnel-offline.tar.gz"
CONTAINER_NAME="seatunnel-server"
DATA_DIR="/data/seatunnel"
CONFIG_DIR="$(pwd)/config"
PORT="8081"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# 检查Docker状态
check_docker() {
  if ! command -v docker &>/dev/null; then
    echo -e "${RED}错误：Docker 未安装！${NC}"
    exit 1
  fi

  if ! systemctl is-active docker &>/dev/null; then
    echo -e "${YELLOW}正在启动Docker服务...${NC}"
    sudo systemctl start docker || {
      echo -e "${RED}Docker启动失败${NC}"
      exit 1
    }
  fi
}

# 加载镜像
load_image() {
  if [ ! -f "$OFFLINE_PACKAGE" ]; then
    echo -e "${RED}错误：未找到离线安装包 $OFFLINE_PACKAGE${NC}"
    exit 1
  fi
  echo -e "${GREEN}正在加载SeaTunnel镜像...${NC}"
  docker load -i "$OFFLINE_PACKAGE" || {
    echo -e "${RED}镜像加载失败！${NC}"
    exit 1
  }
}

# 准备存储目录
prepare_dirs() {
  echo -e "${GREEN}创建持久化目录...${NC}"
  sudo mkdir -p "$DATA_DIR" "$CONFIG_DIR"
  sudo chmod -R 777 "$DATA_DIR" "$CONFIG_DIR"
}

# 运行容器
run_container() {
  echo -e "${GREEN}启动SeaTunnel容器...${NC}"
  docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$PORT:8080" \
    -v "$CONFIG_DIR:/seatunnel/config" \
    -v "$DATA_DIR:/seatunnel/data" \
    "$SEATUNNEL_IMAGE" || {
    echo -e "${RED}容器启动失败！${NC}"
    exit 1
  }
}

# 验证部署
verify_deployment() {
  echo -e "${GREEN}验证部署...${NC}"
  sleep 5
  
  if ! docker ps --filter "name=$CONTAINER_NAME" --format '{{.Status}}' | grep -q "Up"; then
    echo -e "${RED}容器未正常运行，查看日志：docker logs $CONTAINER_NAME${NC}"
    exit 1
  fi

  echo -e "${GREEN}部署成功！访问地址：http://localhost:$PORT${NC}"
}

main() {
  check_docker
  load_image
  prepare_dirs
  run_container
  verify_deployment
}

main