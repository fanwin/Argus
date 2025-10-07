"""
Accessibility Testing Utilities
可访问性测试工具类 - 检查Web应用的可访问性合规性
"""

import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from utilities.logger import log


@dataclass
class AccessibilityIssue:
    """可访问性问题数据类"""
    rule_id: str
    severity: str  # Critical, Serious, Moderate, Minor
    element: str
    description: str
    help_text: str
    wcag_guideline: str
    recommendation: str


class AccessibilityTester:
    """可访问性测试器"""
    
    def __init__(self, selenium_wrapper):
        self.driver = selenium_wrapper.driver
        self.issues: List[AccessibilityIssue] = []
    
    def check_images_alt_text(self) -> List[AccessibilityIssue]:
        """检查图片的alt属性"""
        issues = []
        
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            
            for i, img in enumerate(images):
                src = img.get_attribute("src") or "unknown"
                alt = img.get_attribute("alt")
                
                if not alt:
                    issue = AccessibilityIssue(
                        rule_id="img-alt",
                        severity="Critical",
                        element=f"img[{i}] src='{src[:50]}...'",
                        description="图片缺少alt属性",
                        help_text="所有图片都应该有描述性的alt属性",
                        wcag_guideline="WCAG 2.1 Level A - 1.1.1 Non-text Content",
                        recommendation="为图片添加描述性的alt属性，装饰性图片使用空alt属性"
                    )
                    issues.append(issue)
                elif len(alt.strip()) == 0 and not self._is_decorative_image(img):
                    issue = AccessibilityIssue(
                        rule_id="img-alt-empty",
                        severity="Serious",
                        element=f"img[{i}] src='{src[:50]}...'",
                        description="图片alt属性为空但可能不是装饰性图片",
                        help_text="只有装饰性图片才应该使用空alt属性",
                        wcag_guideline="WCAG 2.1 Level A - 1.1.1 Non-text Content",
                        recommendation="为有意义的图片提供描述性alt文本"
                    )
                    issues.append(issue)
        
        except Exception as e:
            log.error(f"检查图片alt属性失败: {e}")
        
        return issues
    
    def check_form_labels(self) -> List[AccessibilityIssue]:
        """检查表单标签"""
        issues = []
        
        try:
            # 检查input元素
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            for i, input_elem in enumerate(inputs):
                input_type = input_elem.get_attribute("type") or "text"
                input_id = input_elem.get_attribute("id") or f"input-{i}"
                
                # 跳过某些不需要标签的input类型
                if input_type.lower() in ["hidden", "submit", "button", "reset"]:
                    continue
                
                has_label = self._has_associated_label(input_elem)
                has_aria_label = input_elem.get_attribute("aria-label")
                has_aria_labelledby = input_elem.get_attribute("aria-labelledby")
                has_title = input_elem.get_attribute("title")
                
                if not (has_label or has_aria_label or has_aria_labelledby or has_title):
                    issue = AccessibilityIssue(
                        rule_id="form-field-label",
                        severity="Critical",
                        element=f"input[type='{input_type}'] id='{input_id}'",
                        description="表单字段缺少标签",
                        help_text="所有表单字段都应该有关联的标签",
                        wcag_guideline="WCAG 2.1 Level A - 1.3.1 Info and Relationships",
                        recommendation="使用<label>元素、aria-label或aria-labelledby属性为表单字段提供标签"
                    )
                    issues.append(issue)
        
        except Exception as e:
            log.error(f"检查表单标签失败: {e}")
        
        return issues
    
    def check_heading_structure(self) -> List[AccessibilityIssue]:
        """检查标题结构"""
        issues = []
        
        try:
            headings = []
            for level in range(1, 7):  # h1 to h6
                elements = self.driver.find_elements(By.TAG_NAME, f"h{level}")
                for elem in elements:
                    headings.append((level, elem.text.strip()[:50]))
            
            # 检查是否有h1
            h1_count = len([h for h in headings if h[0] == 1])
            if h1_count == 0:
                issue = AccessibilityIssue(
                    rule_id="page-has-heading-one",
                    severity="Moderate",
                    element="page",
                    description="页面缺少h1标题",
                    help_text="每个页面都应该有一个h1标题",
                    wcag_guideline="WCAG 2.1 Level AA - 2.4.6 Headings and Labels",
                    recommendation="为页面添加一个描述性的h1标题"
                )
                issues.append(issue)
            elif h1_count > 1:
                issue = AccessibilityIssue(
                    rule_id="page-has-heading-one",
                    severity="Minor",
                    element="page",
                    description=f"页面有多个h1标题 ({h1_count}个)",
                    help_text="页面通常应该只有一个h1标题",
                    wcag_guideline="WCAG 2.1 Level AA - 2.4.6 Headings and Labels",
                    recommendation="考虑使用单个h1标题和适当的标题层次结构"
                )
                issues.append(issue)
            
            # 检查标题层次结构
            prev_level = 0
            for level, text in headings:
                if level > prev_level + 1:
                    issue = AccessibilityIssue(
                        rule_id="heading-order",
                        severity="Moderate",
                        element=f"h{level}: '{text}'",
                        description=f"标题层次跳跃：从h{prev_level}跳到h{level}",
                        help_text="标题应该按层次顺序使用",
                        wcag_guideline="WCAG 2.1 Level AA - 2.4.6 Headings and Labels",
                        recommendation="使用连续的标题级别，不要跳过级别"
                    )
                    issues.append(issue)
                prev_level = level
        
        except Exception as e:
            log.error(f"检查标题结构失败: {e}")
        
        return issues
    
    def check_color_contrast(self) -> List[AccessibilityIssue]:
        """检查颜色对比度"""
        issues = []
        
        try:
            # 注入axe-core脚本来检查颜色对比度
            axe_script = """
            var elements = document.querySelectorAll('*');
            var contrastIssues = [];
            
            for (var i = 0; i < elements.length; i++) {
                var elem = elements[i];
                var style = window.getComputedStyle(elem);
                var color = style.color;
                var backgroundColor = style.backgroundColor;
                var fontSize = parseFloat(style.fontSize);
                
                if (color && backgroundColor && color !== backgroundColor) {
                    // 简化的对比度检查（实际应用中应使用更精确的算法）
                    var colorRgb = color.match(/\\d+/g);
                    var bgRgb = backgroundColor.match(/\\d+/g);
                    
                    if (colorRgb && bgRgb && colorRgb.length >= 3 && bgRgb.length >= 3) {
                        var textLuminance = 0.299 * colorRgb[0] + 0.587 * colorRgb[1] + 0.114 * colorRgb[2];
                        var bgLuminance = 0.299 * bgRgb[0] + 0.587 * bgRgb[1] + 0.114 * bgRgb[2];
                        var contrast = Math.abs(textLuminance - bgLuminance) / 255;
                        
                        var minContrast = fontSize >= 18 ? 0.3 : 0.4; // 简化的阈值
                        
                        if (contrast < minContrast) {
                            contrastIssues.push({
                                element: elem.tagName + (elem.id ? '#' + elem.id : '') + (elem.className ? '.' + elem.className.split(' ')[0] : ''),
                                color: color,
                                backgroundColor: backgroundColor,
                                contrast: contrast.toFixed(2)
                            });
                        }
                    }
                }
            }
            
            return contrastIssues;
            """
            
            contrast_issues = self.driver.execute_script(axe_script)
            
            for issue_data in contrast_issues[:10]:  # 限制数量避免过多
                issue = AccessibilityIssue(
                    rule_id="color-contrast",
                    severity="Serious",
                    element=issue_data['element'],
                    description=f"颜色对比度不足: {issue_data['contrast']}",
                    help_text="文本和背景之间应该有足够的颜色对比度",
                    wcag_guideline="WCAG 2.1 Level AA - 1.4.3 Contrast (Minimum)",
                    recommendation="增加文本和背景之间的颜色对比度，正常文本至少4.5:1，大文本至少3:1"
                )
                issues.append(issue)
        
        except Exception as e:
            log.error(f"检查颜色对比度失败: {e}")
        
        return issues
    
    def check_keyboard_navigation(self) -> List[AccessibilityIssue]:
        """检查键盘导航"""
        issues = []
        
        try:
            # 检查可聚焦元素
            focusable_elements = self.driver.execute_script("""
                var focusableElements = document.querySelectorAll(
                    'a[href], button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])'
                );
                var results = [];
                
                for (var i = 0; i < focusableElements.length; i++) {
                    var elem = focusableElements[i];
                    var style = window.getComputedStyle(elem);
                    var tabIndex = elem.getAttribute('tabindex');
                    
                    results.push({
                        tagName: elem.tagName,
                        id: elem.id || '',
                        className: elem.className || '',
                        tabIndex: tabIndex,
                        visible: style.display !== 'none' && style.visibility !== 'hidden'
                    });
                }
                
                return results;
            """)
            
            # 检查是否有可聚焦但不可见的元素
            for elem_data in focusable_elements:
                if not elem_data['visible']:
                    issue = AccessibilityIssue(
                        rule_id="focusable-element-visible",
                        severity="Moderate",
                        element=f"{elem_data['tagName']} id='{elem_data['id']}'",
                        description="可聚焦元素不可见",
                        help_text="可聚焦的元素应该是可见的",
                        wcag_guideline="WCAG 2.1 Level A - 2.1.1 Keyboard",
                        recommendation="确保所有可聚焦的元素都是可见的，或使用tabindex='-1'移除焦点"
                    )
                    issues.append(issue)
            
            # 检查跳过链接
            skip_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'skip') or contains(text(), '跳过')]")
            if not skip_links:
                issue = AccessibilityIssue(
                    rule_id="skip-link",
                    severity="Minor",
                    element="page",
                    description="页面缺少跳过链接",
                    help_text="页面应该提供跳过导航的链接",
                    wcag_guideline="WCAG 2.1 Level A - 2.4.1 Bypass Blocks",
                    recommendation="在页面顶部添加'跳到主内容'链接"
                )
                issues.append(issue)
        
        except Exception as e:
            log.error(f"检查键盘导航失败: {e}")
        
        return issues
    
    def check_aria_attributes(self) -> List[AccessibilityIssue]:
        """检查ARIA属性"""
        issues = []
        
        try:
            # 检查aria-label和aria-labelledby
            elements_with_aria = self.driver.find_elements(By.XPATH, "//*[@aria-label or @aria-labelledby]")
            
            for elem in elements_with_aria:
                aria_label = elem.get_attribute("aria-label")
                aria_labelledby = elem.get_attribute("aria-labelledby")
                
                if aria_label and len(aria_label.strip()) == 0:
                    issue = AccessibilityIssue(
                        rule_id="aria-label-empty",
                        severity="Serious",
                        element=f"{elem.tag_name} aria-label=''",
                        description="aria-label属性为空",
                        help_text="aria-label应该提供有意义的描述",
                        wcag_guideline="WCAG 2.1 Level A - 4.1.2 Name, Role, Value",
                        recommendation="为aria-label提供有意义的文本或移除该属性"
                    )
                    issues.append(issue)
                
                if aria_labelledby:
                    # 检查引用的元素是否存在
                    referenced_ids = aria_labelledby.split()
                    for ref_id in referenced_ids:
                        try:
                            self.driver.find_element(By.ID, ref_id)
                        except:
                            issue = AccessibilityIssue(
                                rule_id="aria-labelledby-invalid",
                                severity="Serious",
                                element=f"{elem.tag_name} aria-labelledby='{aria_labelledby}'",
                                description=f"aria-labelledby引用的元素不存在: {ref_id}",
                                help_text="aria-labelledby应该引用存在的元素ID",
                                wcag_guideline="WCAG 2.1 Level A - 4.1.2 Name, Role, Value",
                                recommendation="确保aria-labelledby引用的所有ID都存在于页面中"
                            )
                            issues.append(issue)
        
        except Exception as e:
            log.error(f"检查ARIA属性失败: {e}")
        
        return issues
    
    def _has_associated_label(self, input_elem: WebElement) -> bool:
        """检查input元素是否有关联的label"""
        try:
            input_id = input_elem.get_attribute("id")
            if input_id:
                # 检查是否有label的for属性指向这个input
                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{input_id}']")
                if labels:
                    return True
            
            # 检查input是否在label内部
            parent = input_elem.find_element(By.XPATH, "..")
            while parent and parent.tag_name.lower() != "html":
                if parent.tag_name.lower() == "label":
                    return True
                parent = parent.find_element(By.XPATH, "..")
            
            return False
        except:
            return False
    
    def _is_decorative_image(self, img_elem: WebElement) -> bool:
        """判断图片是否为装饰性图片"""
        try:
            # 检查role属性
            role = img_elem.get_attribute("role")
            if role == "presentation" or role == "none":
                return True
            
            # 检查父元素是否为链接
            parent = img_elem.find_element(By.XPATH, "..")
            if parent and parent.tag_name.lower() == "a":
                # 如果图片在链接中且链接有文本，可能是装饰性的
                link_text = parent.text.strip()
                if link_text:
                    return True
            
            return False
        except:
            return False
    
    def run_comprehensive_accessibility_audit(self) -> List[AccessibilityIssue]:
        """运行综合可访问性审计"""
        log.info("开始综合可访问性审计")
        
        all_issues = []
        
        # 运行各项检查
        all_issues.extend(self.check_images_alt_text())
        all_issues.extend(self.check_form_labels())
        all_issues.extend(self.check_heading_structure())
        all_issues.extend(self.check_color_contrast())
        all_issues.extend(self.check_keyboard_navigation())
        all_issues.extend(self.check_aria_attributes())
        
        # 按严重程度排序
        severity_order = {'Critical': 0, 'Serious': 1, 'Moderate': 2, 'Minor': 3}
        all_issues.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        log.info(f"可访问性审计完成，发现 {len(all_issues)} 个问题")
        return all_issues
    
    def generate_accessibility_report(self, issues: List[AccessibilityIssue], output_file: str = None):
        """生成可访问性测试报告"""
        from datetime import datetime
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"accessibility_report_{timestamp}.json"
        
        reports_dir = Path("reports/accessibility")
        reports_dir.mkdir(exist_ok=True)
        
        # 统计信息
        severity_counts = {}
        rule_counts = {}
        
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            rule_counts[issue.rule_id] = rule_counts.get(issue.rule_id, 0) + 1
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(issues),
                'severity_distribution': severity_counts,
                'rule_distribution': rule_counts
            },
            'issues': [
                {
                    'rule_id': issue.rule_id,
                    'severity': issue.severity,
                    'element': issue.element,
                    'description': issue.description,
                    'help_text': issue.help_text,
                    'wcag_guideline': issue.wcag_guideline,
                    'recommendation': issue.recommendation
                }
                for issue in issues
            ]
        }
        
        output_path = reports_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        log.info(f"可访问性测试报告已保存: {output_path}")
        return output_path
