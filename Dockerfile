# 多阶段构建 - 基础镜像
FROM python:3.10-slim as base

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 创建非root用户
RUN groupadd --gid 1000 testuser \
    && useradd --uid 1000 --gid testuser --shell /bin/bash --create-home testuser

# 安装系统依赖和安全更新
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    unzip \
    curl \
    ca-certificates \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 构建阶段 - 安装浏览器和驱动
FROM base as browser-installer

# 安装Chrome浏览器
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装Firefox浏览器
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装Edge浏览器（Microsoft Edge）
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-edge-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-edge-keyring.gpg] https://packages.microsoft.com/repos/edge stable main" >> /etc/apt/sources.list.d/microsoft-edge.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends microsoft-edge-stable \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装虚拟显示相关工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    fluxbox \
    wmctrl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 驱动程序安装阶段
FROM browser-installer as driver-installer

# 安装ChromeDriver（使用固定版本以提高稳定性）
RUN CHROME_DRIVER_VERSION=119.0.6045.105 \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# 安装GeckoDriver（使用固定版本）
RUN GECKO_DRIVER_VERSION=v0.33.0 \
    && wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && rm /tmp/geckodriver.tar.gz \
    && chmod +x /usr/local/bin/geckodriver

# 安装EdgeDriver
RUN EDGE_DRIVER_VERSION=119.0.2151.44 \
    && wget -O /tmp/edgedriver.zip https://msedgedriver.azureedge.net/$EDGE_DRIVER_VERSION/edgedriver_linux64.zip \
    && unzip /tmp/edgedriver.zip msedgedriver -d /usr/local/bin/ \
    && rm /tmp/edgedriver.zip \
    && chmod +x /usr/local/bin/msedgedriver

# 安装Allure
RUN ALLURE_VERSION=2.24.0 \
    && wget -O /tmp/allure.tgz https://github.com/allure-framework/allure2/releases/download/$ALLURE_VERSION/allure-$ALLURE_VERSION.tgz \
    && tar -xzf /tmp/allure.tgz -C /opt/ \
    && ln -s /opt/allure-$ALLURE_VERSION/bin/allure /usr/local/bin/allure \
    && rm /tmp/allure.tgz

# Python依赖安装阶段
FROM driver-installer as python-deps

# 复制requirements文件
COPY --chown=testuser:testuser requirements.txt /tmp/requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# 最终运行时阶段
FROM python-deps as runtime

# 设置工作目录
WORKDIR /app

# 复制项目文件（排除不必要的文件）
COPY --chown=testuser:testuser . .

# 创建必要的目录并设置权限
RUN mkdir -p /app/reports/allure-results \
    && mkdir -p /app/reports/screenshots \
    && mkdir -p /app/reports/coverage \
    && mkdir -p /app/reports/logs \
    && chown -R testuser:testuser /app

# 设置显示环境变量
ENV DISPLAY=:99

# 创建优化的启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# 启动虚拟显示\n\
echo "Starting Xvfb..."\n\
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &\n\
XVFB_PID=$!\n\
\n\
# 启动窗口管理器\n\
echo "Starting window manager..."\n\
fluxbox &\n\
FLUXBOX_PID=$!\n\
\n\
# 等待X服务器启动\n\
echo "Waiting for X server to start..."\n\
for i in {1..10}; do\n\
    if xdpyinfo -display :99 >/dev/null 2>&1; then\n\
        echo "X server is ready"\n\
        break\n\
    fi\n\
    echo "Waiting for X server... ($i/10)"\n\
    sleep 1\n\
done\n\
\n\
# 清理函数\n\
cleanup() {\n\
    echo "Cleaning up..."\n\
    kill $FLUXBOX_PID 2>/dev/null || true\n\
    kill $XVFB_PID 2>/dev/null || true\n\
    exit 0\n\
}\n\
\n\
# 设置信号处理\n\
trap cleanup SIGTERM SIGINT\n\
\n\
# 执行传入的命令\n\
echo "Executing command: $@"\n\
exec "$@"' > /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh

# 切换到非root用户
USER testuser

# 设置入口点
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# 默认命令
CMD ["python", "test_framework.py"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, os; sys.exit(0 if os.path.exists('/app/test_framework.py') else 1)" || exit 1

# 标签和元数据
LABEL maintainer="argus-team@example.com"
LABEL version="2.0"
LABEL description="Automated Testing Framework with Selenium and Pytest - Multi-stage build"
LABEL org.opencontainers.image.title="Argus Testing Framework"
LABEL org.opencontainers.image.description="Comprehensive automated testing framework with Selenium, Pytest, and monitoring"
LABEL org.opencontainers.image.version="2.0"
LABEL org.opencontainers.image.vendor="Argus Team"
LABEL org.opencontainers.image.licenses="MIT"

# 暴露端口（如果需要）
EXPOSE 8000
