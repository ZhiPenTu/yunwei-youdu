#!/bin/bash
# 下载文件
mv /tmp/nvidia_gpu_exporter_1.3.1_linux_x86_64.tar.gz ./
# 解压文件
tar -zxvf nvidia_gpu_exporter_1.3.1_linux_x86_64.tar.gz
# 移动文件到指定目录
mv nvidia_gpu_exporter /usr/bin

# 创建用户和组
sudo useradd --system --no-create-home --shell /usr/sbin/nologin nvidia_gpu_exporter
# 创建服务文件
cat > /etc/systemd/system/nvidia_gpu_exporter.service <<EOF
[Unit]
Description=Nvidia GPU Exporter
After=network-online.target
[Service]
Type=simple
User=nvidia_gpu_exporter
Group=nvidia_gpu_exporter
ExecStart=/usr/bin/nvidia_gpu_exporter --web.listen-address=:9835 
SyslogIdentifier=nvidia_gpu_exporter
Restart=always
RestartSec=1
[Install]
WantedBy=multi-user.target
EOF
# 启动服务
systemctl daemon-reload
systemctl start nvidia_gpu_exporter
systemctl enable nvidia_gpu_exporter
# 检查服务状态
systemctl status nvidia_gpu_exporter
