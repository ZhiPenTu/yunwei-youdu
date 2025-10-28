#!/bin/bash
set -euo pipefail

# 配置区域（按需修改）
MYSQL_EXPORTER_VERSION="v0.15.1"                   # Exporter 版本
EXPORTER_PORT="9104"                               # Exporter 监听端口
MYSQL_USER="exporter"                              # 监控专用 MySQL 用户名
EXPORTER_INSTALL_DIR="/opt/mysqld_exporter"        # Exporter 安装路径
PROMETHEUS_CONFIG="/etc/prometheus/prometheus.yml" # Prometheus 配置文件
TARGET_HOST="localhost"                          # metrics 目标

# 依赖检查
check_dependencies() {
  for cmd in tar mysql systemctl; do
    if ! command -v $cmd &>/dev/null; then
      echo "错误: 未找到 $cmd，请先安装！"
      exit 1
    fi
  done
}

# 创建 MySQL 监控用户
create_mysql_user() {
  local mysql_root_pass
  read -sp "请输入 MySQL root 密码: " mysql_root_pass
  echo

  mysql -u root -p"${mysql_root_pass}" <<EOF
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_EXPORTER_PASSWORD}' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO '${MYSQL_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

  if [ $? -ne 0 ]; then
    echo "错误: 创建 MySQL 用户失败！"
    exit 1
  fi
}

# 安装 MySQL Exporter
install_exporter() {
  echo "解压到 ${EXPORTER_INSTALL_DIR}..."
  mkdir -p "${EXPORTER_INSTALL_DIR}"
  tar xzf ./mysqld_exporter-0.15.1.linux-amd64.tar.gz -C "${EXPORTER_INSTALL_DIR}" --strip-components=1

  # 创建配置文件
  echo "创建 Exporter 配置文件..."
  cat >"${EXPORTER_INSTALL_DIR}/.my.cnf" <<EOF
[client]
user=${MYSQL_USER}
password=${MYSQL_EXPORTER_PASSWORD}
EOF
  chmod 600 "${EXPORTER_INSTALL_DIR}/.my.cnf"
}

# 配置 Systemd 服务
setup_systemd() {
  echo "创建 Systemd 服务..."
  cat >/etc/systemd/system/mysqld_exporter.service <<EOF
[Unit]
Description=Prometheus MySQL Exporter
After=network.target

[Service]
User=prometheus
ExecStart=${EXPORTER_INSTALL_DIR}/mysqld_exporter \\
  --config.my-cnf=${EXPORTER_INSTALL_DIR}/.my.cnf \\
  --web.listen-address=:${EXPORTER_PORT}
Restart=always

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable --now mysqld_exporter
  if ! systemctl is-active --quiet mysqld_exporter; then
    echo "错误: Exporter 服务启动失败！"
    journalctl -u mysqld_exporter -n 10 --no-pager
    exit 1
  fi
}


# 主流程
main() {
  # 获取密码
  read -sp "请设置 ${MYSQL_USER} 用户的密码: " MYSQL_EXPORTER_PASSWORD
  echo
  read -sp "请再次确认密码: " CONFIRM_PASSWORD
  echo

  if [ "${MYSQL_EXPORTER_PASSWORD}" != "${CONFIRM_PASSWORD}" ]; then
    echo "错误: 两次输入的密码不匹配！"
    exit 1
  fi

  check_dependencies
  create_mysql_user
  install_exporter
  setup_systemd
  cat <<EOF

完成！MySQL 监控已部署成功。
- Exporter 端口: ${EXPORTER_PORT}
- Prometheus 配置: ${PROMETHEUS_CONFIG}
- Grafana 仪表盘推荐 ID: 7362 或 11323
访问以下地址验证:
- Exporter 指标: curl http://${TARGET_HOST}:${EXPORTER_PORT}/metrics
- Prometheus 目标状态: http://${TARGET_HOST}:9090/targets
EOF
}

# 执行主函数
main
