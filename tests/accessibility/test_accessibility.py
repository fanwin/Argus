"""
可访问性测试案例
展示可访问性测试功能：WCAG合规性、屏幕阅读器兼容性、键盘导航等
使用WebGoat和其他网站进行测试
"""

import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from utilities.accessibility_tester import AccessibilityTester, AccessibilityIssue
from utilities.selenium_wrapper import SeleniumWrapper
from utilities.logger import log


@allure.epic("可访问性测试")
@allure.feature("Web可访问性合规验证")
class TestAccessibility:
    """可访问性测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_accessibility_test(self, web_config):
        """设置可访问性测试环境"""
        self.driver_wrapper = SeleniumWrapper()
        self.driver_wrapper.start_driver()
        
        self.accessibility_tester = AccessibilityTester(self.driver_wrapper.driver)
        
        # 测试目标网站
        self.test_urls = {
            "webgoat": "https://owasp.org/www-project-webgoat/",
            "bootstrap": "https://getbootstrap.com/docs/5.0/getting-started/introduction/",
            "github": "https://github.com",
            "w3c": "https://www.w3.org"
        }
        
        log.info("可访问性测试环境初始化完成")
        
        yield
        
        # 清理
        self.driver_wrapper.quit_driver()
    
    @allure.story("图片可访问性测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.accessibility
    @pytest.mark.wcag
    def test_images_accessibility(self):
        """测试图片的可访问性（alt文本）"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.test_urls["webgoat"])
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("检查图片alt文本"):
            issues = self.accessibility_tester.check_images_alt_text()
            
            log.info(f"图片可访问性检查完成，发现 {len(issues)} 个问题")
        
        with allure.step("分析图片可访问性结果"):
            images_report = "图片可访问性测试报告:\n"
            images_report += f"检查的页面: {self.test_urls['webgoat']}\n"
            images_report += f"发现问题数量: {len(issues)}\n\n"
            
            if issues:
                images_report += "发现的问题:\n"
                for i, issue in enumerate(issues, 1):
                    images_report += f"{i}. {issue.description}\n"
                    images_report += f"   元素: {issue.element_info}\n"
                    images_report += f"   严重程度: {issue.severity}\n"
                    images_report += f"   建议: {issue.recommendation}\n\n"
                
                # 统计不同严重程度的问题
                severity_count = {}
                for issue in issues:
                    severity_count[issue.severity] = severity_count.get(issue.severity, 0) + 1
                
                images_report += "问题严重程度统计:\n"
                for severity, count in severity_count.items():
                    images_report += f"  {severity}: {count} 个\n"
            else:
                images_report += "所有图片都有适当的alt文本\n"
            
            allure.attach(
                images_report,
                name="图片可访问性测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 对于严重的可访问性问题，可以设置断言
            critical_issues = [issue for issue in issues if issue.severity == "Critical"]
            if critical_issues:
                log.warning(f"发现 {len(critical_issues)} 个严重的图片可访问性问题")
    
    @allure.story("表单可访问性测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.accessibility
    @pytest.mark.wcag
    def test_form_accessibility(self):
        """测试表单的可访问性（标签关联）"""
        
        with allure.step("导航到包含表单的页面"):
            # 使用GitHub登录页面作为表单测试目标
            self.driver_wrapper.navigate_to("https://github.com/login")
            
            try:
                self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "form"), timeout=10)
            except TimeoutException:
                log.warning("无法加载表单页面，使用备用测试")
                self.driver_wrapper.navigate_to(self.test_urls["webgoat"])
                self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("检查表单标签"):
            issues = self.accessibility_tester.check_form_labels()
            
            log.info(f"表单可访问性检查完成，发现 {len(issues)} 个问题")
        
        with allure.step("分析表单可访问性结果"):
            forms_report = "表单可访问性测试报告:\n"
            forms_report += f"检查的页面: {self.driver_wrapper.get_current_url()}\n"
            forms_report += f"发现问题数量: {len(issues)}\n\n"
            
            if issues:
                forms_report += "发现的问题:\n"
                for i, issue in enumerate(issues, 1):
                    forms_report += f"{i}. {issue.description}\n"
                    forms_report += f"   元素: {issue.element_info}\n"
                    forms_report += f"   严重程度: {issue.severity}\n"
                    forms_report += f"   建议: {issue.recommendation}\n\n"
            else:
                forms_report += "所有表单元素都有适当的标签\n"
            
            allure.attach(
                forms_report,
                name="表单可访问性测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("标题结构测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.accessibility
    @pytest.mark.wcag
    def test_heading_structure(self):
        """测试页面标题结构的可访问性"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.test_urls["bootstrap"])
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("检查标题结构"):
            issues = self.accessibility_tester.check_heading_structure()
            
            log.info(f"标题结构检查完成，发现 {len(issues)} 个问题")
        
        with allure.step("分析标题结构"):
            # 获取页面中的所有标题
            headings = self.driver_wrapper.find_elements((By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6"))
            
            heading_structure = "页面标题结构:\n"
            for heading in headings[:10]:  # 只显示前10个标题
                tag_name = heading.tag_name.upper()
                text = heading.text.strip()[:50]  # 限制文本长度
                heading_structure += f"  {tag_name}: {text}\n"
            
            if len(headings) > 10:
                heading_structure += f"  ... 还有 {len(headings) - 10} 个标题\n"
            
            headings_report = "标题结构可访问性测试报告:\n"
            headings_report += f"检查的页面: {self.test_urls['bootstrap']}\n"
            headings_report += f"总标题数量: {len(headings)}\n"
            headings_report += f"发现问题数量: {len(issues)}\n\n"
            headings_report += heading_structure + "\n"
            
            if issues:
                headings_report += "发现的问题:\n"
                for i, issue in enumerate(issues, 1):
                    headings_report += f"{i}. {issue.description}\n"
                    headings_report += f"   严重程度: {issue.severity}\n"
                    headings_report += f"   建议: {issue.recommendation}\n\n"
            else:
                headings_report += "标题结构符合可访问性要求\n"
            
            allure.attach(
                headings_report,
                name="标题结构可访问性测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("颜色对比度测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.accessibility
    @pytest.mark.wcag
    def test_color_contrast(self):
        """测试颜色对比度的可访问性"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.test_urls["w3c"])
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("检查颜色对比度"):
            issues = self.accessibility_tester.check_color_contrast()
            
            log.info(f"颜色对比度检查完成，发现 {len(issues)} 个问题")
        
        with allure.step("分析颜色对比度结果"):
            contrast_report = "颜色对比度可访问性测试报告:\n"
            contrast_report += f"检查的页面: {self.test_urls['w3c']}\n"
            contrast_report += f"发现问题数量: {len(issues)}\n\n"
            
            if issues:
                contrast_report += "发现的问题:\n"
                for i, issue in enumerate(issues, 1):
                    contrast_report += f"{i}. {issue.description}\n"
                    contrast_report += f"   元素: {issue.element_info}\n"
                    contrast_report += f"   严重程度: {issue.severity}\n"
                    contrast_report += f"   建议: {issue.recommendation}\n\n"
                
                # 按严重程度分类
                severity_stats = {}
                for issue in issues:
                    severity_stats[issue.severity] = severity_stats.get(issue.severity, 0) + 1
                
                contrast_report += "问题严重程度统计:\n"
                for severity, count in severity_stats.items():
                    contrast_report += f"  {severity}: {count} 个\n"
            else:
                contrast_report += "所有文本元素的颜色对比度都符合WCAG要求\n"
            
            allure.attach(
                contrast_report,
                name="颜色对比度测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("键盘导航测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.accessibility
    @pytest.mark.keyboard
    def test_keyboard_navigation(self):
        """测试键盘导航的可访问性"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.test_urls["github"])
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("检查键盘导航"):
            issues = self.accessibility_tester.check_keyboard_navigation()
            
            log.info(f"键盘导航检查完成，发现 {len(issues)} 个问题")
        
        with allure.step("测试Tab键导航"):
            # 获取页面中的可聚焦元素
            focusable_elements = self.driver_wrapper.find_elements((
                By.CSS_SELECTOR, 
                "a, button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
            ))
            
            navigation_log = []
            
            # 测试前几个元素的Tab导航
            for i in range(min(5, len(focusable_elements))):
                try:
                    # 聚焦到body元素，然后使用Tab键导航
                    body = self.driver_wrapper.find_element((By.TAG_NAME, "body"))
                    body.click()
                    
                    # 按Tab键
                    for _ in range(i + 1):
                        body.send_keys(Keys.TAB)
                        time.sleep(0.2)
                    
                    # 获取当前聚焦的元素
                    active_element = self.driver_wrapper.driver.switch_to.active_element
                    element_info = f"{active_element.tag_name}"
                    
                    if active_element.get_attribute("id"):
                        element_info += f"#{active_element.get_attribute('id')}"
                    if active_element.get_attribute("class"):
                        element_info += f".{active_element.get_attribute('class').split()[0]}"
                    
                    navigation_log.append(f"Tab {i+1}: {element_info}")
                    
                except Exception as e:
                    navigation_log.append(f"Tab {i+1}: 导航失败 - {str(e)}")
            
            keyboard_report = "键盘导航可访问性测试报告:\n"
            keyboard_report += f"检查的页面: {self.test_urls['github']}\n"
            keyboard_report += f"可聚焦元素数量: {len(focusable_elements)}\n"
            keyboard_report += f"发现问题数量: {len(issues)}\n\n"
            
            keyboard_report += "Tab键导航测试:\n"
            for log_entry in navigation_log:
                keyboard_report += f"  {log_entry}\n"
            keyboard_report += "\n"
            
            if issues:
                keyboard_report += "发现的问题:\n"
                for i, issue in enumerate(issues, 1):
                    keyboard_report += f"{i}. {issue.description}\n"
                    keyboard_report += f"   严重程度: {issue.severity}\n"
                    keyboard_report += f"   建议: {issue.recommendation}\n\n"
            else:
                keyboard_report += "键盘导航功能正常\n"
            
            allure.attach(
                keyboard_report,
                name="键盘导航测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("ARIA属性测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.accessibility
    @pytest.mark.aria
    def test_aria_attributes(self):
        """测试ARIA属性的可访问性"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.test_urls["bootstrap"])
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("检查ARIA属性"):
            issues = self.accessibility_tester.check_aria_attributes()
            
            log.info(f"ARIA属性检查完成，发现 {len(issues)} 个问题")
        
        with allure.step("分析ARIA属性使用"):
            # 统计页面中的ARIA属性使用情况
            aria_elements = self.driver_wrapper.find_elements((
                By.CSS_SELECTOR, 
                "[aria-label], [aria-labelledby], [aria-describedby], [role], [aria-hidden], [aria-expanded]"
            ))
            
            aria_stats = {}
            for element in aria_elements:
                for attr in ["aria-label", "aria-labelledby", "aria-describedby", "role", "aria-hidden", "aria-expanded"]:
                    if element.get_attribute(attr):
                        aria_stats[attr] = aria_stats.get(attr, 0) + 1
            
            aria_report = "ARIA属性可访问性测试报告:\n"
            aria_report += f"检查的页面: {self.test_urls['bootstrap']}\n"
            aria_report += f"使用ARIA属性的元素数量: {len(aria_elements)}\n"
            aria_report += f"发现问题数量: {len(issues)}\n\n"
            
            aria_report += "ARIA属性使用统计:\n"
            for attr, count in aria_stats.items():
                aria_report += f"  {attr}: {count} 个元素\n"
            aria_report += "\n"
            
            if issues:
                aria_report += "发现的问题:\n"
                for i, issue in enumerate(issues, 1):
                    aria_report += f"{i}. {issue.description}\n"
                    aria_report += f"   元素: {issue.element_info}\n"
                    aria_report += f"   严重程度: {issue.severity}\n"
                    aria_report += f"   建议: {issue.recommendation}\n\n"
            else:
                aria_report += "ARIA属性使用正确\n"
            
            allure.attach(
                aria_report,
                name="ARIA属性测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("综合可访问性审计")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.accessibility
    @pytest.mark.comprehensive
    def test_comprehensive_accessibility_audit(self):
        """执行综合可访问性审计"""
        
        with allure.step("导航到测试页面"):
            self.driver_wrapper.navigate_to(self.test_urls["webgoat"])
            self.driver_wrapper.wait_for_element_visible((By.TAG_NAME, "body"))
        
        with allure.step("执行综合可访问性审计"):
            all_issues = self.accessibility_tester.run_comprehensive_accessibility_audit()
            
            log.info(f"综合可访问性审计完成，总共发现 {len(all_issues)} 个问题")
        
        with allure.step("分析综合审计结果"):
            # 按类型分类问题
            issues_by_type = {}
            for issue in all_issues:
                issue_type = issue.issue_type
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)
            
            # 按严重程度分类问题
            issues_by_severity = {}
            for issue in all_issues:
                severity = issue.severity
                if severity not in issues_by_severity:
                    issues_by_severity[severity] = []
                issues_by_severity[severity].append(issue)
            
            # 生成综合报告
            comprehensive_report = f"综合可访问性审计报告\n"
            comprehensive_report += f"{'='*50}\n"
            comprehensive_report += f"审计目标: {self.test_urls['webgoat']}\n"
            comprehensive_report += f"总发现问题: {len(all_issues)} 个\n\n"
            
            # 按严重程度统计
            comprehensive_report += "按严重程度统计:\n"
            for severity in ["Critical", "Serious", "Moderate", "Minor"]:
                count = len(issues_by_severity.get(severity, []))
                comprehensive_report += f"  {severity}: {count} 个\n"
            comprehensive_report += "\n"
            
            # 按问题类型统计
            comprehensive_report += "按问题类型统计:\n"
            for issue_type, issues in issues_by_type.items():
                comprehensive_report += f"  {issue_type}: {len(issues)} 个\n"
            comprehensive_report += "\n"
            
            # 详细问题列表（只显示前10个最严重的问题）
            if all_issues:
                comprehensive_report += "最严重的问题（前10个）:\n"
                for i, issue in enumerate(all_issues[:10], 1):
                    comprehensive_report += f"{i}. [{issue.severity}] {issue.issue_type}\n"
                    comprehensive_report += f"   描述: {issue.description}\n"
                    comprehensive_report += f"   建议: {issue.recommendation}\n\n"
            
            # 可访问性评分
            total_score = 100
            for issue in all_issues:
                if issue.severity == "Critical":
                    total_score -= 15
                elif issue.severity == "Serious":
                    total_score -= 10
                elif issue.severity == "Moderate":
                    total_score -= 5
                elif issue.severity == "Minor":
                    total_score -= 2
            
            total_score = max(0, total_score)
            
            comprehensive_report += f"可访问性评分: {total_score}/100\n"
            
            if total_score >= 90:
                accessibility_level = "优秀"
            elif total_score >= 70:
                accessibility_level = "良好"
            elif total_score >= 50:
                accessibility_level = "一般"
            else:
                accessibility_level = "需要改进"
            
            comprehensive_report += f"可访问性等级: {accessibility_level}\n"
            
            allure.attach(
                comprehensive_report,
                name="综合可访问性审计报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            log.info(f"可访问性评分: {total_score}/100 ({accessibility_level})")
            
            # 对于严重的可访问性问题，可以设置断言
            critical_issues = [issue for issue in all_issues if issue.severity == "Critical"]
            if len(critical_issues) > 5:  # 如果严重问题超过5个
                log.warning(f"发现过多严重可访问性问题: {len(critical_issues)} 个")
