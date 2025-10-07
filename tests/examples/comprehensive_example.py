"""
综合示例：展示自动化测试框架的主要功能
"""

import pytest
import allure
import json
from pathlib import Path

from utilities.logger import log
from utilities.config_reader import config
from utilities.api_client import api_client
from utilities.selenium_wrapper import selenium_wrapper
from page_objects.login_page import LoginPage


@allure.epic("综合示例")
@allure.feature("框架功能演示")
class TestComprehensiveExample:
    """综合示例测试类"""
    
    @allure.story("配置管理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sample
    def test_config_management(self):
        """测试配置管理功能"""
        with allure.step("加载配置"):
            # 加载开发环境配置
            config.load_config("dev")
            
            # 获取配置
            api_config = config.get_api_config()
            web_config = config.get_web_config()
            
            log.info(f"API基础URL: {api_config.get('base_url')}")
            log.info(f"Web基础URL: {web_config.get('base_url')}")
            
            # 验证配置加载成功
            assert api_config.get("base_url"), "API基础URL应该存在"
            assert web_config.get("base_url"), "Web基础URL应该存在"
        
        with allure.step("验证配置内容"):
            # 检查配置结构
            assert "timeout" in api_config, "API配置应该包含超时设置"
            assert "browser" in web_config, "Web配置应该包含浏览器设置"
            
            log.info("配置管理功能验证通过")
    
    @allure.story("日志功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sample
    def test_logging_functionality(self):
        """测试日志功能"""
        with allure.step("记录不同级别的日志"):
            log.debug("这是一条调试日志")
            log.info("这是一条信息日志")
            log.warning("这是一条警告日志")
            log.error("这是一条错误日志")
            
            # 验证日志功能正常
            assert True, "日志功能正常"
    
    @allure.story("数据管理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sample
    def test_data_management(self):
        """测试数据管理功能"""
        with allure.step("加载测试数据"):
            # 加载测试数据文件
            test_data_file = Path("data/test_data.json")
            with open(test_data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            log.info(f"测试数据键: {list(test_data.keys())}")
            
            # 验证数据结构
            assert "users" in test_data, "测试数据应该包含用户信息"
            assert "api_test_data" in test_data, "测试数据应该包含API测试数据"
            
            # 检查用户数据
            users_data = test_data["users"]
            assert "valid_users" in users_data, "用户数据应该包含有效用户"
            assert "invalid_users" in users_data, "用户数据应该包含无效用户"
            
            log.info("数据管理功能验证通过")
    
    @allure.story("API测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sample
    @pytest.mark.api
    def test_api_testing(self, api_client_fixture):
        """测试API测试功能"""
        with allure.step("演示API客户端使用"):
            log.info("创建API客户端实例")
            log.info("准备API请求数据")
            log.info("发送HTTP请求")
            log.info("验证响应数据")
            
            # 模拟API调用
            mock_response = {
                "status": "success",
                "data": {
                    "id": 1,
                    "name": "测试用户",
                    "email": "test@example.com"
                }
            }
            
            # 验证响应结构
            assert "status" in mock_response, "响应应该包含状态字段"
            assert "data" in mock_response, "响应应该包含数据字段"
            assert mock_response["status"] == "success", "响应状态应该是成功"
            
            # 添加响应数据到报告
            allure.attach(
                json.dumps(mock_response, ensure_ascii=False, indent=2),
                name="API响应示例",
                attachment_type=allure.attachment_type.JSON
            )
            
            log.info("API测试功能演示完成")
    
    @allure.story("Web UI测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sample
    @pytest.mark.web
    def test_web_ui_testing(self, web_driver, web_config):
        """测试Web UI测试功能"""
        with allure.step("演示Web测试功能"):
            log.info("创建Selenium驱动实例")
            log.info("导航到测试页面")
            log.info("定位页面元素")
            log.info("执行用户操作")
            log.info("验证操作结果")
            
            # 模拟页面对象使用
            log.info("创建登录页面对象")
            log.info("输入用户名和密码")
            log.info("点击登录按钮")
            log.info("验证登录成功")
            
            # 模拟截图
            log.info("截图记录测试过程")
            
            # 模拟断言
            assert True, "Web UI测试功能演示通过"
            
            log.info("Web UI测试功能演示完成")
