"""
Selenium封装工具类
提供更友好的Web测试接口和自动截图功能
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from utilities.logger import log
from utilities.config_reader import config


class SeleniumWrapper:
    """Selenium封装类"""
    
    def __init__(self, browser: str = None, headless: bool = None):
        """
        初始化Selenium封装

        Args:
            browser: 浏览器类型 (chrome/firefox/edge)
            headless: 是否无头模式
        """
        self._browser = browser
        self._headless = headless
        self._initialized = False

        self.driver = None
        self.wait = None

        # 确保截图目录存在
        self.screenshot_dir = Path("reports/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # 延迟初始化配置
        self._initialize_config()

    def _initialize_config(self):
        """初始化配置"""
        if self._initialized:
            return

        try:
            # 从配置获取Web设置
            web_config = config.get_web_config()

            self.browser = self._browser or web_config.get("browser", "chrome")
            self.headless = self._headless if self._headless is not None else web_config.get("headless", False)
            self.window_size = web_config.get("window_size", "1920,1080")
            self.implicit_wait = web_config.get("implicit_wait", 10)
            self.explicit_wait = web_config.get("explicit_wait", 30)
            self.page_load_timeout = web_config.get("page_load_timeout", 60)
            self.screenshot_on_failure = web_config.get("screenshot_on_failure", True)

            self._initialized = True
            log.info(f"Selenium封装初始化完成，浏览器: {self.browser}, 无头模式: {self.headless}")

        except RuntimeError:
            # 配置未加载，使用默认值
            self.browser = self._browser or "chrome"
            self.headless = self._headless if self._headless is not None else False
            self.window_size = "1920,1080"
            self.implicit_wait = 10
            self.explicit_wait = 30
            self.page_load_timeout = 60
            self.screenshot_on_failure = True

            self._initialized = True
            log.debug("Selenium封装使用默认配置初始化")
    
    def start_driver(self):
        """启动浏览器驱动"""
        # 确保配置已初始化
        self._initialize_config()

        try:
            if self.browser.lower() == "chrome":
                self.driver = self._create_chrome_driver()
            elif self.browser.lower() == "firefox":
                self.driver = self._create_firefox_driver()
            elif self.browser.lower() == "edge":
                self.driver = self._create_edge_driver()
            else:
                raise ValueError(f"不支持的浏览器类型: {self.browser}")
            
            # 设置等待和超时
            self.driver.implicitly_wait(self.implicit_wait)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.wait = WebDriverWait(self.driver, self.explicit_wait)
            
            # 设置窗口大小
            if not self.headless:
                width, height = map(int, self.window_size.split(","))
                self.driver.set_window_size(width, height)
            
            log.info(f"浏览器驱动启动成功: {self.browser}")
            
        except Exception as e:
            log.error(f"启动浏览器驱动失败: {e}")
            raise
    
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """创建Chrome驱动"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """创建Firefox驱动"""
        options = webdriver.FirefoxOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    def _create_edge_driver(self) -> webdriver.Edge:
        """创建Edge驱动"""
        options = webdriver.EdgeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    
    def quit_driver(self):
        """退出浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
                log.info("浏览器驱动已退出")
            except Exception as e:
                log.warning(f"退出浏览器驱动时出现异常: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def navigate_to(self, url: str):
        """导航到指定URL"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未启动，请先调用start_driver()")
        
        log.info(f"导航到: {url}")
        self.driver.get(url)
    
    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> object:
        """
        查找元素
        
        Args:
            locator: 定位器元组 (By.ID, "element_id")
            timeout: 超时时间
            
        Returns:
            WebElement对象
        """
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located(locator))
        else:
            return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator: Tuple[str, str]) -> List[object]:
        """查找多个元素"""
        return self.driver.find_elements(*locator)
    
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = None) -> object:
        """等待元素可点击"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable(locator))
        else:
            return self.wait.until(EC.element_to_be_clickable(locator))
    
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = None) -> object:
        """等待元素可见"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.visibility_of_element_located(locator))
        else:
            return self.wait.until(EC.visibility_of_element_located(locator))
    
    def click(self, locator: Tuple[str, str]):
        """点击元素"""
        element = self.wait_for_element_clickable(locator)
        element.click()
        log.debug(f"点击元素: {locator}")
    
    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True):
        """输入文本"""
        element = self.find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        log.debug(f"输入文本到元素 {locator}: {text}")
    
    def get_text(self, locator: Tuple[str, str]) -> str:
        """获取元素文本"""
        element = self.find_element(locator)
        text = element.text
        log.debug(f"获取元素文本 {locator}: {text}")
        return text
    
    def get_attribute(self, locator: Tuple[str, str], attribute: str) -> str:
        """获取元素属性"""
        element = self.find_element(locator)
        value = element.get_attribute(attribute)
        log.debug(f"获取元素属性 {locator}.{attribute}: {value}")
        return value
    
    def is_element_present(self, locator: Tuple[str, str]) -> bool:
        """检查元素是否存在"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def is_element_visible(self, locator: Tuple[str, str]) -> bool:
        """检查元素是否可见"""
        try:
            element = self.driver.find_element(*locator)
            return element.is_displayed()
        except NoSuchElementException:
            return False
    
    def scroll_to_element(self, locator: Tuple[str, str]):
        """滚动到元素"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        log.debug(f"滚动到元素: {locator}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """截图"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        screenshot_path = self.screenshot_dir / filename
        
        if self.driver.save_screenshot(str(screenshot_path)):
            log.info(f"截图保存成功: {screenshot_path}")
            return str(screenshot_path)
        else:
            log.error("截图保存失败")
            return ""
    
    def take_screenshot_on_failure(self, test_name: str = None):
        """失败时自动截图"""
        if self.screenshot_on_failure and self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"failure_{test_name or 'unknown'}_{timestamp}.png"
            return self.take_screenshot(filename)
        return ""
    
    def get_current_url(self) -> str:
        """获取当前URL"""
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.driver.title
    
    def refresh_page(self):
        """刷新页面"""
        self.driver.refresh()
        log.debug("页面已刷新")
    
    def go_back(self):
        """后退"""
        self.driver.back()
        log.debug("页面后退")
    
    def go_forward(self):
        """前进"""
        self.driver.forward()
        log.debug("页面前进")


# 创建全局Selenium实例
selenium_wrapper = SeleniumWrapper()
