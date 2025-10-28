#!/bin/bash
# 离线部署Keepalived Exporter的Docker容器脚本
# 作者：Linux运维智录
# 日期：2025-02-27

# 配置参数（按需修改）
EXPORTER_PORT="19400"                  # Exporter监听端口
KEEPALIVED_PID_PATH="/var/run/keepalived.pid"  # Keepalived PID路径
DOCKER_NETWORK="keepalived-monitor"   # Docker网络名称
CONTAINER_NAME="keepalived-exporter"  # 容器名称

# 步骤1: 创建Docker专用网络（避免端口冲突）
docker network create ${DOCKER_NETWORK} > /dev/null 2>&1 || true

# 步骤2: 加载离线镜像（需提前下载）
docker load -i keepalived-exporter.tar > /dev/null 2>&1

# 步骤3: 启动容器（带健康检查）
docker run -d \
  --name ${CONTAINER_NAME} \
  --restart=always \
  --net=${DOCKER_NETWORK} \
  --cap-add=NET_ADMIN \
  -p ${EXPORTER_PORT}:9165 \
  -v ${KEEPALIVED_PID_PATH}:/app/keepalived/keepalived.pid \
  mehdy/keepalived-exporter:latest \
  -ka.pid-path /app/keepalived/keepalived.pid

# 步骤4: 验证容器状态
echo "容器状态检查:"
docker ps -f "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}"

# 步骤5: 生成Prometheus配置模板
cat <<EOF > prometheus-targets.yml
- targets: ['${HOST_IP}:${EXPORTER_PORT}']
  labels:
    service: 'keepalived'
    env: 'production'
EOF
echo "Prometheus配置已生成至：$(pwd)/prometheus-targets.yml"