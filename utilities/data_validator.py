"""
数据验证工具
用于验证测试数据的有效性和完整性
"""

import re
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError

from utilities.logger import log


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        """初始化数据验证器"""
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
        self.url_pattern = re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$')
        
    def validate_email(self, email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否有效
        """
        if not email or not isinstance(email, str):
            return False
        return bool(self.email_pattern.match(email))
    
    def validate_phone(self, phone: str) -> bool:
        """
        验证手机号格式
        
        Args:
            phone: 手机号
            
        Returns:
            是否有效
        """
        if not phone or not isinstance(phone, str):
            return False
        return bool(self.phone_pattern.match(phone.replace(' ', '').replace('-', '')))
    
    def validate_url(self, url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: URL地址
            
        Returns:
            是否有效
        """
        if not url or not isinstance(url, str):
            return False
        return bool(self.url_pattern.match(url))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            验证结果
        """
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if not password or not isinstance(password, str):
            result["valid"] = False
            result["issues"].append("密码不能为空")
            return result
        
        # 长度检查
        if len(password) < 8:
            result["issues"].append("密码长度至少8位")
            result["valid"] = False
        else:
            result["score"] += 1
        
        # 包含小写字母
        if re.search(r'[a-z]', password):
            result["score"] += 1
        else:
            result["issues"].append("密码应包含小写字母")
        
        # 包含大写字母
        if re.search(r'[A-Z]', password):
            result["score"] += 1
        else:
            result["issues"].append("密码应包含大写字母")
        
        # 包含数字
        if re.search(r'\d', password):
            result["score"] += 1
        else:
            result["issues"].append("密码应包含数字")
        
        # 包含特殊字符
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["score"] += 1
        else:
            result["issues"].append("密码应包含特殊字符")
        
        # 不包含常见弱密码
        weak_passwords = ["password", "123456", "qwerty", "admin", "root"]
        if password.lower() in weak_passwords:
            result["issues"].append("密码过于简单")
            result["valid"] = False
        
        return result
    
    def validate_date_format(self, date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            format_str: 日期格式
            
        Returns:
            是否有效
        """
        try:
            datetime.strptime(date_str, format_str)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证用户数据
        
        Args:
            user_data: 用户数据
            
        Returns:
            验证结果
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 必填字段检查
        required_fields = ["username", "email"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                result["errors"].append(f"缺少必填字段: {field}")
                result["valid"] = False
        
        # 邮箱格式验证
        if "email" in user_data and user_data["email"]:
            if not self.validate_email(user_data["email"]):
                result["errors"].append("邮箱格式不正确")
                result["valid"] = False
        
        # 用户名长度验证
        if "username" in user_data and user_data["username"]:
            username = user_data["username"]
            if len(username) < 3:
                result["errors"].append("用户名长度至少3位")
                result["valid"] = False
            elif len(username) > 50:
                result["errors"].append("用户名长度不能超过50位")
                result["valid"] = False
        
        # 密码强度验证
        if "password" in user_data and user_data["password"]:
            password_result = self.validate_password_strength(user_data["password"])
            if not password_result["valid"]:
                result["errors"].extend(password_result["issues"])
                result["valid"] = False
            elif password_result["score"] < 3:
                result["warnings"].append("密码强度较弱")
        
        # 手机号验证
        if "phone" in user_data and user_data["phone"]:
            if not self.validate_phone(user_data["phone"]):
                result["errors"].append("手机号格式不正确")
                result["valid"] = False
        
        # 年龄验证
        if "age" in user_data and user_data["age"]:
            try:
                age = int(user_data["age"])
                if age < 0 or age > 150:
                    result["errors"].append("年龄范围不合理")
                    result["valid"] = False
            except (ValueError, TypeError):
                result["errors"].append("年龄必须是数字")
                result["valid"] = False
        
        return result
    
    def validate_api_response(self, response_data: Dict[str, Any], expected_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证API响应数据
        
        Args:
            response_data: 响应数据
            expected_schema: 期望的JSON Schema
            
        Returns:
            验证结果
        """
        result = {
            "valid": True,
            "errors": [],
            "schema_errors": []
        }
        
        try:
            # JSON Schema验证
            validate(instance=response_data, schema=expected_schema)
            log.debug("API响应数据符合Schema")
        except ValidationError as e:
            result["valid"] = False
            result["schema_errors"].append(str(e))
            log.error(f"API响应数据不符合Schema: {e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Schema验证失败: {e}")
            log.error(f"Schema验证失败: {e}")
        
        return result
    
    def validate_form_data(self, form_data: Dict[str, Any], form_rules: Dict[str, Dict]) -> Dict[str, Any]:
        """
        验证表单数据
        
        Args:
            form_data: 表单数据
            form_rules: 表单验证规则
            
        Returns:
            验证结果
        """
        result = {
            "valid": True,
            "field_errors": {},
            "general_errors": []
        }
        
        for field_name, rules in form_rules.items():
            field_value = form_data.get(field_name)
            field_errors = []
            
            # 必填验证
            if rules.get("required", False):
                if not field_value:
                    field_errors.append(f"{field_name}是必填字段")
            
            # 如果字段有值，进行其他验证
            if field_value:
                # 长度验证
                if "min_length" in rules:
                    if len(str(field_value)) < rules["min_length"]:
                        field_errors.append(f"{field_name}长度至少{rules['min_length']}位")
                
                if "max_length" in rules:
                    if len(str(field_value)) > rules["max_length"]:
                        field_errors.append(f"{field_name}长度不能超过{rules['max_length']}位")
                
                # 类型验证
                if "type" in rules:
                    expected_type = rules["type"]
                    if expected_type == "email" and not self.validate_email(field_value):
                        field_errors.append(f"{field_name}邮箱格式不正确")
                    elif expected_type == "phone" and not self.validate_phone(field_value):
                        field_errors.append(f"{field_name}手机号格式不正确")
                    elif expected_type == "url" and not self.validate_url(field_value):
                        field_errors.append(f"{field_name}URL格式不正确")
                    elif expected_type == "number":
                        try:
                            float(field_value)
                        except (ValueError, TypeError):
                            field_errors.append(f"{field_name}必须是数字")
                
                # 正则表达式验证
                if "pattern" in rules:
                    pattern = re.compile(rules["pattern"])
                    if not pattern.match(str(field_value)):
                        field_errors.append(f"{field_name}格式不正确")
                
                # 选项验证
                if "choices" in rules:
                    if field_value not in rules["choices"]:
                        field_errors.append(f"{field_name}选项无效")
            
            if field_errors:
                result["field_errors"][field_name] = field_errors
                result["valid"] = False
        
        # 密码确认验证
        if "password" in form_data and "confirm_password" in form_data:
            if form_data["password"] != form_data["confirm_password"]:
                result["general_errors"].append("密码和确认密码不匹配")
                result["valid"] = False
        
        return result
    
    def validate_test_data_file(self, file_path: str) -> Dict[str, Any]:
        """
        验证测试数据文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            验证结果
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 统计信息
            result["statistics"]["total_sections"] = len(data)
            result["statistics"]["sections"] = list(data.keys())
            
            # 验证各个数据段
            for section_name, section_data in data.items():
                if isinstance(section_data, dict):
                    # 验证用户数据段
                    if "users" in section_name.lower():
                        self._validate_users_section(section_data, result)
                    
                    # 验证API数据段
                    elif "api" in section_name.lower():
                        self._validate_api_section(section_data, result)
                    
                    # 验证表单数据段
                    elif "form" in section_name.lower():
                        self._validate_form_section(section_data, result)
                
                elif isinstance(section_data, list):
                    result["statistics"][f"{section_name}_count"] = len(section_data)
            
            log.info(f"测试数据文件验证完成: {file_path}")
            
        except FileNotFoundError:
            result["valid"] = False
            result["errors"].append(f"文件不存在: {file_path}")
        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"JSON格式错误: {e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证失败: {e}")
        
        return result
    
    def _validate_users_section(self, users_data: Dict[str, Any], result: Dict[str, Any]):
        """验证用户数据段"""
        for user_type, users in users_data.items():
            if isinstance(users, list):
                for i, user in enumerate(users):
                    user_result = self.validate_user_data(user)
                    if not user_result["valid"]:
                        result["errors"].append(f"{user_type}[{i}]: {', '.join(user_result['errors'])}")
                        result["valid"] = False
                    if user_result["warnings"]:
                        result["warnings"].extend([f"{user_type}[{i}]: {w}" for w in user_result["warnings"]])
    
    def _validate_api_section(self, api_data: Dict[str, Any], result: Dict[str, Any]):
        """验证API数据段"""
        for api_type, api_items in api_data.items():
            if isinstance(api_items, list):
                for i, item in enumerate(api_items):
                    # 检查必要字段
                    required_fields = ["expected_status"]
                    for field in required_fields:
                        if field not in item:
                            result["warnings"].append(f"{api_type}[{i}]: 缺少字段 {field}")
    
    def _validate_form_section(self, form_data: Dict[str, Any], result: Dict[str, Any]):
        """验证表单数据段"""
        for form_type, form_items in form_data.items():
            if isinstance(form_items, list):
                for i, item in enumerate(form_items):
                    # 检查邮箱字段
                    if "email" in item and not self.validate_email(item["email"]):
                        result["errors"].append(f"{form_type}[{i}]: 邮箱格式不正确")
                        result["valid"] = False
    
    def generate_validation_report(self, validation_results: List[Dict[str, Any]]) -> str:
        """
        生成验证报告
        
        Args:
            validation_results: 验证结果列表
            
        Returns:
            验证报告
        """
        report = []
        report.append("=" * 50)
        report.append("数据验证报告")
        report.append("=" * 50)
        
        total_validations = len(validation_results)
        successful_validations = sum(1 for r in validation_results if r.get("valid", False))
        
        report.append(f"总验证数: {total_validations}")
        report.append(f"成功验证: {successful_validations}")
        report.append(f"失败验证: {total_validations - successful_validations}")
        report.append(f"成功率: {successful_validations/total_validations*100:.1f}%")
        report.append("")
        
        # 详细结果
        for i, result in enumerate(validation_results, 1):
            report.append(f"验证 {i}: {'✓' if result.get('valid', False) else '✗'}")
            
            if result.get("errors"):
                report.append("  错误:")
                for error in result["errors"]:
                    report.append(f"    - {error}")
            
            if result.get("warnings"):
                report.append("  警告:")
                for warning in result["warnings"]:
                    report.append(f"    - {warning}")
            
            report.append("")
        
        return "\n".join(report)


# 创建全局数据验证器实例
data_validator = DataValidator()


if __name__ == "__main__":
    # 示例用法
    validator = DataValidator()
    
    # 验证用户数据
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "phone": "+86 13800138000",
        "age": 25
    }
    
    result = validator.validate_user_data(user_data)
    print("用户数据验证结果:")
    print(f"  有效: {result['valid']}")
    if result["errors"]:
        print(f"  错误: {result['errors']}")
    if result["warnings"]:
        print(f"  警告: {result['warnings']}")
    
    # 验证邮箱
    emails = ["test@example.com", "invalid-email", "user@domain.co.uk"]
    print("\n邮箱验证结果:")
    for email in emails:
        is_valid = validator.validate_email(email)
        print(f"  {email}: {'✓' if is_valid else '✗'}")
    
    # 验证密码强度
    passwords = ["123456", "Password123!", "weakpass"]
    print("\n密码强度验证:")
    for password in passwords:
        result = validator.validate_password_strength(password)
        print(f"  {password}: 得分 {result['score']}/5, 有效: {result['valid']}")
        if result["issues"]:
            print(f"    问题: {', '.join(result['issues'])}")
    
    # 验证测试数据文件
    print("\n验证测试数据文件:")
    file_result = validator.validate_test_data_file("data/test_data.json")
    print(f"  文件有效: {file_result['valid']}")
    if file_result.get("statistics"):
        print(f"  统计信息: {file_result['statistics']}")
    if file_result["errors"]:
        print(f"  错误: {file_result['errors']}")
    if file_result["warnings"]:
        print(f"  警告: {file_result['warnings'][:3]}...")  # 只显示前3个警告
