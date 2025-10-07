#!/bin/bash

# Docker环境管理脚本
# 用于管理Argus测试框架的Docker环境

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
Docker环境管理脚本

用法: $0 [命令] [选项]

命令:
    start           启动所有服务
    stop            停止所有服务
    restart         重启所有服务
    status          查看服务状态
    logs            查看服务日志
    clean           清理环境
    backup          备份数据
    restore         恢复数据
    update          更新镜像
    health          健康检查
    scale           扩缩容服务
    monitor         监控资源使用

选项:
    -s, --service SERVICE   指定服务名称
    -f, --file FILE        指定docker-compose文件
    -e, --env ENV          指定环境 (dev/staging/prod)
    -v, --verbose          详细输出
    -h, --help             显示帮助信息

示例:
    $0 start                    # 启动所有服务
    $0 stop -s test-runner      # 停止测试运行器
    $0 logs -s selenium-hub     # 查看Selenium Hub日志
    $0 scale -s chrome-node=3   # 扩展Chrome节点到3个实例
    $0 backup                   # 备份所有数据
    $0 health                   # 执行健康检查

EOF
}

# 默认配置
COMPOSE_FILE="docker-compose.yml"
ENVIRONMENT="dev"
VERBOSE=false
SERVICE=""

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--service)
                SERVICE="$2"
                shift 2
                ;;
            -f|--file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            start|stop|restart|status|logs|clean|backup|restore|update|health|scale|monitor)
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
    export TEST_ENV="$ENVIRONMENT"
    export COMPOSE_PROJECT_NAME="argus-${ENVIRONMENT}"
    
    if [ "$VERBOSE" = true ]; then
        export COMPOSE_LOG_LEVEL="DEBUG"
    fi
}

# 启动服务
start_services() {
    log_info "启动Docker服务..."
    
    if [ -n "$SERVICE" ]; then
        log_info "启动服务: $SERVICE"
        docker-compose -f "$COMPOSE_FILE" up -d "$SERVICE"
    else
        log_info "启动所有服务"
        docker-compose -f "$COMPOSE_FILE" up -d
    fi
    
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止Docker服务..."
    
    if [ -n "$SERVICE" ]; then
        log_info "停止服务: $SERVICE"
        docker-compose -f "$COMPOSE_FILE" stop "$SERVICE"
    else
        log_info "停止所有服务"
        docker-compose -f "$COMPOSE_FILE" stop
    fi
    
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    log_info "重启Docker服务..."
    
    if [ -n "$SERVICE" ]; then
        log_info "重启服务: $SERVICE"
        docker-compose -f "$COMPOSE_FILE" restart "$SERVICE"
    else
        log_info "重启所有服务"
        docker-compose -f "$COMPOSE_FILE" restart
    fi
    
    log_success "服务重启完成"
}

# 查看服务状态
show_status() {
    log_info "查看服务状态..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Docker系统信息:"
    docker system df
}

# 查看日志
show_logs() {
    log_info "查看服务日志..."
    
    if [ -n "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
    else
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# 清理环境
clean_environment() {
    log_warning "清理Docker环境..."
    
    # 停止并删除容器
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
    
    # 清理未使用的镜像
    docker image prune -f
    
    # 清理未使用的卷
    docker volume prune -f
    
    # 清理未使用的网络
    docker network prune -f
    
    log_success "环境清理完成"
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        log_info "备份PostgreSQL数据库..."
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U test_user test_db > "$BACKUP_DIR/postgres_backup.sql"
    fi
    
    # 备份Redis数据
    if docker-compose -f "$COMPOSE_FILE" ps redis | grep -q "Up"; then
        log_info "备份Redis数据..."
        docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli BGSAVE
        docker cp $(docker-compose -f "$COMPOSE_FILE" ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis_backup.rdb"
    fi
    
    # 备份报告和配置
    log_info "备份报告和配置文件..."
    cp -r reports "$BACKUP_DIR/" 2>/dev/null || true
    cp -r configs "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "数据备份完成: $BACKUP_DIR"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    BACKUP_DIR="$1"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi
    
    log_info "恢复数据从: $BACKUP_DIR"
    
    # 恢复数据库
    if [ -f "$BACKUP_DIR/postgres_backup.sql" ]; then
        log_info "恢复PostgreSQL数据库..."
        docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U test_user -d test_db < "$BACKUP_DIR/postgres_backup.sql"
    fi
    
    # 恢复Redis数据
    if [ -f "$BACKUP_DIR/redis_backup.rdb" ]; then
        log_info "恢复Redis数据..."
        docker cp "$BACKUP_DIR/redis_backup.rdb" $(docker-compose -f "$COMPOSE_FILE" ps -q redis):/data/dump.rdb
        docker-compose -f "$COMPOSE_FILE" restart redis
    fi
    
    log_success "数据恢复完成"
}

# 更新镜像
update_images() {
    log_info "更新Docker镜像..."
    
    # 拉取最新镜像
    docker-compose -f "$COMPOSE_FILE" pull
    
    # 重新构建自定义镜像
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    log_success "镜像更新完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查容器状态
    UNHEALTHY_CONTAINERS=$(docker ps --filter "health=unhealthy" --format "table {{.Names}}\t{{.Status}}")
    
    if [ -n "$UNHEALTHY_CONTAINERS" ]; then
        log_warning "发现不健康的容器:"
        echo "$UNHEALTHY_CONTAINERS"
    else
        log_success "所有容器都健康"
    fi
    
    # 检查资源使用
    log_info "资源使用情况:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# 扩缩容服务
scale_service() {
    if [ -z "$SERVICE" ]; then
        log_error "请使用 -s 参数指定服务名称和实例数，格式: service=count"
        exit 1
    fi
    
    log_info "扩缩容服务: $SERVICE"
    docker-compose -f "$COMPOSE_FILE" up -d --scale "$SERVICE"
    
    log_success "服务扩缩容完成"
}

# 监控资源
monitor_resources() {
    log_info "监控资源使用情况..."
    
    # 实时监控
    docker stats
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
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_environment
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$SERVICE"
            ;;
        update)
            update_images
            ;;
        health)
            health_check
            ;;
        scale)
            scale_service
            ;;
        monitor)
            monitor_resources
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
