"""
Security Testing Utilities
安全测试工具类 - 提供常见的安全漏洞检测功能
"""

import re
import time
import requests
import urllib.parse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from utilities.logger import log
from utilities.config_reader import config


class VulnerabilityType(Enum):
    """漏洞类型枚举"""
    SQL_INJECTION = "SQL注入"
    XSS = "跨站脚本攻击"
    CSRF = "跨站请求伪造"
    AUTHENTICATION = "认证绕过"
    AUTHORIZATION = "权限提升"
    INFORMATION_DISCLOSURE = "信息泄露"
    INSECURE_HEADERS = "不安全的HTTP头"
    WEAK_ENCRYPTION = "弱加密"


@dataclass
class SecurityFinding:
    """安全发现数据类"""
    vulnerability_type: VulnerabilityType
    severity: str  # Critical, High, Medium, Low
    url: str
    parameter: Optional[str]
    payload: Optional[str]
    description: str
    evidence: str
    recommendation: str


class SecurityTester:
    """安全测试器"""
    
    def __init__(self):
        self.findings: List[SecurityFinding] = []
        self.session = requests.Session()
        
        # SQL注入测试载荷
        self.sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL, NULL, NULL --",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables) > 0 --",
            "' AND 1=CONVERT(int, (SELECT @@version)) --"
        ]
        
        # XSS测试载荷
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>"
        ]
        
        # 敏感信息泄露模式
        self.sensitive_patterns = [
            (r'password\s*[:=]\s*["\']?([^"\'\s]+)', "密码泄露"),
            (r'api[_-]?key\s*[:=]\s*["\']?([^"\'\s]+)', "API密钥泄露"),
            (r'secret\s*[:=]\s*["\']?([^"\'\s]+)', "密钥泄露"),
            (r'token\s*[:=]\s*["\']?([^"\'\s]+)', "令牌泄露"),
            (r'mysql://[^:\s]+:[^@\s]+@', "数据库连接字符串泄露"),
            (r'postgresql://[^:\s]+:[^@\s]+@', "数据库连接字符串泄露"),
            (r'-----BEGIN [A-Z ]+-----', "私钥泄露")
        ]
    
    def test_sql_injection(self, url: str, parameters: Dict[str, str]) -> List[SecurityFinding]:
        """SQL注入测试"""
        log.info(f"开始SQL注入测试: {url}")
        findings = []
        
        for param_name, param_value in parameters.items():
            for payload in self.sql_payloads:
                test_params = parameters.copy()
                test_params[param_name] = payload
                
                try:
                    response = self.session.get(url, params=test_params, timeout=10)
                    
                    # 检查SQL错误模式
                    sql_error_patterns = [
                        r"SQL syntax.*MySQL",
                        r"Warning.*mysql_.*",
                        r"valid MySQL result",
                        r"PostgreSQL.*ERROR",
                        r"Warning.*pg_.*",
                        r"valid PostgreSQL result",
                        r"Microsoft OLE DB Provider for ODBC Drivers",
                        r"Microsoft JET Database Engine",
                        r"ORA-[0-9]{5}",
                        r"Oracle error",
                        r"SQLite/JDBCDriver",
                        r"SQLite.Exception"
                    ]
                    
                    for pattern in sql_error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            finding = SecurityFinding(
                                vulnerability_type=VulnerabilityType.SQL_INJECTION,
                                severity="High",
                                url=url,
                                parameter=param_name,
                                payload=payload,
                                description=f"在参数 {param_name} 中检测到SQL注入漏洞",
                                evidence=f"响应中包含SQL错误信息: {pattern}",
                                recommendation="使用参数化查询或预编译语句，验证和过滤用户输入"
                            )
                            findings.append(finding)
                            break
                    
                    # 检查时间延迟（盲注）
                    time_payload = f"'; WAITFOR DELAY '00:00:05' --"
                    test_params[param_name] = time_payload
                    
                    start_time = time.time()
                    response = self.session.get(url, params=test_params, timeout=15)
                    end_time = time.time()
                    
                    if end_time - start_time > 4:  # 如果响应时间超过4秒
                        finding = SecurityFinding(
                            vulnerability_type=VulnerabilityType.SQL_INJECTION,
                            severity="High",
                            url=url,
                            parameter=param_name,
                            payload=time_payload,
                            description=f"在参数 {param_name} 中检测到时间盲注漏洞",
                            evidence=f"响应时间异常: {end_time - start_time:.2f}秒",
                            recommendation="使用参数化查询或预编译语句，验证和过滤用户输入"
                        )
                        findings.append(finding)
                
                except Exception as e:
                    log.debug(f"SQL注入测试异常: {e}")
        
        return findings
    
    def test_xss(self, url: str, parameters: Dict[str, str]) -> List[SecurityFinding]:
        """XSS跨站脚本攻击测试"""
        log.info(f"开始XSS测试: {url}")
        findings = []
        
        for param_name, param_value in parameters.items():
            for payload in self.xss_payloads:
                test_params = parameters.copy()
                test_params[param_name] = payload
                
                try:
                    response = self.session.get(url, params=test_params, timeout=10)
                    
                    # 检查载荷是否在响应中未经过滤
                    if payload in response.text:
                        finding = SecurityFinding(
                            vulnerability_type=VulnerabilityType.XSS,
                            severity="Medium",
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            description=f"在参数 {param_name} 中检测到反射型XSS漏洞",
                            evidence=f"载荷在响应中未经过滤: {payload}",
                            recommendation="对用户输入进行HTML编码，使用内容安全策略(CSP)"
                        )
                        findings.append(finding)
                
                except Exception as e:
                    log.debug(f"XSS测试异常: {e}")
        
        return findings
    
    def test_authentication_bypass(self, login_url: str, username_field: str, password_field: str) -> List[SecurityFinding]:
        """认证绕过测试"""
        log.info(f"开始认证绕过测试: {login_url}")
        findings = []
        
        # 测试常见的认证绕过载荷
        bypass_payloads = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", "123456"),
            ("admin", ""),
            ("", ""),
            ("admin' --", "anything"),
            ("admin' OR '1'='1' --", "anything"),
            ("admin'; DROP TABLE users; --", "anything")
        ]
        
        for username, password in bypass_payloads:
            try:
                data = {
                    username_field: username,
                    password_field: password
                }
                
                response = self.session.post(login_url, data=data, timeout=10)
                
                # 检查是否成功绕过认证
                success_indicators = [
                    "welcome", "dashboard", "logout", "profile",
                    "欢迎", "仪表板", "退出", "个人资料"
                ]
                
                if any(indicator in response.text.lower() for indicator in success_indicators):
                    finding = SecurityFinding(
                        vulnerability_type=VulnerabilityType.AUTHENTICATION,
                        severity="Critical",
                        url=login_url,
                        parameter=f"{username_field}, {password_field}",
                        payload=f"{username}:{password}",
                        description="检测到认证绕过漏洞",
                        evidence=f"使用凭据 {username}:{password} 成功绕过认证",
                        recommendation="实施强密码策略，使用多因素认证，避免默认凭据"
                    )
                    findings.append(finding)
            
            except Exception as e:
                log.debug(f"认证绕过测试异常: {e}")
        
        return findings
    
    def test_information_disclosure(self, url: str) -> List[SecurityFinding]:
        """信息泄露测试"""
        log.info(f"开始信息泄露测试: {url}")
        findings = []
        
        # 测试常见的敏感文件和目录
        sensitive_paths = [
            "/.env",
            "/config.php",
            "/wp-config.php",
            "/database.yml",
            "/settings.py",
            "/.git/config",
            "/admin",
            "/backup",
            "/test",
            "/debug",
            "/phpinfo.php",
            "/server-status",
            "/server-info"
        ]
        
        base_url = url.rstrip('/')
        
        for path in sensitive_paths:
            try:
                test_url = base_url + path
                response = self.session.get(test_url, timeout=10)
                
                if response.status_code == 200:
                    # 检查响应中的敏感信息
                    for pattern, description in self.sensitive_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        if matches:
                            finding = SecurityFinding(
                                vulnerability_type=VulnerabilityType.INFORMATION_DISCLOSURE,
                                severity="Medium",
                                url=test_url,
                                parameter=None,
                                payload=None,
                                description=f"检测到{description}",
                                evidence=f"在 {path} 中发现敏感信息: {matches[0][:50]}...",
                                recommendation="移除敏感文件，配置适当的访问控制"
                            )
                            findings.append(finding)
            
            except Exception as e:
                log.debug(f"信息泄露测试异常: {e}")
        
        return findings
    
    def test_security_headers(self, url: str) -> List[SecurityFinding]:
        """安全HTTP头测试"""
        log.info(f"开始安全HTTP头测试: {url}")
        findings = []
        
        try:
            response = self.session.get(url, timeout=10)
            headers = response.headers
            
            # 检查缺失的安全头
            security_headers = {
                'X-Frame-Options': "防止点击劫持攻击",
                'X-Content-Type-Options': "防止MIME类型嗅探",
                'X-XSS-Protection': "启用XSS过滤器",
                'Strict-Transport-Security': "强制HTTPS连接",
                'Content-Security-Policy': "防止XSS和数据注入攻击",
                'Referrer-Policy': "控制引用信息泄露"
            }
            
            for header, description in security_headers.items():
                if header not in headers:
                    finding = SecurityFinding(
                        vulnerability_type=VulnerabilityType.INSECURE_HEADERS,
                        severity="Low",
                        url=url,
                        parameter=header,
                        payload=None,
                        description=f"缺失安全HTTP头: {header}",
                        evidence=f"响应中未包含 {header} 头",
                        recommendation=f"添加 {header} 头以{description}"
                    )
                    findings.append(finding)
            
            # 检查不安全的头值
            if 'Server' in headers:
                server_header = headers['Server']
                if any(tech in server_header.lower() for tech in ['apache', 'nginx', 'iis']):
                    finding = SecurityFinding(
                        vulnerability_type=VulnerabilityType.INFORMATION_DISCLOSURE,
                        severity="Low",
                        url=url,
                        parameter="Server",
                        payload=None,
                        description="服务器信息泄露",
                        evidence=f"Server头泄露服务器信息: {server_header}",
                        recommendation="隐藏或修改Server头以避免信息泄露"
                    )
                    findings.append(finding)
        
        except Exception as e:
            log.debug(f"安全HTTP头测试异常: {e}")
        
        return findings
    
    def comprehensive_security_scan(self, target_url: str, login_params: Dict = None) -> List[SecurityFinding]:
        """综合安全扫描"""
        log.info(f"开始综合安全扫描: {target_url}")
        all_findings = []
        
        # 基本参数用于测试
        test_params = {"id": "1", "search": "test", "page": "1"}
        
        # 执行各种安全测试
        all_findings.extend(self.test_sql_injection(target_url, test_params))
        all_findings.extend(self.test_xss(target_url, test_params))
        all_findings.extend(self.test_information_disclosure(target_url))
        all_findings.extend(self.test_security_headers(target_url))
        
        # 如果提供了登录参数，执行认证测试
        if login_params:
            login_url = login_params.get('url', target_url + '/login')
            username_field = login_params.get('username_field', 'username')
            password_field = login_params.get('password_field', 'password')
            
            all_findings.extend(self.test_authentication_bypass(
                login_url, username_field, password_field
            ))
        
        # 按严重程度排序
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        all_findings.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        log.info(f"安全扫描完成，发现 {len(all_findings)} 个安全问题")
        return all_findings
    
    def generate_security_report(self, findings: List[SecurityFinding], output_file: str = None):
        """生成安全测试报告"""
        from pathlib import Path
        import json
        from datetime import datetime
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"security_report_{timestamp}.json"
        
        reports_dir = Path("reports/security")
        reports_dir.mkdir(exist_ok=True)
        
        # 统计信息
        severity_counts = {}
        vulnerability_counts = {}
        
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            vuln_type = finding.vulnerability_type.value
            vulnerability_counts[vuln_type] = vulnerability_counts.get(vuln_type, 0) + 1
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_findings': len(findings),
                'severity_distribution': severity_counts,
                'vulnerability_distribution': vulnerability_counts
            },
            'findings': [
                {
                    'vulnerability_type': finding.vulnerability_type.value,
                    'severity': finding.severity,
                    'url': finding.url,
                    'parameter': finding.parameter,
                    'payload': finding.payload,
                    'description': finding.description,
                    'evidence': finding.evidence,
                    'recommendation': finding.recommendation
                }
                for finding in findings
            ]
        }
        
        output_path = reports_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        log.info(f"安全测试报告已保存: {output_path}")
        return output_path
