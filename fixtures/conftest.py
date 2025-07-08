"""
全局测试配置和Fixtures
提供测试环境初始化、清理和通用测试工具
"""

import os
import pytest
import allure
from pathlib import Path
from typing import Generator

from utilities.config_reader import config
from utilities.logger import log
from utilities.api_client import api_client
from utilities.selenium_wrapper import selenium_wrapper


def pytest_configure(config):
    """Pytest配置钩子"""
    # 确保报告目录存在
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    (reports_dir / "screenshots").mkdir(exist_ok=True)
    (reports_dir / "allure-results").mkdir(exist_ok=True)
    (reports_dir / "coverage").mkdir(exist_ok=True)


def pytest_sessionstart(session):
    """测试会话开始时的钩子"""
    # 加载配置
    environment = os.getenv("TEST_ENV", "dev")
    config.load_config(environment)
    
    # 配置日志
    from utilities.logger import log as logger_instance
    logger_instance.configure_from_config(config.get_config())
    
    log.info(f"测试会话开始，环境: {environment}")
    log.info(f"配置文件: {config.get_current_environment()}")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时的钩子"""
    log.info(f"测试会话结束，退出状态: {exitstatus}")


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


@pytest.fixture(scope="session")
def test_data():
    """测试数据fixture"""
    return config.get_test_data_config()


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
    # 启动浏览器
    selenium_wrapper.start_driver()
    
    yield selenium_wrapper
    
    # 清理：退出浏览器
    selenium_wrapper.quit_driver()


@pytest.fixture(scope="function")
def authenticated_api_client(api_client_fixture, test_data):
    """已认证的API客户端fixture"""
    # 这里可以添加登录逻辑
    # 例如：使用测试数据中的用户信息进行登录
    admin_user = test_data.get("users", {}).get("admin", {})
    
    if admin_user:
        # 示例：登录获取token（需要根据实际API调整）
        login_data = {
            "username": admin_user.get("username"),
            "password": admin_user.get("password")
        }
        
        try:
            # 这里应该调用实际的登录API
            # response = api_client_fixture.post("/auth/login", json_data=login_data)
            # token = response.json().get("token")
            # api_client_fixture.set_auth_token(token)
            log.info("API客户端认证配置完成")
        except Exception as e:
            log.warning(f"API客户端认证失败: {e}")
    
    yield api_client_fixture


@pytest.fixture(scope="function")
def logged_in_web_driver(web_driver, test_data):
    """已登录的Web驱动fixture"""
    # 导航到登录页面
    web_config = config.get_web_config()
    base_url = web_config.get("base_url", "")
    
    if base_url:
        login_url = f"{base_url}/login"
        web_driver.navigate_to(login_url)
        
        # 这里可以添加自动登录逻辑
        # 例如：使用测试数据中的用户信息进行登录
        admin_user = test_data.get("users", {}).get("admin", {})
        
        if admin_user:
            try:
                # 示例登录逻辑（需要根据实际页面调整）
                # from selenium.webdriver.common.by import By
                # web_driver.send_keys((By.ID, "username"), admin_user.get("username"))
                # web_driver.send_keys((By.ID, "password"), admin_user.get("password"))
                # web_driver.click((By.ID, "login-button"))
                log.info("Web驱动登录配置完成")
            except Exception as e:
                log.warning(f"Web驱动自动登录失败: {e}")
    
    yield web_driver


@pytest.fixture(autouse=True)
def test_logger(request):
    """自动日志记录fixture"""
    test_name = request.node.name
    log.info(f"开始测试: {test_name}")
    
    yield
    
    log.info(f"结束测试: {test_name}")


@pytest.fixture
def temp_file():
    """临时文件fixture"""
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    yield temp_file_path
    
    # 清理临时文件
    try:
        os.unlink(temp_file_path)
    except OSError:
        pass


# Pytest标记
pytestmark = [
    pytest.mark.filterwarnings("ignore::UserWarning"),
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]
