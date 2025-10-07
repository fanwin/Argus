#!/usr/bin/env python3
"""
运行示例测试的便捷脚本
"""

import subprocess
import sys
from pathlib import Path

def run_examples():
    """运行示例测试"""
    print("🚀 运行自动化测试框架示例...")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "pytest",
        "examples/",
        "-m", "sample",
        "-v",
        "--html=reports/examples_report.html",
        "--self-contained-html",
        "--alluredir=reports/allure-results"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # 运行测试
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=False,
            text=True,
            check=False
        )
        
        print("-" * 50)
        if result.returncode == 0:
            print("✅ 示例测试运行成功!")
            print(f"📊 HTML报告: {project_root / 'reports' / 'examples_report.html'}")
            print(f"📁 Allure结果: {project_root / 'reports' / 'allure-results'}")
            return True
        else:
            print("❌ 示例测试运行失败!")
            return False
            
    except Exception as e:
        print(f"❌ 运行示例时发生错误: {e}")
        return False

def main():
    """主函数"""
    success = run_examples()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()