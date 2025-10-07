#!/bin/bash
# 分布式测试启动脚本
# 提供便捷的分布式测试启动和管理功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
Argus 分布式测试启动脚本

用法: $0 [命令] [选项]

命令:
  start           启动分布式测试环境
  stop            停止分布式测试环境
  restart         重启分布式测试环境
  status          查看服务状态
  logs            查看日志
  scale           扩展工作节点
  clean           清理环境
  monitor         打开监控面板

选项:
  --env ENV       测试环境 (dev/staging/prod)，默认: dev
  --type TYPE     测试类型 (api/web/smoke/all)，默认: all
  --workers N     工作节点数量，默认: 3
  --browser B     浏览器类型 (chrome/firefox/edge)，默认: chrome
  --headless      无头模式，默认: true
  --timeout N     超时时间（秒），默认: 3600

示例:
  # 启动默认配置（3个工作节点）
  $0 start

  # 启动5个工作节点执行API测试
  $0 start --workers 5 --type api

  # 启动预发布环境的冒烟测试
  $0 start --env staging --type smoke

  # 扩展到10个工作节点
  $0 scale --workers 10

  # 查看实时日志
  $0 logs

  # 停止所有服务
  $0 stop

EOF
}

# 默认配置
TEST_ENV=${TEST_ENV:-dev}
TEST_TYPE=${TEST_TYPE:-all}
WORKERS=${WORKERS:-3}
BROWSER=${BROWSER:-chrome}
HEADLESS=${HEADLESS:-true}
TIMEOUT=${TIMEOUT:-3600}
COMPOSE_FILE="docker-compose.distributed.yml"

# 解析命令行参数
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|logs|scale|clean|monitor)
            COMMAND=$1
            shift
            ;;
        --env)
            TEST_ENV="$2"
            shift 2
            ;;
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --headless)
            HEADLESS="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查命令
if [ -z "$COMMAND" ]; then
    log_error "请指定命令"
    show_help
    exit 1
fi

# 检查 Docker 和 Docker Compose
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
}

# 启动分布式测试
start_distributed() {
    log_info "启动分布式测试环境"
    log_info "配置信息:"
    log_info "  环境: $TEST_ENV"
    log_info "  类型: $TEST_TYPE"
    log_info "  工作节点: $WORKERS"
    log_info "  浏览器: $BROWSER"
    log_info "  无头模式: $HEADLESS"
    log_info "  超时: ${TIMEOUT}s"
    
    # 设置环境变量
    export TEST_ENV=$TEST_ENV
    export TEST_TYPE=$TEST_TYPE
    export BROWSER=$BROWSER
    export HEADLESS=$HEADLESS
    export TIMEOUT=$TIMEOUT
    
    # 创建报告目录
    mkdir -p reports/allure-results
    mkdir -p reports/logs
    
    # 启动服务
    log_info "启动 Redis 和 Selenium Grid..."
    docker-compose -f $COMPOSE_FILE up -d redis selenium-hub chrome-node firefox-node
    
    # 等待服务就绪
    log_info "等待服务启动..."
    sleep 10
    
    # 启动工作节点
    log_info "启动 $WORKERS 个工作节点..."
    docker-compose -f $COMPOSE_FILE up -d --scale test-worker-1=$WORKERS test-worker-1
    
    # 启动控制器
    log_info "启动测试控制器..."
    docker-compose -f $COMPOSE_FILE up test-controller
    
    log_success "分布式测试完成"
}

# 停止分布式测试
stop_distributed() {
    log_info "停止分布式测试环境"
    docker-compose -f $COMPOSE_FILE down
    log_success "服务已停止"
}

# 重启分布式测试
restart_distributed() {
    log_info "重启分布式测试环境"
    stop_distributed
    sleep 2
    start_distributed
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "Redis 状态:"
    docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping || log_warning "Redis 未运行"
    
    echo ""
    log_info "Selenium Grid 状态:"
    curl -s http://localhost:4444/wd/hub/status | python -m json.tool || log_warning "Selenium Grid 未运行"
}

# 查看日志
show_logs() {
    log_info "查看日志 (Ctrl+C 退出)"
    docker-compose -f $COMPOSE_FILE logs -f
}

# 扩展工作节点
scale_workers() {
    log_info "扩展工作节点到 $WORKERS 个"
    docker-compose -f $COMPOSE_FILE up -d --scale test-worker-1=$WORKERS test-worker-1
    log_success "工作节点已扩展到 $WORKERS 个"
}

# 清理环境
clean_environment() {
    log_warning "清理分布式测试环境"
    read -p "确认清理所有数据? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "停止所有服务..."
        docker-compose -f $COMPOSE_FILE down -v
        
        log_info "清理报告目录..."
        rm -rf reports/allure-results/*
        rm -rf reports/logs/*
        
        log_success "环境已清理"
    else
        log_info "取消清理"
    fi
}

# 打开监控面板
open_monitor() {
    log_info "打开监控面板"
    
    # 检查服务是否运行
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "redis-commander"; then
        log_info "启动 Redis Commander..."
        docker-compose -f $COMPOSE_FILE up -d redis-commander
        sleep 3
    fi
    
    log_info "监控面板地址:"
    log_info "  Redis Commander: http://localhost:8081"
    log_info "  Selenium Grid:   http://localhost:4444"
    log_info "  Allure Report:   http://localhost:5050"
    
    # 尝试打开浏览器
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8081
    elif command -v open &> /dev/null; then
        open http://localhost:8081
    fi
}

# 主逻辑
check_dependencies

case $COMMAND in
    start)
        start_distributed
        ;;
    stop)
        stop_distributed
        ;;
    restart)
        restart_distributed
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    scale)
        scale_workers
        ;;
    clean)
        clean_environment
        ;;
    monitor)
        open_monitor
        ;;
    *)
        log_error "未知命令: $COMMAND"
        show_help
        exit 1
        ;;
esac

exit 0

