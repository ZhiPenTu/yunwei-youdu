# !/bin/bash

# 移动到当前目录下
mv /tmp/node_exporter-1.9.0.linux-amd64.tar.gz ./
# 解压文件
tar -zxvf node_exporter-1.9.0.linux-amd64.tar.gz
# 进入解压后的目录
cd node_exporter-1.9.0.linux-amd64
# 复制可执行文件到 /usr/local/bin 目录
sudo cp node_exporter /usr/local/
# 检查是否复制成功
ls /usr/local/bin/node_exporter
# 将主机名称放入 配置服务文件 --web.listen-address 参数中

cat > /usr/lib/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter for Prometheus
Documentation=https://prometheus.io/docs/guides/node-exporter/
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/node_exporter/node_exporter \
  --web.listen-address=:9100 \ 

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd 配置
sudo systemctl daemon-reload
# 启动服务
sudo systemctl start node_exporter
# 检查服务状态
sudo systemctl status node_exporter
# 配置开机自启动
sudo systemctl enable node_exporter
# 返回 指标
echo "Node Exporter 已安装并配置开机自启动。"
echo "访问地址："


[
  {
    "targets": [
      "35.46.5.44:9100"
    ],
    "labels": {
      "instance": "5.44服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.26:9109"
    ],
    "labels": {
      "instance": "5.26服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.39:9109"
    ],
    "labels": {
      "instance": "5.39服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.16:9109"
    ],
    "labels": {
      "instance": "5.16服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.17:9109"
    ],
    "labels": {
      "instance": "5.17服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.20:9109"
    ],
    "labels": {
      "instance": "5.20服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.35:9109"
    ],
    "labels": {
      "instance": "5.35服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.36:9109"
    ],
    "labels": {
      "instance": "5.36服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.37:9109"
    ],
    "labels": {
      "instance": "5.37服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.41:9109"
    ],
    "labels": {
      "instance": "5.41服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.59:9109"
    ],
    "labels": {
      "instance": "5.59服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.60:9109"
    ],
    "labels": {
      "instance": "5.60服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.61:9109"
    ],
    "labels": {
      "instance": "5.61服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.56:9109"
    ],
    "labels": {
      "instance": "5.56服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.191:9109"
    ],
    "labels": {
      "instance": "5.191服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.21:9109"
    ],
    "labels": {
      "instance": "5.21服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.54:9109"
    ],
    "labels": {
      "instance": "5.54服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.111:9100"
    ],
    "labels": {
      "instance": "5.111服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.113:9100"
    ],
    "labels": {
      "instance": "5.113服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.199:19100"
    ],
    "labels": {
      "instance": "5.199服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.49:19100"
    ],
    "labels": {
      "instance": "5.49服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.80:9100"
    ],
    "labels": {
      "instance": "5.80服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.81:9100"
    ],
    "labels": {
      "instance": "5.81服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.82:9100"
    ],
    "labels": {
      "instance": "5.82服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.28:19100"
    ],
    "labels": {
      "instance": "5.28服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.52:19100"
    ],
    "labels": {
      "instance": "5.52服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.90:19100"
    ],
    "labels": {
      "instance": "5.90服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.84:19100"
    ],
    "labels": {
      "instance": "5.84服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.55:19100"
    ],
    "labels": {
      "instance": "5.55服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.50:19100"
    ],
    "labels": {
      "instance": "5.50服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.15:19100"
    ],
    "labels": {
      "instance": "5.15服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.116:19100"
    ],
    "labels": {
      "instance": "5.116服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.117:19100"
    ],
    "labels": {
      "instance": "5.117服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.118:19100"
    ],
    "labels": {
      "instance": "5.118服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.115:19100"
    ],
    "labels": {
      "instance": "5.115服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.10:19100"
    ],
    "labels": {
      "instance": "5.10服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.13:19100"
    ],
    "labels": {
      "instance": "5.13服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.14:19100"
    ],
    "labels": {
      "instance": "5.14服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.71:19100"
    ],
    "labels": {
      "instance": "5.71服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.72:19100"
    ],
    "labels": {
      "instance": "5.72服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.73:19100"
    ],
    "labels": {
      "instance": "5.73服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.85:19100"
    ],
    "labels": {
      "instance": "5.85服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.86:19100"
    ],
    "labels": {
      "instance": "5.86服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.87:19100"
    ],
    "labels": {
      "instance": "5.87服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.88:19100"
    ],
    "labels": {
      "instance": "5.88服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.57:19100"
    ],
    "labels": {
      "instance": "5.57服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.110:9100"
    ],
    "labels": {
      "instance": "5.110服务器节点"
    }
  },
  {
    "targets": [
      "35.46.5.121:19100"
    ],
    "labels": {
      "instance": "5.121服务器节点"
    }
  }
]



