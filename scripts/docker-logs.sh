#!/bin/bash

# Docker日志管理脚本
# 用于收集、分析和管理Docker容器日志

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
Docker日志管理脚本

用法: $0 [命令] [选项]

命令:
    collect         收集所有容器日志
    analyze         分析日志内容
    clean           清理旧日志
    export          导出日志
    monitor         实时监控日志
    search          搜索日志内容
    stats           显示日志统计信息
    rotate          轮转日志文件

选项:
    -s, --service SERVICE   指定服务名称
    -d, --days DAYS        保留天数 (默认: 7)
    -o, --output DIR       输出目录 (默认: logs)
    -f, --format FORMAT    输出格式 (json/text/csv)
    -q, --query QUERY      搜索查询
    -t, --tail LINES       显示最后N行 (默认: 100)
    -v, --verbose          详细输出
    -h, --help             显示帮助信息

示例:
    $0 collect                      # 收集所有日志
    $0 analyze -s test-runner       # 分析测试运行器日志
    $0 clean -d 3                   # 清理3天前的日志
    $0 search -q "ERROR"            # 搜索错误日志
    $0 monitor -s selenium-hub      # 监控Selenium Hub日志
    $0 export -f json -o /tmp/logs  # 导出JSON格式日志

EOF
}

# 默认配置
COMPOSE_FILE="docker-compose.yml"
SERVICE=""
DAYS=7
OUTPUT_DIR="logs"
FORMAT="text"
QUERY=""
TAIL_LINES=100
VERBOSE=false

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--service)
                SERVICE="$2"
                shift 2
                ;;
            -d|--days)
                DAYS="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -f|--format)
                FORMAT="$2"
                shift 2
                ;;
            -q|--query)
                QUERY="$2"
                shift 2
                ;;
            -t|--tail)
                TAIL_LINES="$2"
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
            collect|analyze|clean|export|monitor|search|stats|rotate)
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
}

# 获取容器列表
get_containers() {
    if [ -n "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" ps -q "$SERVICE"
    else
        docker-compose -f "$COMPOSE_FILE" ps -q
    fi
}

# 收集日志
collect_logs() {
    log_info "收集Docker容器日志..."
    
    mkdir -p "$OUTPUT_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        LOG_FILE="$OUTPUT_DIR/${CONTAINER_NAME}_${TIMESTAMP}.log"
        
        log_info "收集容器日志: $CONTAINER_NAME"
        
        if [ "$VERBOSE" = true ]; then
            docker logs "$container" > "$LOG_FILE" 2>&1
        else
            docker logs "$container" > "$LOG_FILE" 2>/dev/null
        fi
        
        # 压缩日志文件
        gzip "$LOG_FILE"
        log_success "日志已保存: ${LOG_FILE}.gz"
    done
    
    log_success "日志收集完成"
}

# 分析日志
analyze_logs() {
    log_info "分析Docker容器日志..."
    
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        
        log_info "分析容器: $CONTAINER_NAME"
        
        # 获取日志统计
        TOTAL_LINES=$(docker logs "$container" 2>&1 | wc -l)
        ERROR_LINES=$(docker logs "$container" 2>&1 | grep -i "error" | wc -l)
        WARNING_LINES=$(docker logs "$container" 2>&1 | grep -i "warning\|warn" | wc -l)
        
        echo "  总行数: $TOTAL_LINES"
        echo "  错误行数: $ERROR_LINES"
        echo "  警告行数: $WARNING_LINES"
        
        # 显示最近的错误
        if [ "$ERROR_LINES" -gt 0 ]; then
            echo "  最近的错误:"
            docker logs "$container" 2>&1 | grep -i "error" | tail -3 | sed 's/^/    /'
        fi
        
        echo ""
    done
}

# 清理旧日志
clean_logs() {
    log_info "清理 $DAYS 天前的日志文件..."
    
    if [ ! -d "$OUTPUT_DIR" ]; then
        log_warning "日志目录不存在: $OUTPUT_DIR"
        return
    fi
    
    # 清理本地日志文件
    DELETED_COUNT=$(find "$OUTPUT_DIR" -name "*.log*" -mtime +$DAYS -delete -print | wc -l)
    log_success "已删除 $DELETED_COUNT 个旧日志文件"
    
    # 清理Docker日志
    log_info "清理Docker容器日志..."
    docker system prune -f --filter "until=${DAYS}d"
    
    log_success "日志清理完成"
}

# 导出日志
export_logs() {
    log_info "导出日志 (格式: $FORMAT)"
    
    mkdir -p "$OUTPUT_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    case "$FORMAT" in
        json)
            export_json_logs "$TIMESTAMP"
            ;;
        csv)
            export_csv_logs "$TIMESTAMP"
            ;;
        text|*)
            export_text_logs "$TIMESTAMP"
            ;;
    esac
}

# 导出JSON格式日志
export_json_logs() {
    local timestamp="$1"
    local output_file="$OUTPUT_DIR/logs_${timestamp}.json"
    
    echo "[" > "$output_file"
    
    local first=true
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        
        if [ "$first" = false ]; then
            echo "," >> "$output_file"
        fi
        first=false
        
        echo "  {" >> "$output_file"
        echo "    \"container\": \"$CONTAINER_NAME\"," >> "$output_file"
        echo "    \"logs\": [" >> "$output_file"
        
        docker logs "$container" 2>&1 | tail -"$TAIL_LINES" | while IFS= read -r line; do
            echo "      \"$(echo "$line" | sed 's/"/\\"/g')\"," >> "$output_file"
        done
        
        # 移除最后一个逗号
        sed -i '$ s/,$//' "$output_file"
        
        echo "    ]" >> "$output_file"
        echo "  }" >> "$output_file"
    done
    
    echo "]" >> "$output_file"
    
    log_success "JSON日志已导出: $output_file"
}

# 导出CSV格式日志
export_csv_logs() {
    local timestamp="$1"
    local output_file="$OUTPUT_DIR/logs_${timestamp}.csv"
    
    echo "Container,Timestamp,Level,Message" > "$output_file"
    
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        
        docker logs -t "$container" 2>&1 | tail -"$TAIL_LINES" | while IFS= read -r line; do
            # 简单解析日志行
            timestamp=$(echo "$line" | cut -d' ' -f1)
            level="INFO"
            message=$(echo "$line" | cut -d' ' -f2-)
            
            if echo "$line" | grep -qi "error"; then
                level="ERROR"
            elif echo "$line" | grep -qi "warning\|warn"; then
                level="WARNING"
            fi
            
            echo "\"$CONTAINER_NAME\",\"$timestamp\",\"$level\",\"$(echo "$message" | sed 's/"/\\"/g')\"" >> "$output_file"
        done
    done
    
    log_success "CSV日志已导出: $output_file"
}

# 导出文本格式日志
export_text_logs() {
    local timestamp="$1"
    local output_file="$OUTPUT_DIR/logs_${timestamp}.txt"
    
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        
        echo "=== $CONTAINER_NAME ===" >> "$output_file"
        docker logs "$container" 2>&1 | tail -"$TAIL_LINES" >> "$output_file"
        echo "" >> "$output_file"
    done
    
    log_success "文本日志已导出: $output_file"
}

# 监控日志
monitor_logs() {
    log_info "实时监控Docker容器日志..."
    
    if [ -n "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
    else
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# 搜索日志
search_logs() {
    if [ -z "$QUERY" ]; then
        log_error "请使用 -q 参数指定搜索查询"
        exit 1
    fi
    
    log_info "搜索日志内容: $QUERY"
    
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        
        MATCHES=$(docker logs "$container" 2>&1 | grep -i "$QUERY")
        
        if [ -n "$MATCHES" ]; then
            echo "=== $CONTAINER_NAME ==="
            echo "$MATCHES"
            echo ""
        fi
    done
}

# 显示日志统计
show_stats() {
    log_info "显示日志统计信息..."
    
    echo "容器日志统计:"
    echo "=============="
    
    for container in $(get_containers); do
        if [ -z "$container" ]; then
            continue
        fi
        
        CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
        
        # 获取日志大小
        LOG_SIZE=$(docker logs "$container" 2>&1 | wc -c)
        LOG_LINES=$(docker logs "$container" 2>&1 | wc -l)
        
        # 转换字节为可读格式
        if [ "$LOG_SIZE" -gt 1048576 ]; then
            LOG_SIZE_HUMAN="$(($LOG_SIZE / 1048576))MB"
        elif [ "$LOG_SIZE" -gt 1024 ]; then
            LOG_SIZE_HUMAN="$(($LOG_SIZE / 1024))KB"
        else
            LOG_SIZE_HUMAN="${LOG_SIZE}B"
        fi
        
        printf "%-20s %10s %10s\n" "$CONTAINER_NAME" "$LOG_SIZE_HUMAN" "$LOG_LINES lines"
    done
}

# 轮转日志
rotate_logs() {
    log_info "轮转Docker日志文件..."
    
    # 收集当前日志
    collect_logs
    
    # 重启容器以清空日志
    if [ -n "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" restart "$SERVICE"
    else
        log_warning "轮转所有容器日志需要重启所有服务，请手动执行"
        log_info "建议命令: docker-compose restart"
    fi
    
    log_success "日志轮转完成"
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
    
    case "$COMMAND" in
        collect)
            collect_logs
            ;;
        analyze)
            analyze_logs
            ;;
        clean)
            clean_logs
            ;;
        export)
            export_logs
            ;;
        monitor)
            monitor_logs
            ;;
        search)
            search_logs
            ;;
        stats)
            show_stats
            ;;
        rotate)
            rotate_logs
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
