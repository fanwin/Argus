#!/bin/bash
# 简化版分布式测试启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Argus 分布式测试系统${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 默认配置
WORKERS=${WORKERS:-3}
TEST_ENV=${TEST_ENV:-dev}
TEST_TYPE=${TEST_TYPE:-all}

echo -e "${GREEN}配置信息:${NC}"
echo "  环境: $TEST_ENV"
echo "  类型: $TEST_TYPE"
echo "  工作节点: $WORKERS"
echo ""

# 创建必要的目录
echo -e "${BLUE}创建报告目录...${NC}"
mkdir -p reports/allure-results
mkdir -p reports/logs

# 启动服务
echo -e "${BLUE}启动分布式测试环境...${NC}"
export TEST_ENV=$TEST_ENV
export TEST_TYPE=$TEST_TYPE

# 使用 docker-compose 启动
docker-compose -f docker-compose.distributed.yml up --build

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  分布式测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"

