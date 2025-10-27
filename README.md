# 运维有肚 - 本地学习测试项目

## 项目简介

这是一个用于本地学习和测试的运维项目集合，包含各种容器化部署方案和配置文件。

## 项目结构

```
├── zlmediakit/              # ZLMediaKit 流媒体服务器部署
│   ├── docker-compose.yaml # Docker Compose 配置
│   ├── README.md           # 详细部署说明文档
│   └── media/conf/         # 配置文件目录
├── docker/                 # Docker 相关配置
├── prometheus/             # Prometheus 监控配置
├── redis/                  # Redis 配置
├── kafka/                  # Kafka 配置
└── ...                     # 其他服务配置

```

## 主要功能

### ZLMediaKit 流媒体服务器
- 支持 RTMP、RTSP、HLS、HTTP-FLV、WebRTC 等协议
- 完整的 Docker Compose 部署方案
- 详细的配置说明和使用文档
- 包含性能优化和安全建议

### 其他服务
- Docker 离线安装包
- Prometheus 监控系统
- Redis 缓存服务
- Kafka 消息队列
- 各种运维工具和脚本

## 快速开始

### ZLMediaKit 部署

```bash
cd zlmediakit
docker-compose up -d
```

详细部署说明请查看：[ZLMediaKit 部署文档](./zlmediakit/README.md)

## 使用说明

1. **本项目仅用于学习和测试目的**
2. 生产环境使用前请仔细review配置
3. 注意修改默认密码和安全配置
4. 建议在隔离环境中进行测试

## 环境要求

- Linux 操作系统（Ubuntu 18.04+ / CentOS 7+）
- Docker 20.10+
- Docker Compose 1.29+
- 至少 4GB 内存
- 至少 20GB 可用磁盘空间

## 注意事项

- 所有配置文件中的敏感信息已脱敏处理
- 部分服务需要根据实际环境调整配置
- 建议定期更新镜像版本
- 生产使用前请进行充分测试

## 贡献指南

这是个人学习项目，欢迎提出建议和改进意见。

## 许可证

本项目仅用于学习和测试，请遵守相关开源协议。

---

**免责声明：本项目仅供学习测试使用，不承担任何生产环境使用风险。**