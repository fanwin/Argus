"""
数据驱动测试案例
展示数据驱动测试功能：参数化测试、外部数据源、测试数据生成等
"""

import pytest
import allure
import json
import csv
import yaml
from pathlib import Path
from typing import List, Dict, Any

from utilities.data_generator import DataGenerator
from utilities.data_validator import DataValidator
from utilities.api_client import APIClient
from utilities.selenium_wrapper import SeleniumWrapper
from utilities.logger import log


@allure.epic("数据驱动测试")
@allure.feature("参数化和数据源测试")
class TestDataDriven:
    """数据驱动测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_data_driven_test(self):
        """设置数据驱动测试环境"""
        self.data_generator = DataGenerator()
        self.data_validator = DataValidator()
        self.api_client = APIClient()
        
        # 设置测试数据目录
        self.test_data_dir = Path("data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        log.info("数据驱动测试环境初始化完成")
    
    @allure.story("JSON数据驱动测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.data_driven
    @pytest.mark.parametrize("user_data", [
        pytest.param(user, id=f"user_{user.get('id', i)}") 
        for i, user in enumerate(json.loads(Path("data/test_data.json").read_text(encoding='utf-8'))["users"]["valid_users"])
    ])
    def test_json_data_driven_user_validation(self, user_data):
        """使用JSON数据驱动的用户验证测试"""
        
        with allure.step(f"验证用户数据: {user_data.get('username', 'Unknown')}"):
            # 验证用户名
            username = user_data.get("username", "")
            assert self.data_validator.validate_string_length(username, min_length=3, max_length=20), \
                f"用户名长度无效: {username}"
            
            # 验证邮箱
            email = user_data.get("email", "")
            assert self.data_validator.validate_email(email), f"邮箱格式无效: {email}"
            
            # 验证角色
            role = user_data.get("role", "")
            valid_roles = ["admin", "user", "moderator", "guest"]
            assert role in valid_roles, f"角色无效: {role}"
            
            log.info(f"用户数据验证通过: {username} ({role})")
        
        with allure.step("模拟API调用"):
            # 模拟使用用户数据进行API调用
            api_url = "https://httpbin.org/post"
            
            response = self.api_client.post(api_url, json_data=user_data)
            self.api_client.assert_status_code(response, 200)
            
            response_data = self.api_client.get_response_json(response)
            
            # 验证API响应中包含发送的数据
            assert response_data["json"]["username"] == user_data["username"]
            assert response_data["json"]["email"] == user_data["email"]
            
            log.info(f"API调用成功: {user_data['username']}")
    
    @allure.story("CSV数据驱动测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.data_driven
    def test_csv_data_driven_product_validation(self):
        """使用CSV数据驱动的产品验证测试"""
        
        with allure.step("生成CSV测试数据"):
            # 生成产品测试数据
            products = self.data_generator.generate_product_data(10)
            
            # 保存到CSV文件
            csv_file = self.test_data_dir / "products_test.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if products:
                    writer = csv.DictWriter(f, fieldnames=products[0].keys())
                    writer.writeheader()
                    writer.writerows(products)
            
            log.info(f"生成了 {len(products)} 个产品数据到CSV文件")
        
        with allure.step("从CSV读取并验证数据"):
            # 读取CSV数据
            csv_products = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                csv_products = list(reader)
            
            assert len(csv_products) == len(products), "CSV数据数量不匹配"
            
            # 验证每个产品数据
            validation_results = []
            
            for i, product in enumerate(csv_products):
                result = {
                    "index": i,
                    "name": product["name"],
                    "valid": True,
                    "errors": []
                }
                
                # 验证产品名称
                if not self.data_validator.validate_string_length(product["name"], min_length=2, max_length=100):
                    result["valid"] = False
                    result["errors"].append("产品名称长度无效")
                
                # 验证价格
                try:
                    price = float(product["price"])
                    if not self.data_validator.validate_number_range(price, min_value=0, max_value=10000):
                        result["valid"] = False
                        result["errors"].append("价格范围无效")
                except ValueError:
                    result["valid"] = False
                    result["errors"].append("价格格式无效")
                
                # 验证分类
                category = product.get("category", "")
                valid_categories = ["electronics", "books", "clothing", "home", "sports"]
                if category not in valid_categories:
                    result["valid"] = False
                    result["errors"].append("产品分类无效")
                
                validation_results.append(result)
                
                if result["valid"]:
                    log.info(f"产品验证通过: {product['name']}")
                else:
                    log.warning(f"产品验证失败: {product['name']} - {result['errors']}")
            
            # 统计验证结果
            valid_count = sum(1 for r in validation_results if r["valid"])
            invalid_count = len(validation_results) - valid_count
            
            log.info(f"CSV数据验证完成: {valid_count} 个有效, {invalid_count} 个无效")
            
            # 生成验证报告
            csv_report = f"CSV数据驱动测试报告:\n"
            csv_report += f"总产品数量: {len(validation_results)}\n"
            csv_report += f"有效产品: {valid_count}\n"
            csv_report += f"无效产品: {invalid_count}\n"
            csv_report += f"有效率: {valid_count/len(validation_results):.2%}\n\n"
            
            if invalid_count > 0:
                csv_report += "无效产品详情:\n"
                for result in validation_results:
                    if not result["valid"]:
                        csv_report += f"  {result['name']}: {', '.join(result['errors'])}\n"
            
            allure.attach(
                csv_report,
                name="CSV数据验证报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 断言大部分数据应该是有效的
            assert valid_count / len(validation_results) >= 0.8, f"有效数据比例过低: {valid_count/len(validation_results):.2%}"
    
    @allure.story("YAML数据驱动测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.data_driven
    def test_yaml_data_driven_api_scenarios(self):
        """使用YAML数据驱动的API场景测试"""
        
        with allure.step("创建YAML测试场景"):
            # 定义API测试场景
            api_scenarios = {
                "scenarios": [
                    {
                        "name": "获取用户信息",
                        "method": "GET",
                        "url": "https://httpbin.org/get",
                        "params": {"user_id": "123"},
                        "expected_status": 200,
                        "expected_fields": ["args", "headers", "url"]
                    },
                    {
                        "name": "创建用户",
                        "method": "POST",
                        "url": "https://httpbin.org/post",
                        "data": {
                            "username": "testuser",
                            "email": "test@example.com",
                            "role": "user"
                        },
                        "expected_status": 200,
                        "expected_fields": ["json", "data"]
                    },
                    {
                        "name": "更新用户",
                        "method": "PUT",
                        "url": "https://httpbin.org/put",
                        "data": {
                            "user_id": "123",
                            "username": "updateduser",
                            "email": "updated@example.com"
                        },
                        "expected_status": 200,
                        "expected_fields": ["json"]
                    },
                    {
                        "name": "删除用户",
                        "method": "DELETE",
                        "url": "https://httpbin.org/delete",
                        "expected_status": 200,
                        "expected_fields": ["url", "args"]
                    }
                ]
            }
            
            # 保存到YAML文件
            yaml_file = self.test_data_dir / "api_scenarios.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(api_scenarios, f, default_flow_style=False, allow_unicode=True)
            
            log.info(f"创建了 {len(api_scenarios['scenarios'])} 个API测试场景")
        
        with allure.step("执行YAML驱动的API测试"):
            # 读取YAML数据
            with open(yaml_file, 'r', encoding='utf-8') as f:
                loaded_scenarios = yaml.safe_load(f)
            
            scenario_results = []
            
            for scenario in loaded_scenarios["scenarios"]:
                result = {
                    "name": scenario["name"],
                    "success": False,
                    "response_time": 0,
                    "status_code": 0,
                    "errors": []
                }
                
                try:
                    with allure.step(f"执行场景: {scenario['name']}"):
                        import time
                        start_time = time.time()
                        
                        # 根据方法执行API调用
                        method = scenario["method"].lower()
                        url = scenario["url"]
                        
                        if method == "get":
                            response = self.api_client.get(url, params=scenario.get("params", {}))
                        elif method == "post":
                            response = self.api_client.post(url, json_data=scenario.get("data", {}))
                        elif method == "put":
                            response = self.api_client.put(url, json_data=scenario.get("data", {}))
                        elif method == "delete":
                            response = self.api_client.delete(url)
                        else:
                            raise ValueError(f"不支持的HTTP方法: {method}")
                        
                        end_time = time.time()
                        result["response_time"] = (end_time - start_time) * 1000  # 转换为毫秒
                        result["status_code"] = response.status_code
                        
                        # 验证状态码
                        expected_status = scenario["expected_status"]
                        if response.status_code != expected_status:
                            result["errors"].append(f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}")
                        else:
                            # 验证响应字段
                            response_data = self.api_client.get_response_json(response)
                            expected_fields = scenario.get("expected_fields", [])
                            
                            for field in expected_fields:
                                if field not in response_data:
                                    result["errors"].append(f"缺少期望字段: {field}")
                            
                            if not result["errors"]:
                                result["success"] = True
                        
                        log.info(f"场景 '{scenario['name']}' 执行完成: {result['success']}")
                
                except Exception as e:
                    result["errors"].append(f"执行异常: {str(e)}")
                    log.error(f"场景 '{scenario['name']}' 执行失败: {e}")
                
                scenario_results.append(result)
            
            # 生成YAML测试报告
            successful_scenarios = sum(1 for r in scenario_results if r["success"])
            total_scenarios = len(scenario_results)
            
            yaml_report = f"YAML数据驱动API测试报告:\n"
            yaml_report += f"总场景数量: {total_scenarios}\n"
            yaml_report += f"成功场景: {successful_scenarios}\n"
            yaml_report += f"失败场景: {total_scenarios - successful_scenarios}\n"
            yaml_report += f"成功率: {successful_scenarios/total_scenarios:.2%}\n\n"
            
            yaml_report += "场景执行详情:\n"
            for result in scenario_results:
                status = "✅" if result["success"] else "❌"
                yaml_report += f"{status} {result['name']}\n"
                yaml_report += f"   状态码: {result['status_code']}\n"
                yaml_report += f"   响应时间: {result['response_time']:.2f}ms\n"
                if result["errors"]:
                    yaml_report += f"   错误: {'; '.join(result['errors'])}\n"
                yaml_report += "\n"
            
            allure.attach(
                yaml_report,
                name="YAML API测试报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 断言所有场景都应该成功
            assert successful_scenarios == total_scenarios, f"有 {total_scenarios - successful_scenarios} 个场景失败"
    
    @allure.story("动态数据生成测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.data_driven
    @pytest.mark.parametrize("data_type,count", [
        ("users", 5),
        ("products", 8),
        ("orders", 3),
        ("companies", 4)
    ])
    def test_dynamic_data_generation(self, data_type, count):
        """动态数据生成测试"""
        
        with allure.step(f"生成 {count} 个 {data_type} 数据"):
            if data_type == "users":
                generated_data = self.data_generator.generate_user_data(count)
            elif data_type == "products":
                generated_data = self.data_generator.generate_product_data(count)
            elif data_type == "orders":
                generated_data = self.data_generator.generate_order_data(count)
            elif data_type == "companies":
                generated_data = self.data_generator.generate_company_data(count)
            else:
                pytest.fail(f"不支持的数据类型: {data_type}")
            
            assert len(generated_data) == count, f"生成的数据数量不匹配: 期望 {count}, 实际 {len(generated_data)}"
            
            log.info(f"成功生成 {len(generated_data)} 个 {data_type} 数据")
        
        with allure.step("验证生成的数据质量"):
            validation_errors = []
            
            for i, item in enumerate(generated_data):
                if data_type == "users":
                    # 验证用户数据
                    if not self.data_validator.validate_email(item.get("email", "")):
                        validation_errors.append(f"用户 {i}: 邮箱格式无效")
                    
                    if not self.data_validator.validate_string_length(item.get("username", ""), min_length=3):
                        validation_errors.append(f"用户 {i}: 用户名过短")
                
                elif data_type == "products":
                    # 验证产品数据
                    try:
                        price = float(item.get("price", 0))
                        if not self.data_validator.validate_number_range(price, min_value=0):
                            validation_errors.append(f"产品 {i}: 价格无效")
                    except (ValueError, TypeError):
                        validation_errors.append(f"产品 {i}: 价格格式错误")
                
                elif data_type == "orders":
                    # 验证订单数据
                    if not item.get("order_id"):
                        validation_errors.append(f"订单 {i}: 缺少订单ID")
                    
                    try:
                        total = float(item.get("total", 0))
                        if total <= 0:
                            validation_errors.append(f"订单 {i}: 总金额无效")
                    except (ValueError, TypeError):
                        validation_errors.append(f"订单 {i}: 总金额格式错误")
                
                elif data_type == "companies":
                    # 验证公司数据
                    if not self.data_validator.validate_string_length(item.get("name", ""), min_length=2):
                        validation_errors.append(f"公司 {i}: 公司名称过短")
            
            # 生成数据质量报告
            quality_report = f"动态数据生成质量报告:\n"
            quality_report += f"数据类型: {data_type}\n"
            quality_report += f"生成数量: {count}\n"
            quality_report += f"验证错误: {len(validation_errors)} 个\n"
            quality_report += f"数据质量: {(count - len(validation_errors))/count:.2%}\n\n"
            
            if validation_errors:
                quality_report += "发现的问题:\n"
                for error in validation_errors[:10]:  # 只显示前10个错误
                    quality_report += f"  - {error}\n"
                if len(validation_errors) > 10:
                    quality_report += f"  ... 还有 {len(validation_errors) - 10} 个错误\n"
            else:
                quality_report += "所有生成的数据都通过了质量验证\n"
            
            # 添加数据样例
            quality_report += f"\n{data_type} 数据样例:\n"
            for i, item in enumerate(generated_data[:3]):  # 显示前3个样例
                quality_report += f"  样例 {i+1}: {item}\n"
            
            allure.attach(
                quality_report,
                name=f"{data_type}数据生成报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 断言数据质量应该很高
            error_rate = len(validation_errors) / count
            assert error_rate < 0.1, f"{data_type} 数据质量过低，错误率: {error_rate:.2%}"
            
            log.info(f"{data_type} 数据生成质量验证通过，错误率: {error_rate:.2%}")
    
    @allure.story("边界值数据测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.data_driven
    @pytest.mark.parametrize("test_case", [
        {"name": "最小值", "value": 0, "should_pass": True},
        {"name": "负数", "value": -1, "should_pass": False},
        {"name": "正常值", "value": 50, "should_pass": True},
        {"name": "最大值", "value": 100, "should_pass": True},
        {"name": "超出最大值", "value": 101, "should_pass": False},
        {"name": "极大值", "value": 999999, "should_pass": False}
    ])
    def test_boundary_value_testing(self, test_case):
        """边界值数据测试"""
        
        with allure.step(f"测试边界值: {test_case['name']} (值: {test_case['value']})"):
            # 定义验证规则：值应该在0-100之间
            min_value = 0
            max_value = 100
            
            # 执行验证
            is_valid = self.data_validator.validate_number_range(
                test_case["value"], 
                min_value=min_value, 
                max_value=max_value
            )
            
            expected_result = test_case["should_pass"]
            
            # 验证结果是否符合预期
            if expected_result:
                assert is_valid, f"值 {test_case['value']} 应该通过验证但失败了"
                log.info(f"边界值测试通过: {test_case['name']} = {test_case['value']}")
            else:
                assert not is_valid, f"值 {test_case['value']} 应该验证失败但通过了"
                log.info(f"边界值测试通过: {test_case['name']} = {test_case['value']} (正确拒绝)")
        
        with allure.step("记录测试结果"):
            result_info = f"""
边界值测试结果:
- 测试用例: {test_case['name']}
- 测试值: {test_case['value']}
- 期望结果: {'通过' if test_case['should_pass'] else '拒绝'}
- 实际结果: {'通过' if is_valid else '拒绝'}
- 测试状态: ✅ 成功
            """
            
            allure.attach(
                result_info,
                name=f"边界值测试_{test_case['name']}",
                attachment_type=allure.attachment_type.TEXT
            )
