#!/bin/bash

# Docker 离线安装脚本 - 适用于 x86 架构服务器
# 版本: Docker 22.x + Docker Compose
# 作者: 运维有肚团队
# 日期: $(date +%Y-%m-%d)

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
DOCKER_VERSION="22.0.9"
DOCKER_COMPOSE_VERSION="2.20.3"
INSTALL_DIR="/docker-offline"
PACKAGE_DIR="${INSTALL_DIR}/packages"
SERVICE_DIR="/etc/systemd/system"

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
}

# 检查系统架构
check_architecture() {
    local arch=$(uname -m)
    log_info "检测到系统架构: $arch"
    
    case $arch in
        x86_64)
            ARCH="x86_64"
            ;;
        *)
            log_error "不支持的架构: $arch，此脚本仅支持 x86_64 架构"
            exit 1
            ;;
    esac
}

# 检查操作系统
check_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        log_info "检测到操作系统: $PRETTY_NAME"
    else
        log_error "无法检测操作系统版本"
        exit 1
    fi
}

# 检查离线安装包是否存在
check_packages() {
    log_info "检查离线安装包..."
    
    local required_files=(
        "docker-${DOCKER_VERSION}.tgz"
        "docker-compose-linux-${ARCH}-${DOCKER_COMPOSE_VERSION}"
        "containerd.io.rpm"
        "docker-ce.rpm"
        "docker-ce-cli.rpm"
    )
    
    if [[ ! -d "$PACKAGE_DIR" ]]; then
        log_error "安装包目录不存在: $PACKAGE_DIR"
        log_info "请先运行下载脚本 download-packages.sh 下载所需安装包"
        exit 1
    fi
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$PACKAGE_DIR/$file" ]]; then
            log_warning "缺少安装包: $file"
        else
            log_success "找到安装包: $file"
        fi
    done
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get install -y \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release \
                iptables \
                systemd
            ;;
        centos|rhel|rocky|almalinux)
            yum install -y \
                yum-utils \
                device-mapper-persistent-data \
                lvm2 \
                iptables \
                systemd
            ;;
        *)
            log_warning "未知操作系统，跳过依赖安装"
            ;;
    esac
    
    log_success "系统依赖安装完成"
}

# 停止并移除旧版本Docker
remove_old_docker() {
    log_info "检查并移除旧版本Docker..."
    
    # 停止Docker服务
    systemctl stop docker 2>/dev/null || true
    systemctl stop containerd 2>/dev/null || true
    
    case $OS in
        ubuntu|debian)
            apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            ;;
        centos|rhel|rocky|almalinux)
            yum remove -y docker \
                docker-client \
                docker-client-latest \
                docker-common \
                docker-latest \
                docker-latest-logrotate \
                docker-logrotate \
                docker-engine \
                containerd \
                runc 2>/dev/null || true
            ;;
    esac
    
    log_success "旧版本Docker清理完成"
}

# 安装Docker引擎
install_docker() {
    log_info "开始安装Docker引擎 v${DOCKER_VERSION}..."
    
    # 创建安装目录
    mkdir -p /usr/local/bin
    
    # 解压Docker二进制文件
    if [[ -f "$PACKAGE_DIR/docker-${DOCKER_VERSION}.tgz" ]]; then
        tar -xzf "$PACKAGE_DIR/docker-${DOCKER_VERSION}.tgz" -C /tmp/
        cp /tmp/docker/* /usr/local/bin/
        chmod +x /usr/local/bin/docker*
        log_success "Docker二进制文件安装完成"
    else
        log_error "Docker安装包不存在"
        exit 1
    fi
    
    # 创建docker用户组
    groupadd docker 2>/dev/null || true
    
    # 创建Docker配置目录
    mkdir -p /etc/docker
    
    # 创建Docker daemon配置文件
    cat > /etc/docker/daemon.json << EOF
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF
    
    log_success "Docker配置文件创建完成"
}

# 创建Docker systemd服务文件
create_docker_service() {
    log_info "创建Docker systemd服务..."
    
    cat > ${SERVICE_DIR}/docker.service << EOF
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service containerd.service
Wants=network-online.target
Requires=docker.socket containerd.service

[Service]
Type=notify
ExecStart=/usr/local/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
ExecReload=/bin/kill -s HUP \$MAINPID
TimeoutSec=0
RestartSec=2
Restart=always
StartLimitBurst=3
StartLimitInterval=60s
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
TasksMax=infinity
Delegate=yes
KillMode=process
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
EOF
    
    cat > ${SERVICE_DIR}/docker.socket << EOF
[Unit]
Description=Docker Socket for the API

[Socket]
ListenStream=/var/run/docker.sock
SocketMode=0660
SocketUser=root
SocketGroup=docker

[Install]
WantedBy=sockets.target
EOF
    
    log_success "Docker systemd服务文件创建完成"
}

# 安装containerd
install_containerd() {
    log_info "安装containerd..."
    
    # 创建containerd配置目录
    mkdir -p /etc/containerd
    
    # 生成默认配置
    containerd config default > /etc/containerd/config.toml
    
    # 创建containerd systemd服务文件
    cat > ${SERVICE_DIR}/containerd.service << EOF
[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd
Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5
LimitNPROC=infinity
LimitCORE=infinity
LimitNOFILE=infinity
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "containerd安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose v${DOCKER_COMPOSE_VERSION}..."
    
    local compose_file="$PACKAGE_DIR/docker-compose-linux-${ARCH}-${DOCKER_COMPOSE_VERSION}"
    
    if [[ -f "$compose_file" ]]; then
        cp "$compose_file" /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        
        # 创建符号链接
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        
        log_success "Docker Compose安装完成"
    else
        log_error "Docker Compose安装包不存在: $compose_file"
        exit 1
    fi
}

# 启动Docker服务
start_docker_services() {
    log_info "启动Docker服务..."
    
    # 重新加载systemd配置
    systemctl daemon-reload
    
    # 启用并启动containerd
    systemctl enable containerd
    systemctl start containerd
    
    # 启用并启动Docker
    systemctl enable docker.socket
    systemctl enable docker.service
    systemctl start docker.socket
    systemctl start docker.service
    
    # 等待服务启动
    sleep 5
    
    log_success "Docker服务启动完成"
}

# 验证安装
verify_installation() {
    log_info "验证Docker安装..."
    
    # 检查Docker版本
    if docker --version; then
        log_success "Docker安装成功: $(docker --version)"
    else
        log_error "Docker安装失败"
        exit 1
    fi
    
    # 检查Docker Compose版本
    if docker-compose --version; then
        log_success "Docker Compose安装成功: $(docker-compose --version)"
    else
        log_error "Docker Compose安装失败"
        exit 1
    fi
    
    # 检查Docker服务状态
    if systemctl is-active --quiet docker; then
        log_success "Docker服务运行正常"
    else
        log_error "Docker服务未正常运行"
        exit 1
    fi
    
    # 运行测试容器
    log_info "运行测试容器..."
    if docker run --rm hello-world > /dev/null 2>&1; then
        log_success "Docker功能测试通过"
    else
        log_warning "Docker功能测试失败，可能需要手动检查"
    fi
}

# 显示安装后信息
show_post_install_info() {
    log_info "安装完成！以下是一些有用的信息："
    echo
    echo "Docker版本: $(docker --version)"
    echo "Docker Compose版本: $(docker-compose --version)"
    echo
    echo "常用命令:"
    echo "  查看Docker状态: systemctl status docker"
    echo "  重启Docker服务: systemctl restart docker"
    echo "  查看Docker信息: docker info"
    echo "  运行测试容器: docker run hello-world"
    echo
    echo "将用户添加到docker组（可选）:"
    echo "  usermod -aG docker <username>"
    echo "  注意：添加后需要重新登录才能生效"
    echo
    log_success "Docker离线安装完成！"
}

# 主函数
main() {
    log_info "开始Docker离线安装..."
    
    check_root
    check_architecture
    check_os
    check_packages
    
    install_dependencies
    remove_old_docker
    install_docker
    create_docker_service
    install_containerd
    install_docker_compose
    start_docker_services
    verify_installation
    show_post_install_info
    
    log_success "所有安装步骤完成！"
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"