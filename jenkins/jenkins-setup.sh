#!/bin/bash
# Jenkins环境设置脚本
# 用于在Jenkins节点上安装和配置测试环境

set -e

echo "🚀 开始设置Jenkins测试环境..."

# 检查操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "📋 检测到操作系统: $OS"

# 设置Python版本
PYTHON_VERSION=${PYTHON_VERSION:-"3.10"}
echo "🐍 使用Python版本: $PYTHON_VERSION"

# 安装Python依赖
install_python_deps() {
    echo "📦 安装Python依赖..."
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python$PYTHON_VERSION -m venv venv
    fi
    
    # 激活虚拟环境
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装额外的Jenkins相关依赖
    pip install pytest-jenkins pytest-html-reporter pytest-metadata
    
    echo "✅ Python依赖安装完成"
}

# 安装浏览器和驱动
install_browsers() {
    echo "🌐 安装浏览器和驱动..."
    
    if [[ "$OS" == "linux" ]]; then
        # 更新包管理器
        sudo apt-get update
        
        # 安装Chrome
        if ! command -v google-chrome &> /dev/null; then
            echo "📥 安装Google Chrome..."
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
        fi
        
        # 安装Firefox
        if ! command -v firefox &> /dev/null; then
            echo "📥 安装Firefox..."
            sudo apt-get install -y firefox
        fi
        
        # 安装ChromeDriver
        echo "📥 安装ChromeDriver..."
        CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip"
        sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
        sudo chmod +x /usr/local/bin/chromedriver
        rm /tmp/chromedriver.zip
        
        # 安装GeckoDriver
        echo "📥 安装GeckoDriver..."
        GECKO_DRIVER_VERSION=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
        wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz"
        sudo tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/
        sudo chmod +x /usr/local/bin/geckodriver
        rm /tmp/geckodriver.tar.gz
        
        # 安装虚拟显示器
        sudo apt-get install -y xvfb
        
    elif [[ "$OS" == "macos" ]]; then
        # 使用Homebrew安装
        if ! command -v brew &> /dev/null; then
            echo "❌ 请先安装Homebrew"
            exit 1
        fi
        
        # 安装Chrome
        if ! command -v google-chrome &> /dev/null; then
            echo "📥 安装Google Chrome..."
            brew install --cask google-chrome
        fi
        
        # 安装Firefox
        if ! command -v firefox &> /dev/null; then
            echo "📥 安装Firefox..."
            brew install --cask firefox
        fi
        
        # 安装驱动
        brew install chromedriver geckodriver
        
    elif [[ "$OS" == "windows" ]]; then
        echo "⚠️ Windows环境请手动安装浏览器和驱动"
        echo "   或使用Docker方式运行测试"
    fi
    
    echo "✅ 浏览器和驱动安装完成"
}

# 安装Allure
install_allure() {
    echo "📊 安装Allure报告工具..."
    
    ALLURE_VERSION=${ALLURE_VERSION:-"2.24.0"}
    
    if [[ "$OS" == "linux" ]]; then
        # 安装Java (Allure依赖)
        if ! command -v java &> /dev/null; then
            sudo apt-get install -y openjdk-11-jdk
        fi
        
        # 下载并安装Allure
        wget -O /tmp/allure.tgz "https://github.com/allure-framework/allure2/releases/download/$ALLURE_VERSION/allure-$ALLURE_VERSION.tgz"
        sudo tar -xzf /tmp/allure.tgz -C /opt/
        sudo ln -sf /opt/allure-$ALLURE_VERSION/bin/allure /usr/local/bin/allure
        rm /tmp/allure.tgz
        
    elif [[ "$OS" == "macos" ]]; then
        brew install allure
        
    elif [[ "$OS" == "windows" ]]; then
        echo "⚠️ Windows环境请手动安装Allure或使用Docker"
    fi
    
    echo "✅ Allure安装完成"
}

# 创建必要的目录
create_directories() {
    echo "📁 创建必要的目录..."
    
    mkdir -p reports/allure-results
    mkdir -p reports/screenshots
    mkdir -p reports/coverage
    mkdir -p reports/logs
    mkdir -p reports/html
    
    echo "✅ 目录创建完成"
}

# 设置环境变量
setup_environment() {
    echo "🔧 设置环境变量..."
    
    # 创建环境变量文件
    cat > jenkins.env << EOF
# Jenkins测试环境变量
export PYTHONPATH=\$PWD
export TEST_ENV=\${TEST_ENV:-dev}
export BROWSER=\${BROWSER:-chrome}
export HEADLESS=\${HEADLESS:-true}
export PARALLEL_EXECUTION=\${PARALLEL_EXECUTION:-true}

# 报告目录
export REPORTS_DIR=\$PWD/reports
export ALLURE_RESULTS=\$REPORTS_DIR/allure-results
export ALLURE_REPORT=\$REPORTS_DIR/allure-report

# 显示设置（Linux）
export DISPLAY=:99

# Jenkins特定设置
export JENKINS_BUILD=true
export BUILD_NUMBER=\${BUILD_NUMBER:-local}
export BUILD_URL=\${BUILD_URL:-local}
EOF
    
    echo "✅ 环境变量设置完成"
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."
    
    # 激活虚拟环境
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # 检查Python和依赖
    python --version
    pip list | grep -E "(pytest|selenium|allure)"
    
    # 检查浏览器
    if command -v google-chrome &> /dev/null; then
        echo "✅ Chrome: $(google-chrome --version)"
    fi
    
    if command -v firefox &> /dev/null; then
        echo "✅ Firefox: $(firefox --version)"
    fi
    
    # 检查驱动
    if command -v chromedriver &> /dev/null; then
        echo "✅ ChromeDriver: $(chromedriver --version)"
    fi
    
    if command -v geckodriver &> /dev/null; then
        echo "✅ GeckoDriver: $(geckodriver --version)"
    fi
    
    # 检查Allure
    if command -v allure &> /dev/null; then
        echo "✅ Allure: $(allure --version)"
    fi
    
    # 运行框架验证
    echo "🧪 运行框架验证..."
    python test_framework.py
    
    echo "✅ 安装验证完成"
}

# 主函数
main() {
    echo "🎯 Jenkins测试环境设置开始..."
    
    # 检查是否在Jenkins环境中
    if [ -n "$JENKINS_URL" ]; then
        echo "🏗️ 检测到Jenkins环境"
    else
        echo "💻 本地环境设置"
    fi
    
    # 执行安装步骤
    install_python_deps
    
    # 只在非Docker环境中安装浏览器
    if [ -z "$DOCKER_CONTAINER" ]; then
        install_browsers
        install_allure
    else
        echo "🐳 Docker环境，跳过浏览器和Allure安装"
    fi
    
    create_directories
    setup_environment
    verify_installation
    
    echo "🎉 Jenkins测试环境设置完成！"
    echo ""
    echo "📋 使用说明："
    echo "1. 加载环境变量: source jenkins.env"
    echo "2. 激活虚拟环境: source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)"
    echo "3. 运行测试: python run_comprehensive_tests.py"
    echo "4. 查看报告: reports/ 目录"
}

# 执行主函数
main "$@"
