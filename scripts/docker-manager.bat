@echo off
setlocal enabledelayedexpansion

REM Docker环境管理脚本 (Windows版本)
REM 用于管理Argus测试框架的Docker环境

REM 默认配置
set COMPOSE_FILE=docker-compose.yml
set ENVIRONMENT=dev
set VERBOSE=false
set SERVICE=
set COMMAND=

REM 解析命令行参数
:parse_args
if "%~1"=="" goto check_command
if "%~1"=="-s" (
    set SERVICE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--service" (
    set SERVICE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-f" (
    set COMPOSE_FILE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--file" (
    set COMPOSE_FILE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-e" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--env" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="start" (
    set COMMAND=start
    shift
    goto parse_args
)
if "%~1"=="stop" (
    set COMMAND=stop
    shift
    goto parse_args
)
if "%~1"=="restart" (
    set COMMAND=restart
    shift
    goto parse_args
)
if "%~1"=="status" (
    set COMMAND=status
    shift
    goto parse_args
)
if "%~1"=="logs" (
    set COMMAND=logs
    shift
    goto parse_args
)
if "%~1"=="clean" (
    set COMMAND=clean
    shift
    goto parse_args
)
if "%~1"=="backup" (
    set COMMAND=backup
    shift
    goto parse_args
)
if "%~1"=="restore" (
    set COMMAND=restore
    shift
    goto parse_args
)
if "%~1"=="update" (
    set COMMAND=update
    shift
    goto parse_args
)
if "%~1"=="health" (
    set COMMAND=health
    shift
    goto parse_args
)
if "%~1"=="scale" (
    set COMMAND=scale
    shift
    goto parse_args
)
if "%~1"=="monitor" (
    set COMMAND=monitor
    shift
    goto parse_args
)

echo [ERROR] 未知参数: %~1
goto show_help

:check_command
if "%COMMAND%"=="" (
    echo [ERROR] 请指定命令
    goto show_help
)

REM 检查依赖
:check_dependencies
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker未安装或未启动
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose未安装
    exit /b 1
)

if not exist "%COMPOSE_FILE%" (
    echo [ERROR] Docker Compose文件不存在: %COMPOSE_FILE%
    exit /b 1
)

REM 设置环境变量
set TEST_ENV=%ENVIRONMENT%
set COMPOSE_PROJECT_NAME=argus-%ENVIRONMENT%

REM 执行命令
if "%COMMAND%"=="start" goto start_services
if "%COMMAND%"=="stop" goto stop_services
if "%COMMAND%"=="restart" goto restart_services
if "%COMMAND%"=="status" goto show_status
if "%COMMAND%"=="logs" goto show_logs
if "%COMMAND%"=="clean" goto clean_environment
if "%COMMAND%"=="backup" goto backup_data
if "%COMMAND%"=="restore" goto restore_data
if "%COMMAND%"=="update" goto update_images
if "%COMMAND%"=="health" goto health_check
if "%COMMAND%"=="scale" goto scale_service
if "%COMMAND%"=="monitor" goto monitor_resources

echo [ERROR] 未知命令: %COMMAND%
goto show_help

:start_services
echo [INFO] 启动Docker服务...
if not "%SERVICE%"=="" (
    echo [INFO] 启动服务: %SERVICE%
    docker-compose -f "%COMPOSE_FILE%" up -d "%SERVICE%"
) else (
    echo [INFO] 启动所有服务
    docker-compose -f "%COMPOSE_FILE%" up -d
)
echo [SUCCESS] 服务启动完成
goto end

:stop_services
echo [INFO] 停止Docker服务...
if not "%SERVICE%"=="" (
    echo [INFO] 停止服务: %SERVICE%
    docker-compose -f "%COMPOSE_FILE%" stop "%SERVICE%"
) else (
    echo [INFO] 停止所有服务
    docker-compose -f "%COMPOSE_FILE%" stop
)
echo [SUCCESS] 服务停止完成
goto end

:restart_services
echo [INFO] 重启Docker服务...
if not "%SERVICE%"=="" (
    echo [INFO] 重启服务: %SERVICE%
    docker-compose -f "%COMPOSE_FILE%" restart "%SERVICE%"
) else (
    echo [INFO] 重启所有服务
    docker-compose -f "%COMPOSE_FILE%" restart
)
echo [SUCCESS] 服务重启完成
goto end

:show_status
echo [INFO] 查看服务状态...
docker-compose -f "%COMPOSE_FILE%" ps
echo.
echo [INFO] Docker系统信息:
docker system df
goto end

:show_logs
echo [INFO] 查看服务日志...
if not "%SERVICE%"=="" (
    docker-compose -f "%COMPOSE_FILE%" logs -f "%SERVICE%"
) else (
    docker-compose -f "%COMPOSE_FILE%" logs -f
)
goto end

:clean_environment
echo [WARNING] 清理Docker环境...
docker-compose -f "%COMPOSE_FILE%" down --volumes --remove-orphans
docker image prune -f
docker volume prune -f
docker network prune -f
echo [SUCCESS] 环境清理完成
goto end

:backup_data
echo [INFO] 备份数据...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set BACKUP_DIR=backups\%datestamp%
mkdir "%BACKUP_DIR%" 2>nul

REM 备份数据库
docker-compose -f "%COMPOSE_FILE%" ps postgres | findstr "Up" >nul
if not errorlevel 1 (
    echo [INFO] 备份PostgreSQL数据库...
    docker-compose -f "%COMPOSE_FILE%" exec -T postgres pg_dump -U test_user test_db > "%BACKUP_DIR%\postgres_backup.sql"
)

REM 备份报告和配置
echo [INFO] 备份报告和配置文件...
if exist reports xcopy /E /I reports "%BACKUP_DIR%\reports" >nul 2>&1
if exist configs xcopy /E /I configs "%BACKUP_DIR%\configs" >nul 2>&1

echo [SUCCESS] 数据备份完成: %BACKUP_DIR%
goto end

:restore_data
if "%SERVICE%"=="" (
    echo [ERROR] 请指定备份目录
    exit /b 1
)
set BACKUP_DIR=%SERVICE%
if not exist "%BACKUP_DIR%" (
    echo [ERROR] 备份目录不存在: %BACKUP_DIR%
    exit /b 1
)
echo [INFO] 恢复数据从: %BACKUP_DIR%
if exist "%BACKUP_DIR%\postgres_backup.sql" (
    echo [INFO] 恢复PostgreSQL数据库...
    docker-compose -f "%COMPOSE_FILE%" exec -T postgres psql -U test_user -d test_db < "%BACKUP_DIR%\postgres_backup.sql"
)
echo [SUCCESS] 数据恢复完成
goto end

:update_images
echo [INFO] 更新Docker镜像...
docker-compose -f "%COMPOSE_FILE%" pull
docker-compose -f "%COMPOSE_FILE%" build --no-cache
echo [SUCCESS] 镜像更新完成
goto end

:health_check
echo [INFO] 执行健康检查...
docker ps --filter "health=unhealthy" --format "table {{.Names}}\t{{.Status}}"
echo [INFO] 资源使用情况:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
goto end

:scale_service
if "%SERVICE%"=="" (
    echo [ERROR] 请使用 -s 参数指定服务名称和实例数，格式: service=count
    exit /b 1
)
echo [INFO] 扩缩容服务: %SERVICE%
docker-compose -f "%COMPOSE_FILE%" up -d --scale "%SERVICE%"
echo [SUCCESS] 服务扩缩容完成
goto end

:monitor_resources
echo [INFO] 监控资源使用情况...
docker stats
goto end

:show_help
echo.
echo Docker环境管理脚本 (Windows版本)
echo.
echo 用法: %~nx0 [命令] [选项]
echo.
echo 命令:
echo     start           启动所有服务
echo     stop            停止所有服务
echo     restart         重启所有服务
echo     status          查看服务状态
echo     logs            查看服务日志
echo     clean           清理环境
echo     backup          备份数据
echo     restore         恢复数据
echo     update          更新镜像
echo     health          健康检查
echo     scale           扩缩容服务
echo     monitor         监控资源使用
echo.
echo 选项:
echo     -s, --service SERVICE   指定服务名称
echo     -f, --file FILE        指定docker-compose文件
echo     -e, --env ENV          指定环境 (dev/staging/prod)
echo     -v, --verbose          详细输出
echo     -h, --help             显示帮助信息
echo.
echo 示例:
echo     %~nx0 start                    # 启动所有服务
echo     %~nx0 stop -s test-runner      # 停止测试运行器
echo     %~nx0 logs -s selenium-hub     # 查看Selenium Hub日志
echo     %~nx0 scale -s chrome-node=3   # 扩展Chrome节点到3个实例
echo     %~nx0 backup                   # 备份所有数据
echo     %~nx0 health                   # 执行健康检查
echo.
exit /b 0

:end
exit /b 0
