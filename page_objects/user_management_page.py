"""
用户管理页面对象模型
实现用户管理页面的元素定位和操作方法
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from typing import List, Dict, Optional

from page_objects.base_page import BasePage
from utilities.logger import log


class UserManagementPage(BasePage):
    """用户管理页面类"""
    
    # 页面元素定位器
    PAGE_TITLE = (By.CLASS_NAME, "page-title")
    ADD_USER_BUTTON = (By.ID, "add-user-btn")
    SEARCH_INPUT = (By.ID, "user-search")
    SEARCH_BUTTON = (By.ID, "search-btn")
    FILTER_DROPDOWN = (By.ID, "user-filter")
    REFRESH_BUTTON = (By.ID, "refresh-btn")
    
    # 用户表格
    USER_TABLE = (By.ID, "user-table")
    TABLE_HEADERS = (By.CSS_SELECTOR, "#user-table thead th")
    TABLE_ROWS = (By.CSS_SELECTOR, "#user-table tbody tr")
    
    # 表格列（根据实际表格结构调整）
    USER_ID_COLUMN = (By.CSS_SELECTOR, "td:nth-child(1)")
    USERNAME_COLUMN = (By.CSS_SELECTOR, "td:nth-child(2)")
    EMAIL_COLUMN = (By.CSS_SELECTOR, "td:nth-child(3)")
    ROLE_COLUMN = (By.CSS_SELECTOR, "td:nth-child(4)")
    STATUS_COLUMN = (By.CSS_SELECTOR, "td:nth-child(5)")
    ACTIONS_COLUMN = (By.CSS_SELECTOR, "td:nth-child(6)")
    
    # 操作按钮
    EDIT_BUTTON = (By.CLASS_NAME, "edit-btn")
    DELETE_BUTTON = (By.CLASS_NAME, "delete-btn")
    VIEW_BUTTON = (By.CLASS_NAME, "view-btn")
    ACTIVATE_BUTTON = (By.CLASS_NAME, "activate-btn")
    DEACTIVATE_BUTTON = (By.CLASS_NAME, "deactivate-btn")
    
    # 分页元素
    PAGINATION = (By.CLASS_NAME, "pagination")
    PREV_PAGE_BUTTON = (By.CLASS_NAME, "prev-page")
    NEXT_PAGE_BUTTON = (By.CLASS_NAME, "next-page")
    PAGE_INFO = (By.CLASS_NAME, "page-info")
    PAGE_SIZE_SELECT = (By.ID, "page-size")
    
    # 用户表单模态框
    USER_FORM_MODAL = (By.ID, "user-form-modal")
    FORM_TITLE = (By.CLASS_NAME, "form-title")
    USERNAME_INPUT = (By.ID, "username")
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "confirm-password")
    ROLE_SELECT = (By.ID, "role")
    STATUS_SELECT = (By.ID, "status")
    SAVE_BUTTON = (By.ID, "save-btn")
    CANCEL_BUTTON = (By.ID, "cancel-btn")
    
    # 确认删除模态框
    DELETE_CONFIRM_MODAL = (By.ID, "delete-confirm-modal")
    CONFIRM_DELETE_BUTTON = (By.ID, "confirm-delete-btn")
    CANCEL_DELETE_BUTTON = (By.ID, "cancel-delete-btn")
    
    # 页面URL路径
    PAGE_PATH = "/admin/users"
    
    def __init__(self, selenium_wrapper):
        """
        初始化用户管理页面
        
        Args:
            selenium_wrapper: Selenium封装实例
        """
        super().__init__(selenium_wrapper)
        
    @allure.step("导航到用户管理页面")
    def navigate_to_user_management_page(self):
        """导航到用户管理页面"""
        log.info("导航到用户管理页面")
        self.navigate_to(self.PAGE_PATH)
        self.wait_for_page_load()
    
    @allure.step("等待用户管理页面加载完成")
    def wait_for_page_load(self):
        """等待用户管理页面加载完成"""
        try:
            super().wait_for_page_load()
            # 等待用户表格加载
            if self.driver_wrapper.is_element_present(self.USER_TABLE):
                self.wait_for_element_visible(self.USER_TABLE)
            log.debug("用户管理页面加载完成")
        except Exception as e:
            log.error(f"等待用户管理页面加载失败: {e}")
            raise
    
    @allure.step("点击添加用户按钮")
    def click_add_user_button(self):
        """点击添加用户按钮"""
        log.debug("点击添加用户按钮")
        self.driver_wrapper.click(self.ADD_USER_BUTTON)
        self.wait_for_modal()
    
    @allure.step("搜索用户: {keyword}")
    def search_user(self, keyword: str):
        """
        搜索用户
        
        Args:
            keyword: 搜索关键词
        """
        log.info(f"搜索用户: {keyword}")
        self.driver_wrapper.send_keys(self.SEARCH_INPUT, keyword, clear_first=True)
        self.driver_wrapper.click(self.SEARCH_BUTTON)
        self.wait_for_page_load()
    
    @allure.step("设置用户过滤器: {filter_value}")
    def set_user_filter(self, filter_value: str):
        """
        设置用户过滤器
        
        Args:
            filter_value: 过滤器值
        """
        log.debug(f"设置用户过滤器: {filter_value}")
        filter_select = Select(self.driver_wrapper.find_element(self.FILTER_DROPDOWN))
        filter_select.select_by_visible_text(filter_value)
        self.wait_for_page_load()
    
    @allure.step("刷新用户列表")
    def refresh_user_list(self):
        """刷新用户列表"""
        log.debug("刷新用户列表")
        self.driver_wrapper.click(self.REFRESH_BUTTON)
        self.wait_for_page_load()
    
    def get_user_list(self) -> List[Dict[str, str]]:
        """
        获取用户列表
        
        Returns:
            用户信息列表
        """
        users = []
        try:
            if self.driver_wrapper.is_element_present(self.TABLE_ROWS):
                rows = self.driver_wrapper.find_elements(self.TABLE_ROWS)
                
                for row in rows:
                    user_info = {}
                    
                    # 获取用户ID
                    id_element = row.find_element(*self.USER_ID_COLUMN)
                    user_info["id"] = id_element.text
                    
                    # 获取用户名
                    username_element = row.find_element(*self.USERNAME_COLUMN)
                    user_info["username"] = username_element.text
                    
                    # 获取邮箱
                    email_element = row.find_element(*self.EMAIL_COLUMN)
                    user_info["email"] = email_element.text
                    
                    # 获取角色
                    role_element = row.find_element(*self.ROLE_COLUMN)
                    user_info["role"] = role_element.text
                    
                    # 获取状态
                    status_element = row.find_element(*self.STATUS_COLUMN)
                    user_info["status"] = status_element.text
                    
                    users.append(user_info)
                    
        except Exception as e:
            log.error(f"获取用户列表失败: {e}")
        
        return users
    
    @allure.step("根据用户名查找用户行")
    def find_user_row_by_username(self, username: str):
        """
        根据用户名查找用户行
        
        Args:
            username: 用户名
            
        Returns:
            用户行元素，如果未找到则返回None
        """
        try:
            if self.driver_wrapper.is_element_present(self.TABLE_ROWS):
                rows = self.driver_wrapper.find_elements(self.TABLE_ROWS)
                
                for row in rows:
                    username_element = row.find_element(*self.USERNAME_COLUMN)
                    if username_element.text == username:
                        return row
                        
        except Exception as e:
            log.error(f"查找用户行失败: {e}")
        
        return None
    
    @allure.step("编辑用户: {username}")
    def edit_user(self, username: str):
        """
        编辑用户
        
        Args:
            username: 用户名
        """
        log.info(f"编辑用户: {username}")
        user_row = self.find_user_row_by_username(username)
        
        if user_row:
            edit_button = user_row.find_element(*self.EDIT_BUTTON)
            edit_button.click()
            self.wait_for_modal()
        else:
            log.error(f"未找到用户: {username}")
            raise Exception(f"未找到用户: {username}")
    
    @allure.step("删除用户: {username}")
    def delete_user(self, username: str):
        """
        删除用户
        
        Args:
            username: 用户名
        """
        log.info(f"删除用户: {username}")
        user_row = self.find_user_row_by_username(username)
        
        if user_row:
            delete_button = user_row.find_element(*self.DELETE_BUTTON)
            delete_button.click()
            # 等待确认删除模态框
            self.wait_for_element_visible(self.DELETE_CONFIRM_MODAL)
        else:
            log.error(f"未找到用户: {username}")
            raise Exception(f"未找到用户: {username}")
    
    @allure.step("确认删除用户")
    def confirm_delete_user(self):
        """确认删除用户"""
        log.debug("确认删除用户")
        self.driver_wrapper.click(self.CONFIRM_DELETE_BUTTON)
        self.wait_for_element_invisible(self.DELETE_CONFIRM_MODAL)
        self.wait_for_page_load()
    
    @allure.step("取消删除用户")
    def cancel_delete_user(self):
        """取消删除用户"""
        log.debug("取消删除用户")
        self.driver_wrapper.click(self.CANCEL_DELETE_BUTTON)
        self.wait_for_element_invisible(self.DELETE_CONFIRM_MODAL)
    
    @allure.step("查看用户详情: {username}")
    def view_user_details(self, username: str):
        """
        查看用户详情
        
        Args:
            username: 用户名
        """
        log.info(f"查看用户详情: {username}")
        user_row = self.find_user_row_by_username(username)
        
        if user_row:
            view_button = user_row.find_element(*self.VIEW_BUTTON)
            view_button.click()
            self.wait_for_modal()
        else:
            log.error(f"未找到用户: {username}")
            raise Exception(f"未找到用户: {username}")
    
    @allure.step("激活用户: {username}")
    def activate_user(self, username: str):
        """
        激活用户
        
        Args:
            username: 用户名
        """
        log.info(f"激活用户: {username}")
        user_row = self.find_user_row_by_username(username)
        
        if user_row:
            if user_row.find_elements(*self.ACTIVATE_BUTTON):
                activate_button = user_row.find_element(*self.ACTIVATE_BUTTON)
                activate_button.click()
                self.wait_for_page_load()
            else:
                log.warning(f"用户 {username} 可能已经是激活状态")
        else:
            log.error(f"未找到用户: {username}")
            raise Exception(f"未找到用户: {username}")
    
    @allure.step("停用用户: {username}")
    def deactivate_user(self, username: str):
        """
        停用用户
        
        Args:
            username: 用户名
        """
        log.info(f"停用用户: {username}")
        user_row = self.find_user_row_by_username(username)
        
        if user_row:
            if user_row.find_elements(*self.DEACTIVATE_BUTTON):
                deactivate_button = user_row.find_element(*self.DEACTIVATE_BUTTON)
                deactivate_button.click()
                self.wait_for_page_load()
            else:
                log.warning(f"用户 {username} 可能已经是停用状态")
        else:
            log.error(f"未找到用户: {username}")
            raise Exception(f"未找到用户: {username}")
    
    @allure.step("填写用户表单")
    def fill_user_form(self, user_data: Dict[str, str]):
        """
        填写用户表单
        
        Args:
            user_data: 用户数据字典
        """
        log.info("填写用户表单")
        
        # 填写用户名
        if "username" in user_data:
            self.driver_wrapper.send_keys(self.USERNAME_INPUT, user_data["username"], clear_first=True)
        
        # 填写邮箱
        if "email" in user_data:
            self.driver_wrapper.send_keys(self.EMAIL_INPUT, user_data["email"], clear_first=True)
        
        # 填写密码
        if "password" in user_data:
            self.driver_wrapper.send_keys(self.PASSWORD_INPUT, user_data["password"], clear_first=True)
        
        # 确认密码
        if "confirm_password" in user_data:
            self.driver_wrapper.send_keys(self.CONFIRM_PASSWORD_INPUT, user_data["confirm_password"], clear_first=True)
        
        # 选择角色
        if "role" in user_data:
            role_select = Select(self.driver_wrapper.find_element(self.ROLE_SELECT))
            role_select.select_by_visible_text(user_data["role"])
        
        # 选择状态
        if "status" in user_data:
            status_select = Select(self.driver_wrapper.find_element(self.STATUS_SELECT))
            status_select.select_by_visible_text(user_data["status"])
    
    @allure.step("保存用户表单")
    def save_user_form(self):
        """保存用户表单"""
        log.debug("保存用户表单")
        self.driver_wrapper.click(self.SAVE_BUTTON)
        self.wait_for_element_invisible(self.USER_FORM_MODAL)
        self.wait_for_page_load()
    
    @allure.step("取消用户表单")
    def cancel_user_form(self):
        """取消用户表单"""
        log.debug("取消用户表单")
        self.driver_wrapper.click(self.CANCEL_BUTTON)
        self.wait_for_element_invisible(self.USER_FORM_MODAL)
    
    @allure.step("创建新用户")
    def create_user(self, user_data: Dict[str, str]):
        """
        创建新用户
        
        Args:
            user_data: 用户数据字典
        """
        log.info(f"创建新用户: {user_data.get('username', 'Unknown')}")
        self.click_add_user_button()
        self.fill_user_form(user_data)
        self.save_user_form()
    
    @allure.step("更新用户信息")
    def update_user(self, username: str, user_data: Dict[str, str]):
        """
        更新用户信息
        
        Args:
            username: 要更新的用户名
            user_data: 新的用户数据
        """
        log.info(f"更新用户信息: {username}")
        self.edit_user(username)
        self.fill_user_form(user_data)
        self.save_user_form()
    
    @allure.step("转到下一页")
    def go_to_next_page(self):
        """转到下一页"""
        if self.driver_wrapper.is_element_present(self.NEXT_PAGE_BUTTON):
            if self.driver_wrapper.find_element(self.NEXT_PAGE_BUTTON).is_enabled():
                self.driver_wrapper.click(self.NEXT_PAGE_BUTTON)
                self.wait_for_page_load()
                return True
        return False
    
    @allure.step("转到上一页")
    def go_to_previous_page(self):
        """转到上一页"""
        if self.driver_wrapper.is_element_present(self.PREV_PAGE_BUTTON):
            if self.driver_wrapper.find_element(self.PREV_PAGE_BUTTON).is_enabled():
                self.driver_wrapper.click(self.PREV_PAGE_BUTTON)
                self.wait_for_page_load()
                return True
        return False
    
    @allure.step("设置每页显示数量: {page_size}")
    def set_page_size(self, page_size: str):
        """
        设置每页显示数量
        
        Args:
            page_size: 每页显示数量
        """
        log.debug(f"设置每页显示数量: {page_size}")
        page_size_select = Select(self.driver_wrapper.find_element(self.PAGE_SIZE_SELECT))
        page_size_select.select_by_visible_text(page_size)
        self.wait_for_page_load()
    
    def get_page_info(self) -> Optional[str]:
        """
        获取分页信息
        
        Returns:
            分页信息文本
        """
        try:
            if self.driver_wrapper.is_element_present(self.PAGE_INFO):
                return self.driver_wrapper.get_text(self.PAGE_INFO)
        except Exception as e:
            log.debug(f"获取分页信息失败: {e}")
        return None
    
    def get_total_user_count(self) -> int:
        """
        获取用户总数
        
        Returns:
            用户总数
        """
        try:
            page_info = self.get_page_info()
            if page_info:
                # 假设分页信息格式为 "显示 1-10 共 100 条记录"
                import re
                match = re.search(r'共\s*(\d+)\s*条', page_info)
                if match:
                    return int(match.group(1))
        except Exception as e:
            log.debug(f"获取用户总数失败: {e}")
        return 0
    
    def is_page_loaded(self) -> bool:
        """
        检查页面是否已加载
        
        Returns:
            页面是否已加载
        """
        try:
            return (self.driver_wrapper.is_element_present(self.PAGE_TITLE) and
                    self.driver_wrapper.is_element_present(self.USER_TABLE))
        except Exception:
            return False
