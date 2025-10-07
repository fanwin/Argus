"""
API测试样例
演示如何使用框架进行API测试
"""

import pytest
import allure
from utilities.logger import log


@allure.epic("API测试样例")
@allure.feature("用户管理")
class TestSampleUserAPI:
    """用户API测试样例"""
    
    @allure.story("获取用户列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.sample
    def test_sample_get_users(self, api_client_fixture, api_config):
        """测试获取用户列表样例"""
        with allure.step("演示API测试框架功能"):
            # 这是一个示例测试，展示如何使用框架
            # 在实际测试中，这里会进行真实的API测试
            log.info("API测试框架功能演示")
            
            # 模拟API客户端使用
            log.info("创建API客户端")
            log.info("准备API请求数据")
            log.info("发送GET请求到/api/users")
            log.info("接收API响应")
            
            # 模拟响应数据验证
            log.info("验证响应状态码")
            log.info("验证响应数据结构")
            log.info("验证用户数据完整性")
            
            # 模拟断言
            assert True, "示例测试通过"
            
            # 模拟报告附件
            mock_response = {
                "users": [
                    {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
                    {"id": 2, "name": "李四", "email": "lisi@example.com"}
                ],
                "total": 2
            }
            allure.attach(
                str(mock_response),
                name="示例响应数据",
                attachment_type=allure.attachment_type.JSON
            )
