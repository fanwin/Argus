"""
表单页面对象模型
实现各种表单页面的元素定位和操作方法
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from typing import Dict, List, Optional, Any
import time

from page_objects.base_page import BasePage
from utilities.logger import log


class FormPage(BasePage):
    """通用表单页面类"""
    
    # 通用表单元素
    FORM_CONTAINER = (By.CLASS_NAME, "form-container")
    FORM_TITLE = (By.CLASS_NAME, "form-title")
    FORM_DESCRIPTION = (By.CLASS_NAME, "form-description")
    
    # 输入字段
    TEXT_INPUT = (By.CSS_SELECTOR, "input[type='text']")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    NUMBER_INPUT = (By.CSS_SELECTOR, "input[type='number']")
    DATE_INPUT = (By.CSS_SELECTOR, "input[type='date']")
    TEXTAREA = (By.TAG_NAME, "textarea")
    
    # 选择字段
    SELECT_DROPDOWN = (By.TAG_NAME, "select")
    CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    RADIO_BUTTON = (By.CSS_SELECTOR, "input[type='radio']")
    
    # 文件上传
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    FILE_UPLOAD_AREA = (By.CLASS_NAME, "file-upload-area")
    UPLOADED_FILES = (By.CLASS_NAME, "uploaded-file")
    
    # 按钮
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
    RESET_BUTTON = (By.CSS_SELECTOR, "button[type='reset'], input[type='reset']")
    CANCEL_BUTTON = (By.CLASS_NAME, "cancel-btn")
    SAVE_DRAFT_BUTTON = (By.CLASS_NAME, "save-draft-btn")
    
    # 验证消息
    FIELD_ERROR = (By.CLASS_NAME, "field-error")
    FIELD_SUCCESS = (By.CLASS_NAME, "field-success")
    FORM_ERROR = (By.CLASS_NAME, "form-error")
    FORM_SUCCESS = (By.CLASS_NAME, "form-success")
    
    # 必填字段标识
    REQUIRED_FIELD = (By.CLASS_NAME, "required")
    REQUIRED_ASTERISK = (By.CLASS_NAME, "required-asterisk")
    
    def __init__(self, selenium_wrapper):
        """
        初始化表单页面
        
        Args:
            selenium_wrapper: Selenium封装实例
        """
        super().__init__(selenium_wrapper)
        
    @allure.step("等待表单加载完成")
    def wait_for_form_load(self):
        """等待表单加载完成"""
        try:
            super().wait_for_page_load()
            # 等待表单容器加载
            if self.driver_wrapper.is_element_present(self.FORM_CONTAINER):
                self.wait_for_element_visible(self.FORM_CONTAINER)
            log.debug("表单加载完成")
        except Exception as e:
            log.error(f"等待表单加载失败: {e}")
            raise
    
    @allure.step("填写文本字段: {field_name} = {value}")
    def fill_text_field(self, field_locator: tuple, value: str, clear_first: bool = True):
        """
        填写文本字段
        
        Args:
            field_locator: 字段定位器
            value: 字段值
            clear_first: 是否先清空字段
        """
        log.debug(f"填写文本字段: {value}")
        self.driver_wrapper.send_keys(field_locator, value, clear_first=clear_first)
    
    @allure.step("选择下拉框选项: {option}")
    def select_dropdown_option(self, dropdown_locator: tuple, option: str, by_value: bool = False):
        """
        选择下拉框选项
        
        Args:
            dropdown_locator: 下拉框定位器
            option: 选项文本或值
            by_value: 是否按值选择
        """
        log.debug(f"选择下拉框选项: {option}")
        select_element = Select(self.driver_wrapper.find_element(dropdown_locator))
        
        if by_value:
            select_element.select_by_value(option)
        else:
            select_element.select_by_visible_text(option)
    
    @allure.step("勾选复选框")
    def check_checkbox(self, checkbox_locator: tuple):
        """
        勾选复选框
        
        Args:
            checkbox_locator: 复选框定位器
        """
        log.debug("勾选复选框")
        checkbox = self.driver_wrapper.find_element(checkbox_locator)
        if not checkbox.is_selected():
            checkbox.click()
    
    @allure.step("取消勾选复选框")
    def uncheck_checkbox(self, checkbox_locator: tuple):
        """
        取消勾选复选框
        
        Args:
            checkbox_locator: 复选框定位器
        """
        log.debug("取消勾选复选框")
        checkbox = self.driver_wrapper.find_element(checkbox_locator)
        if checkbox.is_selected():
            checkbox.click()
    
    @allure.step("选择单选按钮: {value}")
    def select_radio_button(self, radio_name: str, value: str):
        """
        选择单选按钮
        
        Args:
            radio_name: 单选按钮组名称
            value: 选项值
        """
        log.debug(f"选择单选按钮: {value}")
        radio_locator = (By.CSS_SELECTOR, f"input[type='radio'][name='{radio_name}'][value='{value}']")
        self.driver_wrapper.click(radio_locator)
    
    @allure.step("上传文件: {file_path}")
    def upload_file(self, file_input_locator: tuple, file_path: str):
        """
        上传文件
        
        Args:
            file_input_locator: 文件输入框定位器
            file_path: 文件路径
        """
        log.info(f"上传文件: {file_path}")
        file_input = self.driver_wrapper.find_element(file_input_locator)
        file_input.send_keys(file_path)
        
        # 等待文件上传完成
        time.sleep(1)
    
    @allure.step("拖拽上传文件")
    def drag_drop_upload_file(self, file_path: str):
        """
        拖拽上传文件
        
        Args:
            file_path: 文件路径
        """
        log.info(f"拖拽上传文件: {file_path}")
        # 这里需要使用JavaScript来模拟拖拽上传
        # 具体实现取决于前端的拖拽上传组件
        upload_area = self.driver_wrapper.find_element(self.FILE_UPLOAD_AREA)
        
        # 模拟文件拖拽（简化版本）
        js_script = """
        var fileInput = arguments[0];
        var filePath = arguments[1];
        
        // 创建文件对象（这里只是示例，实际需要根据具体实现调整）
        var event = new Event('drop', { bubbles: true });
        fileInput.dispatchEvent(event);
        """
        
        self.execute_javascript(js_script, upload_area, file_path)
    
    @allure.step("提交表单")
    def submit_form(self):
        """提交表单"""
        log.info("提交表单")
        self.driver_wrapper.click(self.SUBMIT_BUTTON)
        self.wait_for_page_load()
    
    @allure.step("重置表单")
    def reset_form(self):
        """重置表单"""
        log.debug("重置表单")
        if self.driver_wrapper.is_element_present(self.RESET_BUTTON):
            self.driver_wrapper.click(self.RESET_BUTTON)
        else:
            log.warning("重置按钮不存在")
    
    @allure.step("取消表单")
    def cancel_form(self):
        """取消表单"""
        log.debug("取消表单")
        if self.driver_wrapper.is_element_present(self.CANCEL_BUTTON):
            self.driver_wrapper.click(self.CANCEL_BUTTON)
        else:
            # 尝试按ESC键
            self.send_key(Keys.ESCAPE)
    
    @allure.step("保存草稿")
    def save_draft(self):
        """保存草稿"""
        log.debug("保存草稿")
        if self.driver_wrapper.is_element_present(self.SAVE_DRAFT_BUTTON):
            self.driver_wrapper.click(self.SAVE_DRAFT_BUTTON)
        else:
            log.warning("保存草稿按钮不存在")
    
    def get_field_error_message(self, field_locator: tuple) -> Optional[str]:
        """
        获取字段错误消息
        
        Args:
            field_locator: 字段定位器
            
        Returns:
            错误消息文本
        """
        try:
            # 查找字段附近的错误消息
            field_element = self.driver_wrapper.find_element(field_locator)
            parent = field_element.find_element(By.XPATH, "..")
            
            error_element = parent.find_element(*self.FIELD_ERROR)
            return error_element.text
        except Exception as e:
            log.debug(f"获取字段错误消息失败: {e}")
        return None
    
    def get_form_error_message(self) -> Optional[str]:
        """
        获取表单错误消息
        
        Returns:
            表单错误消息
        """
        try:
            if self.driver_wrapper.is_element_present(self.FORM_ERROR):
                return self.driver_wrapper.get_text(self.FORM_ERROR)
        except Exception as e:
            log.debug(f"获取表单错误消息失败: {e}")
        return None
    
    def get_form_success_message(self) -> Optional[str]:
        """
        获取表单成功消息
        
        Returns:
            表单成功消息
        """
        try:
            if self.driver_wrapper.is_element_present(self.FORM_SUCCESS):
                return self.driver_wrapper.get_text(self.FORM_SUCCESS)
        except Exception as e:
            log.debug(f"获取表单成功消息失败: {e}")
        return None
    
    def is_field_required(self, field_locator: tuple) -> bool:
        """
        检查字段是否为必填
        
        Args:
            field_locator: 字段定位器
            
        Returns:
            字段是否为必填
        """
        try:
            field_element = self.driver_wrapper.find_element(field_locator)
            
            # 检查required属性
            if field_element.get_attribute("required"):
                return True
            
            # 检查CSS类
            if "required" in field_element.get_attribute("class"):
                return True
            
            # 检查父元素是否有必填标识
            parent = field_element.find_element(By.XPATH, "..")
            if parent.find_elements(*self.REQUIRED_ASTERISK):
                return True
                
        except Exception as e:
            log.debug(f"检查字段必填状态失败: {e}")
        
        return False
    
    def get_field_value(self, field_locator: tuple) -> str:
        """
        获取字段值
        
        Args:
            field_locator: 字段定位器
            
        Returns:
            字段值
        """
        try:
            field_element = self.driver_wrapper.find_element(field_locator)
            
            # 根据字段类型获取值
            tag_name = field_element.tag_name.lower()
            field_type = field_element.get_attribute("type")
            
            if tag_name == "input":
                if field_type in ["text", "email", "password", "number", "date"]:
                    return field_element.get_attribute("value")
                elif field_type == "checkbox":
                    return str(field_element.is_selected())
                elif field_type == "radio":
                    return field_element.get_attribute("value") if field_element.is_selected() else ""
            elif tag_name == "textarea":
                return field_element.get_attribute("value")
            elif tag_name == "select":
                select_element = Select(field_element)
                return select_element.first_selected_option.text
                
        except Exception as e:
            log.debug(f"获取字段值失败: {e}")
        
        return ""
    
    def validate_form_fields(self, expected_values: Dict[str, Any]) -> Dict[str, bool]:
        """
        验证表单字段值
        
        Args:
            expected_values: 期望值字典，键为字段定位器，值为期望值
            
        Returns:
            验证结果字典
        """
        validation_results = {}
        
        for field_name, expected_value in expected_values.items():
            try:
                # 这里假设field_name是字段ID
                field_locator = (By.ID, field_name)
                actual_value = self.get_field_value(field_locator)
                validation_results[field_name] = (actual_value == str(expected_value))
            except Exception as e:
                log.error(f"验证字段 {field_name} 失败: {e}")
                validation_results[field_name] = False
        
        return validation_results
    
    def fill_form_data(self, form_data: Dict[str, Any]):
        """
        批量填写表单数据
        
        Args:
            form_data: 表单数据字典
        """
        log.info("批量填写表单数据")
        
        for field_name, value in form_data.items():
            try:
                # 假设field_name是字段ID
                field_locator = (By.ID, field_name)
                
                if not self.driver_wrapper.is_element_present(field_locator):
                    log.warning(f"字段不存在: {field_name}")
                    continue
                
                field_element = self.driver_wrapper.find_element(field_locator)
                tag_name = field_element.tag_name.lower()
                field_type = field_element.get_attribute("type")
                
                # 根据字段类型填写数据
                if tag_name == "input":
                    if field_type in ["text", "email", "password", "number", "date"]:
                        self.fill_text_field(field_locator, str(value))
                    elif field_type == "checkbox":
                        if value:
                            self.check_checkbox(field_locator)
                        else:
                            self.uncheck_checkbox(field_locator)
                    elif field_type == "radio":
                        radio_name = field_element.get_attribute("name")
                        self.select_radio_button(radio_name, str(value))
                    elif field_type == "file":
                        self.upload_file(field_locator, str(value))
                        
                elif tag_name == "textarea":
                    self.fill_text_field(field_locator, str(value))
                    
                elif tag_name == "select":
                    self.select_dropdown_option(field_locator, str(value))
                    
            except Exception as e:
                log.error(f"填写字段 {field_name} 失败: {e}")
    
    def get_uploaded_files(self) -> List[str]:
        """
        获取已上传文件列表
        
        Returns:
            已上传文件名列表
        """
        files = []
        try:
            if self.driver_wrapper.is_element_present(self.UPLOADED_FILES):
                file_elements = self.driver_wrapper.find_elements(self.UPLOADED_FILES)
                files = [elem.text for elem in file_elements if elem.text.strip()]
        except Exception as e:
            log.debug(f"获取已上传文件列表失败: {e}")
        return files
    
    def remove_uploaded_file(self, filename: str):
        """
        移除已上传的文件
        
        Args:
            filename: 文件名
        """
        log.debug(f"移除已上传文件: {filename}")
        try:
            if self.driver_wrapper.is_element_present(self.UPLOADED_FILES):
                file_elements = self.driver_wrapper.find_elements(self.UPLOADED_FILES)
                
                for file_elem in file_elements:
                    if filename in file_elem.text:
                        # 查找删除按钮
                        remove_button = file_elem.find_element(By.CLASS_NAME, "remove-file")
                        remove_button.click()
                        break
        except Exception as e:
            log.error(f"移除已上传文件失败: {e}")
    
    def is_form_valid(self) -> bool:
        """
        检查表单是否有效（无错误消息）
        
        Returns:
            表单是否有效
        """
        try:
            # 检查是否有表单级别的错误
            if self.driver_wrapper.is_element_present(self.FORM_ERROR):
                return False
            
            # 检查是否有字段级别的错误
            if self.driver_wrapper.is_element_present(self.FIELD_ERROR):
                return False
            
            return True
            
        except Exception as e:
            log.debug(f"检查表单有效性失败: {e}")
            return False
    
    def is_submit_button_enabled(self) -> bool:
        """
        检查提交按钮是否可用
        
        Returns:
            提交按钮是否可用
        """
        try:
            if self.driver_wrapper.is_element_present(self.SUBMIT_BUTTON):
                submit_button = self.driver_wrapper.find_element(self.SUBMIT_BUTTON)
                return submit_button.is_enabled()
        except Exception as e:
            log.debug(f"检查提交按钮状态失败: {e}")
        return False
    
    def is_page_loaded(self) -> bool:
        """
        检查页面是否已加载
        
        Returns:
            页面是否已加载
        """
        try:
            return self.driver_wrapper.is_element_present(self.FORM_CONTAINER)
        except Exception:
            return False
