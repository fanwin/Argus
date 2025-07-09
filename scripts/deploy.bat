@echo off
setlocal enabledelayedexpansion

REM 自动化测试框架部署脚本 (Windows版本)
REM 用于部署测试环境和执行测试

REM 设置默认参数
set TEST_ENV=dev
set TEST_TYPE=all
set BROWSER=chrome
set PARALLEL=false
set USE_DOCKER=false
set CLEAN_ONLY=false
set REPORT_ONLY=false

REM 解析命令行参数
:parse_args
if "%~1"=="" goto validate_params
if "%~1"=="-e" (
    set TEST_ENV=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--env" (
    set TEST_ENV=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-t" (
    set TEST_TYPE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--type" (
    set TEST_TYPE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-b" (
    set BROWSER=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--browser" (
    set BROWSER=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-p" (
    set PARALLEL=true
    shift
    goto parse_args
)
if "%~1"=="--parallel" (
    set PARALLEL=true
    shift
    goto parse_args
)
if "%~1"=="-d" (
    set USE_DOCKER=true
    shift
    goto parse_args
)
if "%~1"=="--docker" (
    set USE_DOCKER=true
    shift
    goto parse_args
)
if "%~1"=="-c" (
    set CLEAN_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="--clean" (
    set CLEAN_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="-r" (
    set REPORT_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="--report" (
    set REPORT_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help

echo [ERROR] 未知参数: %~1
goto show_help

:show_help
echo.
echo 自动化测试框架部署脚本
echo.
echo 用法: %~nx0 [选项]
echo.
echo 选项:
echo     -e, --env ENV           设置测试环境 (dev/staging/prod)
echo     -t, --type TYPE         设置测试类型 (all/smoke/api/web/regression)
echo     -b, --browser BROWSER   设置浏览器 (chrome/firefox/edge)
echo     -p, --parallel          启用并行测试
echo     -d, --docker            使用Docker运行
echo     -c, --clean             清理环境
echo     -r, --report            只生成报告
echo     -h, --help              显示帮助信息
echo.
echo 示例:
echo     %~nx0 --env dev --type smoke --browser chrome
echo     %~nx0 --docker --env staging --type all --parallel
echo     %~nx0 --clean
echo     %~nx0 --report
echo.
exit /b 0

:validate_params
echo [INFO] 验证参数...

REM 验证测试环境
if not "%TEST_ENV%"=="dev" if not "%TEST_ENV%"=="staging" if not "%TEST_ENV%"=="prod" (
    echo [ERROR] 无效的测试环境: %TEST_ENV%
    exit /b 1
)

REM 验证测试类型
if not "%TEST_TYPE%"=="all" if not "%TEST_TYPE%"=="smoke" if not "%TEST_TYPE%"=="api" if not "%TEST_TYPE%"=="web" if not "%TEST_TYPE%"=="regression" (
    echo [ERROR] 无效的测试类型: %TEST_TYPE%
    exit /b 1
)

REM 验证浏览器
if not "%BROWSER%"=="chrome" if not "%BROWSER%"=="firefox" if not "%BROWSER%"=="edge" (
    echo [ERROR] 无效的浏览器: %BROWSER%
    exit /b 1
)

:check_dependencies
echo [INFO] 检查依赖...

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或未添加到PATH
    exit /b 1
)

REM 检查pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip 未安装或未添加到PATH
    exit /b 1
)

REM 如果使用Docker，检查Docker
if "%USE_DOCKER%"=="true" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker 未安装或未启动
        exit /b 1
    )
    
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose 未安装
        exit /b 1
    )
)

echo [SUCCESS] 依赖检查完成

:clean_environment
echo [INFO] 清理环境...

REM 停止Docker容器
if "%USE_DOCKER%"=="true" (
    docker-compose down --volumes --remove-orphans >nul 2>&1
    docker system prune -f >nul 2>&1
)

REM 清理报告目录
if exist reports (
    rmdir /s /q reports >nul 2>&1
    echo [INFO] 清理报告目录
)

REM 清理缓存
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
del /s /q *.pyc >nul 2>&1
del /s /q *.log >nul 2>&1

echo [SUCCESS] 环境清理完成

REM 如果只是清理，退出
if "%CLEAN_ONLY%"=="true" (
    echo [SUCCESS] 清理完成
    exit /b 0
)

:setup_environment
echo [INFO] 设置环境...

REM 创建必要的目录
mkdir reports\allure-results >nul 2>&1
mkdir reports\screenshots >nul 2>&1
mkdir reports\coverage >nul 2>&1
mkdir reports\logs >nul 2>&1

REM 设置环境变量
set PYTHONPATH=%CD%
set HEADLESS=true

if "%USE_DOCKER%"=="false" (
    REM 创建虚拟环境
    if not exist venv (
        echo [INFO] 创建Python虚拟环境...
        python -m venv venv
    )
    
    REM 激活虚拟环境
    call venv\Scripts\activate.bat
    
    REM 安装依赖
    echo [INFO] 安装Python依赖...
    pip install --upgrade pip
    pip install -r requirements.txt
)

echo [SUCCESS] 环境设置完成

:run_tests
if "%REPORT_ONLY%"=="true" goto generate_reports

echo [INFO] 开始运行测试...
echo [INFO] 测试环境: %TEST_ENV%
echo [INFO] 测试类型: %TEST_TYPE%
echo [INFO] 浏览器: %BROWSER%
echo [INFO] 并行执行: %PARALLEL%
echo [INFO] 使用Docker: %USE_DOCKER%

if "%USE_DOCKER%"=="true" (
    goto run_tests_docker
) else (
    goto run_tests_local
)

:run_tests_local
call venv\Scripts\activate.bat

REM 构建pytest命令
set PYTEST_CMD=pytest

REM 添加标记
if not "%TEST_TYPE%"=="all" (
    set PYTEST_CMD=!PYTEST_CMD! -m %TEST_TYPE%
)

REM 添加并行参数
if "%PARALLEL%"=="true" (
    set PYTEST_CMD=!PYTEST_CMD! -n auto
)

REM 添加报告参数
set PYTEST_CMD=!PYTEST_CMD! --alluredir=reports/allure-results
set PYTEST_CMD=!PYTEST_CMD! --html=reports/report.html --self-contained-html
set PYTEST_CMD=!PYTEST_CMD! --junitxml=reports/junit.xml
set PYTEST_CMD=!PYTEST_CMD! --cov=. --cov-report=html:reports/coverage --cov-report=xml
set PYTEST_CMD=!PYTEST_CMD! -v --tb=short

echo [INFO] 执行命令: !PYTEST_CMD!

REM 运行测试
!PYTEST_CMD!
if errorlevel 1 (
    echo [ERROR] 测试执行失败
    exit /b 1
) else (
    echo [SUCCESS] 测试执行完成
)
goto generate_reports

:run_tests_docker
echo [INFO] 构建Docker镜像...
docker-compose build test-runner

echo [INFO] 启动测试服务...
docker-compose up -d selenium-hub chrome-node firefox-node edge-node

echo [INFO] 等待Selenium Grid启动...
timeout /t 10 /nobreak >nul

REM 构建测试命令
set TEST_CMD=pytest

if not "%TEST_TYPE%"=="all" (
    set TEST_CMD=!TEST_CMD! -m %TEST_TYPE%
)

if "%PARALLEL%"=="true" (
    set TEST_CMD=!TEST_CMD! -n auto
)

set TEST_CMD=!TEST_CMD! --alluredir=reports/allure-results --html=reports/report.html --self-contained-html -v

echo [INFO] 执行测试: !TEST_CMD!
docker-compose run --rm test-runner !TEST_CMD!
if errorlevel 1 (
    echo [ERROR] 测试执行失败
    exit /b 1
) else (
    echo [SUCCESS] 测试执行完成
)

:generate_reports
echo [INFO] 生成测试报告...

REM 检查Allure是否安装
allure --version >nul 2>&1
if not errorlevel 1 (
    if exist reports\allure-results (
        dir /b reports\allure-results | findstr . >nul
        if not errorlevel 1 (
            echo [INFO] 生成Allure报告...
            allure generate reports\allure-results -o reports\allure-report --clean
            echo [SUCCESS] Allure报告生成完成: reports\allure-report\index.html
        ) else (
            echo [WARNING] 没有找到Allure测试结果
        )
    )
) else (
    echo [WARNING] Allure未安装，跳过Allure报告生成
)

REM 启动Allure服务器（如果使用Docker）
if "%USE_DOCKER%"=="true" (
    echo [INFO] 启动Allure报告服务器...
    docker-compose up -d allure-server
    echo [INFO] Allure报告服务器已启动: http://localhost:5050
)

echo [SUCCESS] 报告生成完成

:show_summary
echo [INFO] 测试结果摘要:
echo ==================================
echo 测试环境: %TEST_ENV%
echo 测试类型: %TEST_TYPE%
echo 浏览器: %BROWSER%
echo 并行执行: %PARALLEL%
echo 使用Docker: %USE_DOCKER%
echo ==================================

REM 显示报告链接
if exist reports\report.html (
    echo HTML报告: %CD%\reports\report.html
)

if exist reports\allure-report (
    echo Allure报告: %CD%\reports\allure-report\index.html
)

if exist reports\coverage (
    echo 覆盖率报告: %CD%\reports\coverage\index.html
)

if "%USE_DOCKER%"=="true" (
    echo Allure服务器: http://localhost:5050
    echo Grafana监控: http://localhost:3000 (admin/admin)
    echo Kibana日志: http://localhost:5601
)

echo [SUCCESS] 部署完成！
exit /b 0
