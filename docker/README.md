# Docker 离线安装脚本使用指南

本目录包含了完整的Docker离线安装解决方案，适用于x86架构的Linux服务器环境。

## 📁 文件说明

- `download-packages.sh` - 联网环境下载脚本，用于下载所需的安装包
- `install.sh` - 离线安装脚本，用于在目标服务器上安装Docker
- `README.md` - 本使用说明文档

## 🚀 快速开始

### 第一步：下载安装包（联网环境）

在有网络连接的服务器上运行下载脚本：

```bash
# 给脚本添加执行权限
chmod +x download-packages.sh

# 运行下载脚本
sudo ./download-packages.sh
```

下载完成后，会在 `/opt/docker-offline/packages` 目录下生成所有必要的安装包。

### 第二步：传输到目标服务器

将下载的安装包目录传输到目标服务器：

```bash
# 打包安装包目录
tar -czf docker-offline-packages.tar.gz -C /opt docker-offline

# 传输到目标服务器（示例）
scp docker-offline-packages.tar.gz user@target-server:/tmp/

# 在目标服务器上解压
ssh user@target-server
cd /tmp
sudo tar -xzf docker-offline-packages.tar.gz -C /opt/
```

### 第三步：离线安装（目标服务器）

在目标服务器上运行安装脚本：

```bash
# 进入脚本目录
cd /path/to/install-script

# 给脚本添加执行权限
chmod +x install.sh

# 运行离线安装脚本
sudo ./install.sh
```

## 📋 系统要求

### 支持的操作系统
- CentOS 7/8/9
- RHEL 7/8/9
- Rocky Linux 8/9
- AlmaLinux 8/9
- Ubuntu 18.04/20.04/22.04
- Debian 10/11/12

### 系统架构
- x86_64 (AMD64)

### 最低硬件要求
- CPU: 1核心
- 内存: 1GB
- 磁盘: 10GB可用空间

## 🔧 安装的组件版本

| 组件 | 版本 | 说明 |
|------|------|------|
| Docker Engine | 22.0.9 | 容器运行时引擎 |
| Docker Compose | 2.20.3 | 容器编排工具 |
| containerd | 1.6.24 | 容器运行时 |
| runc | 1.1.9 | OCI运行时 |

## 📝 脚本功能特性

### download-packages.sh 功能
- ✅ 自动检测网络连接
- ✅ 下载Docker二进制文件
- ✅ 下载Docker Compose
- ✅ 下载containerd和runc
- ✅ 下载RPM包（CentOS/RHEL）
- ✅ 下载DEB包（Ubuntu/Debian）
- ✅ 生成安装说明文档
- ✅ 文件完整性验证

### install.sh 功能
- ✅ Root权限检查
- ✅ 系统架构检查
- ✅ 操作系统检测
- ✅ 安装包完整性检查
- ✅ 自动安装系统依赖
- ✅ 清理旧版本Docker
- ✅ 安装Docker引擎
- ✅ 配置systemd服务
- ✅ 安装Docker Compose
- ✅ 服务启动和验证
- ✅ 完整的错误处理
- ✅ 彩色日志输出

## 🛠️ 高级配置

### 自定义安装目录

可以通过修改脚本中的变量来自定义安装路径：

```bash
# 在install.sh中修改
INSTALL_DIR="/opt/docker-offline"  # 安装包目录
PACKAGE_DIR="${INSTALL_DIR}/packages"  # 具体包文件目录
```

### 自定义Docker配置

安装脚本会创建默认的Docker daemon配置文件 `/etc/docker/daemon.json`：

```json
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
```

### 版本自定义

如需安装其他版本，可修改脚本中的版本变量：

```bash
# 在两个脚本中都需要修改
DOCKER_VERSION="22.0.9"          # Docker版本
DOCKER_COMPOSE_VERSION="2.20.3"  # Docker Compose版本
CONTAINERD_VERSION="1.6.24"      # containerd版本
RUNC_VERSION="1.1.9"             # runc版本
```

## 🔍 故障排除

### 常见问题

1. **权限不足**
   ```bash
   # 确保使用root权限运行
   sudo ./install.sh
   ```

2. **安装包缺失**
   ```bash
   # 检查安装包目录
   ls -la /opt/docker-offline/packages/
   
   # 重新运行下载脚本
   sudo ./download-packages.sh
   ```

3. **服务启动失败**
   ```bash
   # 检查服务状态
   systemctl status docker
   systemctl status containerd
   
   # 查看日志
   journalctl -u docker -f
   ```

4. **架构不匹配**
   ```bash
   # 检查系统架构
   uname -m
   # 应该显示 x86_64
   ```

### 日志查看

```bash
# 查看Docker服务日志
journalctl -u docker --no-pager

# 查看containerd服务日志
journalctl -u containerd --no-pager

# 实时查看日志
journalctl -u docker -f
```

### 手动验证安装

```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version

# 检查Docker信息
docker info

# 运行测试容器
docker run --rm hello-world

# 检查服务状态
systemctl status docker
systemctl status containerd
```

## 📞 技术支持

如果在使用过程中遇到问题，请：

1. 检查系统日志：`journalctl -u docker`
2. 确认系统架构：`uname -m`
3. 验证安装包完整性
4. 查看脚本执行日志

## 📄 许可证

本脚本遵循 MIT 许可证，可自由使用和修改。

---

**作者**: 运维有肚团队  
**更新时间**: $(date +%Y-%m-%d)  
**版本**: 1.0.0