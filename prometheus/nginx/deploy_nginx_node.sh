#!/bin/bash
# ==============================================
# 离线部署Nginx Exporter四阶段脚本
# 版本：v2.1 更新日期：2025-02-28
# ==============================================

### 全局配置
readonly EXPORTER_VER="1.6.3"                # Exporter版本[5,7](@ref)
readonly PKG_PATH="/home/tuzhipeng"          # 离线包存放路径[1,6](@ref)
readonly INSTALL_DIR="/usr/local/nginx_exporter" 
readonly SERVICE_USER="nginx"                 # 运行用户[7,8](@ref)
readonly LISTEN_PORT="9101"                   # 监控端口[5](@ref)
readonly NGINX_CONF="/etc/nginx/nginx.conf"    # Nginx主配置[1,3](@ref)
readonly STUB_STATUS_PORT="8080"              # Nginx状态端口[1](@ref)

# ===== 准备阶段 =====
prepare_stage() {
    echo "=== PREPARATION STAGE ==="
    
    # 创建离线包目录（需提前放置nginx_exporter-${EXPORTER_VER}.linux-amd64.tar.gz）
    mkdir -p ${PKG_PATH} || error_exit "目录创建失败"
    
    # 检查依赖工具（基于网页6的依赖检查逻辑）
    for cmd in tar curl systemctl; do
        if ! command -v ${cmd} >/dev/null; then
            error_exit "依赖缺失: ${cmd}"
        fi
    done
    
    # 创建专用用户（参考网页7的用户隔离方案）
    if ! id ${SERVICE_USER} &>/dev/null; then
        useradd -s /sbin/nologin -M ${SERVICE_USER} || error_exit "用户创建失败"
    fi
    
    # 备份Nginx配置（参考网页8的配置备份方案）
    cp ${NGINX_CONF} ${NGINX_CONF}.bak.$(date +%s)
}

# ===== 部署阶段 =====
deploy_stage() {
    echo "=== DEPLOYMENT STAGE ==="
    
    # 解压安装包（网页5的离线安装方案）
    tar -zxvf ${PKG_PATH}/nginx_exporter-${EXPORTER_VER}.linux-amd64.tar.gz -C ${INSTALL_DIR} || error_exit "解压失败"
    ln -s ${INSTALL_DIR}/nginx_exporter-${EXPORTER_VER}.linux-amd64/nginx_exporter /usr/local/bin/
    
    # 配置Nginx状态端点（整合网页1和网页7的访问控制方案）
    if ! grep -q "stub_status" ${NGINX_CONF}; then
        cat <<EOF >> ${NGINX_CONF}
server {
    listen ${STUB_STATUS_PORT};
    server_name localhost;
    location /stub_status {
        stub_status;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
EOF
    fi
    
    # 重载Nginx配置（网页3的配置验证方案）
    nginx -t || error_exit "Nginx配置检查失败"
    systemctl reload nginx || error_exit "Nginx重载失败"

    # 创建systemd服务（网页7的服务管理方案增强）
    cat <<EOF > /etc/systemd/system/nginx_exporter.service
[Unit]
Description=Nginx Exporter
After=network.target nginx.service

[Service]
User=${SERVICE_USER}
Group=${SERVICE_USER}
ExecStart=/usr/local/bin/nginx_exporter \\
    --web.listen-address=:${LISTEN_PORT} \\
    --nginx.scrape-uri=http://localhost:${STUB_STATUS_PORT}/stub_status
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable --now nginx_exporter || error_exit "服务启动失败"
}

# ===== 验证阶段 =====
verify_stage() {
    echo "=== VERIFICATION STAGE ==="
    
    # 服务状态检查（网页7的状态验证方法）
    systemctl is-active nginx_exporter || error_exit "服务未运行"
    
    # 端口监听检查（网页5的网络验证方案）
    ss -tlnp | grep ":${LISTEN_PORT}" || error_exit "端口监听异常"
    
    # 指标抓取测试（网页5的关键指标验证）
    if ! curl -s http://localhost:${LISTEN_PORT}/metrics | grep 'nginx_process_'; then
        error_exit "指标获取失败"
    fi
    
    echo "验证通过，请将 ${HOSTNAME}:${LISTEN_PORT} 添加到Prometheus的监控目标"
}

# ===== 清理阶段 =====
cleanup_stage() {
    echo "=== CLEANUP STAGE ==="
    
    # 停止服务
    systemctl stop nginx_exporter
    systemctl disable nginx_exporter
    
    # 删除文件
    rm -rf ${INSTALL_DIR} /usr/local/bin/nginx_exporter
    rm -f /etc/systemd/system/nginx_exporter.service
    
    # 回滚Nginx配置（网页8的配置回滚方案）
    mv ${NGINX_CONF}.bak* ${NGINX_CONF}
    systemctl reload nginx
    
    # 移除专用用户
    userdel ${SERVICE_USER} 2>/dev/null
}

# ===== 异常处理 =====
error_exit() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    cleanup_stage
    exit 1
}

# ===== 主流程控制 =====
case "$1" in
    prepare)
        prepare_stage
        ;;
    deploy)
        deploy_stage
        ;;
    verify)
        verify_stage
        ;;
    cleanup)
        cleanup_stage
        ;;
    *)
        echo "Usage: $0 {prepare|deploy|verify|cleanup}"
        exit 1
esac