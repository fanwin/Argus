"""
测试数据生成工具
用于生成各种类型的测试数据
"""

import random
import string
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from faker import Faker
import uuid

from utilities.logger import log


class DataGenerator:
    """测试数据生成器"""
    
    def __init__(self, locale: str = 'zh_CN'):
        """
        初始化数据生成器
        
        Args:
            locale: 本地化设置
        """
        self.fake = Faker(locale)
        self.locale = locale
        
    def generate_user_data(self, count: int = 1, include_password: bool = True) -> List[Dict[str, Any]]:
        """
        生成用户数据
        
        Args:
            count: 生成数量
            include_password: 是否包含密码
            
        Returns:
            用户数据列表
        """
        users = []
        
        for _ in range(count):
            user = {
                "id": self.fake.random_int(min=1000, max=9999),
                "username": self.fake.user_name(),
                "email": self.fake.email(),
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "phone": self.fake.phone_number(),
                "address": self.fake.address(),
                "birth_date": self.fake.date_of_birth().strftime("%Y-%m-%d"),
                "gender": random.choice(["男", "女", "其他"]),
                "status": random.choice(["active", "inactive", "pending"]),
                "role": random.choice(["admin", "user", "manager", "guest"]),
                "created_at": self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "last_login": self.fake.date_time_between(start_date='-30d', end_date='now').isoformat()
            }
            
            if include_password:
                user["password"] = self.generate_password()
                user["confirm_password"] = user["password"]
            
            users.append(user)
        
        return users
    
    def generate_password(self, length: int = 12, include_special: bool = True) -> str:
        """
        生成密码
        
        Args:
            length: 密码长度
            include_special: 是否包含特殊字符
            
        Returns:
            生成的密码
        """
        characters = string.ascii_letters + string.digits
        if include_special:
            characters += "!@#$%^&*"
        
        # 确保密码包含大小写字母和数字
        password = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits)
        ]
        
        if include_special:
            password.append(random.choice("!@#$%^&*"))
        
        # 填充剩余长度
        for _ in range(length - len(password)):
            password.append(random.choice(characters))
        
        # 打乱顺序
        random.shuffle(password)
        return ''.join(password)
    
    def generate_email(self, domain: str = None) -> str:
        """
        生成邮箱地址
        
        Args:
            domain: 指定域名
            
        Returns:
            邮箱地址
        """
        if domain:
            username = self.fake.user_name()
            return f"{username}@{domain}"
        return self.fake.email()
    
    def generate_phone_number(self, country_code: str = "+86") -> str:
        """
        生成手机号码
        
        Args:
            country_code: 国家代码
            
        Returns:
            手机号码
        """
        if country_code == "+86":
            # 中国手机号格式
            prefixes = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                       "150", "151", "152", "153", "155", "156", "157", "158", "159",
                       "180", "181", "182", "183", "184", "185", "186", "187", "188", "189"]
            prefix = random.choice(prefixes)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            return f"{country_code} {prefix}{suffix}"
        else:
            return self.fake.phone_number()
    
    def generate_company_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        生成公司数据
        
        Args:
            count: 生成数量
            
        Returns:
            公司数据列表
        """
        companies = []
        
        for _ in range(count):
            company = {
                "id": self.fake.random_int(min=1000, max=9999),
                "name": self.fake.company(),
                "industry": random.choice(["科技", "金融", "教育", "医疗", "制造", "零售", "服务"]),
                "size": random.choice(["1-50", "51-200", "201-500", "501-1000", "1000+"]),
                "website": self.fake.url(),
                "email": self.fake.company_email(),
                "phone": self.fake.phone_number(),
                "address": self.fake.address(),
                "description": self.fake.text(max_nb_chars=200),
                "founded_year": self.fake.random_int(min=1950, max=2023),
                "status": random.choice(["active", "inactive", "pending"])
            }
            companies.append(company)
        
        return companies
    
    def generate_product_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        生成产品数据
        
        Args:
            count: 生成数量
            
        Returns:
            产品数据列表
        """
        products = []
        
        categories = ["电子产品", "服装", "家居", "图书", "运动", "美妆", "食品"]
        
        for _ in range(count):
            product = {
                "id": self.fake.random_int(min=10000, max=99999),
                "name": self.fake.catch_phrase(),
                "category": random.choice(categories),
                "price": round(random.uniform(10.0, 1000.0), 2),
                "currency": "CNY",
                "description": self.fake.text(max_nb_chars=300),
                "sku": self.fake.bothify(text='??-####'),
                "stock": self.fake.random_int(min=0, max=1000),
                "weight": round(random.uniform(0.1, 10.0), 2),
                "dimensions": {
                    "length": round(random.uniform(1.0, 50.0), 1),
                    "width": round(random.uniform(1.0, 50.0), 1),
                    "height": round(random.uniform(1.0, 50.0), 1)
                },
                "rating": round(random.uniform(1.0, 5.0), 1),
                "reviews_count": self.fake.random_int(min=0, max=1000),
                "status": random.choice(["available", "out_of_stock", "discontinued"]),
                "created_at": self.fake.date_time_between(start_date='-2y', end_date='now').isoformat()
            }
            products.append(product)
        
        return products
    
    def generate_order_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        生成订单数据
        
        Args:
            count: 生成数量
            
        Returns:
            订单数据列表
        """
        orders = []
        
        for _ in range(count):
            order = {
                "id": self.fake.uuid4(),
                "order_number": self.fake.bothify(text='ORD-########'),
                "customer_id": self.fake.random_int(min=1000, max=9999),
                "customer_name": self.fake.name(),
                "customer_email": self.fake.email(),
                "total_amount": round(random.uniform(50.0, 2000.0), 2),
                "currency": "CNY",
                "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
                "payment_method": random.choice(["credit_card", "debit_card", "paypal", "alipay", "wechat_pay"]),
                "payment_status": random.choice(["pending", "paid", "failed", "refunded"]),
                "shipping_address": self.fake.address(),
                "billing_address": self.fake.address(),
                "items_count": self.fake.random_int(min=1, max=10),
                "created_at": self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "updated_at": self.fake.date_time_between(start_date='-30d', end_date='now').isoformat()
            }
            orders.append(order)
        
        return orders
    
    def generate_api_test_data(self, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """
        生成API测试数据
        
        Args:
            endpoint: API端点
            method: HTTP方法
            
        Returns:
            API测试数据
        """
        test_data = {
            "endpoint": endpoint,
            "method": method,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "TestClient/1.0"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if method in ["POST", "PUT", "PATCH"]:
            if "user" in endpoint.lower():
                test_data["payload"] = self.generate_user_data(1)[0]
            elif "product" in endpoint.lower():
                test_data["payload"] = self.generate_product_data(1)[0]
            elif "order" in endpoint.lower():
                test_data["payload"] = self.generate_order_data(1)[0]
            else:
                test_data["payload"] = {
                    "id": self.fake.uuid4(),
                    "name": self.fake.name(),
                    "value": self.fake.text(max_nb_chars=100)
                }
        
        return test_data
    
    def generate_form_test_data(self, form_type: str) -> Dict[str, Any]:
        """
        生成表单测试数据
        
        Args:
            form_type: 表单类型
            
        Returns:
            表单测试数据
        """
        if form_type == "registration":
            return {
                "username": self.fake.user_name(),
                "email": self.fake.email(),
                "password": self.generate_password(),
                "confirm_password": None,  # 将在测试中设置
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "phone": self.generate_phone_number(),
                "agree_terms": True
            }
        
        elif form_type == "contact":
            return {
                "name": self.fake.name(),
                "email": self.fake.email(),
                "phone": self.generate_phone_number(),
                "subject": self.fake.sentence(nb_words=6),
                "message": self.fake.text(max_nb_chars=500),
                "company": self.fake.company()
            }
        
        elif form_type == "feedback":
            return {
                "name": self.fake.name(),
                "email": self.fake.email(),
                "rating": random.randint(1, 5),
                "category": random.choice(["产品", "服务", "网站", "其他"]),
                "feedback": self.fake.text(max_nb_chars=300),
                "recommend": random.choice([True, False])
            }
        
        else:
            return {
                "field1": self.fake.word(),
                "field2": self.fake.sentence(),
                "field3": self.fake.random_int(min=1, max=100)
            }
    
    def generate_search_keywords(self, count: int = 10) -> List[str]:
        """
        生成搜索关键词
        
        Args:
            count: 生成数量
            
        Returns:
            搜索关键词列表
        """
        keywords = []
        
        # 常见搜索词
        common_words = ["产品", "服务", "帮助", "文档", "支持", "价格", "功能", "使用", "教程", "下载"]
        
        for _ in range(count):
            if random.choice([True, False]):
                # 使用常见词
                keyword = random.choice(common_words)
            else:
                # 生成随机词
                keyword = self.fake.word()
            
            keywords.append(keyword)
        
        return list(set(keywords))  # 去重
    
    def generate_file_data(self, file_type: str = "text") -> Dict[str, Any]:
        """
        生成文件数据
        
        Args:
            file_type: 文件类型
            
        Returns:
            文件数据
        """
        file_extensions = {
            "text": [".txt", ".doc", ".docx", ".pdf"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "video": [".mp4", ".avi", ".mov", ".wmv"],
            "audio": [".mp3", ".wav", ".flac", ".aac"],
            "archive": [".zip", ".rar", ".7z", ".tar.gz"]
        }
        
        extension = random.choice(file_extensions.get(file_type, [".txt"]))
        
        return {
            "filename": f"{self.fake.word()}{extension}",
            "size": f"{random.randint(1, 100)}MB",
            "type": file_type,
            "extension": extension,
            "created_date": self.fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
            "modified_date": self.fake.date_between(start_date='-30d', end_date='today').strftime("%Y-%m-%d")
        }
    
    def save_test_data_to_file(self, data: Dict[str, Any], filename: str):
        """
        保存测试数据到文件
        
        Args:
            data: 测试数据
            filename: 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            log.info(f"测试数据已保存到: {filename}")
        except Exception as e:
            log.error(f"保存测试数据失败: {e}")
    
    def generate_bulk_test_data(self, data_types: List[str], counts: Dict[str, int]) -> Dict[str, Any]:
        """
        批量生成测试数据
        
        Args:
            data_types: 数据类型列表
            counts: 每种类型的数量
            
        Returns:
            批量测试数据
        """
        bulk_data = {}
        
        for data_type in data_types:
            count = counts.get(data_type, 10)
            
            if data_type == "users":
                bulk_data[data_type] = self.generate_user_data(count)
            elif data_type == "companies":
                bulk_data[data_type] = self.generate_company_data(count)
            elif data_type == "products":
                bulk_data[data_type] = self.generate_product_data(count)
            elif data_type == "orders":
                bulk_data[data_type] = self.generate_order_data(count)
            elif data_type == "search_keywords":
                bulk_data[data_type] = self.generate_search_keywords(count)
            else:
                log.warning(f"未知的数据类型: {data_type}")
        
        return bulk_data


# 创建全局数据生成器实例
data_generator = DataGenerator()


if __name__ == "__main__":
    # 示例用法
    generator = DataGenerator()
    
    # 生成用户数据
    users = generator.generate_user_data(5)
    print("生成的用户数据:")
    for user in users:
        print(f"  {user['username']} - {user['email']}")
    
    # 生成产品数据
    products = generator.generate_product_data(3)
    print("\n生成的产品数据:")
    for product in products:
        print(f"  {product['name']} - ¥{product['price']}")
    
    # 生成API测试数据
    api_data = generator.generate_api_test_data("/api/users", "POST")
    print(f"\nAPI测试数据: {api_data['endpoint']}")
    
    # 批量生成数据
    bulk_data = generator.generate_bulk_test_data(
        ["users", "products", "orders"],
        {"users": 10, "products": 5, "orders": 8}
    )
    print(f"\n批量数据包含: {list(bulk_data.keys())}")
    
    # 保存到文件
    generator.save_test_data_to_file(bulk_data, "generated_test_data.json")
