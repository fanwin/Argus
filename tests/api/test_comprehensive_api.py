"""
综合API测试案例
展示API测试的各种功能：CRUD操作、认证、错误处理、数据验证等
"""

import json
import pytest
import allure
from pathlib import Path
from typing import Dict, Any

from utilities.api_client import APIClient
from utilities.logger import log
from utilities.data_generator import DataGenerator
from utilities.data_validator import DataValidator


@allure.epic("综合API测试")
@allure.feature("RESTful API完整测试")
class TestComprehensiveAPI:
    """综合API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self, api_config):
        """设置测试环境"""
        self.api_client = APIClient()
        self.data_generator = DataGenerator()
        self.data_validator = DataValidator()
        
        # 使用httpbin.org作为测试API
        self.base_url = "https://httpbin.org"
        self.api_client.base_url = self.base_url
        
        # 生成测试数据
        self.test_users = self.data_generator.generate_user_data(5)
        self.test_products = self.data_generator.generate_product_data(3)
        
        log.info(f"API测试环境初始化完成，基础URL: {self.base_url}")
    
    @allure.story("HTTP方法测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    def test_http_methods_comprehensive(self):
        """测试各种HTTP方法"""
        
        with allure.step("测试GET请求"):
            response = self.api_client.get("/get", params={"test": "value"})
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert "args" in response_data
            assert response_data["args"]["test"] == "value"
            log.info("GET请求测试通过")
        
        with allure.step("测试POST请求"):
            test_data = {"name": "测试用户", "email": "test@example.com"}
            response = self.api_client.post("/post", json_data=test_data)
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert "json" in response_data
            assert response_data["json"]["name"] == test_data["name"]
            log.info("POST请求测试通过")
        
        with allure.step("测试PUT请求"):
            update_data = {"name": "更新用户", "status": "active"}
            response = self.api_client.put("/put", json_data=update_data)
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert response_data["json"]["name"] == update_data["name"]
            log.info("PUT请求测试通过")
        
        with allure.step("测试DELETE请求"):
            response = self.api_client.delete("/delete")
            self.api_client.assert_status_code(response, 200)
            log.info("DELETE请求测试通过")
    
    @allure.story("请求头和认证测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_headers_and_auth(self):
        """测试请求头和认证功能"""
        
        with allure.step("测试自定义请求头"):
            custom_headers = {
                "X-Custom-Header": "test-value",
                "User-Agent": "AutoTest/1.0"
            }
            response = self.api_client.get("/headers", headers=custom_headers)
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            headers = response_data["headers"]
            assert headers["X-Custom-Header"] == "test-value"
            assert "AutoTest/1.0" in headers["User-Agent"]
            log.info("自定义请求头测试通过")
        
        with allure.step("测试Basic认证"):
            # 设置Basic认证
            self.api_client.set_basic_auth("testuser", "testpass")
            response = self.api_client.get("/basic-auth/testuser/testpass")
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert response_data["authenticated"] is True
            assert response_data["user"] == "testuser"
            log.info("Basic认证测试通过")
        
        with allure.step("测试Bearer Token认证"):
            # 设置Bearer Token
            test_token = "test-bearer-token-12345"
            self.api_client.set_bearer_token(test_token)
            response = self.api_client.get("/bearer", headers={"Authorization": f"Bearer {test_token}"})
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert response_data["authenticated"] is True
            assert response_data["token"] == test_token
            log.info("Bearer Token认证测试通过")
    
    @allure.story("数据验证测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.regression
    def test_data_validation(self):
        """测试数据验证功能"""
        
        with allure.step("测试JSON数据验证"):
            # 定义期望的JSON Schema
            expected_schema = {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "args": {"type": "object"},
                    "headers": {"type": "object"},
                    "origin": {"type": "string"}
                },
                "required": ["url", "args", "headers", "origin"]
            }
            
            response = self.api_client.get("/get")
            response_data = self.api_client.get_response_json(response)
            
            # 使用数据验证器验证响应
            validation_result = self.data_validator.validate_api_response(
                response_data, expected_schema
            )
            
            assert validation_result["valid"], f"数据验证失败: {validation_result['errors']}"
            log.info("JSON数据验证测试通过")
        
        with allure.step("测试用户数据验证"):
            # 生成并验证用户数据
            user_data = self.test_users[0]
            
            # 验证邮箱格式
            assert self.data_validator.validate_email(user_data["email"]), "邮箱格式无效"
            
            # 验证用户名长度
            assert self.data_validator.validate_string_length(
                user_data["username"], min_length=3, max_length=20
            ), "用户名长度无效"
            
            log.info(f"用户数据验证通过: {user_data['username']}")
    
    @allure.story("错误处理测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_error_handling(self):
        """测试错误处理和状态码"""
        
        with allure.step("测试404错误"):
            response = self.api_client.get("/status/404")
            self.api_client.assert_status_code(response, 404)
            log.info("404错误处理测试通过")
        
        with allure.step("测试500错误"):
            response = self.api_client.get("/status/500")
            self.api_client.assert_status_code(response, 500)
            log.info("500错误处理测试通过")
        
        with allure.step("测试超时处理"):
            # 测试延迟响应
            response = self.api_client.get("/delay/2")  # 2秒延迟
            self.api_client.assert_status_code(response, 200)
            log.info("超时处理测试通过")
        
        with allure.step("测试重定向"):
            response = self.api_client.get("/redirect/3")  # 3次重定向
            self.api_client.assert_status_code(response, 200)
            log.info("重定向处理测试通过")
    
    @allure.story("批量数据处理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.slow
    def test_batch_operations(self):
        """测试批量数据处理"""
        
        with allure.step("批量创建用户数据"):
            created_users = []
            
            for i, user in enumerate(self.test_users[:3]):  # 只测试前3个用户
                with allure.step(f"创建用户 {i+1}: {user['username']}"):
                    response = self.api_client.post("/post", json_data=user)
                    self.api_client.assert_status_code(response, 200)
                    
                    response_data = self.api_client.get_response_json(response)
                    created_users.append(response_data["json"])
                    
                    log.info(f"用户创建成功: {user['username']}")
            
            assert len(created_users) == 3, "应该创建3个用户"
            log.info(f"批量创建完成，共创建 {len(created_users)} 个用户")
        
        with allure.step("验证批量数据一致性"):
            for i, (original, created) in enumerate(zip(self.test_users[:3], created_users)):
                assert created["username"] == original["username"], f"用户{i+1}用户名不匹配"
                assert created["email"] == original["email"], f"用户{i+1}邮箱不匹配"
            
            log.info("批量数据一致性验证通过")
    
    @allure.story("API性能基准测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    @pytest.mark.performance
    def test_api_performance_baseline(self):
        """测试API性能基准"""
        import time
        
        with allure.step("测试单个请求性能"):
            start_time = time.time()
            response = self.api_client.get("/get")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            self.api_client.assert_status_code(response, 200)
            assert response_time < 5000, f"响应时间过长: {response_time:.2f}ms"
            
            log.info(f"API响应时间: {response_time:.2f}ms")
            
            # 添加性能数据到Allure报告
            allure.attach(
                f"响应时间: {response_time:.2f}ms",
                name="性能数据",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("内容类型测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_content_types(self):
        """测试不同内容类型的处理"""
        
        with allure.step("测试JSON内容类型"):
            json_data = {"message": "Hello JSON", "timestamp": "2024-01-01T00:00:00Z"}
            response = self.api_client.post("/post", json_data=json_data)
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert response_data["json"]["message"] == json_data["message"]
            log.info("JSON内容类型测试通过")
        
        with allure.step("测试表单数据"):
            form_data = {"username": "testuser", "password": "testpass"}
            response = self.api_client.post("/post", data=form_data)
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            assert response_data["form"]["username"] == form_data["username"]
            log.info("表单数据测试通过")
        
        with allure.step("测试XML响应"):
            response = self.api_client.get("/xml")
            self.api_client.assert_status_code(response, 200)
            
            # 验证响应是XML格式
            assert "xml" in response.headers.get("content-type", "").lower()
            assert "<?xml" in response.text
            log.info("XML响应测试通过")
