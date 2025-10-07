#!/usr/bin/env python3
"""
分布式测试主控制器
协调多个工作节点执行测试
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utilities.logger import log
from utilities.config_reader import config
from utilities.distributed_runner import DistributedTestRunner
from utilities.test_collector import TestCollector


class DistributedTestController:
    """分布式测试控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.runner = DistributedTestRunner()
        self.collector = TestCollector()
        self.start_time = None
        self.end_time = None
        
    def collect_and_distribute_tests(self, markers: List[str] = None, test_type: str = None):
        """
        收集并分发测试任务
        
        Args:
            markers: pytest标记
            test_type: 测试类型
        """
        log.info("=" * 60)
        log.info("开始收集测试用例")
        log.info("=" * 60)
        
        # 收集测试
        tests = self.collector.collect_tests(markers=markers, test_type=test_type)
        
        if not tests:
            log.warning("未找到任何测试用例")
            return
        
        # 显示统计信息
        stats = self.collector.get_statistics()
        log.info(f"总测试数: {stats['total_tests']}")
        log.info(f"按文件分布: {len(stats['by_file'])} 个文件")
        log.info(f"按标记分布: {stats['by_marker']}")
        
        # 创建任务
        tasks = self.collector.create_tasks()
        
        # 清空旧队列
        self.runner.clear_queue()
        
        # 推送任务到队列
        log.info(f"推送 {len(tasks)} 个任务到分布式队列")
        self.runner.push_tasks(tasks)
        
        log.info("任务分发完成")
    
    def wait_for_completion(self, timeout: int = 3600, check_interval: int = 5):
        """
        等待所有任务完成
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
        """
        log.info("=" * 60)
        log.info("等待测试执行完成")
        log.info("=" * 60)
        
        self.start_time = time.time()
        last_queue_size = -1
        no_change_count = 0
        
        while True:
            elapsed = time.time() - self.start_time
            
            # 检查超时
            if elapsed > timeout:
                log.error(f"等待超时 ({timeout}秒)")
                break
            
            # 获取队列大小
            queue_size = self.runner.get_queue_size()
            
            # 获取活跃节点
            active_nodes = self.runner.get_active_nodes()
            
            # 显示进度
            log.info(f"进度 - 剩余任务: {queue_size}, 活跃节点: {len(active_nodes)}, 已用时: {elapsed:.1f}s")
            
            # 检查是否完成
            if queue_size == 0:
                # 等待一段时间确保所有节点完成
                if no_change_count >= 3:
                    log.info("所有任务已完成")
                    break
                no_change_count += 1
            else:
                no_change_count = 0
            
            # 检查是否有节点在工作
            if queue_size > 0 and len(active_nodes) == 0:
                log.warning("没有活跃的工作节点，但仍有任务待执行")
            
            last_queue_size = queue_size
            time.sleep(check_interval)
        
        self.end_time = time.time()
    
    def collect_results(self) -> List[Dict[str, Any]]:
        """收集测试结果"""
        log.info("=" * 60)
        log.info("收集测试结果")
        log.info("=" * 60)
        
        results = self.runner.get_all_results()
        
        log.info(f"收集到 {len(results)} 个测试结果")
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """
        生成测试报告
        
        Args:
            results: 测试结果列表
        """
        log.info("=" * 60)
        log.info("生成测试报告")
        log.info("=" * 60)
        
        # 统计结果
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        error = sum(1 for r in results if r.get("status") == "error")
        timeout = sum(1 for r in results if r.get("status") == "timeout")
        
        # 计算总时间
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # 按节点统计
        node_stats = {}
        for result in results:
            node_id = result.get("node_id", "unknown")
            if node_id not in node_stats:
                node_stats[node_id] = {"total": 0, "passed": 0, "failed": 0}
            node_stats[node_id]["total"] += 1
            if result.get("status") == "passed":
                node_stats[node_id]["passed"] += 1
            elif result.get("status") == "failed":
                node_stats[node_id]["failed"] += 1
        
        # 生成报告
        report = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "error": error,
                "timeout": timeout,
                "pass_rate": f"{(passed/total*100):.2f}%" if total > 0 else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None
            },
            "node_statistics": node_stats,
            "results": results
        }
        
        # 保存报告
        report_file = Path("reports/distributed_test_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        log.info(f"报告已保存: {report_file}")
        
        # 打印摘要
        log.info("=" * 60)
        log.info("测试执行摘要")
        log.info("=" * 60)
        log.info(f"总测试数: {total}")
        log.info(f"通过: {passed} ({(passed/total*100):.1f}%)" if total > 0 else "通过: 0")
        log.info(f"失败: {failed}")
        log.info(f"错误: {error}")
        log.info(f"超时: {timeout}")
        log.info(f"总耗时: {total_duration:.2f}s")
        log.info(f"参与节点: {len(node_stats)}")
        
        # 打印节点统计
        log.info("\n节点统计:")
        for node_id, stats in node_stats.items():
            log.info(f"  {node_id}: {stats['total']} 测试 ({stats['passed']} 通过, {stats['failed']} 失败)")
        
        # 打印失败的测试
        if failed > 0 or error > 0:
            log.info("\n失败的测试:")
            for result in results:
                if result.get("status") in ["failed", "error"]:
                    log.error(f"  ❌ {result.get('full_name', result.get('test_name'))}")
                    if result.get("error"):
                        log.error(f"     错误: {result['error']}")
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="分布式测试控制器")
    parser.add_argument(
        "--mode",
        choices=["controller", "worker"],
        default="controller",
        help="运行模式: controller(控制器) 或 worker(工作节点)"
    )
    parser.add_argument(
        "--env",
        default="dev",
        help="测试环境 (dev/staging/prod)"
    )
    parser.add_argument(
        "--type",
        help="测试类型 (api/web/smoke/regression)"
    )
    parser.add_argument(
        "--markers",
        help="pytest标记，逗号分隔"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="等待超时时间（秒）"
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        help="工作节点最大执行任务数"
    )
    
    args = parser.parse_args()
    
    # 设置环境
    os.environ['TEST_ENV'] = args.env
    
    # 加载配置
    try:
        config.load_config(args.env)
        log.info(f"配置加载成功: {args.env}")
    except Exception as e:
        log.warning(f"配置加载失败: {e}")
    
    if args.mode == "controller":
        # 控制器模式
        log.info("=" * 60)
        log.info("分布式测试控制器启动")
        log.info("=" * 60)
        
        controller = DistributedTestController()
        
        # 解析标记
        markers = args.markers.split(",") if args.markers else None
        
        # 收集并分发测试
        controller.collect_and_distribute_tests(markers=markers, test_type=args.type)
        
        # 等待完成
        controller.wait_for_completion(timeout=args.timeout)
        
        # 收集结果
        results = controller.collect_results()
        
        # 生成报告
        report = controller.generate_report(results)
        
        # 返回退出码
        if report["summary"]["failed"] > 0 or report["summary"]["error"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    
    elif args.mode == "worker":
        # 工作节点模式
        log.info("=" * 60)
        log.info("分布式测试工作节点启动")
        log.info("=" * 60)
        
        runner = DistributedTestRunner()
        
        try:
            runner.run_worker(max_tasks=args.max_tasks)
        except KeyboardInterrupt:
            log.info("工作节点被中断")
        except Exception as e:
            log.error(f"工作节点异常: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

