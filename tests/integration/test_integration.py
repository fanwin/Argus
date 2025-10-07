"""
集成测试案例
展示集成测试功能：端到端测试、系统集成、服务间通信等
"""

import pytest
import allure
import time
import json
from typing import Dict, Any, List

from utilities.api_client import APIClient
from utilities.selenium_wrapper import SeleniumWrapper
from utilities.data_generator import DataGenerator
from utilities.logger import log


@allure.epic("集成测试")
@allure.feature("端到端系统集成验证")
class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_integration_test(self):
        """设置集成测试环境"""
        self.api_client = APIClient()
        self.data_generator = DataGenerator()
        
        # 测试服务端点
        self.services = {
            "api_service": "https://httpbin.org",
            "web_service": "https://owasp.org/www-project-webgoat/",
            "json_service": "https://jsonplaceholder.typicode.com"
        }
        
        # 存储测试过程中创建的数据
        self.test_data_store = {}
        
        log.info("集成测试环境初始化完成")
        
        yield
        
        # 清理测试数据
        self._cleanup_test_data()
    
    def _cleanup_test_data(self):
        """清理测试数据"""
        log.info("清理集成测试数据")
        # 在实际环境中，这里会清理创建的测试数据
        self.test_data_store.clear()
    
    @allure.story("API服务集成测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.api
    def test_api_service_integration(self):
        """测试API服务集成"""
        
        with allure.step("测试API服务连通性"):
            # 测试基础连通性
            response = self.api_client.get(f"{self.services['api_service']}/get")
            self.api_client.assert_status_code(response, 200)
            
            log.info("API服务连通性测试通过")
        
        with allure.step("测试数据创建流程"):
            # 生成测试用户数据
            user_data = self.data_generator.generate_user_data(1)[0]
            
            # 模拟创建用户
            create_response = self.api_client.post(
                f"{self.services['api_service']}/post",
                json_data=user_data
            )
            self.api_client.assert_status_code(create_response, 200)
            
            # 从响应中提取用户信息
            response_data = self.api_client.get_response_json(create_response)
            created_user = response_data["json"]
            
            # 存储创建的用户数据供后续测试使用
            self.test_data_store["created_user"] = created_user
            
            log.info(f"用户创建成功: {created_user['username']}")
        
        with allure.step("测试数据查询流程"):
            # 模拟查询用户信息
            query_params = {"username": created_user["username"]}
            query_response = self.api_client.get(
                f"{self.services['api_service']}/get",
                params=query_params
            )
            self.api_client.assert_status_code(query_response, 200)
            
            query_data = self.api_client.get_response_json(query_response)
            
            # 验证查询参数正确传递
            assert query_data["args"]["username"] == created_user["username"]
            
            log.info("用户查询测试通过")
        
        with allure.step("测试数据更新流程"):
            # 更新用户信息
            updated_data = created_user.copy()
            updated_data["email"] = f"updated_{updated_data['email']}"
            
            update_response = self.api_client.put(
                f"{self.services['api_service']}/put",
                json_data=updated_data
            )
            self.api_client.assert_status_code(update_response, 200)
            
            update_result = self.api_client.get_response_json(update_response)
            
            # 验证更新成功
            assert update_result["json"]["email"] == updated_data["email"]
            
            log.info("用户更新测试通过")
        
        with allure.step("生成API集成测试报告"):
            api_integration_report = f"""
API服务集成测试报告:
- 服务端点: {self.services['api_service']}
- 测试用户: {created_user['username']}
- 创建操作: ✅ 成功
- 查询操作: ✅ 成功  
- 更新操作: ✅ 成功
- 数据一致性: ✅ 验证通过

测试流程:
1. 连通性验证
2. 用户数据创建
3. 用户信息查询
4. 用户信息更新
5. 数据一致性验证
            """
            
            allure.attach(
                api_integration_report,
                name="API集成测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("Web服务集成测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    @pytest.mark.web
    def test_web_service_integration(self):
        """测试Web服务集成"""
        
        driver_wrapper = SeleniumWrapper()
        
        try:
            with allure.step("启动Web浏览器"):
                driver_wrapper.start_driver()
                log.info("Web浏览器启动成功")
            
            with allure.step("测试Web服务访问"):
                # 访问Web服务
                driver_wrapper.navigate_to(self.services["web_service"])
                driver_wrapper.wait_for_element_visible(("tag name", "body"))
                
                # 验证页面加载
                page_title = driver_wrapper.get_page_title()
                assert "WebGoat" in page_title, f"页面标题不正确: {page_title}"
                
                log.info(f"Web服务访问成功: {page_title}")
            
            with allure.step("测试页面交互"):
                # 获取页面信息
                page_info = driver_wrapper.execute_script("""
                    return {
                        url: window.location.href,
                        title: document.title,
                        linksCount: document.links.length,
                        formsCount: document.forms.length
                    };
                """)
                
                # 验证页面基本元素
                assert page_info["linksCount"] > 0, "页面应该包含链接"
                
                log.info(f"页面交互测试通过: {page_info['linksCount']} 个链接")
            
            with allure.step("测试响应式功能"):
                # 测试不同屏幕尺寸
                screen_sizes = [(1920, 1080), (768, 1024), (375, 667)]
                
                for width, height in screen_sizes:
                    driver_wrapper.driver.set_window_size(width, height)
                    time.sleep(1)
                    
                    # 验证页面在不同尺寸下正常显示
                    body_element = driver_wrapper.find_element(("tag name", "body"))
                    assert body_element.is_displayed(), f"页面在 {width}x{height} 尺寸下应该正常显示"
                
                log.info("响应式功能测试通过")
            
            with allure.step("截图记录"):
                screenshot_path = driver_wrapper.take_screenshot("web_integration_test.png")
                if screenshot_path:
                    allure.attach.file(
                        screenshot_path,
                        name="Web集成测试截图",
                        attachment_type=allure.attachment_type.PNG
                    )
        
        finally:
            driver_wrapper.quit_driver()
    
    @allure.story("跨服务数据流测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.cross_service
    def test_cross_service_data_flow(self):
        """测试跨服务数据流"""
        
        with allure.step("准备测试数据"):
            # 生成测试数据
            test_post = {
                "title": "集成测试文章",
                "body": "这是一篇用于集成测试的文章内容",
                "userId": 1
            }
            
            log.info("测试数据准备完成")
        
        with allure.step("服务A: 创建数据"):
            # 在JSONPlaceholder服务创建文章
            create_response = self.api_client.post(
                f"{self.services['json_service']}/posts",
                json_data=test_post
            )
            self.api_client.assert_status_code(create_response, 201)
            
            created_post = self.api_client.get_response_json(create_response)
            post_id = created_post["id"]
            
            self.test_data_store["created_post"] = created_post
            
            log.info(f"文章创建成功，ID: {post_id}")
        
        with allure.step("服务B: 数据传输验证"):
            # 使用httpbin验证数据传输
            transfer_response = self.api_client.post(
                f"{self.services['api_service']}/post",
                json_data=created_post
            )
            self.api_client.assert_status_code(transfer_response, 200)
            
            transfer_data = self.api_client.get_response_json(transfer_response)
            
            # 验证数据完整性
            assert transfer_data["json"]["title"] == test_post["title"]
            assert transfer_data["json"]["body"] == test_post["body"]
            assert transfer_data["json"]["id"] == post_id
            
            log.info("数据传输验证成功")
        
        with allure.step("服务A: 数据查询验证"):
            # 查询创建的文章
            get_response = self.api_client.get(
                f"{self.services['json_service']}/posts/{post_id}"
            )
            self.api_client.assert_status_code(get_response, 200)
            
            retrieved_post = self.api_client.get_response_json(get_response)
            
            # 验证数据一致性
            assert retrieved_post["title"] == test_post["title"]
            assert retrieved_post["body"] == test_post["body"]
            assert retrieved_post["userId"] == test_post["userId"]
            
            log.info("数据查询验证成功")
        
        with allure.step("数据流完整性验证"):
            # 验证整个数据流的完整性
            data_flow_steps = [
                {"step": "数据创建", "service": "JSONPlaceholder", "status": "✅"},
                {"step": "数据传输", "service": "HTTPBin", "status": "✅"},
                {"step": "数据查询", "service": "JSONPlaceholder", "status": "✅"},
                {"step": "数据一致性", "service": "跨服务", "status": "✅"}
            ]
            
            data_flow_report = "跨服务数据流测试报告:\n"
            data_flow_report += f"测试文章ID: {post_id}\n"
            data_flow_report += f"测试标题: {test_post['title']}\n\n"
            
            data_flow_report += "数据流步骤:\n"
            for step in data_flow_steps:
                data_flow_report += f"{step['status']} {step['step']} ({step['service']})\n"
            
            data_flow_report += f"\n数据流完整性: ✅ 验证通过\n"
            data_flow_report += f"涉及服务数量: {len(set(step['service'] for step in data_flow_steps))}\n"
            
            allure.attach(
                data_flow_report,
                name="跨服务数据流报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            log.info("跨服务数据流测试完成")
    
    @allure.story("端到端业务流程测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_end_to_end_business_flow(self):
        """测试端到端业务流程"""
        
        business_flow_results = []
        
        with allure.step("步骤1: 用户注册流程"):
            # 生成新用户数据
            new_user = self.data_generator.generate_user_data(1)[0]
            
            # 模拟用户注册
            register_response = self.api_client.post(
                f"{self.services['api_service']}/post",
                json_data=new_user
            )
            
            if register_response.status_code == 200:
                business_flow_results.append({"step": "用户注册", "status": "成功"})
                self.test_data_store["registered_user"] = new_user
                log.info(f"用户注册成功: {new_user['username']}")
            else:
                business_flow_results.append({"step": "用户注册", "status": "失败"})
                pytest.fail("用户注册失败")
        
        with allure.step("步骤2: 用户登录验证"):
            # 模拟用户登录
            login_data = {
                "username": new_user["username"],
                "password": "test_password"
            }
            
            login_response = self.api_client.post(
                f"{self.services['api_service']}/post",
                json_data=login_data
            )
            
            if login_response.status_code == 200:
                business_flow_results.append({"step": "用户登录", "status": "成功"})
                log.info("用户登录验证成功")
            else:
                business_flow_results.append({"step": "用户登录", "status": "失败"})
        
        with allure.step("步骤3: 创建业务数据"):
            # 生成订单数据
            order_data = self.data_generator.generate_order_data(1)[0]
            order_data["user_id"] = new_user.get("id", "test_user_id")
            
            # 创建订单
            order_response = self.api_client.post(
                f"{self.services['json_service']}/posts",
                json_data={
                    "title": f"订单 {order_data['order_id']}",
                    "body": json.dumps(order_data),
                    "userId": 1
                }
            )
            
            if order_response.status_code == 201:
                business_flow_results.append({"step": "创建订单", "status": "成功"})
                order_result = self.api_client.get_response_json(order_response)
                self.test_data_store["created_order"] = order_result
                log.info(f"订单创建成功: {order_data['order_id']}")
            else:
                business_flow_results.append({"step": "创建订单", "status": "失败"})
        
        with allure.step("步骤4: 数据处理流程"):
            # 模拟数据处理
            if "created_order" in self.test_data_store:
                order = self.test_data_store["created_order"]
                
                # 处理订单数据
                processing_response = self.api_client.put(
                    f"{self.services['api_service']}/put",
                    json_data={
                        "order_id": order["id"],
                        "status": "processed",
                        "processed_at": "2024-01-01T00:00:00Z"
                    }
                )
                
                if processing_response.status_code == 200:
                    business_flow_results.append({"step": "数据处理", "status": "成功"})
                    log.info("订单处理成功")
                else:
                    business_flow_results.append({"step": "数据处理", "status": "失败"})
            else:
                business_flow_results.append({"step": "数据处理", "status": "跳过"})
        
        with allure.step("步骤5: 结果验证"):
            # 验证整个流程的结果
            verification_response = self.api_client.get(
                f"{self.services['api_service']}/get",
                params={"user": new_user["username"]}
            )
            
            if verification_response.status_code == 200:
                business_flow_results.append({"step": "结果验证", "status": "成功"})
                log.info("端到端流程验证成功")
            else:
                business_flow_results.append({"step": "结果验证", "status": "失败"})
        
        with allure.step("生成端到端测试报告"):
            successful_steps = sum(1 for result in business_flow_results if result["status"] == "成功")
            total_steps = len(business_flow_results)
            
            e2e_report = f"端到端业务流程测试报告:\n"
            e2e_report += f"总步骤数: {total_steps}\n"
            e2e_report += f"成功步骤: {successful_steps}\n"
            e2e_report += f"成功率: {successful_steps/total_steps:.2%}\n\n"
            
            e2e_report += "流程步骤详情:\n"
            for i, result in enumerate(business_flow_results, 1):
                status_icon = "✅" if result["status"] == "成功" else "❌" if result["status"] == "失败" else "⏭️"
                e2e_report += f"{i}. {status_icon} {result['step']}: {result['status']}\n"
            
            e2e_report += f"\n测试用户: {new_user['username']}\n"
            e2e_report += f"测试邮箱: {new_user['email']}\n"
            
            if "created_order" in self.test_data_store:
                e2e_report += f"创建订单ID: {self.test_data_store['created_order']['id']}\n"
            
            allure.attach(
                e2e_report,
                name="端到端业务流程报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 断言业务流程成功率
            success_rate = successful_steps / total_steps
            assert success_rate >= 0.8, f"端到端业务流程成功率过低: {success_rate:.2%}"
            
            log.info(f"端到端业务流程测试完成，成功率: {success_rate:.2%}")
    
    @allure.story("系统健康检查")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    @pytest.mark.health_check
    def test_system_health_check(self):
        """测试系统健康检查"""
        
        health_results = {}
        
        with allure.step("检查各服务健康状态"):
            for service_name, service_url in self.services.items():
                try:
                    start_time = time.time()
                    
                    # 发送健康检查请求
                    if service_name == "json_service":
                        health_response = self.api_client.get(f"{service_url}/posts/1")
                    else:
                        health_response = self.api_client.get(f"{service_url}/get")
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # 转换为毫秒
                    
                    health_results[service_name] = {
                        "status": "健康" if health_response.status_code == 200 else "异常",
                        "status_code": health_response.status_code,
                        "response_time": response_time,
                        "url": service_url
                    }
                    
                    log.info(f"{service_name} 健康检查: {health_results[service_name]['status']} ({response_time:.2f}ms)")
                
                except Exception as e:
                    health_results[service_name] = {
                        "status": "错误",
                        "error": str(e),
                        "url": service_url
                    }
                    log.error(f"{service_name} 健康检查失败: {e}")
        
        with allure.step("生成系统健康报告"):
            healthy_services = sum(1 for result in health_results.values() if result["status"] == "健康")
            total_services = len(health_results)
            
            health_report = f"系统健康检查报告:\n"
            health_report += f"检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            health_report += f"总服务数: {total_services}\n"
            health_report += f"健康服务: {healthy_services}\n"
            health_report += f"健康率: {healthy_services/total_services:.2%}\n\n"
            
            health_report += "服务详情:\n"
            for service_name, result in health_results.items():
                status_icon = "✅" if result["status"] == "健康" else "❌"
                health_report += f"{status_icon} {service_name}:\n"
                health_report += f"   状态: {result['status']}\n"
                health_report += f"   URL: {result['url']}\n"
                
                if "status_code" in result:
                    health_report += f"   状态码: {result['status_code']}\n"
                    health_report += f"   响应时间: {result['response_time']:.2f}ms\n"
                
                if "error" in result:
                    health_report += f"   错误: {result['error']}\n"
                
                health_report += "\n"
            
            allure.attach(
                health_report,
                name="系统健康检查报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 断言系统健康率
            health_rate = healthy_services / total_services
            assert health_rate >= 0.7, f"系统健康率过低: {health_rate:.2%}"
            
            log.info(f"系统健康检查完成，健康率: {health_rate:.2%}")
