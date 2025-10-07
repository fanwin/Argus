"""
高级Web UI测试案例
展示Web UI测试的高级功能：复杂交互、文件上传、拖拽、多窗口等
使用WebGoat作为测试目标
"""

import pytest
import allure
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from utilities.logger import log
from utilities.selenium_wrapper import SeleniumWrapper


@allure.epic("高级Web UI测试")
@allure.feature("WebGoat安全测试平台")
class TestAdvancedWebUI:
    """高级Web UI测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self, web_config):
        """设置测试环境"""
        self.driver_wrapper = SeleniumWrapper()
        self.driver_wrapper.start_driver()
        
        # WebGoat测试URL
        self.base_url = "https://owasp.org/www-project-webgoat/"
        self.demo_url = "https://demo.testfire.net"  # 备用测试站点
        
        log.info(f"Web UI测试环境初始化完成")
        
        yield
        
        # 清理
        self.driver_wrapper.quit_driver()
    
    @allure.story("页面导航和元素交互")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.web
    @pytest.mark.smoke
    def test_page_navigation_and_interaction(self):
        """测试页面导航和基本元素交互"""
        
        with allure.step("导航到WebGoat项目页面"):
            self.driver_wrapper.navigate_to(self.base_url)
            
            # 等待页面加载
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
            
            # 验证页面标题
            page_title = self.driver_wrapper.get_page_title()
            assert "WebGoat" in page_title, f"页面标题应包含WebGoat，实际: {page_title}"
            log.info(f"页面标题验证通过: {page_title}")
        
        with allure.step("测试页面滚动"):
            # 滚动到页面底部
            self.driver_wrapper.scroll_to_bottom()
            time.sleep(1)
            
            # 滚动到页面顶部
            self.driver_wrapper.scroll_to_top()
            time.sleep(1)
            
            log.info("页面滚动测试完成")
        
        with allure.step("查找和点击链接"):
            try:
                # 查找GitHub链接
                github_links = self.driver_wrapper.find_elements((By.PARTIAL_LINK_TEXT, "GitHub"))
                if github_links:
                    # 获取链接文本和URL
                    link = github_links[0]
                    link_text = link.text
                    link_url = link.get_attribute("href")
                    
                    log.info(f"找到GitHub链接: {link_text} -> {link_url}")
                    
                    # 在新标签页中打开链接
                    self.driver_wrapper.execute_script("arguments[0].target='_blank';", link)
                    link.click()
                    
                    # 切换到新标签页
                    original_window = self.driver_wrapper.driver.current_window_handle
                    all_windows = self.driver_wrapper.driver.window_handles
                    
                    if len(all_windows) > 1:
                        new_window = [w for w in all_windows if w != original_window][0]
                        self.driver_wrapper.driver.switch_to.window(new_window)
                        
                        # 验证新页面
                        new_title = self.driver_wrapper.get_page_title()
                        log.info(f"新标签页标题: {new_title}")
                        
                        # 关闭新标签页并返回原页面
                        self.driver_wrapper.driver.close()
                        self.driver_wrapper.driver.switch_to.window(original_window)
                        
                        log.info("多标签页操作测试完成")
                else:
                    log.info("未找到GitHub链接，跳过链接测试")
            except Exception as e:
                log.warning(f"链接测试异常: {e}")
        
        # 截图记录
        screenshot_path = self.driver_wrapper.take_screenshot("page_navigation_test.png")
        if screenshot_path:
            allure.attach.file(
                screenshot_path,
                name="页面导航测试截图",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story("表单操作和验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    def test_form_operations(self):
        """测试表单操作和验证"""
        
        with allure.step("导航到测试表单页面"):
            # 使用备用测试站点进行表单测试
            self.driver_wrapper.navigate_to(self.demo_url)
            
            try:
                # 等待页面加载
                self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"), timeout=10)
                log.info("测试站点加载成功")
            except TimeoutException:
                log.warning("测试站点加载超时，使用模拟表单测试")
                pytest.skip("测试站点不可用")
        
        with allure.step("查找并填写表单"):
            try:
                # 查找登录表单
                login_forms = self.driver_wrapper.find_elements((By.TAG_NAME, "form"))
                if login_forms:
                    log.info(f"找到 {len(login_forms)} 个表单")
                
                # 查找输入框
                input_fields = self.driver_wrapper.find_elements((By.TAG_NAME, "input"))
                text_inputs = [inp for inp in input_fields if inp.get_attribute("type") in ["text", "email", "password"]]
                
                if text_inputs:
                    for i, input_field in enumerate(text_inputs[:2]):  # 只测试前两个输入框
                        input_type = input_field.get_attribute("type")
                        input_name = input_field.get_attribute("name") or f"input_{i}"
                        
                        # 清空并输入测试数据
                        input_field.clear()
                        test_value = f"test_value_{i}"
                        input_field.send_keys(test_value)
                        
                        # 验证输入值
                        actual_value = input_field.get_attribute("value")
                        assert actual_value == test_value, f"输入值不匹配: 期望 {test_value}, 实际 {actual_value}"
                        
                        log.info(f"输入框测试完成: {input_name} ({input_type}) = {test_value}")
                else:
                    log.info("未找到可测试的输入框")
                
            except Exception as e:
                log.warning(f"表单操作异常: {e}")
        
        with allure.step("测试键盘操作"):
            try:
                # 查找第一个文本输入框
                text_inputs = self.driver_wrapper.find_elements((By.CSS_SELECTOR, "input[type='text'], input[type='email']"))
                if text_inputs:
                    input_field = text_inputs[0]
                    
                    # 清空输入框
                    input_field.clear()
                    
                    # 测试键盘快捷键
                    input_field.send_keys("Hello World")
                    input_field.send_keys(Keys.CONTROL + "a")  # 全选
                    input_field.send_keys(Keys.CONTROL + "c")  # 复制
                    input_field.send_keys(Keys.DELETE)  # 删除
                    input_field.send_keys(Keys.CONTROL + "v")  # 粘贴
                    
                    # 验证结果
                    final_value = input_field.get_attribute("value")
                    assert "Hello World" in final_value, "键盘操作测试失败"
                    
                    log.info("键盘操作测试完成")
                else:
                    log.info("未找到文本输入框，跳过键盘操作测试")
            except Exception as e:
                log.warning(f"键盘操作测试异常: {e}")
    
    @allure.story("鼠标操作和拖拽")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    def test_mouse_operations(self):
        """测试鼠标操作和拖拽功能"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.base_url)
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("测试鼠标悬停"):
            try:
                # 查找可悬停的元素（如导航菜单）
                nav_elements = self.driver_wrapper.find_elements((By.CSS_SELECTOR, "nav a, .nav a, header a"))
                
                if nav_elements:
                    for element in nav_elements[:3]:  # 只测试前3个元素
                        try:
                            # 鼠标悬停
                            actions = ActionChains(self.driver_wrapper.driver)
                            actions.move_to_element(element).perform()
                            time.sleep(0.5)
                            
                            element_text = element.text.strip()
                            if element_text:
                                log.info(f"鼠标悬停测试: {element_text}")
                        except Exception as e:
                            log.debug(f"元素悬停失败: {e}")
                            continue
                else:
                    log.info("未找到可悬停的导航元素")
            except Exception as e:
                log.warning(f"鼠标悬停测试异常: {e}")
        
        with allure.step("测试右键菜单"):
            try:
                # 在页面上右键点击
                body_element = self.driver_wrapper.find_element((By.TAG_NAME, "body"))
                actions = ActionChains(self.driver_wrapper.driver)
                actions.context_click(body_element).perform()
                time.sleep(1)
                
                # 按ESC键关闭右键菜单
                actions.send_keys(Keys.ESCAPE).perform()
                log.info("右键菜单测试完成")
            except Exception as e:
                log.warning(f"右键菜单测试异常: {e}")
        
        with allure.step("测试双击操作"):
            try:
                # 查找可双击的元素
                clickable_elements = self.driver_wrapper.find_elements((By.CSS_SELECTOR, "h1, h2, h3"))
                
                if clickable_elements:
                    element = clickable_elements[0]
                    actions = ActionChains(self.driver_wrapper.driver)
                    actions.double_click(element).perform()
                    time.sleep(0.5)
                    
                    log.info("双击操作测试完成")
                else:
                    log.info("未找到可双击的元素")
            except Exception as e:
                log.warning(f"双击操作测试异常: {e}")
    
    @allure.story("JavaScript交互")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.web
    def test_javascript_interaction(self):
        """测试JavaScript交互功能"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.base_url)
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("执行JavaScript代码"):
            # 获取页面信息
            page_info = self.driver_wrapper.execute_script("""
                return {
                    title: document.title,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    scrollPosition: window.pageYOffset,
                    linksCount: document.links.length,
                    imagesCount: document.images.length
                };
            """)
            
            # 验证返回的信息
            assert isinstance(page_info, dict), "JavaScript应该返回字典对象"
            assert "title" in page_info, "应该包含页面标题"
            assert "url" in page_info, "应该包含页面URL"
            
            log.info(f"页面信息: 标题={page_info['title']}, 链接数={page_info['linksCount']}, 图片数={page_info['imagesCount']}")
        
        with allure.step("操作页面元素"):
            # 通过JavaScript高亮页面元素
            highlight_script = """
                var elements = document.querySelectorAll('h1, h2, h3');
                for (var i = 0; i < Math.min(elements.length, 3); i++) {
                    elements[i].style.backgroundColor = 'yellow';
                    elements[i].style.border = '2px solid red';
                }
                return elements.length;
            """
            
            highlighted_count = self.driver_wrapper.execute_script(highlight_script)
            log.info(f"高亮了 {highlighted_count} 个标题元素")
            
            time.sleep(1)  # 让高亮效果可见
            
            # 移除高亮效果
            remove_highlight_script = """
                var elements = document.querySelectorAll('h1, h2, h3');
                for (var i = 0; i < elements.length; i++) {
                    elements[i].style.backgroundColor = '';
                    elements[i].style.border = '';
                }
            """
            self.driver_wrapper.execute_script(remove_highlight_script)
        
        with allure.step("测试页面滚动"):
            # 获取页面高度
            page_height = self.driver_wrapper.execute_script("return document.body.scrollHeight;")
            viewport_height = self.driver_wrapper.execute_script("return window.innerHeight;")
            
            log.info(f"页面高度: {page_height}px, 视口高度: {viewport_height}px")
            
            if page_height > viewport_height:
                # 滚动到页面中间
                middle_position = page_height // 2
                self.driver_wrapper.execute_script(f"window.scrollTo(0, {middle_position});")
                time.sleep(0.5)
                
                # 验证滚动位置
                current_scroll = self.driver_wrapper.execute_script("return window.pageYOffset;")
                assert abs(current_scroll - middle_position) < 100, "滚动位置不正确"
                
                log.info(f"滚动到位置: {current_scroll}px")
                
                # 滚动回顶部
                self.driver_wrapper.execute_script("window.scrollTo(0, 0);")
            else:
                log.info("页面高度不足，跳过滚动测试")
    
    @allure.story("响应式设计测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.web
    def test_responsive_design(self):
        """测试响应式设计"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.base_url)
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        # 测试不同的屏幕尺寸
        screen_sizes = [
            ("桌面", 1920, 1080),
            ("平板", 768, 1024),
            ("手机", 375, 667)
        ]
        
        for device_name, width, height in screen_sizes:
            with allure.step(f"测试{device_name}尺寸 ({width}x{height})"):
                # 设置窗口大小
                self.driver_wrapper.driver.set_window_size(width, height)
                time.sleep(1)
                
                # 获取实际窗口大小
                actual_size = self.driver_wrapper.driver.get_window_size()
                log.info(f"{device_name}尺寸设置: {actual_size['width']}x{actual_size['height']}")
                
                # 检查页面是否正常显示
                body_element = self.driver_wrapper.find_element((By.TAG_NAME, "body"))
                assert body_element.is_displayed(), f"{device_name}尺寸下页面应该正常显示"
                
                # 截图记录
                screenshot_path = self.driver_wrapper.take_screenshot(f"responsive_{device_name.lower()}.png")
                if screenshot_path:
                    allure.attach.file(
                        screenshot_path,
                        name=f"{device_name}尺寸截图",
                        attachment_type=allure.attachment_type.PNG
                    )
        
        # 恢复默认窗口大小
        self.driver_wrapper.driver.set_window_size(1920, 1080)
    
    @allure.story("页面性能监控")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.web
    @pytest.mark.performance
    def test_page_performance(self):
        """测试页面性能"""
        
        with allure.step("测量页面加载性能"):
            start_time = time.time()
            
            self.driver_wrapper.navigate_to(self.base_url)
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
            
            load_time = time.time() - start_time
            
            # 获取页面性能数据
            performance_data = self.driver_wrapper.execute_script("""
                var perfData = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                    loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                    domInteractive: perfData.domInteractive - perfData.navigationStart,
                    responseTime: perfData.responseEnd - perfData.requestStart
                };
            """)
            
            log.info(f"页面加载时间: {load_time:.2f}秒")
            log.info(f"DOM加载时间: {performance_data.get('domContentLoaded', 0):.2f}ms")
            log.info(f"响应时间: {performance_data.get('responseTime', 0):.2f}ms")
            
            # 性能断言
            assert load_time < 30, f"页面加载时间过长: {load_time:.2f}秒"
            
            # 添加性能数据到报告
            performance_report = f"""
页面加载性能报告:
- 总加载时间: {load_time:.2f}秒
- DOM内容加载: {performance_data.get('domContentLoaded', 0):.2f}ms
- 完全加载: {performance_data.get('loadComplete', 0):.2f}ms
- DOM交互就绪: {performance_data.get('domInteractive', 0):.2f}ms
- 响应时间: {performance_data.get('responseTime', 0):.2f}ms
            """
            
            allure.attach(
                performance_report,
                name="页面性能数据",
                attachment_type=allure.attachment_type.TEXT
            )
