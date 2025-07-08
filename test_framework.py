#!/usr/bin/env python3
"""
测试框架验证脚本
用于验证框架的基本功能是否正常工作
"""

import os
import sys
import subprocess
from pathlib import Path


def test_imports():
    """测试所有模块是否可以正常导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试工具类导入
        from utilities.logger import log
        from utilities.config_reader import config
        from utilities.api_client import api_client
        from utilities.selenium_wrapper import selenium_wrapper
        
        # 测试页面对象导入
        from page_objects.login_page import LoginPage
        
        print("✅ 所有模块导入成功")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_config_loading():
    """测试配置加载功能"""
    print("🔍 测试配置加载...")
    
    try:
        from utilities.config_reader import config
        
        # 测试加载开发环境配置
        dev_config = config.load_config("dev")
        
        # 验证配置结构
        assert "api" in dev_config
        assert "web" in dev_config
        assert "logging" in dev_config
        
        print("✅ 配置加载成功")
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def test_logger():
    """测试日志功能"""
    print("🔍 测试日志功能...")
    
    try:
        from utilities.logger import log
        
        # 测试各种日志级别
        log.info("这是一条测试信息日志")
        log.debug("这是一条测试调试日志")
        log.warning("这是一条测试警告日志")
        
        print("✅ 日志功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 日志功能失败: {e}")
        return False


def test_data_loading():
    """测试数据加载功能"""
    print("🔍 测试数据加载...")
    
    try:
        import json
        from pathlib import Path
        
        # 加载测试数据
        test_data_file = Path("data/test_data.json")
        with open(test_data_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # 验证数据结构
        assert "users" in test_data
        assert "api_test_data" in test_data
        
        print("✅ 测试数据加载成功")
        return True
        
    except Exception as e:
        print(f"❌ 测试数据加载失败: {e}")
        return False


def test_pytest_config():
    """测试Pytest配置"""
    print("🔍 测试Pytest配置...")
    
    try:
        # 检查pytest.ini文件是否存在
        pytest_ini = Path("pytest.ini")
        assert pytest_ini.exists(), "pytest.ini文件不存在"
        
        # 尝试运行pytest --help来验证配置
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Pytest配置正常")
            return True
        else:
            print(f"❌ Pytest配置有问题: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Pytest配置测试失败: {e}")
        return False


def test_directory_structure():
    """测试目录结构"""
    print("🔍 测试目录结构...")
    
    required_dirs = [
        "configs",
        "tests",
        "tests/api",
        "tests/web",
        "page_objects",
        "utilities",
        "fixtures",
        "data",
        "reports"
    ]
    
    required_files = [
        "pytest.ini",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "configs/dev.yaml",
        "configs/staging.yaml",
        "configs/prod.yaml",
        "utilities/logger.py",
        "utilities/config_reader.py",
        "utilities/api_client.py",
        "utilities/selenium_wrapper.py",
        "page_objects/login_page.py",
        "fixtures/conftest.py",
        "data/test_data.json",
        "tests/api/test_user_api.py",
        "tests/web/test_login.py"
    ]
    
    try:
        # 检查目录
        for dir_path in required_dirs:
            path = Path(dir_path)
            assert path.exists() and path.is_dir(), f"目录不存在: {dir_path}"
        
        # 检查文件
        for file_path in required_files:
            path = Path(file_path)
            assert path.exists() and path.is_file(), f"文件不存在: {file_path}"
        
        print("✅ 目录结构完整")
        return True
        
    except AssertionError as e:
        print(f"❌ 目录结构检查失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 目录结构测试失败: {e}")
        return False


def run_sample_test():
    """运行示例测试"""
    print("🔍 运行示例测试...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env["TEST_ENV"] = "dev"
        
        # 运行一个简单的测试收集
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        
        if result.returncode == 0:
            print("✅ 测试收集成功")
            print(f"收集到的测试: {result.stdout.count('test_')}")
            return True
        else:
            print(f"❌ 测试收集失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 示例测试运行失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始验证Pytest测试框架...")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置加载", test_config_loading),
        ("日志功能", test_logger),
        ("数据加载", test_data_loading),
        ("目录结构", test_directory_structure),
        ("Pytest配置", test_pytest_config),
        ("示例测试", run_sample_test),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   跳过后续测试...")
            break
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 恭喜！测试框架验证成功！")
        print("\n📚 接下来你可以:")
        print("   1. 安装依赖: pip install -r requirements.txt")
        print("   2. 运行测试: pytest")
        print("   3. 生成报告: pytest --alluredir=reports/allure-results")
        print("   4. 查看文档: 阅读 README.md")
        return True
    else:
        print("❌ 测试框架验证失败，请检查错误信息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
