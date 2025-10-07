"""
移动端测试案例
展示移动端测试功能：Android/iOS应用测试、手势操作、设备功能等
注意：需要配置Appium服务器和移动设备/模拟器
"""

import pytest
import allure
import time
from typing import Dict, Any

from utilities.mobile_tester import MobileTester, MobileDevice, TouchGesture, CrossPlatformTester
from utilities.logger import log


@allure.epic("移动端测试")
@allure.feature("移动应用自动化测试")
class TestMobile:
    """移动端测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_mobile_test(self):
        """设置移动端测试环境"""
        # Android设备配置
        self.android_device = MobileDevice(
            platform_name="Android",
            platform_version="11.0",
            device_name="Android Emulator",
            app_package="com.android.chrome",
            app_activity="com.google.android.apps.chrome.Main",
            automation_name="UiAutomator2"
        )
        
        # iOS设备配置
        self.ios_device = MobileDevice(
            platform_name="iOS",
            platform_version="15.0",
            device_name="iPhone 13",
            bundle_id="com.apple.mobilesafari",
            automation_name="XCUITest"
        )
        
        # 测试URL
        self.test_urls = {
            "mobile_friendly": "https://m.baidu.com",
            "responsive": "https://getbootstrap.com",
            "webgoat_mobile": "https://owasp.org/www-project-webgoat/"
        }
        
        log.info("移动端测试环境配置完成")
    
    @allure.story("Android应用测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.mobile
    @pytest.mark.android
    def test_android_app_functionality(self):
        """测试Android应用功能"""
        
        # 检查Appium是否可用
        try:
            from utilities.mobile_tester import APPIUM_AVAILABLE
            if not APPIUM_AVAILABLE:
                pytest.skip("Appium不可用，跳过移动端测试")
        except ImportError:
            pytest.skip("移动端测试依赖不可用")
        
        mobile_tester = MobileTester(self.android_device)
        
        try:
            with allure.step("启动Android应用"):
                # 注意：这需要真实的Android设备或模拟器
                # 在CI/CD环境中，这个测试通常会被跳过
                try:
                    mobile_tester.start_session()
                    log.info("Android应用启动成功")
                except Exception as e:
                    log.warning(f"Android应用启动失败: {e}")
                    pytest.skip("无法连接到Android设备/模拟器")
            
            with allure.step("获取设备信息"):
                device_info = mobile_tester.get_device_info()
                
                log.info(f"设备信息: {device_info}")
                
                # 验证设备信息
                assert device_info.get("platform") == "Android"
                
                # 添加设备信息到报告
                allure.attach(
                    str(device_info),
                    name="Android设备信息",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            with allure.step("测试应用导航"):
                # 模拟导航到网页
                try:
                    mobile_tester.navigate_to_url(self.test_urls["mobile_friendly"])
                    time.sleep(3)  # 等待页面加载
                    
                    log.info("网页导航成功")
                except Exception as e:
                    log.warning(f"网页导航失败: {e}")
            
            with allure.step("测试触摸操作"):
                # 获取屏幕尺寸
                screen_size = mobile_tester.get_screen_size()
                log.info(f"屏幕尺寸: {screen_size}")
                
                if screen_size:
                    # 在屏幕中央点击
                    center_x = screen_size["width"] // 2
                    center_y = screen_size["height"] // 2
                    
                    mobile_tester.tap(center_x, center_y)
                    log.info(f"在屏幕中央点击: ({center_x}, {center_y})")
                    
                    time.sleep(1)
            
            with allure.step("测试滑动手势"):
                if screen_size:
                    # 向上滑动
                    start_x = screen_size["width"] // 2
                    start_y = screen_size["height"] * 3 // 4
                    end_x = screen_size["width"] // 2
                    end_y = screen_size["height"] // 4
                    
                    mobile_tester.swipe(start_x, start_y, end_x, end_y, duration=1000)
                    log.info("执行向上滑动手势")
                    
                    time.sleep(1)
            
            with allure.step("截图记录"):
                screenshot_path = mobile_tester.take_screenshot("android_test.png")
                if screenshot_path:
                    allure.attach.file(
                        screenshot_path,
                        name="Android测试截图",
                        attachment_type=allure.attachment_type.PNG
                    )
        
        finally:
            # 清理
            mobile_tester.stop_session()
    
    @allure.story("iOS应用测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.mobile
    @pytest.mark.ios
    def test_ios_app_functionality(self):
        """测试iOS应用功能"""
        
        # 检查Appium是否可用
        try:
            from utilities.mobile_tester import APPIUM_AVAILABLE
            if not APPIUM_AVAILABLE:
                pytest.skip("Appium不可用，跳过移动端测试")
        except ImportError:
            pytest.skip("移动端测试依赖不可用")
        
        mobile_tester = MobileTester(self.ios_device)
        
        try:
            with allure.step("启动iOS应用"):
                try:
                    mobile_tester.start_session()
                    log.info("iOS应用启动成功")
                except Exception as e:
                    log.warning(f"iOS应用启动失败: {e}")
                    pytest.skip("无法连接到iOS设备/模拟器")
            
            with allure.step("获取设备信息"):
                device_info = mobile_tester.get_device_info()
                
                log.info(f"设备信息: {device_info}")
                
                # 验证设备信息
                assert device_info.get("platform") == "iOS"
                
                # 添加设备信息到报告
                allure.attach(
                    str(device_info),
                    name="iOS设备信息",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            with allure.step("测试Safari浏览器"):
                try:
                    mobile_tester.navigate_to_url(self.test_urls["responsive"])
                    time.sleep(3)
                    
                    log.info("Safari导航成功")
                except Exception as e:
                    log.warning(f"Safari导航失败: {e}")
            
            with allure.step("测试iOS特有手势"):
                screen_size = mobile_tester.get_screen_size()
                
                if screen_size:
                    # iOS特有的边缘滑动（返回手势）
                    mobile_tester.swipe(
                        start_x=10,
                        start_y=screen_size["height"] // 2,
                        end_x=screen_size["width"] // 2,
                        end_y=screen_size["height"] // 2,
                        duration=500
                    )
                    log.info("执行iOS边缘滑动手势")
                    
                    time.sleep(1)
            
            with allure.step("截图记录"):
                screenshot_path = mobile_tester.take_screenshot("ios_test.png")
                if screenshot_path:
                    allure.attach.file(
                        screenshot_path,
                        name="iOS测试截图",
                        attachment_type=allure.attachment_type.PNG
                    )
        
        finally:
            # 清理
            mobile_tester.stop_session()
    
    @allure.story("跨平台兼容性测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.mobile
    @pytest.mark.cross_platform
    def test_cross_platform_compatibility(self):
        """测试跨平台兼容性"""
        
        # 检查Appium是否可用
        try:
            from utilities.mobile_tester import APPIUM_AVAILABLE
            if not APPIUM_AVAILABLE:
                pytest.skip("Appium不可用，跳过移动端测试")
        except ImportError:
            pytest.skip("移动端测试依赖不可用")
        
        def mobile_web_test(mobile_tester: MobileTester) -> Dict[str, Any]:
            """移动端Web测试函数"""
            try:
                # 导航到测试页面
                mobile_tester.navigate_to_url(self.test_urls["webgoat_mobile"])
                time.sleep(3)
                
                # 获取页面标题
                page_title = mobile_tester.get_page_title()
                
                # 获取屏幕尺寸
                screen_size = mobile_tester.get_screen_size()
                
                # 执行基本交互
                if screen_size:
                    mobile_tester.tap(
                        screen_size["width"] // 2,
                        screen_size["height"] // 2
                    )
                
                return {
                    "page_title": page_title,
                    "screen_size": screen_size,
                    "navigation_success": True
                }
            except Exception as e:
                log.error(f"移动端Web测试失败: {e}")
                return {
                    "error": str(e),
                    "navigation_success": False
                }
        
        with allure.step("执行跨平台测试"):
            # 创建跨平台测试器
            cross_platform_tester = CrossPlatformTester([
                self.android_device,
                # self.ios_device  # 在实际环境中可以启用
            ])
            
            try:
                # 执行跨平台测试
                results = cross_platform_tester.run_cross_platform_test(mobile_web_test)
                
                log.info(f"跨平台测试完成，测试了 {len(results)} 个平台")
            except Exception as e:
                log.warning(f"跨平台测试失败: {e}")
                pytest.skip("跨平台测试环境不可用")
                return
        
        with allure.step("分析跨平台测试结果"):
            cross_platform_report = "跨平台兼容性测试报告:\n"
            cross_platform_report += f"测试平台数量: {len(results)}\n\n"
            
            successful_platforms = 0
            
            for device_name, result in results.items():
                cross_platform_report += f"设备: {device_name}\n"
                
                if result.get("success", False):
                    successful_platforms += 1
                    test_result = result.get("result", {})
                    device_info = result.get("device_info", {})
                    
                    cross_platform_report += f"  状态: 成功\n"
                    cross_platform_report += f"  页面标题: {test_result.get('page_title', 'N/A')}\n"
                    cross_platform_report += f"  屏幕尺寸: {test_result.get('screen_size', 'N/A')}\n"
                    cross_platform_report += f"  平台版本: {device_info.get('platformVersion', 'N/A')}\n"
                else:
                    cross_platform_report += f"  状态: 失败\n"
                    cross_platform_report += f"  错误: {result.get('error', 'Unknown error')}\n"
                
                cross_platform_report += "\n"
            
            # 计算兼容性率
            compatibility_rate = successful_platforms / len(results) if results else 0
            cross_platform_report += f"兼容性率: {compatibility_rate:.2%}\n"
            
            allure.attach(
                cross_platform_report,
                name="跨平台兼容性测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            log.info(f"跨平台兼容性率: {compatibility_rate:.2%}")
            
            # 断言兼容性率
            assert compatibility_rate >= 0.5, f"跨平台兼容性率过低: {compatibility_rate:.2%}"
    
    @allure.story("移动端性能测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.mobile
    @pytest.mark.performance
    def test_mobile_performance(self):
        """测试移动端性能"""
        
        # 检查Appium是否可用
        try:
            from utilities.mobile_tester import APPIUM_AVAILABLE
            if not APPIUM_AVAILABLE:
                pytest.skip("Appium不可用，跳过移动端测试")
        except ImportError:
            pytest.skip("移动端测试依赖不可用")
        
        mobile_tester = MobileTester(self.android_device)
        
        try:
            with allure.step("启动移动应用"):
                try:
                    mobile_tester.start_session()
                except Exception as e:
                    pytest.skip(f"无法启动移动应用: {e}")
            
            with allure.step("测量页面加载性能"):
                start_time = time.time()
                
                try:
                    mobile_tester.navigate_to_url(self.test_urls["mobile_friendly"])
                    
                    # 等待页面加载完成
                    mobile_tester.wait_for_element_by_id("wrapper", timeout=10)
                    
                except Exception:
                    # 如果找不到特定元素，等待固定时间
                    time.sleep(5)
                
                load_time = time.time() - start_time
                
                log.info(f"移动端页面加载时间: {load_time:.2f}秒")
                
                # 性能断言
                assert load_time < 30, f"移动端页面加载时间过长: {load_time:.2f}秒"
            
            with allure.step("测试滚动性能"):
                scroll_start_time = time.time()
                
                screen_size = mobile_tester.get_screen_size()
                if screen_size:
                    # 执行多次滚动
                    for i in range(5):
                        mobile_tester.swipe(
                            start_x=screen_size["width"] // 2,
                            start_y=screen_size["height"] * 3 // 4,
                            end_x=screen_size["width"] // 2,
                            end_y=screen_size["height"] // 4,
                            duration=300
                        )
                        time.sleep(0.2)
                
                scroll_time = time.time() - scroll_start_time
                
                log.info(f"滚动操作总时间: {scroll_time:.2f}秒")
            
            with allure.step("生成移动端性能报告"):
                performance_report = f"""
移动端性能测试报告:
- 页面加载时间: {load_time:.2f}秒
- 滚动操作时间: {scroll_time:.2f}秒
- 设备平台: {self.android_device.platform_name}
- 设备版本: {self.android_device.platform_version}

性能建议:
- 页面加载时间应小于3秒
- 滚动操作应流畅无卡顿
- 优化图片和资源大小
- 使用响应式设计
                """
                
                allure.attach(
                    performance_report,
                    name="移动端性能测试报告",
                    attachment_type=allure.attachment_type.TEXT
                )
        
        finally:
            mobile_tester.stop_session()
    
    @allure.story("移动端手势测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.mobile
    def test_mobile_gestures(self):
        """测试移动端手势操作"""
        
        # 检查Appium是否可用
        try:
            from utilities.mobile_tester import APPIUM_AVAILABLE
            if not APPIUM_AVAILABLE:
                pytest.skip("Appium不可用，跳过移动端测试")
        except ImportError:
            pytest.skip("移动端测试依赖不可用")
        
        mobile_tester = MobileTester(self.android_device)
        
        try:
            with allure.step("启动移动应用"):
                try:
                    mobile_tester.start_session()
                except Exception as e:
                    pytest.skip(f"无法启动移动应用: {e}")
            
            with allure.step("导航到测试页面"):
                mobile_tester.navigate_to_url(self.test_urls["responsive"])
                time.sleep(3)
            
            screen_size = mobile_tester.get_screen_size()
            if not screen_size:
                pytest.skip("无法获取屏幕尺寸")
            
            with allure.step("测试点击手势"):
                # 单击
                mobile_tester.tap(
                    screen_size["width"] // 2,
                    screen_size["height"] // 2
                )
                log.info("执行单击手势")
                time.sleep(1)
                
                # 双击
                mobile_tester.double_tap(
                    screen_size["width"] // 2,
                    screen_size["height"] // 2
                )
                log.info("执行双击手势")
                time.sleep(1)
            
            with allure.step("测试滑动手势"):
                # 向上滑动
                mobile_tester.swipe(
                    start_x=screen_size["width"] // 2,
                    start_y=screen_size["height"] * 3 // 4,
                    end_x=screen_size["width"] // 2,
                    end_y=screen_size["height"] // 4,
                    duration=1000
                )
                log.info("执行向上滑动")
                time.sleep(1)
                
                # 向下滑动
                mobile_tester.swipe(
                    start_x=screen_size["width"] // 2,
                    start_y=screen_size["height"] // 4,
                    end_x=screen_size["width"] // 2,
                    end_y=screen_size["height"] * 3 // 4,
                    duration=1000
                )
                log.info("执行向下滑动")
                time.sleep(1)
                
                # 左右滑动
                mobile_tester.swipe(
                    start_x=screen_size["width"] * 3 // 4,
                    start_y=screen_size["height"] // 2,
                    end_x=screen_size["width"] // 4,
                    end_y=screen_size["height"] // 2,
                    duration=800
                )
                log.info("执行左滑动")
                time.sleep(1)
            
            with allure.step("测试长按手势"):
                mobile_tester.long_press(
                    screen_size["width"] // 2,
                    screen_size["height"] // 2,
                    duration=2000
                )
                log.info("执行长按手势")
                time.sleep(1)
            
            with allure.step("截图记录手势测试"):
                screenshot_path = mobile_tester.take_screenshot("gesture_test.png")
                if screenshot_path:
                    allure.attach.file(
                        screenshot_path,
                        name="手势测试截图",
                        attachment_type=allure.attachment_type.PNG
                    )
            
            log.info("移动端手势测试完成")
        
        finally:
            mobile_tester.stop_session()
