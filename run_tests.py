#!/usr/bin/env python3
"""
测试运行脚本
提供简单的命令行界面来运行各种测试
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utilities.logger import log
from utilities.config_reader import config


def setup_environment():
    """设置测试环境"""
    # 设置环境变量
    os.environ['PYTHONPATH'] = str(project_root)
    
    # 创建报告目录
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    for subdir in ["allure-results", "screenshots", "coverage", "logs"]:
        (reports_dir / subdir).mkdir(exist_ok=True)


def run_command(cmd, cwd=None):
    """运行命令"""
    log.info(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or project_root,
            capture_output=False,
            text=True,
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        log.error(f"命令执行失败: {e}")
        return False
    except FileNotFoundError as e:
        log.error(f"命令未找到: {e}")
        return False


def run_framework_validation():
    """运行框架验证"""
    log.info("运行框架验证...")
    return run_command([sys.executable, "test_framework.py"])


def run_pytest_tests(test_type, browser, env, parallel, markers):
    """运行pytest测试"""
    log.info(f"运行测试 - 类型: {test_type}, 浏览器: {browser}, 环境: {env}")
    
    # 设置环境变量
    os.environ['TEST_ENV'] = env
    os.environ['BROWSER'] = browser
    os.environ['HEADLESS'] = 'true'
    
    # 构建pytest命令
    cmd = [sys.executable, "-m", "pytest"]
    
    # 添加测试标记
    if test_type != "all":
        cmd.extend(["-m", test_type])
    elif markers:
        cmd.extend(["-m", markers])
    
    # 添加并行参数
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # 添加报告参数
    cmd.extend([
        "--alluredir=reports/allure-results",
        "--html=reports/report.html",
        "--self-contained-html",
        "--junitxml=reports/junit.xml",
        "--cov=.",
        "--cov-report=html:reports/coverage",
        "--cov-report=xml",
        "-v",
        "--tb=short"
    ])
    
    return run_command(cmd)


def generate_allure_report():
    """生成Allure报告"""
    log.info("生成Allure报告...")
    
    allure_results = project_root / "reports" / "allure-results"
    allure_report = project_root / "reports" / "allure-report"
    
    if not allure_results.exists() or not any(allure_results.iterdir()):
        log.warning("没有找到Allure测试结果")
        return False
    
    cmd = [
        "allure", "generate", 
        str(allure_results), 
        "-o", str(allure_report), 
        "--clean"
    ]
    
    if run_command(cmd):
        log.info(f"✅ Allure报告生成完成: {allure_report / 'index.html'}")
        return True
    else:
        log.warning("Allure报告生成失败，可能是Allure未安装")
        return False


def serve_allure_report():
    """启动Allure报告服务器"""
    log.info("启动Allure报告服务器...")
    
    allure_results = project_root / "reports" / "allure-results"
    
    if not allure_results.exists() or not any(allure_results.iterdir()):
        log.warning("没有找到Allure测试结果")
        return False
    
    cmd = ["allure", "serve", str(allure_results)]
    
    try:
        subprocess.run(cmd, cwd=project_root)
        return True
    except KeyboardInterrupt:
        log.info("Allure服务器已停止")
        return True
    except Exception as e:
        log.error(f"启动Allure服务器失败: {e}")
        return False


def clean_reports():
    """清理报告目录"""
    log.info("清理报告目录...")
    
    reports_dir = project_root / "reports"
    if reports_dir.exists():
        import shutil
        shutil.rmtree(reports_dir)
        log.info("报告目录已清理")
    
    # 重新创建目录
    setup_environment()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动化测试运行脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type smoke --browser chrome --env dev
  %(prog)s --type api --parallel --env staging
  %(prog)s --validate
  %(prog)s --report
  %(prog)s --serve
  %(prog)s --clean
        """
    )
    
    parser.add_argument(
        "-t", "--type",
        choices=["all", "smoke", "api", "web", "regression"],
        default="all",
        help="测试类型 (默认: all)"
    )
    
    parser.add_argument(
        "-b", "--browser",
        choices=["chrome", "firefox", "edge"],
        default="chrome",
        help="浏览器类型 (默认: chrome)"
    )
    
    parser.add_argument(
        "-e", "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="测试环境 (默认: dev)"
    )
    
    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help="启用并行测试"
    )
    
    parser.add_argument(
        "-m", "--markers",
        help="自定义pytest标记 (例如: 'smoke and api')"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="只运行框架验证"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="只生成Allure报告"
    )
    
    parser.add_argument(
        "--serve",
        action="store_true",
        help="启动Allure报告服务器"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理报告目录"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    log.info("=" * 50)
    log.info("自动化测试框架")
    log.info("=" * 50)
    
    # 设置环境
    setup_environment()
    
    success = True
    
    try:
        # 清理报告
        if args.clean:
            clean_reports()
            log.info("✅ 清理完成")
            return
        
        # 启动Allure服务器
        if args.serve:
            serve_allure_report()
            return
        
        # 只生成报告
        if args.report:
            generate_allure_report()
            return
        
        # 只运行框架验证
        if args.validate:
            success = run_framework_validation()
        else:
            # 运行框架验证
            log.info("步骤 1/3: 框架验证")
            if not run_framework_validation():
                log.error("框架验证失败")
                success = False
            else:
                log.info("✅ 框架验证通过")
            
            # 运行测试
            if success:
                log.info("步骤 2/3: 运行测试")
                success = run_pytest_tests(
                    args.type, 
                    args.browser, 
                    args.env, 
                    args.parallel,
                    args.markers
                )
                
                if success:
                    log.info("✅ 测试执行完成")
                else:
                    log.error("测试执行失败")
            
            # 生成报告
            if success:
                log.info("步骤 3/3: 生成报告")
                generate_allure_report()
        
        # 显示结果摘要
        log.info("=" * 50)
        log.info("测试结果摘要")
        log.info("=" * 50)
        log.info(f"测试类型: {args.type}")
        log.info(f"浏览器: {args.browser}")
        log.info(f"环境: {args.env}")
        log.info(f"并行执行: {args.parallel}")
        log.info(f"自定义标记: {args.markers or '无'}")
        
        # 显示报告链接
        reports_dir = project_root / "reports"
        
        html_report = reports_dir / "report.html"
        if html_report.exists():
            log.info(f"HTML报告: {html_report}")
        
        allure_report = reports_dir / "allure-report" / "index.html"
        if allure_report.exists():
            log.info(f"Allure报告: {allure_report}")
        
        coverage_report = reports_dir / "coverage" / "index.html"
        if coverage_report.exists():
            log.info(f"覆盖率报告: {coverage_report}")
        
        if success:
            log.info("✅ 所有步骤完成！")
        else:
            log.error("❌ 执行过程中出现错误")
            
    except KeyboardInterrupt:
        log.warning("用户中断执行")
        success = False
    except Exception as e:
        log.error(f"执行失败: {e}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
