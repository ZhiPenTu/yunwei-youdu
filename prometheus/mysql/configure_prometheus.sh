#!/bin/bash
set -euo pipefail

# 依赖检查
check_dependencies() {
    for cmd in tar mysql systemctl; do
        if ! command -v $cmd &>/dev/null; then
            echo "错误: 未找到 $cmd，请先安装！"
            exit 1
        fi
    done
}

# 配置 Prometheus
configure_prometheus() {
    echo "更新 Prometheus 配置..."
    if ! grep -q "job_name: 'mysql'" "${PROMETHEUS_CONFIG}"; then
        cat >>"${PROMETHEUS_CONFIG}" <<EOF

  - job_name: 'mysql'
    static_configs:
      - targets: ['localhost:${EXPORTER_PORT}']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'mysql-main'
EOF
    fi

    systemctl reload prometheus || systemctl restart prometheus
}

# 验证安装
verify_installation() {
    echo "验证 Exporter 状态..."
    if curl -s "http://${TARGET_HOST}:${EXPORTER_PORT}/metrics" | grep -q 'mysql_up'; then
        echo "Exporter 指标已暴露"
    else
        echo "错误: Exporter 指标获取失败！"
        exit 1
    fi

    echo "检查 Prometheus 目标..."
    if curl -s "http://${TARGET_HOST}:9090/api/v1/targets" | grep -A5 '"mysql"' | grep -q '"health":"up"'; then
        echo "Prometheus 抓取正常"
    else
        echo "警告: Prometheus 目标状态异常，请检查配置！"
    fi
}

# 函数主流程
main() {

    check_dependencies
    configure_prometheus
    verify_installation
    cat <<EOF
完成！MySQL 监控已部署成功。
- Exporter 端口: ${EXPORTER_PORT}
- Prometheus 配置: ${PROMETHEUS_CONFIG}
- Grafana 仪表盘推荐 ID: 7362 或 11323

访问以下地址验证:
- Exporter 指标: curl http://localhost:${EXPORTER_PORT}/metrics
- Prometheus 目标状态: http://localhost:9090/targets
EOF
}
