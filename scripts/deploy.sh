#!/bin/bash

# 自动化测试框架部署脚本
# 用于部署测试环境和执行测试

set -e  # 遇到错误立即退出

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
自动化测试框架部署脚本

用法: $0 [选项]

选项:
    -e, --env ENV           设置测试环境 (dev/staging/prod)
    -t, --type TYPE         设置测试类型 (all/smoke/api/web/regression)
    -b, --browser BROWSER   设置浏览器 (chrome/firefox/edge)
    -p, --parallel          启用并行测试
    -d, --docker            使用Docker运行
    -c, --clean             清理环境
    -r, --report            只生成报告
    -h, --help              显示帮助信息

示例:
    $0 --env dev --type smoke --browser chrome
    $0 --docker --env staging --type all --parallel
    $0 --clean
    $0 --report

EOF
}

# 默认参数
TEST_ENV="dev"
TEST_TYPE="all"
BROWSER="chrome"
PARALLEL=false
USE_DOCKER=false
CLEAN_ONLY=false
REPORT_ONLY=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            TEST_ENV="$2"
            shift 2
            ;;
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -d|--docker)
            USE_DOCKER=true
            shift
            ;;
        -c|--clean)
            CLEAN_ONLY=true
            shift
            ;;
        -r|--report)
            REPORT_ONLY=true
            shift
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

# 验证参数
validate_params() {
    if [[ ! "$TEST_ENV" =~ ^(dev|staging|prod)$ ]]; then
        log_error "无效的测试环境: $TEST_ENV"
        exit 1
    fi

    if [[ ! "$TEST_TYPE" =~ ^(all|smoke|api|web|regression)$ ]]; then
        log_error "无效的测试类型: $TEST_TYPE"
        exit 1
    fi

    if [[ ! "$BROWSER" =~ ^(chrome|firefox|edge)$ ]]; then
        log_error "无效的浏览器: $BROWSER"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi

    # 如果使用Docker，检查Docker和Docker Compose
    if [ "$USE_DOCKER" = true ]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker 未安装"
            exit 1
        fi

        if ! command -v docker-compose &> /dev/null; then
            log_error "Docker Compose 未安装"
            exit 1
        fi
    fi

    log_success "依赖检查完成"
}

# 清理环境
clean_environment() {
    log_info "清理环境..."

    # 停止Docker容器
    if [ "$USE_DOCKER" = true ]; then
        docker-compose down --volumes --remove-orphans 2>/dev/null || true
        docker system prune -f 2>/dev/null || true
    fi

    # 清理报告目录
    if [ -d "reports" ]; then
        rm -rf reports/*
        log_info "清理报告目录"
    fi

    # 清理缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    # 清理日志文件
    find . -name "*.log" -delete 2>/dev/null || true

    log_success "环境清理完成"
}

# 设置环境
setup_environment() {
    log_info "设置环境..."

    # 创建必要的目录
    mkdir -p reports/allure-results
    mkdir -p reports/screenshots
    mkdir -p reports/coverage
    mkdir -p reports/logs

    # 设置环境变量
    export TEST_ENV="$TEST_ENV"
    export BROWSER="$BROWSER"
    export HEADLESS="true"
    export PYTHONPATH="$(pwd)"

    if [ "$USE_DOCKER" = false ]; then
        # 创建虚拟环境
        if [ ! -d "venv" ]; then
            log_info "创建Python虚拟环境..."
            python3 -m venv venv
        fi

        # 激活虚拟环境
        source venv/bin/activate

        # 安装依赖
        log_info "安装Python依赖..."
        pip install --upgrade pip
        pip install -r requirements.txt
    fi

    log_success "环境设置完成"
}

# 运行测试
run_tests() {
    log_info "开始运行测试..."
    log_info "测试环境: $TEST_ENV"
    log_info "测试类型: $TEST_TYPE"
    log_info "浏览器: $BROWSER"
    log_info "并行执行: $PARALLEL"
    log_info "使用Docker: $USE_DOCKER"

    if [ "$USE_DOCKER" = true ]; then
        run_tests_docker
    else
        run_tests_local
    fi
}

# 本地运行测试
run_tests_local() {
    source venv/bin/activate

    # 构建pytest命令
    PYTEST_CMD="pytest"

    # 添加标记
    if [ "$TEST_TYPE" != "all" ]; then
        PYTEST_CMD="$PYTEST_CMD -m $TEST_TYPE"
    fi

    # 添加并行参数
    if [ "$PARALLEL" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -n auto"
    fi

    # 添加报告参数
    PYTEST_CMD="$PYTEST_CMD --alluredir=reports/allure-results"
    PYTEST_CMD="$PYTEST_CMD --html=reports/report.html --self-contained-html"
    PYTEST_CMD="$PYTEST_CMD --junitxml=reports/junit.xml"
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=html:reports/coverage --cov-report=xml"
    PYTEST_CMD="$PYTEST_CMD -v --tb=short"

    log_info "执行命令: $PYTEST_CMD"
    
    # 运行测试
    if eval $PYTEST_CMD; then
        log_success "测试执行完成"
    else
        log_error "测试执行失败"
        return 1
    fi
}

# Docker运行测试
run_tests_docker() {
    # 设置Docker环境变量
    export TEST_ENV="$TEST_ENV"
    export BROWSER="$BROWSER"
    export HEADLESS="true"

    # 构建Docker镜像
    log_info "构建Docker镜像..."
    docker-compose build test-runner

    # 启动服务
    log_info "启动测试服务..."
    docker-compose up -d selenium-hub chrome-node firefox-node edge-node

    # 等待服务启动
    log_info "等待Selenium Grid启动..."
    sleep 10

    # 构建测试命令
    TEST_CMD="pytest"
    
    if [ "$TEST_TYPE" != "all" ]; then
        TEST_CMD="$TEST_CMD -m $TEST_TYPE"
    fi

    if [ "$PARALLEL" = true ]; then
        TEST_CMD="$TEST_CMD -n auto"
    fi

    TEST_CMD="$TEST_CMD --alluredir=reports/allure-results --html=reports/report.html --self-contained-html -v"

    # 运行测试
    log_info "执行测试: $TEST_CMD"
    if docker-compose run --rm test-runner $TEST_CMD; then
        log_success "测试执行完成"
    else
        log_error "测试执行失败"
        return 1
    fi
}

# 生成报告
generate_reports() {
    log_info "生成测试报告..."

    # 检查Allure是否安装
    if command -v allure &> /dev/null; then
        if [ -d "reports/allure-results" ] && [ "$(ls -A reports/allure-results)" ]; then
            log_info "生成Allure报告..."
            allure generate reports/allure-results -o reports/allure-report --clean
            log_success "Allure报告生成完成: reports/allure-report/index.html"
        else
            log_warning "没有找到Allure测试结果"
        fi
    else
        log_warning "Allure未安装，跳过Allure报告生成"
    fi

    # 启动Allure服务器（如果使用Docker）
    if [ "$USE_DOCKER" = true ]; then
        log_info "启动Allure报告服务器..."
        docker-compose up -d allure-server
        log_info "Allure报告服务器已启动: http://localhost:5050"
    fi

    log_success "报告生成完成"
}

# 显示结果摘要
show_summary() {
    log_info "测试结果摘要:"
    echo "=================================="
    echo "测试环境: $TEST_ENV"
    echo "测试类型: $TEST_TYPE"
    echo "浏览器: $BROWSER"
    echo "并行执行: $PARALLEL"
    echo "使用Docker: $USE_DOCKER"
    echo "=================================="

    # 显示报告链接
    if [ -f "reports/report.html" ]; then
        echo "HTML报告: $(pwd)/reports/report.html"
    fi

    if [ -d "reports/allure-report" ]; then
        echo "Allure报告: $(pwd)/reports/allure-report/index.html"
    fi

    if [ -d "reports/coverage" ]; then
        echo "覆盖率报告: $(pwd)/reports/coverage/index.html"
    fi

    if [ "$USE_DOCKER" = true ]; then
        echo "Allure服务器: http://localhost:5050"
        echo "Grafana监控: http://localhost:3000 (admin/admin)"
        echo "Kibana日志: http://localhost:5601"
    fi
}

# 主函数
main() {
    log_info "开始部署自动化测试框架..."

    # 验证参数
    validate_params

    # 检查依赖
    check_dependencies

    # 如果只是清理，执行清理后退出
    if [ "$CLEAN_ONLY" = true ]; then
        clean_environment
        log_success "清理完成"
        exit 0
    fi

    # 清理环境
    clean_environment

    # 如果只是生成报告，跳过测试执行
    if [ "$REPORT_ONLY" = false ]; then
        # 设置环境
        setup_environment

        # 运行测试
        if ! run_tests; then
            log_error "测试执行失败"
            exit 1
        fi
    fi

    # 生成报告
    generate_reports

    # 显示摘要
    show_summary

    log_success "部署完成！"
}

# 捕获中断信号
trap 'log_warning "脚本被中断"; clean_environment; exit 1' INT TERM

# 执行主函数
main "$@"
