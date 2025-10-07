@echo off
REM 分布式测试启动脚本 (Windows)
REM 提供便捷的分布式测试启动和管理功能

setlocal enabledelayedexpansion

REM 默认配置
set TEST_ENV=dev
set TEST_TYPE=all
set WORKERS=3
set BROWSER=chrome
set HEADLESS=true
set TIMEOUT=3600
set COMPOSE_FILE=docker-compose.distributed.yml

REM 解析命令行参数
set COMMAND=%1
shift

:parse_args
if "%1"=="" goto end_parse
if "%1"=="--env" (
    set TEST_ENV=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--type" (
    set TEST_TYPE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--workers" (
    set WORKERS=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--browser" (
    set BROWSER=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--headless" (
    set HEADLESS=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--timeout" (
    set TIMEOUT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="-h" goto show_help
if "%1"=="--help" goto show_help
shift
goto parse_args

:end_parse

REM 检查命令
if "%COMMAND%"=="" (
    echo [ERROR] 请指定命令
    goto show_help
)

REM 执行命令
if "%COMMAND%"=="start" goto start_distributed
if "%COMMAND%"=="stop" goto stop_distributed
if "%COMMAND%"=="restart" goto restart_distributed
if "%COMMAND%"=="status" goto show_status
if "%COMMAND%"=="logs" goto show_logs
if "%COMMAND%"=="scale" goto scale_workers
if "%COMMAND%"=="clean" goto clean_environment
if "%COMMAND%"=="monitor" goto open_monitor
if "%COMMAND%"=="help" goto show_help

echo [ERROR] 未知命令: %COMMAND%
goto show_help

:show_help
echo.
echo Argus 分布式测试启动脚本 (Windows)
echo.
echo 用法: %~nx0 [命令] [选项]
echo.
echo 命令:
echo   start           启动分布式测试环境
echo   stop            停止分布式测试环境
echo   restart         重启分布式测试环境
echo   status          查看服务状态
echo   logs            查看日志
echo   scale           扩展工作节点
echo   clean           清理环境
echo   monitor         打开监控面板
echo   help            显示帮助信息
echo.
echo 选项:
echo   --env ENV       测试环境 (dev/staging/prod)，默认: dev
echo   --type TYPE     测试类型 (api/web/smoke/all)，默认: all
echo   --workers N     工作节点数量，默认: 3
echo   --browser B     浏览器类型 (chrome/firefox/edge)，默认: chrome
echo   --headless      无头模式，默认: true
echo   --timeout N     超时时间（秒），默认: 3600
echo.
echo 示例:
echo   %~nx0 start
echo   %~nx0 start --workers 5 --type api
echo   %~nx0 start --env staging --type smoke
echo   %~nx0 scale --workers 10
echo   %~nx0 logs
echo   %~nx0 stop
echo.
goto end

:start_distributed
echo [INFO] 启动分布式测试环境
echo [INFO] 配置信息:
echo [INFO]   环境: %TEST_ENV%
echo [INFO]   类型: %TEST_TYPE%
echo [INFO]   工作节点: %WORKERS%
echo [INFO]   浏览器: %BROWSER%
echo [INFO]   无头模式: %HEADLESS%
echo [INFO]   超时: %TIMEOUT%s

REM 创建报告目录
if not exist "reports\allure-results" mkdir reports\allure-results
if not exist "reports\logs" mkdir reports\logs

REM 启动服务
echo [INFO] 启动 Redis 和 Selenium Grid...
docker-compose -f %COMPOSE_FILE% up -d redis selenium-hub chrome-node firefox-node

REM 等待服务就绪
echo [INFO] 等待服务启动...
timeout /t 10 /nobreak >nul

REM 启动工作节点
echo [INFO] 启动 %WORKERS% 个工作节点...
docker-compose -f %COMPOSE_FILE% up -d --scale test-worker-1=%WORKERS% test-worker-1

REM 启动控制器
echo [INFO] 启动测试控制器...
docker-compose -f %COMPOSE_FILE% up test-controller

echo [SUCCESS] 分布式测试完成
goto end

:stop_distributed
echo [INFO] 停止分布式测试环境
docker-compose -f %COMPOSE_FILE% down
echo [SUCCESS] 服务已停止
goto end

:restart_distributed
echo [INFO] 重启分布式测试环境
call :stop_distributed
timeout /t 2 /nobreak >nul
call :start_distributed
goto end

:show_status
echo [INFO] 服务状态:
docker-compose -f %COMPOSE_FILE% ps

echo.
echo [INFO] Redis 状态:
docker-compose -f %COMPOSE_FILE% exec -T redis redis-cli ping

echo.
echo [INFO] Selenium Grid 状态:
curl -s http://localhost:4444/wd/hub/status
goto end

:show_logs
echo [INFO] 查看日志 (Ctrl+C 退出)
docker-compose -f %COMPOSE_FILE% logs -f
goto end

:scale_workers
echo [INFO] 扩展工作节点到 %WORKERS% 个
docker-compose -f %COMPOSE_FILE% up -d --scale test-worker-1=%WORKERS% test-worker-1
echo [SUCCESS] 工作节点已扩展到 %WORKERS% 个
goto end

:clean_environment
echo [WARNING] 清理分布式测试环境
set /p CONFIRM="确认清理所有数据? (y/N): "
if /i "%CONFIRM%"=="y" (
    echo [INFO] 停止所有服务...
    docker-compose -f %COMPOSE_FILE% down -v
    
    echo [INFO] 清理报告目录...
    if exist "reports\allure-results" del /q reports\allure-results\*
    if exist "reports\logs" del /q reports\logs\*
    
    echo [SUCCESS] 环境已清理
) else (
    echo [INFO] 取消清理
)
goto end

:open_monitor
echo [INFO] 打开监控面板

REM 检查服务是否运行
docker-compose -f %COMPOSE_FILE% ps | findstr "redis-commander" >nul
if errorlevel 1 (
    echo [INFO] 启动 Redis Commander...
    docker-compose -f %COMPOSE_FILE% up -d redis-commander
    timeout /t 3 /nobreak >nul
)

echo [INFO] 监控面板地址:
echo [INFO]   Redis Commander: http://localhost:8081
echo [INFO]   Selenium Grid:   http://localhost:4444
echo [INFO]   Allure Report:   http://localhost:5050

REM 打开浏览器
start http://localhost:8081
goto end

:end
endlocal
exit /b 0

