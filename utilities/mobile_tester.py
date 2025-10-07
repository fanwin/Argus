"""
Mobile Testing Utilities
移动端测试工具类 - 支持Android和iOS应用测试
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    from appium import webdriver
    from appium.webdriver.common.appiumby import AppiumBy
    from appium.webdriver.common.touch_action import TouchAction
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False

from utilities.logger import log
from utilities.config_reader import config


@dataclass
class MobileDevice:
    """移动设备配置"""
    platform_name: str  # Android or iOS
    platform_version: str
    device_name: str
    app_package: Optional[str] = None  # Android
    app_activity: Optional[str] = None  # Android
    bundle_id: Optional[str] = None  # iOS
    udid: Optional[str] = None
    automation_name: Optional[str] = None


@dataclass
class TouchGesture:
    """触摸手势数据"""
    action_type: str  # tap, swipe, pinch, zoom
    coordinates: Tuple[int, int]
    duration: int = 1000
    end_coordinates: Optional[Tuple[int, int]] = None


class MobileTester:
    """移动端测试器"""
    
    def __init__(self, device_config: MobileDevice, appium_server_url: str = "http://localhost:4723/wd/hub"):
        if not APPIUM_AVAILABLE:
            raise ImportError("Appium not available. Install with: pip install Appium-Python-Client")
        
        self.device_config = device_config
        self.appium_server_url = appium_server_url
        self.driver = None
        self.wait = None
        
    def start_session(self, app_path: str = None):
        """启动移动应用测试会话"""
        log.info(f"启动移动端测试会话: {self.device_config.platform_name}")
        
        desired_caps = {
            'platformName': self.device_config.platform_name,
            'platformVersion': self.device_config.platform_version,
            'deviceName': self.device_config.device_name,
            'automationName': self.device_config.automation_name or self._get_default_automation_name(),
            'newCommandTimeout': 300,
            'noReset': True
        }
        
        # Android特定配置
        if self.device_config.platform_name.lower() == 'android':
            if self.device_config.app_package:
                desired_caps['appPackage'] = self.device_config.app_package
            if self.device_config.app_activity:
                desired_caps['appActivity'] = self.device_config.app_activity
            if app_path:
                desired_caps['app'] = app_path
        
        # iOS特定配置
        elif self.device_config.platform_name.lower() == 'ios':
            if self.device_config.bundle_id:
                desired_caps['bundleId'] = self.device_config.bundle_id
            if self.device_config.udid:
                desired_caps['udid'] = self.device_config.udid
            if app_path:
                desired_caps['app'] = app_path
        
        try:
            self.driver = webdriver.Remote(self.appium_server_url, desired_caps)
            self.wait = WebDriverWait(self.driver, 30)
            log.info("移动端测试会话启动成功")
            
            # 等待应用启动
            time.sleep(3)
            
        except Exception as e:
            log.error(f"启动移动端测试会话失败: {e}")
            raise
    
    def stop_session(self):
        """停止测试会话"""
        if self.driver:
            try:
                self.driver.quit()
                log.info("移动端测试会话已停止")
            except Exception as e:
                log.error(f"停止测试会话失败: {e}")
    
    def _get_default_automation_name(self):
        """获取默认的自动化引擎名称"""
        if self.device_config.platform_name.lower() == 'android':
            return 'UiAutomator2'
        elif self.device_config.platform_name.lower() == 'ios':
            return 'XCUITest'
        return None
    
    def find_element_by_id(self, element_id: str, timeout: int = 10):
        """通过ID查找元素"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((AppiumBy.ID, element_id)))
            return element
        except Exception as e:
            log.error(f"查找元素失败 (ID: {element_id}): {e}")
            return None
    
    def find_element_by_xpath(self, xpath: str, timeout: int = 10):
        """通过XPath查找元素"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
            return element
        except Exception as e:
            log.error(f"查找元素失败 (XPath: {xpath}): {e}")
            return None
    
    def find_element_by_accessibility_id(self, accessibility_id: str, timeout: int = 10):
        """通过Accessibility ID查找元素"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id)))
            return element
        except Exception as e:
            log.error(f"查找元素失败 (Accessibility ID: {accessibility_id}): {e}")
            return None
    
    def tap_element(self, element_locator: Tuple[str, str], timeout: int = 10):
        """点击元素"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(element_locator))
            element.click()
            log.info(f"点击元素成功: {element_locator}")
            return True
        except Exception as e:
            log.error(f"点击元素失败: {e}")
            return False
    
    def input_text(self, element_locator: Tuple[str, str], text: str, clear_first: bool = True):
        """输入文本"""
        try:
            element = self.wait.until(EC.presence_of_element_located(element_locator))
            if clear_first:
                element.clear()
            element.send_keys(text)
            log.info(f"输入文本成功: {text}")
            return True
        except Exception as e:
            log.error(f"输入文本失败: {e}")
            return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        """滑动手势"""
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            log.info(f"滑动手势成功: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            return True
        except Exception as e:
            log.error(f"滑动手势失败: {e}")
            return False
    
    def scroll_to_element(self, element_text: str, direction: str = "down"):
        """滚动到指定元素"""
        try:
            if self.device_config.platform_name.lower() == 'android':
                # Android UiScrollable
                scrollable_selector = f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                element_selector = f'.scrollIntoView(new UiSelector().textContains("{element_text}").instance(0))'
                self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scrollable_selector + element_selector)
            else:
                # iOS滚动实现
                self._ios_scroll_to_element(element_text, direction)
            
            log.info(f"滚动到元素成功: {element_text}")
            return True
        except Exception as e:
            log.error(f"滚动到元素失败: {e}")
            return False
    
    def _ios_scroll_to_element(self, element_text: str, direction: str):
        """iOS滚动到元素的实现"""
        max_attempts = 10
        for _ in range(max_attempts):
            try:
                element = self.driver.find_element(AppiumBy.XPATH, f"//*[contains(@name, '{element_text}')]")
                if element.is_displayed():
                    return element
            except:
                pass
            
            # 执行滚动
            size = self.driver.get_window_size()
            if direction == "down":
                self.swipe(size['width'] // 2, size['height'] * 0.8, 
                          size['width'] // 2, size['height'] * 0.2)
            else:
                self.swipe(size['width'] // 2, size['height'] * 0.2, 
                          size['width'] // 2, size['height'] * 0.8)
        
        raise Exception(f"无法找到元素: {element_text}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """截图"""
        try:
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"mobile_screenshot_{timestamp}.png"
            
            screenshots_dir = Path("reports/screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            screenshot_path = screenshots_dir / filename
            self.driver.save_screenshot(str(screenshot_path))
            
            log.info(f"截图保存成功: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            log.error(f"截图失败: {e}")
            return None
    
    def get_device_info(self) -> Dict:
        """获取设备信息"""
        try:
            device_info = {
                'platform_name': self.device_config.platform_name,
                'platform_version': self.device_config.platform_version,
                'device_name': self.device_config.device_name,
                'screen_size': self.driver.get_window_size(),
                'orientation': self.driver.orientation
            }
            
            if self.device_config.platform_name.lower() == 'android':
                device_info.update({
                    'app_package': self.device_config.app_package,
                    'app_activity': self.device_config.app_activity
                })
            
            return device_info
        except Exception as e:
            log.error(f"获取设备信息失败: {e}")
            return {}
    
    def install_app(self, app_path: str):
        """安装应用"""
        try:
            self.driver.install_app(app_path)
            log.info(f"应用安装成功: {app_path}")
            return True
        except Exception as e:
            log.error(f"应用安装失败: {e}")
            return False
    
    def uninstall_app(self, app_id: str):
        """卸载应用"""
        try:
            self.driver.remove_app(app_id)
            log.info(f"应用卸载成功: {app_id}")
            return True
        except Exception as e:
            log.error(f"应用卸载失败: {e}")
            return False
    
    def launch_app(self):
        """启动应用"""
        try:
            self.driver.launch_app()
            log.info("应用启动成功")
            return True
        except Exception as e:
            log.error(f"应用启动失败: {e}")
            return False
    
    def close_app(self):
        """关闭应用"""
        try:
            self.driver.close_app()
            log.info("应用关闭成功")
            return True
        except Exception as e:
            log.error(f"应用关闭失败: {e}")
            return False
    
    def background_app(self, seconds: int = 5):
        """将应用置于后台"""
        try:
            self.driver.background_app(seconds)
            log.info(f"应用已置于后台 {seconds} 秒")
            return True
        except Exception as e:
            log.error(f"应用后台操作失败: {e}")
            return False
    
    def rotate_device(self, orientation: str):
        """旋转设备"""
        try:
            self.driver.orientation = orientation.upper()
            log.info(f"设备旋转成功: {orientation}")
            return True
        except Exception as e:
            log.error(f"设备旋转失败: {e}")
            return False
    
    def get_app_performance_data(self, package_name: str, data_type: str = "cpuinfo") -> Dict:
        """获取应用性能数据"""
        try:
            if self.device_config.platform_name.lower() == 'android':
                performance_data = self.driver.get_performance_data(package_name, data_type)
                return {
                    'package_name': package_name,
                    'data_type': data_type,
                    'data': performance_data
                }
            else:
                log.warning("iOS性能数据获取功能暂不支持")
                return {}
        except Exception as e:
            log.error(f"获取性能数据失败: {e}")
            return {}
    
    def execute_mobile_command(self, command: str, params: Dict = None):
        """执行移动端特定命令"""
        try:
            result = self.driver.execute_script(f"mobile: {command}", params or {})
            log.info(f"移动端命令执行成功: {command}")
            return result
        except Exception as e:
            log.error(f"移动端命令执行失败: {e}")
            return None


class MobileTestSuite:
    """移动端测试套件"""
    
    def __init__(self, device_configs: List[MobileDevice]):
        self.device_configs = device_configs
        self.test_results = []
    
    def run_cross_platform_test(self, test_function: callable, *args, **kwargs):
        """跨平台测试执行"""
        results = {}
        
        for device_config in self.device_configs:
            log.info(f"在设备上执行测试: {device_config.device_name}")
            
            mobile_tester = MobileTester(device_config)
            
            try:
                mobile_tester.start_session()
                result = test_function(mobile_tester, *args, **kwargs)
                results[device_config.device_name] = {
                    'success': True,
                    'result': result,
                    'device_info': mobile_tester.get_device_info()
                }
            except Exception as e:
                log.error(f"设备 {device_config.device_name} 测试失败: {e}")
                results[device_config.device_name] = {
                    'success': False,
                    'error': str(e),
                    'device_info': {}
                }
            finally:
                mobile_tester.stop_session()
        
        return results
    
    def generate_compatibility_report(self, test_results: Dict, output_file: str = None):
        """生成兼容性测试报告"""
        from datetime import datetime
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"mobile_compatibility_report_{timestamp}.json"
        
        reports_dir = Path("reports/mobile")
        reports_dir.mkdir(exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_devices': len(test_results),
            'successful_devices': sum(1 for r in test_results.values() if r['success']),
            'failed_devices': sum(1 for r in test_results.values() if not r['success']),
            'device_results': test_results
        }
        
        output_path = reports_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        log.info(f"移动端兼容性报告已保存: {output_path}")
        return output_path
