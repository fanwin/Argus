"""
搜索页面对象模型
实现搜索页面的元素定位和操作方法
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from typing import List, Dict, Optional

from page_objects.base_page import BasePage
from utilities.logger import log


class SearchPage(BasePage):
    """搜索页面类"""
    
    # 页面元素定位器
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BUTTON = (By.ID, "search-button")
    SEARCH_SUGGESTIONS = (By.CLASS_NAME, "search-suggestions")
    SUGGESTION_ITEM = (By.CLASS_NAME, "suggestion-item")
    
    # 搜索过滤器
    FILTER_PANEL = (By.CLASS_NAME, "filter-panel")
    CATEGORY_FILTER = (By.ID, "category-filter")
    DATE_FILTER = (By.ID, "date-filter")
    SORT_BY_SELECT = (By.ID, "sort-by")
    SORT_ORDER_SELECT = (By.ID, "sort-order")
    APPLY_FILTERS_BUTTON = (By.ID, "apply-filters")
    CLEAR_FILTERS_BUTTON = (By.ID, "clear-filters")
    
    # 搜索结果
    SEARCH_RESULTS = (By.CLASS_NAME, "search-results")
    RESULT_ITEM = (By.CLASS_NAME, "result-item")
    RESULT_TITLE = (By.CLASS_NAME, "result-title")
    RESULT_DESCRIPTION = (By.CLASS_NAME, "result-description")
    RESULT_URL = (By.CLASS_NAME, "result-url")
    RESULT_DATE = (By.CLASS_NAME, "result-date")
    RESULT_CATEGORY = (By.CLASS_NAME, "result-category")
    
    # 搜索统计
    SEARCH_STATS = (By.CLASS_NAME, "search-stats")
    RESULTS_COUNT = (By.CLASS_NAME, "results-count")
    SEARCH_TIME = (By.CLASS_NAME, "search-time")
    
    # 分页
    PAGINATION = (By.CLASS_NAME, "pagination")
    PREV_PAGE = (By.CLASS_NAME, "prev-page")
    NEXT_PAGE = (By.CLASS_NAME, "next-page")
    PAGE_NUMBERS = (By.CLASS_NAME, "page-number")
    CURRENT_PAGE = (By.CLASS_NAME, "current-page")
    
    # 无结果状态
    NO_RESULTS = (By.CLASS_NAME, "no-results")
    NO_RESULTS_MESSAGE = (By.CLASS_NAME, "no-results-message")
    SEARCH_SUGGESTIONS_TEXT = (By.CLASS_NAME, "search-suggestions-text")
    
    # 高级搜索
    ADVANCED_SEARCH_TOGGLE = (By.ID, "advanced-search-toggle")
    ADVANCED_SEARCH_PANEL = (By.CLASS_NAME, "advanced-search-panel")
    EXACT_PHRASE_INPUT = (By.ID, "exact-phrase")
    ANY_WORDS_INPUT = (By.ID, "any-words")
    EXCLUDE_WORDS_INPUT = (By.ID, "exclude-words")
    
    # 页面URL路径
    PAGE_PATH = "/search"
    
    def __init__(self, selenium_wrapper):
        """
        初始化搜索页面
        
        Args:
            selenium_wrapper: Selenium封装实例
        """
        super().__init__(selenium_wrapper)
        
    @allure.step("导航到搜索页面")
    def navigate_to_search_page(self):
        """导航到搜索页面"""
        log.info("导航到搜索页面")
        self.navigate_to(self.PAGE_PATH)
        self.wait_for_page_load()
    
    @allure.step("等待搜索页面加载完成")
    def wait_for_page_load(self):
        """等待搜索页面加载完成"""
        try:
            super().wait_for_page_load()
            # 等待搜索输入框加载
            self.wait_for_element_visible(self.SEARCH_INPUT)
            log.debug("搜索页面加载完成")
        except Exception as e:
            log.error(f"等待搜索页面加载失败: {e}")
            raise
    
    @allure.step("执行搜索: {keyword}")
    def search(self, keyword: str):
        """
        执行搜索
        
        Args:
            keyword: 搜索关键词
        """
        log.info(f"执行搜索: {keyword}")
        self.driver_wrapper.send_keys(self.SEARCH_INPUT, keyword, clear_first=True)
        self.driver_wrapper.click(self.SEARCH_BUTTON)
        self.wait_for_search_results()
    
    @allure.step("等待搜索结果加载")
    def wait_for_search_results(self):
        """等待搜索结果加载"""
        try:
            # 等待搜索结果或无结果消息出现
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, 30)
            wait.until(
                lambda driver: (
                    self.driver_wrapper.is_element_present(self.SEARCH_RESULTS) or
                    self.driver_wrapper.is_element_present(self.NO_RESULTS)
                )
            )
            log.debug("搜索结果加载完成")
        except Exception as e:
            log.error(f"等待搜索结果失败: {e}")
            raise
    
    @allure.step("获取搜索建议")
    def get_search_suggestions(self) -> List[str]:
        """
        获取搜索建议
        
        Returns:
            搜索建议列表
        """
        suggestions = []
        try:
            if self.driver_wrapper.is_element_present(self.SEARCH_SUGGESTIONS):
                suggestion_elements = self.driver_wrapper.find_elements(self.SUGGESTION_ITEM)
                suggestions = [elem.text for elem in suggestion_elements if elem.text.strip()]
        except Exception as e:
            log.debug(f"获取搜索建议失败: {e}")
        return suggestions
    
    @allure.step("点击搜索建议: {suggestion}")
    def click_search_suggestion(self, suggestion: str):
        """
        点击搜索建议
        
        Args:
            suggestion: 建议文本
        """
        log.debug(f"点击搜索建议: {suggestion}")
        try:
            if self.driver_wrapper.is_element_present(self.SEARCH_SUGGESTIONS):
                suggestion_elements = self.driver_wrapper.find_elements(self.SUGGESTION_ITEM)
                for elem in suggestion_elements:
                    if elem.text == suggestion:
                        elem.click()
                        self.wait_for_search_results()
                        return
            log.warning(f"未找到搜索建议: {suggestion}")
        except Exception as e:
            log.error(f"点击搜索建议失败: {e}")
            raise
    
    @allure.step("设置分类过滤器: {category}")
    def set_category_filter(self, category: str):
        """
        设置分类过滤器
        
        Args:
            category: 分类名称
        """
        log.debug(f"设置分类过滤器: {category}")
        category_select = Select(self.driver_wrapper.find_element(self.CATEGORY_FILTER))
        category_select.select_by_visible_text(category)
    
    @allure.step("设置日期过滤器: {date_range}")
    def set_date_filter(self, date_range: str):
        """
        设置日期过滤器
        
        Args:
            date_range: 日期范围
        """
        log.debug(f"设置日期过滤器: {date_range}")
        date_select = Select(self.driver_wrapper.find_element(self.DATE_FILTER))
        date_select.select_by_visible_text(date_range)
    
    @allure.step("设置排序方式: {sort_by}")
    def set_sort_by(self, sort_by: str):
        """
        设置排序方式
        
        Args:
            sort_by: 排序方式
        """
        log.debug(f"设置排序方式: {sort_by}")
        sort_select = Select(self.driver_wrapper.find_element(self.SORT_BY_SELECT))
        sort_select.select_by_visible_text(sort_by)
    
    @allure.step("设置排序顺序: {sort_order}")
    def set_sort_order(self, sort_order: str):
        """
        设置排序顺序
        
        Args:
            sort_order: 排序顺序（升序/降序）
        """
        log.debug(f"设置排序顺序: {sort_order}")
        order_select = Select(self.driver_wrapper.find_element(self.SORT_ORDER_SELECT))
        order_select.select_by_visible_text(sort_order)
    
    @allure.step("应用过滤器")
    def apply_filters(self):
        """应用过滤器"""
        log.debug("应用过滤器")
        self.driver_wrapper.click(self.APPLY_FILTERS_BUTTON)
        self.wait_for_search_results()
    
    @allure.step("清除过滤器")
    def clear_filters(self):
        """清除过滤器"""
        log.debug("清除过滤器")
        self.driver_wrapper.click(self.CLEAR_FILTERS_BUTTON)
        self.wait_for_search_results()
    
    def get_search_results(self) -> List[Dict[str, str]]:
        """
        获取搜索结果
        
        Returns:
            搜索结果列表
        """
        results = []
        try:
            if self.driver_wrapper.is_element_present(self.RESULT_ITEM):
                result_elements = self.driver_wrapper.find_elements(self.RESULT_ITEM)
                
                for result in result_elements:
                    result_info = {}
                    
                    # 获取标题
                    try:
                        title_element = result.find_element(*self.RESULT_TITLE)
                        result_info["title"] = title_element.text
                    except:
                        result_info["title"] = ""
                    
                    # 获取描述
                    try:
                        desc_element = result.find_element(*self.RESULT_DESCRIPTION)
                        result_info["description"] = desc_element.text
                    except:
                        result_info["description"] = ""
                    
                    # 获取URL
                    try:
                        url_element = result.find_element(*self.RESULT_URL)
                        result_info["url"] = url_element.text
                    except:
                        result_info["url"] = ""
                    
                    # 获取日期
                    try:
                        date_element = result.find_element(*self.RESULT_DATE)
                        result_info["date"] = date_element.text
                    except:
                        result_info["date"] = ""
                    
                    # 获取分类
                    try:
                        category_element = result.find_element(*self.RESULT_CATEGORY)
                        result_info["category"] = category_element.text
                    except:
                        result_info["category"] = ""
                    
                    results.append(result_info)
                    
        except Exception as e:
            log.error(f"获取搜索结果失败: {e}")
        
        return results
    
    @allure.step("点击搜索结果: {title}")
    def click_search_result(self, title: str):
        """
        点击搜索结果
        
        Args:
            title: 结果标题
        """
        log.info(f"点击搜索结果: {title}")
        try:
            if self.driver_wrapper.is_element_present(self.RESULT_ITEM):
                result_elements = self.driver_wrapper.find_elements(self.RESULT_ITEM)
                
                for result in result_elements:
                    try:
                        title_element = result.find_element(*self.RESULT_TITLE)
                        if title_element.text == title:
                            title_element.click()
                            return
                    except:
                        continue
                        
            log.warning(f"未找到搜索结果: {title}")
            raise Exception(f"未找到搜索结果: {title}")
            
        except Exception as e:
            log.error(f"点击搜索结果失败: {e}")
            raise
    
    def get_results_count(self) -> Optional[int]:
        """
        获取搜索结果数量
        
        Returns:
            搜索结果数量
        """
        try:
            if self.driver_wrapper.is_element_present(self.RESULTS_COUNT):
                count_text = self.driver_wrapper.get_text(self.RESULTS_COUNT)
                # 提取数字
                import re
                match = re.search(r'(\d+)', count_text)
                if match:
                    return int(match.group(1))
        except Exception as e:
            log.debug(f"获取搜索结果数量失败: {e}")
        return None
    
    def get_search_time(self) -> Optional[str]:
        """
        获取搜索耗时
        
        Returns:
            搜索耗时
        """
        try:
            if self.driver_wrapper.is_element_present(self.SEARCH_TIME):
                return self.driver_wrapper.get_text(self.SEARCH_TIME)
        except Exception as e:
            log.debug(f"获取搜索耗时失败: {e}")
        return None
    
    def has_search_results(self) -> bool:
        """
        检查是否有搜索结果
        
        Returns:
            是否有搜索结果
        """
        return (self.driver_wrapper.is_element_present(self.SEARCH_RESULTS) and
                self.driver_wrapper.is_element_present(self.RESULT_ITEM))
    
    def has_no_results(self) -> bool:
        """
        检查是否无搜索结果
        
        Returns:
            是否无搜索结果
        """
        return self.driver_wrapper.is_element_present(self.NO_RESULTS)
    
    def get_no_results_message(self) -> Optional[str]:
        """
        获取无结果消息
        
        Returns:
            无结果消息
        """
        try:
            if self.driver_wrapper.is_element_present(self.NO_RESULTS_MESSAGE):
                return self.driver_wrapper.get_text(self.NO_RESULTS_MESSAGE)
        except Exception as e:
            log.debug(f"获取无结果消息失败: {e}")
        return None
    
    @allure.step("转到下一页")
    def go_to_next_page(self):
        """转到下一页"""
        if self.driver_wrapper.is_element_present(self.NEXT_PAGE):
            next_button = self.driver_wrapper.find_element(self.NEXT_PAGE)
            if next_button.is_enabled():
                next_button.click()
                self.wait_for_search_results()
                return True
        return False
    
    @allure.step("转到上一页")
    def go_to_previous_page(self):
        """转到上一页"""
        if self.driver_wrapper.is_element_present(self.PREV_PAGE):
            prev_button = self.driver_wrapper.find_element(self.PREV_PAGE)
            if prev_button.is_enabled():
                prev_button.click()
                self.wait_for_search_results()
                return True
        return False
    
    @allure.step("转到指定页面: {page_number}")
    def go_to_page(self, page_number: int):
        """
        转到指定页面
        
        Args:
            page_number: 页码
        """
        log.debug(f"转到第 {page_number} 页")
        try:
            page_elements = self.driver_wrapper.find_elements(self.PAGE_NUMBERS)
            for page_elem in page_elements:
                if page_elem.text == str(page_number):
                    page_elem.click()
                    self.wait_for_search_results()
                    return True
        except Exception as e:
            log.error(f"转到指定页面失败: {e}")
        return False
    
    def get_current_page_number(self) -> Optional[int]:
        """
        获取当前页码
        
        Returns:
            当前页码
        """
        try:
            if self.driver_wrapper.is_element_present(self.CURRENT_PAGE):
                page_text = self.driver_wrapper.get_text(self.CURRENT_PAGE)
                return int(page_text)
        except Exception as e:
            log.debug(f"获取当前页码失败: {e}")
        return None
    
    @allure.step("切换高级搜索")
    def toggle_advanced_search(self):
        """切换高级搜索面板"""
        log.debug("切换高级搜索")
        self.driver_wrapper.click(self.ADVANCED_SEARCH_TOGGLE)
        # 等待面板展开或收起
        import time
        time.sleep(0.5)
    
    @allure.step("执行高级搜索")
    def advanced_search(self, exact_phrase: str = "", any_words: str = "", exclude_words: str = ""):
        """
        执行高级搜索
        
        Args:
            exact_phrase: 精确短语
            any_words: 任意词语
            exclude_words: 排除词语
        """
        log.info("执行高级搜索")
        
        # 确保高级搜索面板打开
        if not self.driver_wrapper.is_element_present(self.ADVANCED_SEARCH_PANEL):
            self.toggle_advanced_search()
        
        # 填写搜索条件
        if exact_phrase:
            self.driver_wrapper.send_keys(self.EXACT_PHRASE_INPUT, exact_phrase, clear_first=True)
        
        if any_words:
            self.driver_wrapper.send_keys(self.ANY_WORDS_INPUT, any_words, clear_first=True)
        
        if exclude_words:
            self.driver_wrapper.send_keys(self.EXCLUDE_WORDS_INPUT, exclude_words, clear_first=True)
        
        # 执行搜索
        self.driver_wrapper.click(self.SEARCH_BUTTON)
        self.wait_for_search_results()
    
    def is_page_loaded(self) -> bool:
        """
        检查页面是否已加载
        
        Returns:
            页面是否已加载
        """
        try:
            return self.driver_wrapper.is_element_present(self.SEARCH_INPUT)
        except Exception:
            return False
