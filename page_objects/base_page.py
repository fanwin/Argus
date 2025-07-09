"""
基础页面对象模型
提供所有页面对象的通用功能和方法
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from typing import Tuple, List, Optional, Any
import time

from utilities.selenium_wrapper import SeleniumWrapper
from utilities.logger import log
from utilities.config_reader import config


class BasePage:
    """基础页面类，所有页面对象的父类"""
    
    # 通用元素定位器
    LOADING_SPINNER = (By.CLASS_NAME, "loading")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    MODAL_DIALOG = (By.CLASS_NAME, "modal")
    MODAL_CLOSE_BUTTON = (By.CLASS_NAME, "modal-close")
    BREADCRUMB = (By.CLASS_NAME, "breadcrumb")
    
    # 导航元素
    HEADER = (By.TAG_NAME, "header")
    FOOTER = (By.TAG_NAME, "footer")
    NAVIGATION_MENU = (By.CLASS_NAME, "nav-menu")
    USER_MENU = (By.CLASS_NAME, "user-menu")
    LOGOUT_BUTTON = (By.ID, "logout")
    
    def __init__(self, selenium_wrapper: SeleniumWrapper):
        """
        初始化基础页面
        
        Args:
            selenium_wrapper: Selenium封装实例
        """
        self.driver_wrapper = selenium_wrapper
        self.driver = selenium_wrapper.driver
        self.wait = WebDriverWait(self.driver, 30)
        self.actions = ActionChains(self.driver)
        
        # 从配置获取基础URL
        try:
            web_config = config.get_web_config()
            self.base_url = web_config.get("base_url", "")
        except:
            self.base_url = ""
    
    @allure.step("等待页面加载完成")
    def wait_for_page_load(self, timeout: int = 30):
        """
        等待页面加载完成
        
        Args:
            timeout: 超时时间（秒）
        """
        try:
            # 等待页面就绪状态
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 等待加载动画消失
            if self.driver_wrapper.is_element_present(self.LOADING_SPINNER):
                self.wait.until_not(EC.presence_of_element_located(self.LOADING_SPINNER))
            
            log.debug("页面加载完成")
        except Exception as e:
            log.warning(f"等待页面加载时出现异常: {e}")
    
    @allure.step("导航到URL: {url}")
    def navigate_to(self, url: str):
        """
        导航到指定URL
        
        Args:
            url: 目标URL
        """
        if not url.startswith("http"):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        
        log.info(f"导航到: {url}")
        self.driver_wrapper.navigate_to(url)
        self.wait_for_page_load()
    
    @allure.step("刷新页面")
    def refresh_page(self):
        """刷新当前页面"""
        log.debug("刷新页面")
        self.driver.refresh()
        self.wait_for_page_load()
    
    @allure.step("返回上一页")
    def go_back(self):
        """返回上一页"""
        log.debug("返回上一页")
        self.driver.back()
        self.wait_for_page_load()
    
    @allure.step("前进到下一页")
    def go_forward(self):
        """前进到下一页"""
        log.debug("前进到下一页")
        self.driver.forward()
        self.wait_for_page_load()
    
    def get_current_url(self) -> str:
        """获取当前URL"""
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.driver.title
    
    def get_page_source(self) -> str:
        """获取页面源码"""
        return self.driver.page_source
    
    @allure.step("等待元素可见: {locator}")
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = 30):
        """
        等待元素可见
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（秒）
        """
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    @allure.step("等待元素可点击: {locator}")
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = 30):
        """
        等待元素可点击
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（秒）
        """
        return self.wait.until(EC.element_to_be_clickable(locator))
    
    @allure.step("等待元素消失: {locator}")
    def wait_for_element_invisible(self, locator: Tuple[str, str], timeout: int = 30):
        """
        等待元素消失
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（秒）
        """
        return self.wait.until(EC.invisibility_of_element_located(locator))
    
    @allure.step("滚动到元素: {locator}")
    def scroll_to_element(self, locator: Tuple[str, str]):
        """
        滚动到指定元素
        
        Args:
            locator: 元素定位器
        """
        element = self.driver_wrapper.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # 等待滚动完成
    
    @allure.step("滚动到页面顶部")
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
    
    @allure.step("滚动到页面底部")
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
    
    @allure.step("悬停在元素上: {locator}")
    def hover_over_element(self, locator: Tuple[str, str]):
        """
        悬停在指定元素上
        
        Args:
            locator: 元素定位器
        """
        element = self.driver_wrapper.find_element(locator)
        self.actions.move_to_element(element).perform()
        time.sleep(0.5)
    
    @allure.step("双击元素: {locator}")
    def double_click_element(self, locator: Tuple[str, str]):
        """
        双击指定元素
        
        Args:
            locator: 元素定位器
        """
        element = self.driver_wrapper.find_element(locator)
        self.actions.double_click(element).perform()
    
    @allure.step("右键点击元素: {locator}")
    def right_click_element(self, locator: Tuple[str, str]):
        """
        右键点击指定元素
        
        Args:
            locator: 元素定位器
        """
        element = self.driver_wrapper.find_element(locator)
        self.actions.context_click(element).perform()
    
    @allure.step("拖拽元素")
    def drag_and_drop(self, source_locator: Tuple[str, str], target_locator: Tuple[str, str]):
        """
        拖拽元素
        
        Args:
            source_locator: 源元素定位器
            target_locator: 目标元素定位器
        """
        source = self.driver_wrapper.find_element(source_locator)
        target = self.driver_wrapper.find_element(target_locator)
        self.actions.drag_and_drop(source, target).perform()
    
    @allure.step("按键操作: {key}")
    def send_key(self, key: str):
        """
        发送键盘按键
        
        Args:
            key: 按键（如Keys.ENTER, Keys.TAB等）
        """
        self.actions.send_keys(key).perform()
    
    @allure.step("组合键操作")
    def send_key_combination(self, *keys):
        """
        发送组合键
        
        Args:
            keys: 按键组合
        """
        self.actions.key_down(keys[0])
        for key in keys[1:]:
            self.actions.key_down(key)
        for key in reversed(keys):
            self.actions.key_up(key)
        self.actions.perform()
    
    def get_error_message(self) -> Optional[str]:
        """
        获取错误消息
        
        Returns:
            错误消息文本，如果没有则返回None
        """
        try:
            if self.driver_wrapper.is_element_present(self.ERROR_MESSAGE):
                return self.driver_wrapper.get_text(self.ERROR_MESSAGE)
        except Exception as e:
            log.debug(f"获取错误消息失败: {e}")
        return None
    
    def get_success_message(self) -> Optional[str]:
        """
        获取成功消息
        
        Returns:
            成功消息文本，如果没有则返回None
        """
        try:
            if self.driver_wrapper.is_element_present(self.SUCCESS_MESSAGE):
                return self.driver_wrapper.get_text(self.SUCCESS_MESSAGE)
        except Exception as e:
            log.debug(f"获取成功消息失败: {e}")
        return None
    
    @allure.step("关闭模态对话框")
    def close_modal(self):
        """关闭模态对话框"""
        if self.driver_wrapper.is_element_present(self.MODAL_DIALOG):
            if self.driver_wrapper.is_element_present(self.MODAL_CLOSE_BUTTON):
                self.driver_wrapper.click(self.MODAL_CLOSE_BUTTON)
            else:
                # 尝试按ESC键关闭
                self.send_key(Keys.ESCAPE)
    
    def is_modal_open(self) -> bool:
        """
        检查模态对话框是否打开
        
        Returns:
            模态对话框是否打开
        """
        return self.driver_wrapper.is_element_present(self.MODAL_DIALOG)
    
    @allure.step("等待模态对话框出现")
    def wait_for_modal(self, timeout: int = 10):
        """
        等待模态对话框出现
        
        Args:
            timeout: 超时时间（秒）
        """
        self.wait.until(EC.presence_of_element_located(self.MODAL_DIALOG))
    
    @allure.step("等待模态对话框消失")
    def wait_for_modal_close(self, timeout: int = 10):
        """
        等待模态对话框消失
        
        Args:
            timeout: 超时时间（秒）
        """
        self.wait.until(EC.invisibility_of_element_located(self.MODAL_DIALOG))
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        截图
        
        Args:
            filename: 截图文件名
            
        Returns:
            截图文件路径
        """
        return self.driver_wrapper.take_screenshot(filename)
    
    @allure.step("执行JavaScript代码")
    def execute_javascript(self, script: str, *args) -> Any:
        """
        执行JavaScript代码
        
        Args:
            script: JavaScript代码
            args: 参数
            
        Returns:
            执行结果
        """
        return self.driver.execute_script(script, *args)
    
    @allure.step("切换到iframe: {locator}")
    def switch_to_iframe(self, locator: Tuple[str, str]):
        """
        切换到iframe
        
        Args:
            locator: iframe定位器
        """
        iframe = self.driver_wrapper.find_element(locator)
        self.driver.switch_to.frame(iframe)
    
    @allure.step("切换回主框架")
    def switch_to_default_content(self):
        """切换回主框架"""
        self.driver.switch_to.default_content()
    
    @allure.step("切换到新窗口")
    def switch_to_new_window(self):
        """切换到新窗口"""
        windows = self.driver.window_handles
        if len(windows) > 1:
            self.driver.switch_to.window(windows[-1])
    
    @allure.step("关闭当前窗口")
    def close_current_window(self):
        """关闭当前窗口"""
        self.driver.close()
    
    @allure.step("切换回主窗口")
    def switch_to_main_window(self):
        """切换回主窗口"""
        windows = self.driver.window_handles
        if windows:
            self.driver.switch_to.window(windows[0])
    
    def get_breadcrumb_text(self) -> List[str]:
        """
        获取面包屑导航文本
        
        Returns:
            面包屑导航文本列表
        """
        try:
            if self.driver_wrapper.is_element_present(self.BREADCRUMB):
                breadcrumb_elements = self.driver_wrapper.find_elements(
                    (By.CSS_SELECTOR, f"{self.BREADCRUMB[1]} a, {self.BREADCRUMB[1]} span")
                )
                return [element.text for element in breadcrumb_elements if element.text.strip()]
        except Exception as e:
            log.debug(f"获取面包屑导航失败: {e}")
        return []
    
    @allure.step("注销登录")
    def logout(self):
        """注销登录"""
        if self.driver_wrapper.is_element_present(self.LOGOUT_BUTTON):
            self.driver_wrapper.click(self.LOGOUT_BUTTON)
            self.wait_for_page_load()
            log.info("用户已注销")
        else:
            log.warning("未找到注销按钮")
