#!/bin/bash

# Docker安全扫描脚本
# 用于检查Docker镜像和容器的安全性

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
Docker安全扫描脚本

用法: $0 [命令] [选项]

命令:
    scan-image      扫描Docker镜像
    scan-container  扫描运行中的容器
    scan-compose    扫描docker-compose配置
    benchmark       运行CIS Docker基准测试
    vulnerabilities 扫描漏洞
    compliance      合规性检查
    report          生成安全报告

选项:
    -i, --image IMAGE       指定镜像名称
    -c, --container NAME    指定容器名称
    -f, --file FILE         指定docker-compose文件
    -o, --output DIR        输出目录
    -v, --verbose           详细输出
    -h, --help              显示帮助信息

示例:
    $0 scan-image -i argus-test-runner
    $0 scan-container -c test-runner
    $0 scan-compose -f docker-compose.yml
    $0 benchmark
    $0 vulnerabilities
    $0 report -o security-reports

EOF
}

# 默认配置
IMAGE=""
CONTAINER=""
COMPOSE_FILE="docker-compose.yml"
OUTPUT_DIR="security-reports"
VERBOSE=false

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--image)
                IMAGE="$2"
                shift 2
                ;;
            -c|--container)
                CONTAINER="$2"
                shift 2
                ;;
            -f|--file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
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
            scan-image|scan-container|scan-compose|benchmark|vulnerabilities|compliance|report)
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
    local missing_tools=()
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v trivy &> /dev/null; then
        log_warning "Trivy未安装，将跳过漏洞扫描"
    fi
    
    if ! command -v hadolint &> /dev/null; then
        log_warning "Hadolint未安装，将跳过Dockerfile检查"
    fi
    
    if ! command -v docker-bench-security &> /dev/null; then
        log_warning "Docker Bench Security未安装，将跳过基准测试"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具: ${missing_tools[*]}"
        exit 1
    fi
}

# 创建输出目录
setup_output() {
    mkdir -p "$OUTPUT_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
}

# 扫描Docker镜像
scan_image() {
    if [ -z "$IMAGE" ]; then
        log_error "请使用 -i 参数指定镜像名称"
        exit 1
    fi
    
    log_info "扫描Docker镜像: $IMAGE"
    
    # 检查镜像是否存在
    if ! docker image inspect "$IMAGE" &> /dev/null; then
        log_error "镜像不存在: $IMAGE"
        exit 1
    fi
    
    # 基本信息
    log_info "获取镜像信息..."
    docker image inspect "$IMAGE" > "$OUTPUT_DIR/image_info_${TIMESTAMP}.json"
    
    # 历史记录
    docker history "$IMAGE" > "$OUTPUT_DIR/image_history_${TIMESTAMP}.txt"
    
    # 漏洞扫描
    if command -v trivy &> /dev/null; then
        log_info "运行Trivy漏洞扫描..."
        trivy image --format json --output "$OUTPUT_DIR/trivy_scan_${TIMESTAMP}.json" "$IMAGE"
        trivy image --format table --output "$OUTPUT_DIR/trivy_report_${TIMESTAMP}.txt" "$IMAGE"
    fi
    
    # 检查用户权限
    log_info "检查用户权限..."
    USER_INFO=$(docker image inspect "$IMAGE" | jq -r '.[0].Config.User // "root"')
    if [ "$USER_INFO" = "root" ] || [ "$USER_INFO" = "" ]; then
        log_warning "镜像以root用户运行，存在安全风险"
        echo "WARNING: Image runs as root user" >> "$OUTPUT_DIR/security_issues_${TIMESTAMP}.txt"
    fi
    
    # 检查暴露的端口
    log_info "检查暴露的端口..."
    EXPOSED_PORTS=$(docker image inspect "$IMAGE" | jq -r '.[0].Config.ExposedPorts // {} | keys[]' 2>/dev/null || echo "")
    if [ -n "$EXPOSED_PORTS" ]; then
        echo "Exposed ports: $EXPOSED_PORTS" >> "$OUTPUT_DIR/security_info_${TIMESTAMP}.txt"
    fi
    
    log_success "镜像扫描完成: $OUTPUT_DIR"
}

# 扫描运行中的容器
scan_container() {
    if [ -z "$CONTAINER" ]; then
        log_error "请使用 -c 参数指定容器名称"
        exit 1
    fi
    
    log_info "扫描容器: $CONTAINER"
    
    # 检查容器是否存在
    if ! docker container inspect "$CONTAINER" &> /dev/null; then
        log_error "容器不存在: $CONTAINER"
        exit 1
    fi
    
    # 容器信息
    log_info "获取容器信息..."
    docker container inspect "$CONTAINER" > "$OUTPUT_DIR/container_info_${TIMESTAMP}.json"
    
    # 进程信息
    docker exec "$CONTAINER" ps aux > "$OUTPUT_DIR/container_processes_${TIMESTAMP}.txt" 2>/dev/null || true
    
    # 网络信息
    docker exec "$CONTAINER" netstat -tulpn > "$OUTPUT_DIR/container_network_${TIMESTAMP}.txt" 2>/dev/null || true
    
    # 文件系统权限检查
    log_info "检查文件系统权限..."
    docker exec "$CONTAINER" find / -perm -4000 -type f 2>/dev/null > "$OUTPUT_DIR/suid_files_${TIMESTAMP}.txt" || true
    docker exec "$CONTAINER" find / -perm -2000 -type f 2>/dev/null > "$OUTPUT_DIR/sgid_files_${TIMESTAMP}.txt" || true
    
    # 检查运行用户
    RUNNING_USER=$(docker exec "$CONTAINER" whoami 2>/dev/null || echo "unknown")
    if [ "$RUNNING_USER" = "root" ]; then
        log_warning "容器以root用户运行，存在安全风险"
        echo "WARNING: Container runs as root user" >> "$OUTPUT_DIR/security_issues_${TIMESTAMP}.txt"
    fi
    
    # 检查特权模式
    PRIVILEGED=$(docker container inspect "$CONTAINER" | jq -r '.[0].HostConfig.Privileged')
    if [ "$PRIVILEGED" = "true" ]; then
        log_warning "容器运行在特权模式，存在高安全风险"
        echo "CRITICAL: Container runs in privileged mode" >> "$OUTPUT_DIR/security_issues_${TIMESTAMP}.txt"
    fi
    
    log_success "容器扫描完成: $OUTPUT_DIR"
}

# 扫描docker-compose配置
scan_compose() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose文件不存在: $COMPOSE_FILE"
        exit 1
    fi
    
    log_info "扫描Docker Compose配置: $COMPOSE_FILE"
    
    # 检查特权模式
    if grep -q "privileged.*true" "$COMPOSE_FILE"; then
        log_warning "发现特权模式配置"
        echo "WARNING: Privileged mode found in compose file" >> "$OUTPUT_DIR/compose_issues_${TIMESTAMP}.txt"
    fi
    
    # 检查网络模式
    if grep -q "network_mode.*host" "$COMPOSE_FILE"; then
        log_warning "发现host网络模式"
        echo "WARNING: Host network mode found" >> "$OUTPUT_DIR/compose_issues_${TIMESTAMP}.txt"
    fi
    
    # 检查卷挂载
    if grep -q "/var/run/docker.sock" "$COMPOSE_FILE"; then
        log_warning "发现Docker socket挂载"
        echo "WARNING: Docker socket mounted" >> "$OUTPUT_DIR/compose_issues_${TIMESTAMP}.txt"
    fi
    
    # 检查环境变量
    if grep -qE "(PASSWORD|SECRET|KEY).*=" "$COMPOSE_FILE"; then
        log_warning "发现明文密码或密钥"
        echo "WARNING: Plain text secrets found" >> "$OUTPUT_DIR/compose_issues_${TIMESTAMP}.txt"
    fi
    
    log_success "Compose配置扫描完成: $OUTPUT_DIR"
}

# 运行CIS Docker基准测试
run_benchmark() {
    log_info "运行CIS Docker基准测试..."
    
    if command -v docker-bench-security &> /dev/null; then
        docker run --rm --net host --pid host --userns host --cap-add audit_control \
            -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
            -v /etc:/etc:ro \
            -v /usr/bin/containerd:/usr/bin/containerd:ro \
            -v /usr/bin/runc:/usr/bin/runc:ro \
            -v /usr/lib/systemd:/usr/lib/systemd:ro \
            -v /var/lib:/var/lib:ro \
            -v /var/run/docker.sock:/var/run/docker.sock:ro \
            --label docker_bench_security \
            docker/docker-bench-security > "$OUTPUT_DIR/docker_bench_${TIMESTAMP}.txt"
        
        log_success "基准测试完成: $OUTPUT_DIR/docker_bench_${TIMESTAMP}.txt"
    else
        log_warning "Docker Bench Security未安装，跳过基准测试"
    fi
}

# 扫描漏洞
scan_vulnerabilities() {
    log_info "扫描系统漏洞..."
    
    if command -v trivy &> /dev/null; then
        # 扫描所有本地镜像
        log_info "扫描本地Docker镜像..."
        docker images --format "table {{.Repository}}:{{.Tag}}" | tail -n +2 | while read -r image; do
            if [ "$image" != "<none>:<none>" ]; then
                log_info "扫描镜像: $image"
                trivy image --format json --output "$OUTPUT_DIR/vuln_${image//[\/:]/_}_${TIMESTAMP}.json" "$image" 2>/dev/null || true
            fi
        done
        
        # 扫描文件系统
        log_info "扫描文件系统..."
        trivy fs --format json --output "$OUTPUT_DIR/fs_scan_${TIMESTAMP}.json" . 2>/dev/null || true
        
        log_success "漏洞扫描完成"
    else
        log_warning "Trivy未安装，跳过漏洞扫描"
    fi
}

# 合规性检查
compliance_check() {
    log_info "执行合规性检查..."
    
    # 检查Docker版本
    DOCKER_VERSION=$(docker version --format '{{.Server.Version}}')
    echo "Docker Version: $DOCKER_VERSION" > "$OUTPUT_DIR/compliance_${TIMESTAMP}.txt"
    
    # 检查Docker配置
    if [ -f "/etc/docker/daemon.json" ]; then
        echo "Docker daemon configuration found" >> "$OUTPUT_DIR/compliance_${TIMESTAMP}.txt"
        cat /etc/docker/daemon.json >> "$OUTPUT_DIR/compliance_${TIMESTAMP}.txt"
    else
        echo "WARNING: No Docker daemon configuration found" >> "$OUTPUT_DIR/compliance_${TIMESTAMP}.txt"
    fi
    
    # 检查用户组
    if groups | grep -q docker; then
        echo "User is in docker group" >> "$OUTPUT_DIR/compliance_${TIMESTAMP}.txt"
    fi
    
    log_success "合规性检查完成"
}

# 生成安全报告
generate_report() {
    log_info "生成安全报告..."
    
    REPORT_FILE="$OUTPUT_DIR/security_report_${TIMESTAMP}.html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Docker安全扫描报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .warning { background-color: #fff3cd; border-color: #ffeaa7; }
        .error { background-color: #f8d7da; border-color: #f5c6cb; }
        .success { background-color: #d4edda; border-color: #c3e6cb; }
        pre { background-color: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Docker安全扫描报告</h1>
        <p>生成时间: $(date)</p>
        <p>扫描目标: Docker环境</p>
    </div>
    
    <div class="section">
        <h2>扫描摘要</h2>
        <p>本报告包含了Docker环境的安全扫描结果，包括镜像漏洞、配置问题和合规性检查。</p>
    </div>
    
    <div class="section">
        <h2>发现的问题</h2>
EOF

    # 添加问题列表
    if [ -f "$OUTPUT_DIR/security_issues_${TIMESTAMP}.txt" ]; then
        echo "<div class='error'>" >> "$REPORT_FILE"
        echo "<h3>安全问题</h3>" >> "$REPORT_FILE"
        echo "<pre>" >> "$REPORT_FILE"
        cat "$OUTPUT_DIR/security_issues_${TIMESTAMP}.txt" >> "$REPORT_FILE"
        echo "</pre>" >> "$REPORT_FILE"
        echo "</div>" >> "$REPORT_FILE"
    fi
    
    # 结束HTML
    cat >> "$REPORT_FILE" << EOF
    </div>
    
    <div class="section">
        <h2>建议</h2>
        <ul>
            <li>使用非root用户运行容器</li>
            <li>定期更新基础镜像</li>
            <li>使用最小权限原则</li>
            <li>启用Docker Content Trust</li>
            <li>定期进行安全扫描</li>
        </ul>
    </div>
</body>
</html>
EOF
    
    log_success "安全报告已生成: $REPORT_FILE"
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
    setup_output
    
    case "$COMMAND" in
        scan-image)
            scan_image
            ;;
        scan-container)
            scan_container
            ;;
        scan-compose)
            scan_compose
            ;;
        benchmark)
            run_benchmark
            ;;
        vulnerabilities)
            scan_vulnerabilities
            ;;
        compliance)
            compliance_check
            ;;
        report)
            generate_report
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
