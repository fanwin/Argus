"""
示例测试的配置和Fixtures
为示例测试提供必要的fixtures
"""

import os
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from utilities.config_reader import config
from utilities.api_client import api_client
from utilities.selenium_wrapper import selenium_wrapper


def pytest_sessionstart(session):
    """测试会话开始时的钩子"""
    # 加载配置
    environment = os.getenv("TEST_ENV", "dev")
    config.load_config(environment)


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
    # 注意：在示例中我们不实际启动浏览器，只返回包装器实例
    # 在实际测试中，这里会启动浏览器
    yield selenium_wrapper
    
    # 在实际测试中，这里会退出浏览器
    # selenium_wrapper.quit_driver()
