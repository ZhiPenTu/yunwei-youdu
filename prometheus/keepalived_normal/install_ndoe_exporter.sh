#!/bin/bash
# 离线环境主部署脚本，需提前将离线包传至/opt目录
INSTALL_DIR="/data/node_exporter"

mkdir -p $INSTALL_DIR

# 安装node_exporter(网页6方案)
cd $INSTALL_DIR
tar -zxvf node_exporter-*.tar.gz
mv node_exporter-*/node_exporter /usr/local/bin/
useradd --no-create-home --shell /sbin/nologin node_exporter
chown node_exporter:node_exporter /usr/local/bin/node_exporter

# 配置textfile收集器(方案一核心)
mkdir -p /var/lib/node_exporter/textfile
chown -R node_exporter:node_exporter /var/lib/node_exporter