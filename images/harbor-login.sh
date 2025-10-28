
# 配置Harbor参数
HARBOR_HOST="dockerhub.kubekey.htcf"
HARBOR_IP="35.46.5.92"
HARBOR_PROJECT="htcfproject"
HARBOR_USER="admin"
HARBOR_PASS="Harbor12345"
# 登录Harbor
echo "[Deployment] 登录Harbor仓库 $HARBOR_HOST"
cat /etc/docker_passwd  | docker login "$HARBOR_HOST" -u "$HARBOR_USER" --password-stdin || {
    echo "[Error] 登录Harbor失败，请检查用户名和密码"
    exit 1
}
