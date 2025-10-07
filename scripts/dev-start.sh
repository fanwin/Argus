#!/bin/bash

# 开发环境启动脚本
# 用于快速启动和管理开发环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
开发环境启动脚本

用法: $0 [命令] [选项]

命令:
    start           启动开发环境
    stop            停止开发环境
    restart         重启开发环境
    status          查看开发环境状态
    logs            查看开发环境日志
    shell           进入开发容器shell
    test            运行测试
    debug           启动调试模式
    jupyter         启动Jupyter Lab
    quality         运行代码质量检查
    clean           清理开发环境

选项:
    -s, --service SERVICE   指定服务名称
    -d, --detach           后台运行
    -v, --verbose          详细输出
    -h, --help             显示帮助信息

示例:
    $0 start                    # 启动开发环境
    $0 test                     # 运行测试
    $0 debug                    # 启动调试模式
    $0 jupyter                  # 启动Jupyter Lab
    $0 shell                    # 进入开发容器
    $0 quality                  # 运行代码质量检查

EOF
}

# 默认配置
COMPOSE_FILE="docker-compose.dev.yml"
SERVICE=""
DETACH=false
VERBOSE=false

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--service)
                SERVICE="$2"
                shift 2
                ;;
            -d|--detach)
                DETACH=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            start|stop|restart|status|logs|shell|test|debug|jupyter|quality|clean)
                COMMAND="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查依赖
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose文件不存在: $COMPOSE_FILE"
        exit 1
    fi
}

# 设置环境变量
setup_environment() {
    export COMPOSE_PROJECT_NAME="argus-dev"
    export BROWSER="${BROWSER:-chrome}"
    export HEADLESS="${HEADLESS:-false}"
    
    if [ "$VERBOSE" = true ]; then
        export COMPOSE_LOG_LEVEL="DEBUG"
    fi
}

# 启动开发环境
start_dev() {
    log_info "启动开发环境..."
    
    # 创建必要的目录
    mkdir -p reports/allure-results
    mkdir -p reports/screenshots
    mkdir -p reports/coverage
    mkdir -p reports/logs
    mkdir -p dev-tools/mock-data
    
    if [ "$DETACH" = true ]; then
        docker-compose -f "$COMPOSE_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" up
    fi
    
    if [ "$DETACH" = true ]; then
        log_success "开发环境已在后台启动"
        log_info "访问地址:"
        log_info "  - 测试运行器: http://localhost:8000"
        log_info "  - Selenium Hub: http://localhost:4444"
        log_info "  - Jupyter Lab: http://localhost:8888"
        log_info "  - 文件服务器: http://localhost:8081"
        log_info "  - Mock API: http://localhost:1080"
        log_info "  - 覆盖率报告: http://localhost:8082"
    fi
}

# 停止开发环境
stop_dev() {
    log_info "停止开发环境..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "开发环境已停止"
}

# 重启开发环境
restart_dev() {
    log_info "重启开发环境..."
    docker-compose -f "$COMPOSE_FILE" restart
    log_success "开发环境已重启"
}

# 查看状态
show_status() {
    log_info "开发环境状态:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# 查看日志
show_logs() {
    log_info "查看开发环境日志..."
    
    if [ -n "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
    else
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# 进入开发容器shell
enter_shell() {
    log_info "进入开发容器shell..."
    
    CONTAINER="test-runner-dev"
    if [ -n "$SERVICE" ]; then
        CONTAINER="$SERVICE"
    fi
    
    docker-compose -f "$COMPOSE_FILE" exec "$CONTAINER" bash
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    docker-compose -f "$COMPOSE_FILE" exec test-runner-dev bash -c "
        echo 'Running tests in development environment...'
        pytest -v --tb=short --cov=. --cov-report=html --cov-report=term
    "
    
    log_success "测试完成，查看覆盖率报告: http://localhost:8082"
}

# 启动调试模式
start_debug() {
    log_info "启动调试模式..."
    
    log_info "调试信息:"
    log_info "  - Python调试端口: 5678"
    log_info "  - VNC端口: 5900 (密码: 无)"
    log_info "  - 在IDE中连接到 localhost:5678 进行远程调试"
    
    docker-compose -f "$COMPOSE_FILE" up test-runner-dev
}

# 启动Jupyter Lab
start_jupyter() {
    log_info "启动Jupyter Lab..."
    
    docker-compose -f "$COMPOSE_FILE" up -d dev-tools
    
    log_success "Jupyter Lab已启动"
    log_info "访问地址: http://localhost:8888"
    log_info "无需密码或token"
}

# 运行代码质量检查
run_quality_check() {
    log_info "运行代码质量检查..."
    
    docker-compose -f "$COMPOSE_FILE" run --rm code-quality
    
    log_success "代码质量检查完成"
    log_info "查看报告:"
    log_info "  - Flake8: reports/flake8-report.txt"
    log_info "  - Pylint: reports/pylint-report.txt"
    log_info "  - Bandit: reports/bandit-report.json"
    log_info "  - Safety: reports/safety-report.json"
}

# 清理开发环境
clean_dev() {
    log_warning "清理开发环境..."
    
    # 停止并删除容器
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
    
    # 清理开发镜像
    docker image prune -f --filter label=environment=development
    
    # 清理开发卷
    docker volume prune -f
    
    log_success "开发环境清理完成"
}

# 主函数
main() {
    parse_args "$@"
    
    if [ -z "$COMMAND" ]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
    
    check_dependencies
    setup_environment
    
    case "$COMMAND" in
        start)
            start_dev
            ;;
        stop)
            stop_dev
            ;;
        restart)
            restart_dev
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        shell)
            enter_shell
            ;;
        test)
            run_tests
            ;;
        debug)
            start_debug
            ;;
        jupyter)
            start_jupyter
            ;;
        quality)
            run_quality_check
            ;;
        clean)
            clean_dev
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
