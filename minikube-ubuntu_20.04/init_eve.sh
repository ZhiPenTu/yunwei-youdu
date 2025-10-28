#!/bin/bash
set -e

# 配置参数
DOCKER_VERSION="20.10.9"
CRI_VERSION="1.0.0"
INSTALL_DIR="/usr/local/bin"
DOCKER_DATA="/var/lib/docker"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# 检查系统架构
check_architecture() {
  local arch=$(uname -m)
  case $arch in
    x86_64) echo "amd64" ;;
    *) 
      echo -e "${RED}错误：不支持的架构 $arch${NC}"
      exit 1
      ;;
  esac
}

# 安装Docker
install_docker() {
  local arch=$(check_architecture)
  
  echo -e "${YELLOW}开始安装Docker...${NC}"
  
  # 解压Docker二进制包
  if [ ! -f "docker-${DOCKER_VERSION}_${arch}.tgz" ]; then
    echo -e "${RED}错误：未找到Docker安装包${NC}"
    exit 1
  fi
  
  tar -xzvf "docker-${DOCKER_VERSION}_${arch}.tgz"
  sudo cp docker/* "$INSTALL_DIR"
  
  # 创建systemd服务
  sudo tee /etc/systemd/system/docker.service > /dev/null <<EOF
[Unit]
Description=Docker Application Container Engine
After=network.target

[Service]
Type=notify
ExecStart=$INSTALL_DIR/dockerd \
  --data-root=$DOCKER_DATA \
  --iptables=false \
  --selinux-enabled=false
ExecReload=/bin/kill -s HUP \$MAINPID
TimeoutStartSec=0
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
  
  # 启动服务
  sudo systemctl daemon-reload
  sudo systemctl enable docker
  sudo systemctl start docker
  
  echo -e "${GREEN}Docker安装完成！${NC}"
}

# 安装Docker CRI
install_cri() {
  echo -e "${YELLOW}开始安装Docker CRI插件...${NC}"
  
  if [ ! -f "cri-dockerd-${CRI_VERSION}.amd64.tgz" ]; then
    echo -e "${RED}错误：未找到CRI插件安装包${NC}"
    exit 1
  fi
  
  tar -xzvf "cri-dockerd-${CRI_VERSION}.amd64.tgz"
  sudo cp cri-dockerd "$INSTALL_DIR"
  
  # 创建systemd服务
  sudo tee /etc/systemd/system/cri-docker.service > /dev/null <<EOF
[Unit]
Description=CRI Interface for Docker Application Container Engine
Documentation=https://docs.mirantis.com
After=network.target
After=docker.service

[Service]
Type=notify
ExecStart=$INSTALL_DIR/cri-dockerd --container-runtime-endpoint unix:///var/run/docker.sock
ExecReload=/bin/kill -s HUP \$MAINPID
TimeoutSec=0
RestartSec=2
Restart=always

[Install]
WantedBy=multi-user.target
EOF
  
  # 启动服务
  sudo systemctl daemon-reload
  sudo systemctl enable cri-docker
  sudo systemctl start cri-docker
  
  echo -e "${GREEN}Docker CRI插件安装完成！${NC}"
}

# 主流程
main() {
  check_architecture
  install_docker
  install_cri
  
  echo -e "${GREEN}安装完成！请运行以下命令验证：${NC}"
  echo "docker --version"
  echo "systemctl status cri-docker"
}

main "$@"