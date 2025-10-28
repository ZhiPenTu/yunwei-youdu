#!/bin/bash

# 跨平台环境检查
detect_os() {
  case "$(uname -s)" in
    Darwin*) echo "macos" ;;
    Linux*)  echo "ubuntu" ;;
    MINGW*|CYGWIN*|MSYS*) echo "windows" ;;
    *)        echo "unknown" ;;
  esac
}

OS="$(detect_os)"

# 工具包名映射
# 工具包列表
if [ "$OS" = "ubuntu" ]; then
  PKG_LIST="curl jq parallel"
elif [ "$OS" = "macos" ]; then
  PKG_LIST="curl jq parallel"
elif [ "$OS" = "windows" ]; then
  PKG_LIST="curl jq gnu-parallel" # 假设使用 Chocolatey 安装
fi

# 包管理器配置
# 包管理器命令
if [ "$OS" = "ubuntu" ]; then
  PM_CMD="sudo apt-get install -y"
elif [ "$OS" = "macos" ]; then
  PM_CMD="brew install"
elif [ "$OS" = "windows" ]; then
  PM_CMD="choco install -y" # 假设使用 Chocolatey
fi

# 安装Homebrew（macOS）
install_brew() {
  if ! command -v brew &> /dev/null; then
    echo "正在安装Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
}

# 安装Chocolatey（Windows）
install_chocolatey() {
  if ! command -v choco &> /dev/null; then
    echo "正在安装Chocolatey..."
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
  fi
}

# 主检查逻辑
check_tools() {
  missing=()
  for tool in $PKG_LIST; do
    if ! command -v "${tool##*/}" &> /dev/null; then
      missing+=("$tool")
    fi
  done

  if [ ${#missing[@]} -ne 0 ]; then
    echo "缺少必要工具: ${missing[*]}"
    
    if [ "$OS" = "macos" ]; then
      install_brew
    elif [ "$OS" = "ubuntu" ] && [ "$(id -u)" -ne 0 ]; then
      echo "检测到Ubuntu系统需要sudo权限"
      if ! sudo -v &> /dev/null; then
        echo "错误: 无sudo权限，请手动运行安装命令:"
        echo "${PM_CMD[$OS]} ${missing[*]}"
        exit 1
      fi
    elif [ "$OS" = "windows" ]; then
      install_chocolatey
    fi

    echo "正在安装: ${missing[*]}"
    ${PM_CMD} ${missing[@]} || {
      echo "安装失败，请手动运行:"
      echo "${PM_CMD[$OS]} ${missing[*]}"
      exit 1
    }
  fi
}

check_tools

# 确保parallel命令别名（macOS）
if [ "$OS" = "macos" ] && command -v parallel &> /dev/null; then
  if ! parallel --version | grep -q GNU; then
    echo "检测到非GNU parallel，创建别名..."
    alias parallel=gparallel
  fi
fi

# 0.配置参数
NEXUS_URL="http://35.46.5.91:32373/repository/npm/" # Nexus 仓库地址
DOWNLOAD_DIR="./npm-dependencies"                   # 本地下载目录
USERNAME="admin"                                    # Nexus 用户名
PASSWORD="HTcf@2022!"                               # Nexus 密码

# 检查 package-lock.json 文件是否存在
if [[ ! -f "package-lock.json" ]]; then
  echo "错误: package-lock.json 文件不存在"
  exit 1
fi
# 获取 npm 版本
# 获取npm主版本号（兼容带版本前缀的格式）
npm_version=$(npm -v | awk -F. '{print $1}' | sed 's/[^0-9]*//g')
echo "npm 主版本号: $npm_version"


# 1. 登录 Nexus 仓库（优化为兼容不同版本的 npm）
echo "配置 Nexus 认证信息..."
npm config set registry "$NEXUS_URL"
# 使用 _authToken 方式进行认证，兼容 npm v7+ 和更低版本
AUTH_TOKEN=$(printf "%s" "$USERNAME:$PASSWORD" | base64 | tr -d '\n')
# 新版npm使用带仓库路径的认证配置
echo "配置兼容性认证信息..."
if (( npm_version >= 7 )); then
  npm config set "//$(echo ${NEXUS_URL} | sed -e 's/^http[s]*:\/\///' -e 's/\/$//')/:_auth" "$AUTH_TOKEN"
else
  # 旧版npm认证格式
  npm config set "_auth" "$AUTH_TOKEN"
fi

echo "执行npm配置自动修复..."
npm config fix
npm config delete _auth --force
npm config delete //35.46.5.91:32373/repository/npm/:_auth --force
echo "删除遗留的旧版auth配置"

# 验证认证配置
echo "测试认证配置..."
echo "调试信息："
echo "NEXUS_URL: $NEXUS_URL"
echo "AUTH_TOKEN 前5位: ${AUTH_TOKEN:0:5}"
npm config list --global | grep registry
echo "当前npm配置："
npm config get registry
echo "完整认证配置："
npm config list | grep -E '_auth|registry'

# 直接设置认证信息，避免使用 npm adduser
npm config set "//$(echo ${NEXUS_URL} | sed -e 's/^http[s]*:\/\///' -e 's/\/$//')/:username" "$USERNAME"
npm config set "//$(echo ${NEXUS_URL} | sed -e 's/^http[s]*:\/\///' -e 's/\/$//')/:_password" "$(printf "%s" "$PASSWORD" | base64 | tr -d '\n')"
npm config set "//$(echo ${NEXUS_URL} | sed -e 's/^http[s]*:\/\///' -e 's/\/$//')/:email" "$USERNAME@example.com"

if ! npm whoami --registry "$NEXUS_URL" --auth-type=legacy --loglevel verbose 2>&1 | sed 's/\b[A-Za-z0-9=]\{20,\}\b/******/g'; then
  echo "错误: 认证配置失败，请检查凭证和网络连接"
  exit 1
fi

# 3.版本判断逻辑优化
if (( npm_version >= 7 )); then
  echo "npm v7+ 检测到，使用扁平化结构解析方式"
  RESOLVED_URLS=$(jq -r '.packages[] | select(.resolved)  | .resolved' package-lock.json 2>/dev/null)
else
  echo "npm v5-6 检测到，使用嵌套结构解析方式" 
  RESOLVED_URLS=$(jq -r '.dependencies[] | select(.resolved) | .resolved' package-lock.json 2>/dev/null)
fi

# 4.检查 jq 命令是否执行成功
if [[ $? -ne 0 ]]; then
  echo "错误: 解析 package-lock.json 文件失败，请检查文件格式"
  exit 1
fi

# 5. 创建下载目录
mkdir -p "$DOWNLOAD_DIR"

# 6. 并行批量下载优化
# 生成URL列表文件
echo "$RESOLVED_URLS" | tr ' ' '\n' > urls.list

echo "开始并行下载 (使用 $(nproc) 线程)..."
cat urls.list | parallel --bar -j $(nproc) --joblog download.log \
"url={} \
&& filename=\$(echo \$url | sed 's/.*\///;s/[?=]/_/g') \
&& if [[ -f \"$DOWNLOAD_DIR/\$filename\" ]]; then \
  echo \"[跳过] \$filename\"; \
  exit 0; \
fi; \
for retry in {1..3}; do \
  echo -n \"[尝试\$retry] 下载: \$filename \"; \
  curl -Lf# --compressed --http1.1 --max-time 300 \
    -o \"$DOWNLOAD_DIR/\$filename\" \"\$url\"; \
  if [ \$? -eq 0 ]; then \
    echo \"成功\"; \
    exit 0; \
  else \
    echo \"失败\"; \
    sleep \$((retry*2)); \
  fi; \
done; \
echo \"[错误] 最终下载失败: \$url\" | tee -a npm-dependency-errors.log; \
exit 1"

# 带宽统计
avg_speed=$(grep -oP '\d+%\s+\K\d+\.\d+ [kM]B/s' download.log | awk '{sum+=$1} END {print sum/NR}')
echo "平均下载速度: ${avg_speed:-N/A}"

# 清理临时文件
rm -f urls.list

# 7. 并行批量上传（使用GNU parallel加速）
echo "开始并行上传到 Nexus..."
find "$DOWNLOAD_DIR" -type f -name "*.tgz" -print0 | \
parallel -0 -j 12 --progress --bar --joblog upload.log \
"echo '上传: {}'; npm publish {} --registry="$NEXUS_URL" --_auth="$AUTH_TOKEN" --auth-type=legacy --loglevel verbose 2>&1 | sed 's/\b[A-Za-z0-9=]\{20,\}\b/******/g' || echo '[错误] 上传失败: {}' | tee -a npm-dependency-errors.log"

echo "\n上传完成，错误统计:"
touch npm-dependency-errors.log
grep -c "错误" npm-dependency-errors.log || true
rm -f npm-dependency-errors.log
rm -rf "$DOWNLOAD_DIR"
rm -f download.log
rm -f upload.log

echo "操作完成！"
