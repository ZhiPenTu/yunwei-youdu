#!/bin/bash
set -e
mv /tmp/cadvisor.tar ./
# 配置参数（按需修改）
CADVISOR_IMAGE_TAR="./cadvisor.tar"      # 预下载的 cAdvisor 镜像路径
CADVISOR_VERSION="v0.47.2"               # 需与离线镜像版本一致
CADVISOR_PORT="19300"                    # cAdvisor 暴露端口
DOCKER_SERVICE_NAME="cadvisor"           # 容器名称

# 颜色定义（用于输出提示）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 恢复默认

# 检查 Docker 是否安装
check_docker() {
  if ! command -v docker &>/dev/null; then
    echo -e "${RED}错误：Docker 未安装，请离线安装 Docker 后再执行本脚本！${NC}"
    exit 1
  fi
}

# 检查 Docker 服务状态
check_docker_service() {
  if ! systemctl is-active docker &>/dev/null; then
    echo -e "${YELLOW}警告：Docker 服务未运行，正在尝试启动...${NC}"
    sudo systemctl start docker || {
      echo -e "${RED}错误：Docker 服务启动失败，请手动处理！${NC}"
      exit 1
    }
    echo -e "${GREEN}Docker 服务已启动${NC}"
  fi
}

# 加载离线镜像
load_image() {
  if [ ! -f "$CADVISOR_IMAGE_TAR" ]; then
    echo -e "${RED}错误：未找到 cAdvisor 镜像文件 $CADVISOR_IMAGE_TAR${NC}"
    echo -e "${YELLOW}请从有网络的环境执行以下命令导出镜像："
    echo -e "docker pull gcr.io/cadvisor/cadvisor:$CADVISOR_VERSION"
    echo -e "docker save -o cadvisor.tar gcr.io/cadvisor/cadvisor:$CADVISOR_VERSION${NC}"
    exit 1
  fi

  echo -e "${GREEN}正在加载 cAdvisor 镜像...${NC}"
  sudo docker load -i "$CADVISOR_IMAGE_TAR" || {
    echo -e "${RED}错误：镜像加载失败！${NC}"
    exit 1
  }
}

# 检查端口冲突
check_port() {
  if ss -tuln | grep -q ":$CADVISOR_PORT "; then
    echo -e "${RED}错误：端口 $CADVISOR_PORT 已被占用，请释放端口或修改脚本中的 CADVISOR_PORT 变量${NC}"
    exit 1
  fi
}

# 运行 cAdvisor 容器
# run_cadvisor() {
#   echo -e "${GREEN}正在启动 cAdvisor 容器...${NC}"
#   sudo docker run -d \
#     --name="$DOCKER_SERVICE_NAME" \
#     --volume=/:/rootfs:ro \
#     --volume=/var/run:/var/run:ro \
#     --volume=/sys:/sys:ro \
#     --volume=/var/lib/docker/:/var/lib/docker:ro \
#     --volume=/dev/disk/:/dev/disk:ro \
#     --publish="$CADVISOR_PORT:8080" \
#     --privileged \
#     --device=/dev/kmsg \
#     "gcr.io/cadvisor/cadvisor:$CADVISOR_VERSION" || {
#     echo -e "${RED}错误：容器启动失败！${NC}"
#     exit 1
#   }
# }

 
run_cadvisor() {
  echo -e "${GREEN}正在启动 cAdvisor 容器...${NC}"
  sudo docker run \
  --name=cadvisor \
  --detach=true \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:rw \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker:/var/lib/docker:ro \
  --volume=/dev/kmsg:/dev/kmsg:ro \
  --publish=19300:8080 \
  --privileged \
  --device=/dev/kmsg \
  "gcr.io/cadvisor/cadvisor:$CADVISOR_VERSION" || {
    echo -e "${RED}错误：容器启动失败！${NC}"
    exit 1
  }
}

# 验证部署
verify_deployment() {
  echo -e "${GREEN}正在验证部署...${NC}"
  sleep 5 # 等待容器初始化

  # 检查容器状态
  if ! sudo docker ps --filter "name=$DOCKER_SERVICE_NAME" --format '{{.Status}}' | grep -q "Up"; then
    echo -e "${RED}错误：容器未正常运行，查看日志：docker logs $DOCKER_SERVICE_NAME${NC}"
    exit 1
  fi

  # 检查指标接口
  if ! curl -s "http://localhost:$CADVISOR_PORT/metrics" | grep -q "cadvisor_version_info"; then
    echo -e "${RED}错误：cAdvisor 指标接口不可访问！${NC}"
    exit 1
  fi

  echo -e "${GREEN}部署成功！cAdvisor 运行在端口 $CADVISOR_PORT${NC}"
  echo -e "访问指标接口：curl http://localhost:$CADVISOR_PORT/metrics"
}

# 主函数
main() {
  check_docker
  check_docker_service
  load_image
  check_port
  run_cadvisor
  verify_deployment
}

# 执行主函数
main

