"""
用户API测试用例
测试用户相关的API接口功能
"""

import json
import pytest
import allure
from pathlib import Path

from utilities.api_client import APIClient
from utilities.logger import log


@allure.epic("API测试")
@allure.feature("用户管理")
class TestUserAPI:
    """用户API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """设置测试数据"""
        # 加载测试数据
        test_data_file = Path("data/test_data.json")
        with open(test_data_file, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
        
        self.api_test_data = self.test_data["api_test_data"]
    
    @allure.story("用户创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    def test_create_user_success(self, api_client_fixture):
        """测试成功创建用户"""
        with allure.step("准备测试数据"):
            user_data = self.api_test_data["user_creation"][0]
            expected_status = user_data.pop("expected_status")
        
        with allure.step("发送创建用户请求"):
            response = api_client_fixture.post("/api/users", json_data=user_data)
        
        with allure.step("验证响应"):
            api_client_fixture.assert_status_code(response, expected_status)
            
            response_data = api_client_fixture.get_response_json(response)
            
            # 验证返回的用户信息
            assert response_data["name"] == user_data["name"]
            assert response_data["email"] == user_data["email"]
            assert response_data["age"] == user_data["age"]
            assert response_data["department"] == user_data["department"]
            assert "id" in response_data
            
            log.info(f"用户创建成功，ID: {response_data.get('id')}")
        
        # 添加响应到Allure报告
        allure.attach(
            response.text,
            name="API响应",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("用户创建")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.parametrize("user_data", [
        pytest.param(data, id=f"invalid_user_{i}") 
        for i, data in enumerate(json.loads(Path("data/test_data.json").read_text(encoding='utf-8'))["api_test_data"]["invalid_requests"])
    ])
    def test_create_user_invalid_data(self, api_client_fixture, user_data):
        """测试使用无效数据创建用户"""
        with allure.step("准备无效测试数据"):
            expected_status = user_data.pop("expected_status")
            expected_error = user_data.pop("expected_error")
        
        with allure.step("发送创建用户请求"):
            response = api_client_fixture.post("/api/users", json_data=user_data)
        
        with allure.step("验证错误响应"):
            api_client_fixture.assert_status_code(response, expected_status)
            
            response_data = api_client_fixture.get_response_json(response)
            
            # 验证错误信息
            assert "error" in response_data
            assert expected_error in response_data["error"]
            
            log.info(f"无效数据测试通过，错误信息: {response_data['error']}")
        
        # 添加响应到Allure报告
        allure.attach(
            response.text,
            name="错误响应",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("用户查询")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.regression
    def test_get_user_list(self, api_client_fixture):
        """测试获取用户列表"""
        with allure.step("发送获取用户列表请求"):
            response = api_client_fixture.get("/api/users")
        
        with allure.step("验证响应"):
            api_client_fixture.assert_status_code(response, 200)
            
            response_data = api_client_fixture.get_response_json(response)
            
            # 验证响应结构
            assert "users" in response_data
            assert "total" in response_data
            assert "page" in response_data
            assert "page_size" in response_data
            
            # 验证用户列表
            users = response_data["users"]
            assert isinstance(users, list)
            
            if users:  # 如果有用户数据
                user = users[0]
                required_fields = ["id", "name", "email", "department"]
                for field in required_fields:
                    assert field in user, f"用户对象缺少字段: {field}"
            
            log.info(f"获取到 {len(users)} 个用户")
        
        # 添加响应到Allure报告
        allure.attach(
            response.text,
            name="用户列表响应",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("用户查询")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_user_by_id(self, api_client_fixture):
        """测试根据ID获取用户"""
        user_id = 1  # 假设存在ID为1的用户
        
        with allure.step(f"发送获取用户请求，ID: {user_id}"):
            response = api_client_fixture.get(f"/api/users/{user_id}")
        
        with allure.step("验证响应"):
            if response.status_code == 200:
                response_data = api_client_fixture.get_response_json(response)
                
                # 验证用户信息
                assert response_data["id"] == user_id
                required_fields = ["name", "email", "department"]
                for field in required_fields:
                    assert field in response_data, f"用户对象缺少字段: {field}"
                
                log.info(f"成功获取用户信息: {response_data['name']}")
                
            elif response.status_code == 404:
                log.info(f"用户不存在，ID: {user_id}")
                response_data = api_client_fixture.get_response_json(response)
                assert "error" in response_data
            else:
                pytest.fail(f"意外的状态码: {response.status_code}")
        
        # 添加响应到Allure报告
        allure.attach(
            response.text,
            name="用户详情响应",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("用户更新")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_update_user(self, api_client_fixture):
        """测试更新用户信息"""
        # 首先创建一个用户
        with allure.step("创建测试用户"):
            create_data = self.api_test_data["user_creation"][0].copy()
            create_data.pop("expected_status", None)
            
            create_response = api_client_fixture.post("/api/users", json_data=create_data)
            
            if create_response.status_code == 201:
                user_data = api_client_fixture.get_response_json(create_response)
                user_id = user_data["id"]
            else:
                pytest.skip("无法创建测试用户，跳过更新测试")
        
        # 更新用户信息
        with allure.step("更新用户信息"):
            update_data = self.api_test_data["user_update"][0].copy()
            expected_status = update_data.pop("expected_status")
            update_data.pop("id", None)  # 移除ID字段
            
            response = api_client_fixture.put(f"/api/users/{user_id}", json_data=update_data)
        
        with allure.step("验证更新响应"):
            api_client_fixture.assert_status_code(response, expected_status)
            
            response_data = api_client_fixture.get_response_json(response)
            
            # 验证更新后的信息
            assert response_data["id"] == user_id
            assert response_data["name"] == update_data["name"]
            assert response_data["email"] == update_data["email"]
            
            log.info(f"用户更新成功，ID: {user_id}")
        
        # 添加响应到Allure报告
        allure.attach(
            response.text,
            name="更新响应",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.story("用户删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_delete_user(self, api_client_fixture):
        """测试删除用户"""
        # 首先创建一个用户
        with allure.step("创建测试用户"):
            create_data = self.api_test_data["user_creation"][1].copy()
            create_data.pop("expected_status", None)
            
            create_response = api_client_fixture.post("/api/users", json_data=create_data)
            
            if create_response.status_code == 201:
                user_data = api_client_fixture.get_response_json(create_response)
                user_id = user_data["id"]
            else:
                pytest.skip("无法创建测试用户，跳过删除测试")
        
        # 删除用户
        with allure.step("删除用户"):
            response = api_client_fixture.delete(f"/api/users/{user_id}")
        
        with allure.step("验证删除响应"):
            api_client_fixture.assert_status_code(response, 204)
            log.info(f"用户删除成功，ID: {user_id}")
        
        # 验证用户已被删除
        with allure.step("验证用户已被删除"):
            get_response = api_client_fixture.get(f"/api/users/{user_id}")
            api_client_fixture.assert_status_code(get_response, 404)
            log.info("确认用户已被删除")
    
    @allure.story("认证测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.security
    def test_unauthorized_access(self, api_client_fixture):
        """测试未授权访问"""
        with allure.step("移除认证信息"):
            api_client_fixture.remove_auth()
        
        with allure.step("尝试访问受保护的资源"):
            response = api_client_fixture.get("/api/users")
        
        with allure.step("验证未授权响应"):
            api_client_fixture.assert_status_code(response, 401)
            
            response_data = api_client_fixture.get_response_json(response)
            assert "error" in response_data
            assert "unauthorized" in response_data["error"].lower()
            
            log.info("未授权访问测试通过")
        
        # 添加响应到Allure报告
        allure.attach(
            response.text,
            name="未授权响应",
            attachment_type=allure.attachment_type.JSON
        )
