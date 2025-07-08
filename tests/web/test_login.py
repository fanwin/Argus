"""
登录功能Web UI测试用例
测试登录页面的各种功能和场景
"""

import json
import pytest
import allure
from pathlib import Path

from page_objects.login_page import LoginPage
from utilities.logger import log


@allure.epic("Web UI测试")
@allure.feature("用户认证")
class TestLogin:
    """登录测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, web_config):
        """设置测试数据"""
        # 加载测试数据
        test_data_file = Path("data/test_data.json")
        with open(test_data_file, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
        
        self.base_url = web_config.get("base_url", "https://example.com")
        self.users_data = self.test_data["users"]
    
    @pytest.fixture
    def login_page(self, web_driver):
        """登录页面fixture"""
        page = LoginPage(web_driver)
        page.navigate_to_login_page(self.base_url)
        return page
    
    @allure.story("成功登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.web
    @pytest.mark.smoke
    def test_login_success_admin(self, login_page):
        """测试管理员成功登录"""
        admin_user = self.users_data["valid_users"][0]
        
        with allure.step("执行登录操作"):
            login_page.login(
                username=admin_user["username"],
                password=admin_user["password"]
            )
        
        with allure.step("验证登录结果"):
            assert login_page.is_login_successful(), "登录应该成功"
            log.info(f"管理员登录成功: {admin_user['username']}")
        
        # 截图记录
        screenshot_path = login_page.take_screenshot("login_success_admin.png")
        if screenshot_path:
            allure.attach.file(
                screenshot_path,
                name="登录成功截图",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story("成功登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    @pytest.mark.parametrize("user_data", [
        pytest.param(user, id=f"user_{user['role']}") 
        for user in json.loads(Path("data/test_data.json").read_text(encoding='utf-8'))["users"]["valid_users"]
    ])
    def test_login_success_all_users(self, login_page, user_data):
        """测试所有有效用户登录"""
        with allure.step(f"测试用户登录: {user_data['role']}"):
            login_page.login(
                username=user_data["username"],
                password=user_data["password"]
            )
        
        with allure.step("验证登录结果"):
            assert login_page.is_login_successful(), f"{user_data['role']}用户登录应该成功"
            log.info(f"{user_data['role']}用户登录成功: {user_data['username']}")
    
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    @pytest.mark.parametrize("user_data", [
        pytest.param(user, id=f"invalid_{i}") 
        for i, user in enumerate(json.loads(Path("data/test_data.json").read_text(encoding='utf-8'))["users"]["invalid_users"])
    ])
    def test_login_failure(self, login_page, user_data):
        """测试登录失败场景"""
        with allure.step(f"使用无效凭据登录"):
            login_page.login(
                username=user_data["username"],
                password=user_data["password"]
            )
        
        with allure.step("验证登录失败"):
            assert not login_page.is_login_successful(), "登录应该失败"
            
            # 检查错误消息
            error_message = login_page.get_error_message()
            if error_message:
                assert user_data["expected_error"] in error_message, f"错误消息不匹配，期望包含: {user_data['expected_error']}, 实际: {error_message}"
                log.info(f"登录失败测试通过，错误消息: {error_message}")
            else:
                log.warning("未获取到错误消息")
        
        # 截图记录
        screenshot_path = login_page.take_screenshot(f"login_failure_{user_data.get('username', 'empty')}.png")
        if screenshot_path:
            allure.attach.file(
                screenshot_path,
                name="登录失败截图",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story("记住我功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    def test_remember_me_functionality(self, login_page):
        """测试记住我功能"""
        admin_user = self.users_data["valid_users"][0]
        
        with allure.step("勾选记住我并登录"):
            login_page.login(
                username=admin_user["username"],
                password=admin_user["password"],
                remember_me=True
            )
        
        with allure.step("验证登录成功"):
            assert login_page.is_login_successful(), "登录应该成功"
        
        # 这里可以添加更多验证逻辑，比如检查cookie等
        log.info("记住我功能测试完成")
    
    @allure.story("页面元素")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.web
    def test_login_page_elements(self, login_page):
        """测试登录页面元素存在性"""
        with allure.step("验证页面已加载"):
            assert login_page.is_page_loaded(), "登录页面应该已加载"
        
        with allure.step("验证页面标题"):
            page_title = login_page.get_page_title()
            assert "登录" in page_title or "Login" in page_title, f"页面标题应包含登录相关文字，实际: {page_title}"
        
        with allure.step("验证必要元素存在"):
            # 这些检查在is_page_loaded中已经包含，这里是额外的验证
            assert login_page.driver_wrapper.is_element_present(login_page.USERNAME_INPUT), "用户名输入框应该存在"
            assert login_page.driver_wrapper.is_element_present(login_page.PASSWORD_INPUT), "密码输入框应该存在"
            assert login_page.driver_wrapper.is_element_present(login_page.LOGIN_BUTTON), "登录按钮应该存在"
        
        log.info("登录页面元素验证完成")
    
    @allure.story("表单验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    def test_empty_form_submission(self, login_page):
        """测试空表单提交"""
        with allure.step("清空表单并提交"):
            login_page.clear_form()
            login_page.click_login_button()
        
        with allure.step("验证表单验证"):
            # 等待一下让验证消息显示
            import time
            time.sleep(1)
            
            assert not login_page.is_login_successful(), "空表单提交不应该成功"
            
            # 检查是否有错误消息
            error_message = login_page.get_error_message()
            if error_message:
                log.info(f"空表单验证消息: {error_message}")
            else:
                log.info("空表单提交被阻止（可能是前端验证）")
    
    @allure.story("忘记密码")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.web
    def test_forgot_password_link(self, login_page):
        """测试忘记密码链接"""
        with allure.step("检查忘记密码链接是否存在"):
            if login_page.driver_wrapper.is_element_present(login_page.FORGOT_PASSWORD_LINK):
                with allure.step("点击忘记密码链接"):
                    current_url = login_page.driver_wrapper.get_current_url()
                    login_page.click_forgot_password()
                    
                    # 等待页面跳转
                    import time
                    time.sleep(2)
                    
                    new_url = login_page.driver_wrapper.get_current_url()
                    assert new_url != current_url, "点击忘记密码后应该跳转到新页面"
                    
                    log.info(f"忘记密码链接功能正常，跳转到: {new_url}")
            else:
                log.info("忘记密码链接不存在，跳过测试")
                pytest.skip("忘记密码链接不存在")
    
    @allure.story("页面响应性")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.web
    @pytest.mark.slow
    def test_page_load_performance(self, web_driver):
        """测试页面加载性能"""
        import time
        
        with allure.step("测量页面加载时间"):
            start_time = time.time()
            
            page = LoginPage(web_driver)
            page.navigate_to_login_page(self.base_url)
            
            # 等待页面完全加载
            page.wait_for_page_load()
            
            load_time = time.time() - start_time
        
        with allure.step("验证加载时间"):
            max_load_time = 10.0  # 最大允许加载时间（秒）
            assert load_time < max_load_time, f"页面加载时间过长: {load_time:.2f}秒 > {max_load_time}秒"
            
            log.info(f"页面加载时间: {load_time:.2f}秒")
        
        # 添加性能数据到Allure报告
        allure.attach(
            f"页面加载时间: {load_time:.2f}秒",
            name="性能数据",
            attachment_type=allure.attachment_type.TEXT
        )
    
    @allure.story("浏览器兼容性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    def test_browser_compatibility(self, login_page):
        """测试浏览器兼容性"""
        admin_user = self.users_data["valid_users"][0]
        
        with allure.step("在当前浏览器中测试登录功能"):
            login_page.login(
                username=admin_user["username"],
                password=admin_user["password"]
            )
        
        with allure.step("验证功能正常"):
            assert login_page.is_login_successful(), "登录功能在当前浏览器中应该正常工作"
            
            browser_info = login_page.driver_wrapper.driver.capabilities
            log.info(f"浏览器兼容性测试通过: {browser_info.get('browserName', 'Unknown')} {browser_info.get('browserVersion', 'Unknown')}")
        
        # 添加浏览器信息到Allure报告
        allure.attach(
            str(browser_info),
            name="浏览器信息",
            attachment_type=allure.attachment_type.TEXT
        )
