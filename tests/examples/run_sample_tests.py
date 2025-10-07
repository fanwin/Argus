#!/usr/bin/env python3
"""
运行示例测试的脚本
演示如何使用框架运行测试
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utilities.logger import log


def setup_environment():
    """设置测试环境"""
    # 设置环境变量
    os.environ['TEST_ENV'] = 'dev'
    os.environ['PYTHONPATH'] = str(project_root)
    
    # 创建必要的目录
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    for subdir in ["allure-results", "screenshots", "coverage"]:
        (reports_dir / subdir).mkdir(exist_ok=True)


def run_sample_tests():
    """运行示例测试"""
    log.info("开始运行示例测试...")
    
    # 设置环境
    setup_environment()
    
    # 构建pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        "examples/",  # 测试目录
        "-v",  # 详细输出
        "-m", "sample",  # 只运行标记为sample的测试
        "--alluredir=reports/allure-results",  # Allure报告
        "--html=reports/sample_report.html",  # HTML报告
        "--self-contained-html",  # 独立HTML报告
        "--tb=short",  # 简短的回溯信息
        "-p", "no:warnings"  # 禁用警告
    ]
    
    log.info(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 运行测试
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=False,
            text=True,
            check=False  # 不抛出异常，我们自己处理返回码
        )
        
        if result.returncode == 0:
            log.info("✅ 示例测试运行成功")
            return True
        else:
            log.error("❌ 示例测试运行失败")
            return False
            
    except FileNotFoundError:
        log.error("❌ pytest未找到，请确保已安装依赖")
        return False
    except Exception as e:
        log.error(f"❌ 运行测试时发生错误: {e}")
        return False


def run_framework_validation():
    """运行框架验证"""
    log.info("运行框架验证...")
    
    cmd = [sys.executable, "test_framework.py"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=False,
            text=True,
            check=False
        )
        
        return result.returncode == 0
        
    except Exception as e:
        log.error(f"框架验证失败: {e}")
        return False


def main():
    """主函数"""
    log.info("=" * 50)
    log.info("自动化测试框架 - 示例测试运行器")
    log.info("=" * 50)
    
    success = True
    
    try:
        # 1. 运行框架验证
        log.info("步骤 1/2: 框架验证")
        if not run_framework_validation():
            log.error("框架验证失败")
            success = False
        else:
            log.info("✅ 框架验证通过")
        
        # 2. 运行示例测试
        if success:
            log.info("步骤 2/2: 运行示例测试")
            success = run_sample_tests()
        
        # 显示结果
        log.info("=" * 50)
        if success:
            log.info("✅ 所有示例测试完成！")
            log.info("查看报告:")
            log.info(f"  - HTML报告: {project_root / 'reports' / 'sample_report.html'}")
            log.info(f"  - Allure结果: {project_root / 'reports' / 'allure-results'}")
        else:
            log.error("❌ 示例测试执行失败")
            
    except KeyboardInterrupt:
        log.warning("用户中断执行")
        success = False
    except Exception as e:
        log.error(f"执行失败: {e}")
        success = False
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
