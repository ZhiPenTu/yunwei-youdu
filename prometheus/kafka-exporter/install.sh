#!/bin/bash

# 移动到当前目录下
mv /tmp/kafka_exporter-1.8.0.linux-amd64.tar.gz ./
# 解压文件
tar -zxvf kafka_exporter-1.8.0.linux-amd64.tar.gz
# 进入解压后的目录
cd kafka_exporter-1.8.0.linux-amd64
# 复制可执行文件到 /usr/local/bin 目录
sudo cp kafka_exporter /usr/local/bin/
# 检查是否复制成功
ls /usr/local/bin/kafka_exporter
# 将主机名称放入 配置服务文件 --kafka.server 参数中
sudo tee /etc/systemd/system/kafka_exporter.service <<EOF
[Unit]
Description=Kafka Exporter
After=network.target
[Service]
ExecStart=/usr/local/bin/kafka_exporter --web.listen-address=:9308 --kafka.server=bigdata01:9092
Restart=always
[Install]
WantedBy=multi-user.target
EOF 
# 重新加载 systemd 配置
sudo systemctl daemon-reload
# 启动服务
sudo systemctl start kafka_exporter
# 检查服务状态
sudo systemctl status kafka_exporter
# 配置开机自启动
sudo systemctl enable kafka_exporter
# 返回 指标
echo "Kafka Exporter 已安装并配置开机自启动。"
echo "访问地址："
echo "URL_ADDRESSecho "http://localhost:9308/metrics"