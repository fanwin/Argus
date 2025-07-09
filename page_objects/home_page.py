"""
主页页面对象模型
实现主页的元素定位和操作方法
"""

import allure
from selenium.webdriver.common.by import By
from typing import List, Optional

from page_objects.base_page import BasePage
from utilities.logger import log


class HomePage(BasePage):
    """主页页面类"""
    
    # 页面元素定位器
    WELCOME_MESSAGE = (By.CLASS_NAME, "welcome-message")
    MAIN_NAVIGATION = (By.CLASS_NAME, "main-nav")
    SEARCH_BOX = (By.ID, "search-box")
    SEARCH_BUTTON = (By.ID, "search-btn")
    HERO_SECTION = (By.CLASS_NAME, "hero-section")
    FEATURE_CARDS = (By.CLASS_NAME, "feature-card")
    NEWS_SECTION = (By.CLASS_NAME, "news-section")
    NEWS_ITEMS = (By.CLASS_NAME, "news-item")
    FOOTER_LINKS = (By.CSS_SELECTOR, "footer a")
    
    # 导航链接
    HOME_LINK = (By.LINK_TEXT, "首页")
    PRODUCTS_LINK = (By.LINK_TEXT, "产品")
    SERVICES_LINK = (By.LINK_TEXT, "服务")
    ABOUT_LINK = (By.LINK_TEXT, "关于我们")
    CONTACT_LINK = (By.LINK_TEXT, "联系我们")
    LOGIN_LINK = (By.LINK_TEXT, "登录")
    REGISTER_LINK = (By.LINK_TEXT, "注册")
    
    # 用户相关元素（已登录状态）
    USER_AVATAR = (By.CLASS_NAME, "user-avatar")
    USER_DROPDOWN = (By.CLASS_NAME, "user-dropdown")
    PROFILE_LINK = (By.LINK_TEXT, "个人资料")
    SETTINGS_LINK = (By.LINK_TEXT, "设置")
    DASHBOARD_LINK = (By.LINK_TEXT, "仪表板")
    
    # 页面URL路径
    PAGE_PATH = "/"
    
    def __init__(self, selenium_wrapper):
        """
        初始化主页
        
        Args:
            selenium_wrapper: Selenium封装实例
        """
        super().__init__(selenium_wrapper)
        
    @allure.step("导航到主页")
    def navigate_to_home_page(self):
        """导航到主页"""
        log.info("导航到主页")
        self.navigate_to(self.PAGE_PATH)
        self.wait_for_page_load()
    
    @allure.step("等待主页加载完成")
    def wait_for_page_load(self):
        """等待主页加载完成"""
        try:
            super().wait_for_page_load()
            # 等待主要内容加载
            if self.driver_wrapper.is_element_present(self.HERO_SECTION):
                self.wait_for_element_visible(self.HERO_SECTION)
            log.debug("主页加载完成")
        except Exception as e:
            log.error(f"等待主页加载失败: {e}")
            raise
    
    @allure.step("搜索内容: {keyword}")
    def search(self, keyword: str):
        """
        执行搜索
        
        Args:
            keyword: 搜索关键词
        """
        log.info(f"搜索关键词: {keyword}")
        
        if self.driver_wrapper.is_element_present(self.SEARCH_BOX):
            self.driver_wrapper.send_keys(self.SEARCH_BOX, keyword)
            
            if self.driver_wrapper.is_element_present(self.SEARCH_BUTTON):
                self.driver_wrapper.click(self.SEARCH_BUTTON)
            else:
                # 如果没有搜索按钮，尝试按回车键
                from selenium.webdriver.common.keys import Keys
                self.driver_wrapper.send_keys(self.SEARCH_BOX, Keys.RETURN)
            
            self.wait_for_page_load()
        else:
            log.warning("搜索框不存在")
            raise Exception("搜索框不存在")
    
    @allure.step("点击导航链接: {link_text}")
    def click_navigation_link(self, link_text: str):
        """
        点击导航链接
        
        Args:
            link_text: 链接文本
        """
        log.debug(f"点击导航链接: {link_text}")
        link_locator = (By.LINK_TEXT, link_text)
        
        if self.driver_wrapper.is_element_present(link_locator):
            self.driver_wrapper.click(link_locator)
            self.wait_for_page_load()
        else:
            log.warning(f"导航链接不存在: {link_text}")
            raise Exception(f"导航链接不存在: {link_text}")
    
    @allure.step("点击登录链接")
    def click_login_link(self):
        """点击登录链接"""
        self.click_navigation_link("登录")
    
    @allure.step("点击注册链接")
    def click_register_link(self):
        """点击注册链接"""
        self.click_navigation_link("注册")
    
    @allure.step("点击产品链接")
    def click_products_link(self):
        """点击产品链接"""
        self.click_navigation_link("产品")
    
    @allure.step("点击服务链接")
    def click_services_link(self):
        """点击服务链接"""
        self.click_navigation_link("服务")
    
    @allure.step("点击关于我们链接")
    def click_about_link(self):
        """点击关于我们链接"""
        self.click_navigation_link("关于我们")
    
    @allure.step("点击联系我们链接")
    def click_contact_link(self):
        """点击联系我们链接"""
        self.click_navigation_link("联系我们")
    
    @allure.step("点击用户头像")
    def click_user_avatar(self):
        """点击用户头像（已登录状态）"""
        if self.driver_wrapper.is_element_present(self.USER_AVATAR):
            self.driver_wrapper.click(self.USER_AVATAR)
            # 等待下拉菜单出现
            if self.driver_wrapper.is_element_present(self.USER_DROPDOWN):
                self.wait_for_element_visible(self.USER_DROPDOWN)
        else:
            log.warning("用户头像不存在，可能未登录")
            raise Exception("用户头像不存在，可能未登录")
    
    @allure.step("点击个人资料链接")
    def click_profile_link(self):
        """点击个人资料链接"""
        self.click_user_avatar()
        if self.driver_wrapper.is_element_present(self.PROFILE_LINK):
            self.driver_wrapper.click(self.PROFILE_LINK)
            self.wait_for_page_load()
        else:
            log.warning("个人资料链接不存在")
            raise Exception("个人资料链接不存在")
    
    @allure.step("点击设置链接")
    def click_settings_link(self):
        """点击设置链接"""
        self.click_user_avatar()
        if self.driver_wrapper.is_element_present(self.SETTINGS_LINK):
            self.driver_wrapper.click(self.SETTINGS_LINK)
            self.wait_for_page_load()
        else:
            log.warning("设置链接不存在")
            raise Exception("设置链接不存在")
    
    @allure.step("点击仪表板链接")
    def click_dashboard_link(self):
        """点击仪表板链接"""
        self.click_user_avatar()
        if self.driver_wrapper.is_element_present(self.DASHBOARD_LINK):
            self.driver_wrapper.click(self.DASHBOARD_LINK)
            self.wait_for_page_load()
        else:
            log.warning("仪表板链接不存在")
            raise Exception("仪表板链接不存在")
    
    def get_welcome_message(self) -> Optional[str]:
        """
        获取欢迎消息
        
        Returns:
            欢迎消息文本，如果没有则返回None
        """
        try:
            if self.driver_wrapper.is_element_present(self.WELCOME_MESSAGE):
                return self.driver_wrapper.get_text(self.WELCOME_MESSAGE)
        except Exception as e:
            log.debug(f"获取欢迎消息失败: {e}")
        return None
    
    def get_feature_cards(self) -> List[dict]:
        """
        获取功能卡片信息
        
        Returns:
            功能卡片信息列表
        """
        cards = []
        try:
            if self.driver_wrapper.is_element_present(self.FEATURE_CARDS):
                card_elements = self.driver_wrapper.find_elements(self.FEATURE_CARDS)
                
                for card in card_elements:
                    card_info = {}
                    
                    # 获取卡片标题
                    title_element = card.find_element(By.CLASS_NAME, "card-title")
                    if title_element:
                        card_info["title"] = title_element.text
                    
                    # 获取卡片描述
                    desc_element = card.find_element(By.CLASS_NAME, "card-description")
                    if desc_element:
                        card_info["description"] = desc_element.text
                    
                    # 获取卡片链接
                    link_element = card.find_element(By.TAG_NAME, "a")
                    if link_element:
                        card_info["link"] = link_element.get_attribute("href")
                    
                    cards.append(card_info)
                    
        except Exception as e:
            log.debug(f"获取功能卡片失败: {e}")
        
        return cards
    
    def get_news_items(self) -> List[dict]:
        """
        获取新闻条目信息
        
        Returns:
            新闻条目信息列表
        """
        news = []
        try:
            if self.driver_wrapper.is_element_present(self.NEWS_ITEMS):
                news_elements = self.driver_wrapper.find_elements(self.NEWS_ITEMS)
                
                for item in news_elements:
                    news_info = {}
                    
                    # 获取新闻标题
                    title_element = item.find_element(By.CLASS_NAME, "news-title")
                    if title_element:
                        news_info["title"] = title_element.text
                    
                    # 获取新闻摘要
                    summary_element = item.find_element(By.CLASS_NAME, "news-summary")
                    if summary_element:
                        news_info["summary"] = summary_element.text
                    
                    # 获取新闻日期
                    date_element = item.find_element(By.CLASS_NAME, "news-date")
                    if date_element:
                        news_info["date"] = date_element.text
                    
                    # 获取新闻链接
                    link_element = item.find_element(By.TAG_NAME, "a")
                    if link_element:
                        news_info["link"] = link_element.get_attribute("href")
                    
                    news.append(news_info)
                    
        except Exception as e:
            log.debug(f"获取新闻条目失败: {e}")
        
        return news
    
    def get_footer_links(self) -> List[dict]:
        """
        获取页脚链接信息
        
        Returns:
            页脚链接信息列表
        """
        links = []
        try:
            if self.driver_wrapper.is_element_present(self.FOOTER_LINKS):
                link_elements = self.driver_wrapper.find_elements(self.FOOTER_LINKS)
                
                for link in link_elements:
                    link_info = {
                        "text": link.text,
                        "href": link.get_attribute("href")
                    }
                    links.append(link_info)
                    
        except Exception as e:
            log.debug(f"获取页脚链接失败: {e}")
        
        return links
    
    def is_user_logged_in(self) -> bool:
        """
        检查用户是否已登录
        
        Returns:
            用户是否已登录
        """
        return self.driver_wrapper.is_element_present(self.USER_AVATAR)
    
    def is_page_loaded(self) -> bool:
        """
        检查页面是否已加载
        
        Returns:
            页面是否已加载
        """
        try:
            # 检查主要导航是否存在
            if not self.driver_wrapper.is_element_present(self.MAIN_NAVIGATION):
                return False
            
            # 检查页面标题
            title = self.get_page_title()
            if not title or title == "":
                return False
            
            return True
            
        except Exception:
            return False
    
    @allure.step("验证页面元素")
    def verify_page_elements(self):
        """验证页面主要元素是否存在"""
        elements_to_check = [
            (self.MAIN_NAVIGATION, "主导航"),
            (self.SEARCH_BOX, "搜索框"),
            (self.HERO_SECTION, "主要内容区域")
        ]
        
        missing_elements = []
        for locator, name in elements_to_check:
            if not self.driver_wrapper.is_element_present(locator):
                missing_elements.append(name)
        
        if missing_elements:
            log.warning(f"以下元素缺失: {', '.join(missing_elements)}")
            return False
        
        log.info("页面主要元素验证通过")
        return True
