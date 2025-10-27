# ZLMediaKit Docker Compose 部署说明

## 概述

ZLMediaKit 是一个基于 C++11 的高性能流媒体服务器框架，支持 RTMP、RTSP、HLS、HTTP-FLV、WebRTC 等多种协议。本文档介绍如何在 Linux 环境下使用 Docker Compose 方式部署 ZLMediaKit。

## 系统要求

- Linux 操作系统（Ubuntu 18.04+ / CentOS 7+ / Debian 9+）
- Docker 20.10+
- Docker Compose 1.29+
- 至少 2GB 内存
- 至少 10GB 可用磁盘空间

## 快速开始

### 1. 安装 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证 Docker 服务是否正常启动
docker info
```

### 2. 准备部署目录

```bash
# 创建项目目录
mkdir -p /data/zlmediakit/media/conf
cd /path/to/your/project/zlmediakit

# 确保配置文件目录存在
sudo mkdir -p /data/zlmediakit/media/conf
sudo chown -R $USER:$USER /data/zlmediakit
```

### 3. 配置文件说明

项目包含以下关键文件：
- `docker-compose.yaml`: Docker Compose 配置文件
- `media/conf/config.ini`: ZLMediaKit 主配置文件

配置文件挂载路径：
- 容器内路径: `/opt/media/conf`
- 宿主机路径: `/data/zlmediakit/media/conf`

### 4. 镜像下载

使用的 Docker 镜像：
- 镜像名称: `zlmediakit/zlmediakit:master`
- 镜像来源: Docker Hub 官方仓库

```bash
# 预先拉取镜像（可选）
docker pull zlmediakit/zlmediakit:master
```

### 5. 启动 ZLMediaKit

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f zlmediakit
```

### 6. 端口说明

服务暴露的端口映射：

| 协议 | 宿主机端口 | 容器端口 | 说明 |
|------|------------|----------|------|
| RTMP | 1935 | 1935 | RTMP 推拉流端口 |
| HTTP | 8080 | 80 | Web 管理界面和 HTTP-FLV |
| RTSP | 8554 | 554 | RTSP 推拉流端口 |
| RTP | 10000 | 10000 | RTP 传输端口 (TCP/UDP) |
| WebRTC | 8000 | 8000 | WebRTC UDP 端口 |
| RTP范围 | 30000-30500 | 30000-30500 | RTP 端口范围 (TCP/UDP) |

### 7. 访问服务

```bash
# 访问 ZLMediaKit Web 管理界面
open http://localhost:8080

# 访问 ZLMediaKit API 文档
open http://localhost:8080/index/api/getApiList
```

### 8. 常用操作

#### 停止服务
```bash
docker-compose down
```

#### 重启服务
```bash
docker-compose restart
```

#### 查看实时日志
```bash
docker-compose logs -f
```

#### 进入容器
```bash
docker exec -it zlmediakit /bin/bash
```

## 配置说明

### 主要配置项

配置文件位于 `media/conf/config.ini`，主要配置项说明：

#### HTTP 配置
- `port=80`: HTTP 服务端口
- `allow_cross_domains=1`: 允许跨域访问

#### RTMP 配置
- `port=1935`: RTMP 服务端口
- `directProxy=1`: 启用直接代理

#### RTSP 配置
- `port=554`: RTSP 服务端口
- `lowLatency=0`: 低延迟模式

#### RTP 配置
- `port=10000`: RTP 服务端口
- `port_range=30000-30500`: RTP 端口范围

### 自定义配置

如需修改配置：

1. 编辑 `media/conf/config.ini` 文件
2. 重启服务使配置生效：
   ```bash
   docker-compose restart
   ```

## 测试验证

### 推流测试

使用 FFmpeg 推流测试：

```bash
# RTMP 推流
ffmpeg -re -i test.mp4 -c copy -f flv rtmp://localhost:1935/live/test

# RTSP 推流
ffmpeg -re -i test.mp4 -c copy -f rtsp rtsp://localhost:8554/live/test
```

### 拉流测试

```bash
# RTMP 拉流
ffplay rtmp://localhost:1935/live/test

# RTSP 拉流
ffplay rtsp://localhost:8554/live/test

# HTTP-FLV 拉流
ffplay http://localhost:8080/live/test.flv

# HLS 拉流
ffplay http://localhost:8080/live/test/hls.m3u8
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep :8080
   
   # 修改 docker-compose.yaml 中的端口映射
   ```

2. **配置文件权限问题**
   ```bash
   # 修复权限
   sudo chown -R $USER:$USER /data/zlmediakit
   ```

3. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs zlmediakit
   
   # 检查配置文件语法
   docker-compose config
   ```

### 日志查看

```bash
# 查看容器日志
docker logs zlmediakit

# 实时查看日志
docker logs -f zlmediakit

# 查看最近100行日志
docker logs --tail 100 zlmediakit
```

## 性能优化

### 系统优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# 优化网络参数
echo "net.core.rmem_max = 134217728" >> /etc/sysctl.conf
echo "net.core.wmem_max = 134217728" >> /etc/sysctl.conf
sysctl -p
```

### Docker 优化

在 `docker-compose.yaml` 中添加资源限制：

```yaml
services:
  zlmediakit:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
```

## 安全建议

1. **修改默认密钥**：编辑 `config.ini` 中的 `secret` 值
2. **限制访问IP**：配置 `allow_ip_range` 参数
3. **启用HTTPS**：配置SSL证书和 `sslport`
4. **防火墙配置**：只开放必要的端口

## 备份与恢复

### 备份配置
```bash
# 备份配置文件
tar -czf zlmediakit-config-$(date +%Y%m%d).tar.gz /data/zlmediakit/media/conf/
```

### 恢复配置
```bash
# 恢复配置文件
tar -xzf zlmediakit-config-20231027.tar.gz -C /
docker-compose restart
```

## 版本升级

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d

# 清理旧镜像
docker image prune -f
```

---

**注意事项：**
- 确保防火墙已开放相应端口
- 生产环境建议使用具体版本标签而非 `master`
- 定期备份配置文件和重要数据
- 监控服务运行状态和资源使用情况