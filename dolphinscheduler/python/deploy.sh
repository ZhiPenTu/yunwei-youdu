#!/bin/bash
# -*- coding: utf-8 -*-

# SeaTunnel数据同步任务部署脚本
# 用于快速部署和配置DolphinScheduler Python任务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="SeaTunnel数据同步任务"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${PROJECT_DIR}/deploy.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 显示帮助信息
show_help() {
    cat << EOF
${PROJECT_NAME} 部署脚本

用法: $0 [选项]

选项:
    -h, --help          显示此帮助信息
    -i, --install       安装依赖包
    -c, --config        配置环境变量
    -t, --test          运行测试
    -d, --deploy        完整部署（安装+配置+测试）
    -s, --start         启动DolphinScheduler服务
    --clean             清理临时文件
    --status            检查服务状态

示例:
    $0 --deploy         # 完整部署
    $0 --install        # 仅安装依赖
    $0 --test           # 仅运行测试
    $0 --status         # 检查状态

EOF
}

# 检查系统环境
check_system() {
    log_info "检查系统环境..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_info "Python版本: $PYTHON_VERSION"
        
        # 检查Python版本是否满足要求（>=3.7）
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
            log_success "Python版本满足要求"
        else
            log_error "Python版本过低，需要3.7或更高版本"
            exit 1
        fi
    else
        log_error "未找到Python3，请先安装Python3"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3已安装"
    else
        log_error "未找到pip3，请先安装pip3"
        exit 1
    fi
    
    # 检查虚拟环境工具
    if python3 -c "import venv" 2>/dev/null; then
        log_success "venv模块可用"
    else
        log_warning "venv模块不可用，将使用系统Python环境"
    fi
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    
    VENV_DIR="${PROJECT_DIR}/venv"
    
    if [ -d "$VENV_DIR" ]; then
        log_warning "虚拟环境已存在，跳过创建"
        return 0
    fi
    
    if python3 -c "import venv" 2>/dev/null; then
        python3 -m venv "$VENV_DIR"
        log_success "虚拟环境创建成功: $VENV_DIR"
        
        # 激活虚拟环境
        source "$VENV_DIR/bin/activate"
        log_info "虚拟环境已激活"
    else
        log_warning "无法创建虚拟环境，将使用系统Python环境"
    fi
}

# 安装依赖包
install_dependencies() {
    log_info "安装Python依赖包..."
    
    # 升级pip
    log_info "升级pip..."
    pip3 install --upgrade pip
    
    # 首先尝试安装基础依赖
    log_info "安装基础依赖包..."
    pip3 install PyMySQL requests python-dotenv
    
    if [ $? -eq 0 ]; then
        log_success "基础依赖包安装成功"
    else
        log_warning "基础依赖包安装失败，但继续运行"
    fi
    
    # 尝试安装可选依赖
    log_info "尝试安装可选依赖包..."
    pip3 install pandas numpy python-dateutil 2>/dev/null || log_warning "可选依赖包安装失败，跳过"
    
    # 尝试安装DolphinScheduler（可能失败）
    log_info "尝试安装DolphinScheduler..."
    pip3 install apache-dolphinscheduler 2>/dev/null || log_warning "DolphinScheduler安装失败，将以独立模式运行"
    
    # 检查requirements.txt文件并安装（如果存在）
    REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt"
    if [ -f "$REQUIREMENTS_FILE" ]; then
        log_info "发现requirements.txt文件，安装额外依赖..."
        pip3 install -r "$REQUIREMENTS_FILE" || log_warning "requirements.txt中的某些依赖安装失败"
    else
        log_info "未找到requirements.txt文件，跳过"
    fi
    
    log_success "依赖包安装完成"
}

# 配置环境变量
setup_config() {
    log_info "配置环境变量..."
    
    ENV_FILE="${PROJECT_DIR}/.env"
    ENV_EXAMPLE_FILE="${PROJECT_DIR}/.env.example"
    
    # 检查.env文件是否存在
    if [ -f "$ENV_FILE" ]; then
        log_warning ".env文件已存在，跳过配置"
        return 0
    fi
    
    # 检查.env.example文件
    if [ ! -f "$ENV_EXAMPLE_FILE" ]; then
        log_error "未找到.env.example文件"
        exit 1
    fi
    
    # 复制示例配置文件
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    log_success "已创建.env配置文件"
    
    log_warning "请编辑 $ENV_FILE 文件，配置正确的数据库连接信息"
    log_info "配置文件位置: $ENV_FILE"
    
    # 提示用户编辑配置
    read -p "是否现在编辑配置文件？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v nano &> /dev/null; then
            nano "$ENV_FILE"
        elif command -v vim &> /dev/null; then
            vim "$ENV_FILE"
        elif command -v vi &> /dev/null; then
            vi "$ENV_FILE"
        else
            log_warning "未找到文本编辑器，请手动编辑配置文件"
        fi
    fi
}

# 运行测试
run_tests() {
    log_info "运行项目测试..."
    
    TEST_FILE="${PROJECT_DIR}/test_task.py"
    if [ ! -f "$TEST_FILE" ]; then
        log_error "未找到测试文件: $TEST_FILE"
        exit 1
    fi
    
    # 运行测试
    log_info "执行单元测试..."
    if python3 "$TEST_FILE"; then
        log_success "测试通过"
    else
        log_error "测试失败"
        exit 1
    fi
}

# 验证配置
validate_config() {
    log_info "验证配置文件..."
    
    # 检查主要配置文件
    CONFIG_FILE="${PROJECT_DIR}/config.py"
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "未找到配置文件: $CONFIG_FILE"
        exit 1
    fi
    
    # 检查主脚本文件
    MAIN_SCRIPT="${PROJECT_DIR}/seatunnel_to_doris_task.py"
    if [ ! -f "$MAIN_SCRIPT" ]; then
        log_error "未找到主脚本文件: $MAIN_SCRIPT"
        exit 1
    fi
    
    # 验证Python语法
    log_info "验证Python语法..."
    if python3 -m py_compile "$CONFIG_FILE" && python3 -m py_compile "$MAIN_SCRIPT"; then
        log_success "Python语法验证通过"
    else
        log_error "Python语法验证失败"
        exit 1
    fi
    
    # 验证配置
    log_info "验证配置有效性..."
    if python3 -c "from config import Config; print('配置验证:', Config.validate_config())"; then
        log_success "配置验证通过"
    else
        log_warning "配置验证失败，请检查.env文件中的配置"
    fi
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    # 检查DolphinScheduler进程
    if pgrep -f "dolphinscheduler" > /dev/null; then
        log_success "DolphinScheduler服务正在运行"
    else
        log_warning "DolphinScheduler服务未运行"
    fi
    
    # 检查Python Gateway Service
    if pgrep -f "pydolphinscheduler" > /dev/null; then
        log_success "Python Gateway Service正在运行"
    else
        log_warning "Python Gateway Service未运行"
    fi
    
    # 检查端口占用
    log_info "检查端口占用情况..."
    
    # DolphinScheduler API端口（默认12345）
    if lsof -i :12345 > /dev/null 2>&1; then
        log_success "DolphinScheduler API端口(12345)正常"
    else
        log_warning "DolphinScheduler API端口(12345)未监听"
    fi
    
    # Python Gateway端口（默认25333）
    if lsof -i :25333 > /dev/null 2>&1; then
        log_success "Python Gateway端口(25333)正常"
    else
        log_warning "Python Gateway端口(25333)未监听"
    fi
}

# 启动服务
start_services() {
    log_info "启动DolphinScheduler服务..."
    
    # 检查DolphinScheduler安装目录
    DOLPHIN_HOME=${DOLPHINSCHEDULER_HOME:-"/opt/dolphinscheduler"}
    
    if [ ! -d "$DOLPHIN_HOME" ]; then
        log_error "未找到DolphinScheduler安装目录: $DOLPHIN_HOME"
        log_info "请设置DOLPHINSCHEDULER_HOME环境变量或安装DolphinScheduler"
        exit 1
    fi
    
    # 启动服务
    log_info "启动DolphinScheduler服务..."
    if [ -f "$DOLPHIN_HOME/bin/dolphinscheduler-daemon.sh" ]; then
        "$DOLPHIN_HOME/bin/dolphinscheduler-daemon.sh" start standalone-server
        log_success "DolphinScheduler服务启动完成"
    else
        log_error "未找到DolphinScheduler启动脚本"
        exit 1
    fi
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    check_status
}

# 清理临时文件
clean_temp() {
    log_info "清理临时文件..."
    
    # 清理Python缓存
    find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # 清理日志文件（保留最近的）
    if [ -f "$LOG_FILE" ]; then
        tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
    
    log_success "临时文件清理完成"
}

# 完整部署
full_deploy() {
    log_info "开始完整部署..."
    
    check_system
    create_venv
    install_dependencies
    setup_config
    validate_config
    run_tests
    
    log_success "部署完成！"
    log_info "下一步："
    log_info "1. 编辑 .env 文件配置数据库连接"
    log_info "2. 运行 $0 --start 启动服务"
    log_info "3. 运行 python3 seatunnel_to_doris_task.py 执行任务"
}

# 显示项目信息
show_info() {
    cat << EOF

${GREEN}========================================${NC}
${GREEN}    ${PROJECT_NAME}${NC}
${GREEN}========================================${NC}

项目目录: ${PROJECT_DIR}
日志文件: ${LOG_FILE}

文件列表:
$(ls -la "$PROJECT_DIR" | grep -E '\.(py|txt|md|sh|env)$' | awk '{print "  " $9}')

${GREEN}========================================${NC}

EOF
}

# 主函数
main() {
    # 创建日志文件
    touch "$LOG_FILE"
    
    # 显示项目信息
    show_info
    
    # 解析命令行参数
    case "${1:-}" in
        -h|--help)
            show_help
            ;;
        -i|--install)
            check_system
            create_venv
            install_dependencies
            ;;
        -c|--config)
            setup_config
            validate_config
            ;;
        -t|--test)
            run_tests
            ;;
        -d|--deploy)
            full_deploy
            ;;
        -s|--start)
            start_services
            ;;
        --clean)
            clean_temp
            ;;
        --status)
            check_status
            ;;
        "")
            log_info "使用 $0 --help 查看帮助信息"
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"