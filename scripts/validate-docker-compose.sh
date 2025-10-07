#!/bin/bash

# Docker Compose 配置验证脚本
# 用于验证 docker-compose.distributed.yml 配置是否正确

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[INFO] 开始验证 Docker Compose 配置...${NC}"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker 未安装或不在 PATH 中${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Docker 已安装${NC}"

# 检查 Docker Compose 版本
echo -e "${YELLOW}[INFO] 检查 Docker Compose 版本...${NC}"

# 尝试 docker-compose 命令
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}[✓] 使用 docker-compose: $COMPOSE_VERSION${NC}"
# 尝试 docker compose 插件
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}[✓] 使用 docker compose 插件: $COMPOSE_VERSION${NC}"
else
    echo -e "${RED}[ERROR] Docker Compose 未安装${NC}"
    exit 1
fi

# 验证配置文件语法
echo -e "${YELLOW}[INFO] 验证配置文件语法...${NC}"

if $COMPOSE_CMD -f docker-compose.distributed.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}[✓] 配置文件语法正确${NC}"
else
    echo -e "${RED}[ERROR] 配置文件语法错误:${NC}"
    $COMPOSE_CMD -f docker-compose.distributed.yml config
    exit 1
fi

# 显示配置摘要
echo -e "${YELLOW}[INFO] 配置摘要:${NC}"
echo -e "  - 服务数量: $($COMPOSE_CMD -f docker-compose.distributed.yml config --services | wc -l)"
echo -e "  - 网络: $($COMPOSE_CMD -f docker-compose.distributed.yml config --volumes | wc -l)"
echo -e "  - 卷: $($COMPOSE_CMD -f docker-compose.distributed.yml config --volumes | wc -l)"

# 列出所有服务
echo -e "${YELLOW}[INFO] 服务列表:${NC}"
$COMPOSE_CMD -f docker-compose.distributed.yml config --services | while read service; do
    echo -e "  - ${GREEN}$service${NC}"
done

# 检查必需的环境变量
echo -e "${YELLOW}[INFO] 检查环境变量...${NC}"

REQUIRED_VARS=()
OPTIONAL_VARS=("TEST_ENV" "TEST_TYPE" "BROWSER" "HEADLESS" "TIMEOUT" "REDIS_PASSWORD")

for var in "${OPTIONAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "  - ${YELLOW}$var${NC}: 未设置 (将使用默认值)"
    else
        echo -e "  - ${GREEN}$var${NC}: ${!var}"
    fi
done

# 检查 Dockerfile 是否存在
echo -e "${YELLOW}[INFO] 检查 Dockerfile...${NC}"
if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}[✓] Dockerfile 存在${NC}"
else
    echo -e "${RED}[ERROR] Dockerfile 不存在${NC}"
    exit 1
fi

# 检查必需的目录
echo -e "${YELLOW}[INFO] 检查必需的目录...${NC}"
REQUIRED_DIRS=("reports" "configs" "data")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  - ${GREEN}$dir${NC}: 存在"
    else
        echo -e "  - ${YELLOW}$dir${NC}: 不存在，将自动创建"
        mkdir -p "$dir"
    fi
done

# 检查 Docker 守护进程是否运行
echo -e "${YELLOW}[INFO] 检查 Docker 守护进程...${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}[✓] Docker 守护进程正在运行${NC}"
else
    echo -e "${RED}[ERROR] Docker 守护进程未运行${NC}"
    exit 1
fi

# 检查磁盘空间
echo -e "${YELLOW}[INFO] 检查磁盘空间...${NC}"
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    echo -e "${YELLOW}[WARNING] 可用磁盘空间不足 10GB (当前: ${AVAILABLE_SPACE}GB)${NC}"
else
    echo -e "${GREEN}[✓] 磁盘空间充足 (${AVAILABLE_SPACE}GB 可用)${NC}"
fi

# 检查内存
echo -e "${YELLOW}[INFO] 检查系统内存...${NC}"
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -lt 8 ]; then
        echo -e "${YELLOW}[WARNING] 系统内存不足 8GB (当前: ${TOTAL_MEM}GB)${NC}"
        echo -e "${YELLOW}           建议至少 8GB 内存以运行所有服务${NC}"
    else
        echo -e "${GREEN}[✓] 系统内存充足 (${TOTAL_MEM}GB)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}[✓] 验证完成！配置文件可以使用${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo -e "  1. 启动服务: ${GREEN}./scripts/run-distributed.sh start${NC}"
echo -e "  2. 查看日志: ${GREEN}$COMPOSE_CMD -f docker-compose.distributed.yml logs -f${NC}"
echo -e "  3. 停止服务: ${GREEN}./scripts/run-distributed.sh stop${NC}"
echo ""

