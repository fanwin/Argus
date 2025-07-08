"""
登录页面对象模型
实现登录页面的元素定位和操作方法
"""

import allure
from selenium.webdriver.common.by import By
from typing import Tuple

from utilities.selenium_wrapper import SeleniumWrapper
from utilities.logger import log


class LoginPage:
    """登录页面类"""
    
    # 页面元素定位器
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember-me")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "忘记密码?")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    LOADING_SPINNER = (By.CLASS_NAME, "loading-spinner")
    
    # 页面URL路径
    PAGE_PATH = "/login"
    
    def __init__(self, selenium_wrapper: SeleniumWrapper):
        """
        初始化登录页面
        
        Args:
            selenium_wrapper: Selenium封装实例
        """
        self.driver_wrapper = selenium_wrapper
        self.driver = selenium_wrapper.driver
        
    @allure.step("导航到登录页面")
    def navigate_to_login_page(self, base_url: str):
        """
        导航到登录页面
        
        Args:
            base_url: 基础URL
        """
        login_url = f"{base_url.rstrip('/')}{self.PAGE_PATH}"
        log.info(f"导航到登录页面: {login_url}")
        self.driver_wrapper.navigate_to(login_url)
        
        # 等待页面加载完成
        self.wait_for_page_load()
    
    @allure.step("等待页面加载完成")
    def wait_for_page_load(self):
        """等待登录页面加载完成"""
        try:
            self.driver_wrapper.wait_for_element_visible(self.USERNAME_INPUT, timeout=10)
            self.driver_wrapper.wait_for_element_visible(self.PASSWORD_INPUT, timeout=10)
            self.driver_wrapper.wait_for_element_visible(self.LOGIN_BUTTON, timeout=10)
            log.debug("登录页面加载完成")
        except Exception as e:
            log.error(f"等待登录页面加载失败: {e}")
            raise
    
    @allure.step("输入用户名: {username}")
    def enter_username(self, username: str):
        """
        输入用户名
        
        Args:
            username: 用户名
        """
        log.debug(f"输入用户名: {username}")
        self.driver_wrapper.send_keys(self.USERNAME_INPUT, username)
    
    @allure.step("输入密码")
    def enter_password(self, password: str):
        """
        输入密码
        
        Args:
            password: 密码
        """
        log.debug("输入密码")
        self.driver_wrapper.send_keys(self.PASSWORD_INPUT, password)
    
    @allure.step("点击登录按钮")
    def click_login_button(self):
        """点击登录按钮"""
        log.debug("点击登录按钮")
        self.driver_wrapper.click(self.LOGIN_BUTTON)
    
    @allure.step("勾选记住我")
    def check_remember_me(self):
        """勾选记住我复选框"""
        log.debug("勾选记住我")
        if not self.is_remember_me_checked():
            self.driver_wrapper.click(self.REMEMBER_ME_CHECKBOX)
    
    @allure.step("取消勾选记住我")
    def uncheck_remember_me(self):
        """取消勾选记住我复选框"""
        log.debug("取消勾选记住我")
        if self.is_remember_me_checked():
            self.driver_wrapper.click(self.REMEMBER_ME_CHECKBOX)
    
    def is_remember_me_checked(self) -> bool:
        """检查记住我是否已勾选"""
        try:
            checkbox = self.driver_wrapper.find_element(self.REMEMBER_ME_CHECKBOX)
            return checkbox.is_selected()
        except Exception:
            return False
    
    @allure.step("点击忘记密码链接")
    def click_forgot_password(self):
        """点击忘记密码链接"""
        log.debug("点击忘记密码链接")
        self.driver_wrapper.click(self.FORGOT_PASSWORD_LINK)
    
    @allure.step("执行登录操作")
    def login(self, username: str, password: str, remember_me: bool = False):
        """
        执行完整的登录操作
        
        Args:
            username: 用户名
            password: 密码
            remember_me: 是否记住我
        """
        log.info(f"执行登录操作，用户名: {username}")
        
        self.enter_username(username)
        self.enter_password(password)
        
        if remember_me:
            self.check_remember_me()
        else:
            self.uncheck_remember_me()
        
        self.click_login_button()
        
        # 等待登录处理完成
        self.wait_for_login_completion()
    
    @allure.step("等待登录完成")
    def wait_for_login_completion(self, timeout: int = 10):
        """
        等待登录处理完成
        
        Args:
            timeout: 超时时间（秒）
        """
        try:
            # 等待加载动画消失（如果有的话）
            if self.driver_wrapper.is_element_present(self.LOADING_SPINNER):
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                wait = WebDriverWait(self.driver, timeout)
                wait.until_not(EC.presence_of_element_located(self.LOADING_SPINNER))
            
            log.debug("登录处理完成")
        except Exception as e:
            log.warning(f"等待登录完成时出现异常: {e}")
    
    def get_error_message(self) -> str:
        """
        获取错误消息
        
        Returns:
            错误消息文本
        """
        try:
            if self.driver_wrapper.is_element_visible(self.ERROR_MESSAGE):
                error_text = self.driver_wrapper.get_text(self.ERROR_MESSAGE)
                log.debug(f"获取到错误消息: {error_text}")
                return error_text
        except Exception as e:
            log.debug(f"获取错误消息失败: {e}")
        return ""
    
    def get_success_message(self) -> str:
        """
        获取成功消息
        
        Returns:
            成功消息文本
        """
        try:
            if self.driver_wrapper.is_element_visible(self.SUCCESS_MESSAGE):
                success_text = self.driver_wrapper.get_text(self.SUCCESS_MESSAGE)
                log.debug(f"获取到成功消息: {success_text}")
                return success_text
        except Exception as e:
            log.debug(f"获取成功消息失败: {e}")
        return ""
    
    def is_login_successful(self) -> bool:
        """
        检查登录是否成功
        
        Returns:
            登录是否成功
        """
        try:
            # 检查是否跳转到其他页面（URL变化）
            current_url = self.driver_wrapper.get_current_url()
            if self.PAGE_PATH not in current_url:
                log.debug("登录成功：页面已跳转")
                return True
            
            # 检查是否有成功消息
            if self.get_success_message():
                log.debug("登录成功：显示成功消息")
                return True
            
            # 检查是否有错误消息
            if self.get_error_message():
                log.debug("登录失败：显示错误消息")
                return False
            
            log.debug("登录状态未知")
            return False
            
        except Exception as e:
            log.error(f"检查登录状态失败: {e}")
            return False
    
    def clear_form(self):
        """清空表单"""
        log.debug("清空登录表单")
        self.driver_wrapper.send_keys(self.USERNAME_INPUT, "", clear_first=True)
        self.driver_wrapper.send_keys(self.PASSWORD_INPUT, "", clear_first=True)
        self.uncheck_remember_me()
    
    def is_page_loaded(self) -> bool:
        """
        检查页面是否已加载
        
        Returns:
            页面是否已加载
        """
        try:
            return (self.driver_wrapper.is_element_present(self.USERNAME_INPUT) and
                    self.driver_wrapper.is_element_present(self.PASSWORD_INPUT) and
                    self.driver_wrapper.is_element_present(self.LOGIN_BUTTON))
        except Exception:
            return False
    
    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.driver_wrapper.get_page_title()
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        截图
        
        Args:
            filename: 截图文件名
            
        Returns:
            截图文件路径
        """
        return self.driver_wrapper.take_screenshot(filename)
