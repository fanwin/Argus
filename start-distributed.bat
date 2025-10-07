@echo off
REM 简化版分布式测试启动脚本 (Windows)

echo ========================================
echo   Argus 分布式测试系统
echo ========================================
echo.

REM 默认配置
if "%WORKERS%"=="" set WORKERS=3
if "%TEST_ENV%"=="" set TEST_ENV=dev
if "%TEST_TYPE%"=="" set TEST_TYPE=all

echo 配置信息:
echo   环境: %TEST_ENV%
echo   类型: %TEST_TYPE%
echo   工作节点: %WORKERS%
echo.

REM 创建必要的目录
echo 创建报告目录...
if not exist "reports\allure-results" mkdir reports\allure-results
if not exist "reports\logs" mkdir reports\logs

REM 启动服务
echo 启动分布式测试环境...
docker-compose -f docker-compose.distributed.yml up --build

echo.
echo ========================================
echo   分布式测试完成！
echo ========================================

