#!/bin/bash

# Docker 离线安装包下载脚本
# 用于在联网环境下下载Docker和Docker Compose安装包
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
CONTAINERD_VERSION="1.6.24"
RUNC_VERSION="1.1.9"
INSTALL_DIR="./docker-offline"
PACKAGE_DIR="${INSTALL_DIR}/packages"
ARCH="x86_64"

# Docker官方下载地址
DOCKER_DOWNLOAD_URL="https://download.docker.com/linux/static/stable/x86_64"
DOCKER_COMPOSE_URL="https://github.com/docker/compose/releases/download"
CONTAINERD_URL="https://github.com/containerd/containerd/releases/download"
RUNC_URL="https://github.com/opencontainers/runc/releases/download"

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    
    if ping -c 1 github.com > /dev/null 2>&1; then
        log_success "网络连接正常"
    else
        log_error "网络连接失败，请检查网络设置"
        exit 1
    fi
}

# 检查必要工具
check_tools() {
    log_info "检查必要工具..."
    
    local tools=("curl" "wget" "tar")
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" > /dev/null 2>&1; then
            log_success "找到工具: $tool"
        else
            log_error "缺少必要工具: $tool"
            log_info "请安装: sudo apt-get install $tool 或 sudo yum install $tool"
            exit 1
        fi
    done
}

# 创建下载目录
create_directories() {
    log_info "创建下载目录..."
    
    mkdir -p "$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR/rpm"
    mkdir -p "$PACKAGE_DIR/deb"
    
    log_success "目录创建完成: $PACKAGE_DIR"
}

# 下载Docker二进制文件
download_docker_binary() {
    log_info "下载Docker二进制文件 v${DOCKER_VERSION}..."
    
    local docker_file="docker-${DOCKER_VERSION}.tgz"
    local download_url="${DOCKER_DOWNLOAD_URL}/${docker_file}"
    
    if [[ -f "$PACKAGE_DIR/$docker_file" ]]; then
        log_warning "文件已存在: $docker_file"
        return 0
    fi
    
    log_info "下载地址: $download_url"
    
    if curl -L -o "$PACKAGE_DIR/$docker_file" "$download_url"; then
        log_success "Docker二进制文件下载完成: $docker_file"
    else
        log_error "Docker二进制文件下载失败"
        exit 1
    fi
}

# 下载containerd
download_containerd() {
    log_info "下载containerd v${CONTAINERD_VERSION}..."
    
    local containerd_file="containerd-${CONTAINERD_VERSION}-linux-amd64.tar.gz"
    local download_url="${CONTAINERD_URL}/v${CONTAINERD_VERSION}/${containerd_file}"
    
    if [[ -f "$PACKAGE_DIR/$containerd_file" ]]; then
        log_warning "文件已存在: $containerd_file"
        return 0
    fi
    
    log_info "下载地址: $download_url"
    
    if curl -L -o "$PACKAGE_DIR/$containerd_file" "$download_url"; then
        log_success "containerd下载完成: $containerd_file"
    else
        log_error "containerd下载失败"
        exit 1
    fi
}

# 下载runc
download_runc() {
    log_info "下载runc v${RUNC_VERSION}..."
    
    local runc_file="runc.amd64"
    local download_url="${RUNC_URL}/v${RUNC_VERSION}/${runc_file}"
    
    if [[ -f "$PACKAGE_DIR/$runc_file" ]]; then
        log_warning "文件已存在: $runc_file"
        return 0
    fi
    
    log_info "下载地址: $download_url"
    
    if curl -L -o "$PACKAGE_DIR/$runc_file" "$download_url"; then
        chmod +x "$PACKAGE_DIR/$runc_file"
        log_success "runc下载完成: $runc_file"
    else
        log_error "runc下载失败"
        exit 1
    fi
}

# 下载Docker Compose
download_docker_compose() {
    log_info "下载Docker Compose v${DOCKER_COMPOSE_VERSION}..."
    
    local compose_file="docker-compose-linux-${ARCH}-${DOCKER_COMPOSE_VERSION}"
    local download_url="${DOCKER_COMPOSE_URL}/v${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64"
    
    if [[ -f "$PACKAGE_DIR/$compose_file" ]]; then
        log_warning "文件已存在: $compose_file"
        return 0
    fi
    
    log_info "下载地址: $download_url"
    
    if curl -L -o "$PACKAGE_DIR/$compose_file" "$download_url"; then
        chmod +x "$PACKAGE_DIR/$compose_file"
        log_success "Docker Compose下载完成: $compose_file"
    else
        log_error "Docker Compose下载失败"
        exit 1
    fi
}

# 下载CentOS/RHEL RPM包
download_centos_packages() {
    log_info "下载CentOS/RHEL RPM包..."
    
    local base_url="https://download.docker.com/linux/centos/7/x86_64/stable/Packages"
    
    # 获取最新的包列表（这里使用固定版本，实际使用时可能需要更新）
    local packages=(
        "containerd.io-1.6.24-3.1.el7.x86_64.rpm"
        "docker-ce-22.0.9-1.el7.x86_64.rpm"
        "docker-ce-cli-22.0.9-1.el7.x86_64.rpm"
        "docker-buildx-plugin-0.11.2-1.el7.x86_64.rpm"
        "docker-compose-plugin-2.20.3-1.el7.x86_64.rpm"
    )
    
    for package in "${packages[@]}"; do
        if [[ -f "$PACKAGE_DIR/rpm/$package" ]]; then
            log_warning "文件已存在: $package"
            continue
        fi
        
        log_info "下载: $package"
        
        if curl -L -o "$PACKAGE_DIR/rpm/$package" "$base_url/$package"; then
            log_success "下载完成: $package"
        else
            log_warning "下载失败: $package (可能版本不存在)"
        fi
    done
}

# 下载Ubuntu/Debian DEB包
download_ubuntu_packages() {
    log_info "下载Ubuntu/Debian DEB包..."
    
    local base_url="https://download.docker.com/linux/ubuntu/dists/focal/pool/stable/amd64"
    
    # 获取最新的包列表（这里使用固定版本，实际使用时可能需要更新）
    local packages=(
        "containerd.io_1.6.24-1_amd64.deb"
        "docker-ce_5%3a22.0.9-1~ubuntu.20.04~focal_amd64.deb"
        "docker-ce-cli_5%3a22.0.9-1~ubuntu.20.04~focal_amd64.deb"
        "docker-buildx-plugin_0.11.2-1~ubuntu.20.04~focal_amd64.deb"
        "docker-compose-plugin_2.20.3-1~ubuntu.20.04~focal_amd64.deb"
    )
    
    for package in "${packages[@]}"; do
        local filename=$(echo "$package" | sed 's/%3a/:/g')
        
        if [[ -f "$PACKAGE_DIR/deb/$filename" ]]; then
            log_warning "文件已存在: $filename"
            continue
        fi
        
        log_info "下载: $filename"
        
        if curl -L -o "$PACKAGE_DIR/deb/$filename" "$base_url/$package"; then
            log_success "下载完成: $filename"
        else
            log_warning "下载失败: $filename (可能版本不存在)"
        fi
    done
}

# 创建安装说明文件
create_readme() {
    log_info "创建安装说明文件..."
    
    cat > "$PACKAGE_DIR/README.md" << 'EOF'
# Docker 离线安装包

本目录包含Docker和Docker Compose的离线安装包，适用于x86_64架构的Linux服务器。

## 目录结构

```
packages/
├── docker-22.0.9.tgz                    # Docker二进制文件
├── containerd-1.6.24-linux-amd64.tar.gz # containerd运行时
├── runc.amd64                            # runc运行时
├── docker-compose-linux-x86_64-2.20.3   # Docker Compose二进制文件
├── rpm/                                  # CentOS/RHEL RPM包
│   ├── containerd.io-*.rpm
│   ├── docker-ce-*.rpm
│   ├── docker-ce-cli-*.rpm
│   ├── docker-buildx-plugin-*.rpm
│   └── docker-compose-plugin-*.rpm
├── deb/                                  # Ubuntu/Debian DEB包
│   ├── containerd.io_*.deb
│   ├── docker-ce_*.deb
│   ├── docker-ce-cli_*.deb
│   ├── docker-buildx-plugin_*.deb
│   └── docker-compose-plugin_*.deb
└── README.md                             # 本文件
```

## 使用方法

1. 将整个packages目录复制到目标服务器的 `/opt/docker-offline/` 目录下
2. 运行离线安装脚本：
   ```bash
   sudo bash install.sh
   ```

## 支持的操作系统

- CentOS 7/8
- RHEL 7/8
- Rocky Linux 8/9
- AlmaLinux 8/9
- Ubuntu 18.04/20.04/22.04
- Debian 10/11

## 版本信息

- Docker: 22.0.9
- Docker Compose: 2.20.3
- containerd: 1.6.24
- runc: 1.1.9

## 注意事项

1. 安装脚本需要root权限运行
2. 确保目标服务器架构为x86_64
3. 安装前会自动清理旧版本Docker
4. 安装完成后Docker服务会自动启动

EOF

    log_success "安装说明文件创建完成"
}

# 验证下载的文件
verify_downloads() {
    log_info "验证下载的文件..."
    
    local files=(
        "docker-${DOCKER_VERSION}.tgz"
        "containerd-${CONTAINERD_VERSION}-linux-amd64.tar.gz"
        "runc.amd64"
        "docker-compose-linux-${ARCH}-${DOCKER_COMPOSE_VERSION}"
    )
    
    local all_ok=true
    
    for file in "${files[@]}"; do
        if [[ -f "$PACKAGE_DIR/$file" ]]; then
            local size=$(du -h "$PACKAGE_DIR/$file" | cut -f1)
            log_success "✓ $file ($size)"
        else
            log_error "✗ $file (缺失)"
            all_ok=false
        fi
    done
    
    if $all_ok; then
        log_success "所有核心文件下载完成"
    else
        log_error "部分文件下载失败"
        exit 1
    fi
}

# 显示下载完成信息
show_completion_info() {
    log_info "下载完成！"
    echo
    echo "下载目录: $PACKAGE_DIR"
    echo "总大小: $(du -sh $PACKAGE_DIR | cut -f1)"
    echo
    echo "下一步操作:"
    echo "1. 将 $PACKAGE_DIR 目录复制到目标服务器"
    echo "2. 在目标服务器上运行: sudo bash install.sh"
    echo
    echo "文件清单:"
    ls -la "$PACKAGE_DIR"
    echo
    log_success "Docker离线安装包准备完成！"
}

# 主函数
main() {
    log_info "开始下载Docker离线安装包..."
    
    check_network
    check_tools
    create_directories
    
    download_docker_binary
    download_containerd
    download_runc
    download_docker_compose
    download_centos_packages
    download_ubuntu_packages
    
    create_readme
    verify_downloads
    show_completion_info
    
    log_success "所有下载任务完成！"
}

# 错误处理
trap 'log_error "下载过程中发生错误，请检查网络连接和权限"; exit 1' ERR

# 执行主函数
main "$@"