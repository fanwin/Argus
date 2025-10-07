#!/usr/bin/env python3
"""
综合测试运行器
运行所有类型的测试案例
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from utilities.logger import log


def run_test_suite(test_type: str, markers: str = None, parallel: bool = False, verbose: bool = True):
    """
    运行指定类型的测试套件
    
    Args:
        test_type: 测试类型 (api, web, performance, security, mobile, accessibility, data_driven, integration, all)
        markers: pytest标记过滤器
        parallel: 是否并行运行
        verbose: 是否详细输出
    """
    
    # 设置环境变量
    os.environ['TEST_ENV'] = os.getenv('TEST_ENV', 'dev')
    os.environ['BROWSER'] = os.getenv('BROWSER', 'chrome')
    os.environ['HEADLESS'] = os.getenv('HEADLESS', 'true')
    
    # 构建pytest命令
    cmd = [sys.executable, "-m", "pytest"]
    
    # 添加测试路径
    if test_type == "all":
        cmd.append("tests/")
    elif test_type == "api":
        cmd.append("tests/api/")
    elif test_type == "web":
        cmd.append("tests/web/")
    elif test_type == "performance":
        cmd.append("tests/performance/")
    elif test_type == "security":
        cmd.append("tests/security/")
    elif test_type == "mobile":
        cmd.append("tests/mobile/")
    elif test_type == "accessibility":
        cmd.append("tests/accessibility/")
    elif test_type == "data_driven":
        cmd.append("tests/data_driven/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    else:
        raise ValueError(f"不支持的测试类型: {test_type}")
    
    # 添加标记过滤器
    if markers:
        cmd.extend(["-m", markers])
    elif test_type != "all":
        cmd.extend(["-m", test_type])
    
    # 添加并行参数
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # 添加详细输出
    if verbose:
        cmd.append("-v")
    
    # 添加报告参数
    cmd.extend([
        "--alluredir=reports/allure-results",
        "--html=reports/comprehensive_report.html",
        "--self-contained-html",
        "--junitxml=reports/junit.xml",
        "--cov=.",
        "--cov-report=html:reports/coverage",
        "--cov-report=xml",
        "--tb=short"
    ])
    
    log.info(f"运行测试命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path.cwd(),
            capture_output=False,
            text=True,
            check=False
        )
        
        return result.returncode == 0
        
    except Exception as e:
        log.error(f"运行测试时出现异常: {e}")
        return False


def run_specific_scenarios():
    """运行特定测试场景"""
    
    scenarios = {
        "smoke": {
            "description": "冒烟测试 - 快速验证核心功能",
            "markers": "smoke",
            "parallel": True
        },
        "regression": {
            "description": "回归测试 - 验证修复和新功能",
            "markers": "regression",
            "parallel": True
        },
        "critical": {
            "description": "关键功能测试",
            "markers": "critical",
            "parallel": False
        },
        "comprehensive": {
            "description": "综合测试 - 完整功能验证",
            "markers": "comprehensive",
            "parallel": False
        }
    }
    
    print("可用的测试场景:")
    for key, scenario in scenarios.items():
        print(f"  {key}: {scenario['description']}")
    
    choice = input("\n请选择测试场景 (或按Enter跳过): ").strip()
    
    if choice in scenarios:
        scenario = scenarios[choice]
        log.info(f"运行测试场景: {scenario['description']}")
        
        return run_test_suite(
            test_type="all",
            markers=scenario["markers"],
            parallel=scenario["parallel"]
        )
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="综合测试运行器")
    
    parser.add_argument(
        "--type", "-t",
        choices=["api", "web", "performance", "security", "mobile", "accessibility", "data_driven", "integration", "all"],
        default="all",
        help="测试类型"
    )
    
    parser.add_argument(
        "--markers", "-m",
        help="pytest标记过滤器"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="并行运行测试"
    )
    
    parser.add_argument(
        "--scenario", "-s",
        action="store_true",
        help="选择特定测试场景"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式"
    )
    
    args = parser.parse_args()
    
    print("🚀 综合自动化测试框架")
    print("=" * 50)
    
    success = True
    
    try:
        if args.scenario:
            # 运行特定场景
            success = run_specific_scenarios()
        else:
            # 运行指定类型的测试
            log.info(f"开始运行 {args.type} 测试")
            success = run_test_suite(
                test_type=args.type,
                markers=args.markers,
                parallel=args.parallel,
                verbose=not args.quiet
            )
        
        print("\n" + "=" * 50)
        if success:
            print("✅ 测试运行完成!")
            print("📊 查看报告:")
            print(f"  - HTML报告: {Path.cwd() / 'reports' / 'comprehensive_report.html'}")
            print(f"  - Allure结果: {Path.cwd() / 'reports' / 'allure-results'}")
            print(f"  - 覆盖率报告: {Path.cwd() / 'reports' / 'coverage'}")
        else:
            print("❌ 测试运行失败!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试运行")
        return 1
    except Exception as e:
        print(f"\n❌ 运行测试时出现异常: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
