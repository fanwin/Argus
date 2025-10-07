"""
测试配置文件
为所有测试模块提供通用的fixtures和配置
"""

import os
import pytest
import allure
from pathlib import Path
from typing import Generator

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from utilities.config_reader import config
from utilities.logger import log
from utilities.api_client import api_client
from utilities.selenium_wrapper import selenium_wrapper
from utilities.data_generator import DataGenerator
from utilities.data_validator import DataValidator


def pytest_configure(config_obj):
    """Pytest配置钩子"""
    # 确保报告目录存在
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    (reports_dir / "screenshots").mkdir(exist_ok=True)
    (reports_dir / "allure-results").mkdir(exist_ok=True)
    (reports_dir / "coverage").mkdir(exist_ok=True)
    (reports_dir / "logs").mkdir(exist_ok=True)


def pytest_sessionstart(session):
    """测试会话开始时的钩子"""
    # 加载配置
    environment = os.getenv("TEST_ENV", "dev")
    try:
        config.load_config(environment)
        log.info(f"测试配置加载成功: {environment}")
    except Exception as e:
        log.warning(f"配置加载失败: {e}，使用默认配置")


def pytest_runtest_makereport(item, call):
    """测试报告生成钩子"""
    if call.when == "call":
        # 测试失败时自动截图
        if call.excinfo is not None and hasattr(item, "funcargs"):
            if "web_driver" in item.funcargs:
                driver_fixture = item.funcargs["web_driver"]
                if hasattr(driver_fixture, "driver") and driver_fixture.driver:
                    screenshot_path = selenium_wrapper.take_screenshot_on_failure(item.name)
                    if screenshot_path:
                        # 添加截图到Allure报告
                        allure.attach.file(
                            screenshot_path,
                            name="失败截图",
                            attachment_type=allure.attachment_type.PNG
                        )


# ==========================================
# 通用Fixtures
# ==========================================

@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    return config.get_config()


@pytest.fixture(scope="session")
def api_config():
    """API配置fixture"""
    return config.get_api_config()


@pytest.fixture(scope="session")
def web_config():
    """Web配置fixture"""
    return config.get_web_config()


@pytest.fixture(scope="function")
def api_client_fixture():
    """API客户端fixture"""
    # 重新初始化API客户端以确保使用最新配置
    api_client.__init__()
    yield api_client
    # 清理认证信息
    api_client.remove_auth()


@pytest.fixture(scope="function")
def web_driver():
    """Web驱动fixture"""
    driver_wrapper = selenium_wrapper
    driver_wrapper.start_driver()
    yield driver_wrapper
    driver_wrapper.quit_driver()


@pytest.fixture(scope="function")
def data_generator():
    """数据生成器fixture"""
    return DataGenerator()


@pytest.fixture(scope="function")
def data_validator():
    """数据验证器fixture"""
    return DataValidator()


# ==========================================
# 性能测试Fixtures
# ==========================================

@pytest.fixture(scope="function")
def performance_test_config():
    """性能测试配置"""
    return {
        "max_response_time": 5000,  # 最大响应时间(ms)
        "concurrent_users": 5,      # 并发用户数
        "total_requests": 20,       # 总请求数
        "success_rate_threshold": 0.95  # 成功率阈值
    }


# ==========================================
# 安全测试Fixtures
# ==========================================

@pytest.fixture(scope="function")
def security_test_config():
    """安全测试配置"""
    return {
        "sql_injection_payloads": [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --"
        ],
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ],
        "security_headers": [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
    }


# ==========================================
# 移动端测试Fixtures
# ==========================================

@pytest.fixture(scope="function")
def mobile_test_config():
    """移动端测试配置"""
    return {
        "android_device": {
            "platform_name": "Android",
            "platform_version": "11.0",
            "device_name": "Android Emulator",
            "app_package": "com.android.chrome",
            "app_activity": "com.google.android.apps.chrome.Main"
        },
        "ios_device": {
            "platform_name": "iOS",
            "platform_version": "15.0",
            "device_name": "iPhone 13",
            "bundle_id": "com.apple.mobilesafari"
        }
    }


# ==========================================
# 可访问性测试Fixtures
# ==========================================

@pytest.fixture(scope="function")
def accessibility_test_config():
    """可访问性测试配置"""
    return {
        "wcag_level": "AA",  # WCAG合规级别
        "color_contrast_ratio": 4.5,  # 颜色对比度比例
        "check_images": True,
        "check_forms": True,
        "check_headings": True,
        "check_keyboard_nav": True
    }


# ==========================================
# 数据驱动测试Fixtures
# ==========================================

@pytest.fixture(scope="function")
def test_data_config():
    """测试数据配置"""
    return {
        "data_sources": {
            "json": "data/test_data.json",
            "csv": "data/test_data.csv",
            "yaml": "data/test_data.yaml"
        },
        "generated_data_count": {
            "users": 10,
            "products": 15,
            "orders": 8,
            "companies": 5
        }
    }


# ==========================================
# 集成测试Fixtures
# ==========================================

@pytest.fixture(scope="function")
def integration_test_config():
    """集成测试配置"""
    return {
        "services": {
            "api_service": "https://httpbin.org",
            "web_service": "https://owasp.org/www-project-webgoat/",
            "json_service": "https://jsonplaceholder.typicode.com"
        },
        "timeout": 30,
        "retry_count": 3,
        "health_check_interval": 60
    }


# ==========================================
# 测试环境清理
# ==========================================

@pytest.fixture(scope="function", autouse=True)
def test_cleanup():
    """测试清理fixture"""
    yield
    
    # 测试后清理
    try:
        # 清理临时文件
        temp_files = Path("reports").glob("temp_*")
        for temp_file in temp_files:
            if temp_file.is_file():
                temp_file.unlink()
        
        # 清理测试数据
        test_data_files = [
            "data/generated_test_data.json",
            "data/products_test.csv",
            "data/api_scenarios.yaml"
        ]
        
        for file_path in test_data_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                file_obj.unlink()
                
    except Exception as e:
        log.warning(f"测试清理时出现异常: {e}")


# ==========================================
# 自定义标记
# ==========================================

def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line(
        "markers", "comprehensive: 综合测试标记"
    )
    config.addinivalue_line(
        "markers", "cross_platform: 跨平台测试标记"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端测试标记"
    )
    config.addinivalue_line(
        "markers", "health_check: 健康检查测试标记"
    )
    config.addinivalue_line(
        "markers", "network: 网络相关测试标记"
    )
    config.addinivalue_line(
        "markers", "keyboard: 键盘操作测试标记"
    )
    config.addinivalue_line(
        "markers", "aria: ARIA属性测试标记"
    )
    config.addinivalue_line(
        "markers", "wcag: WCAG合规性测试标记"
    )
    config.addinivalue_line(
        "markers", "android: Android平台测试标记"
    )
    config.addinivalue_line(
        "markers", "ios: iOS平台测试标记"
    )


# ==========================================
# 跳过条件
# ==========================================

def pytest_collection_modifyitems(config, items):
    """修改测试项集合"""
    # 根据环境变量跳过某些测试
    skip_mobile = pytest.mark.skip(reason="移动端测试环境不可用")
    skip_security = pytest.mark.skip(reason="安全测试在CI环境中跳过")
    
    for item in items:
        # 如果没有Appium环境，跳过移动端测试
        if "mobile" in item.keywords:
            try:
                from utilities.mobile_tester import APPIUM_AVAILABLE
                if not APPIUM_AVAILABLE:
                    item.add_marker(skip_mobile)
            except ImportError:
                item.add_marker(skip_mobile)
        
        # 在CI环境中跳过某些安全测试
        if "security" in item.keywords and os.getenv("CI"):
            if "comprehensive" in item.keywords:
                item.add_marker(skip_security)
