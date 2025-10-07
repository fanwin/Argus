"""
测试收集器
收集和分析测试用例，用于分布式执行
"""

import os
import ast
import json
import hashlib
from typing import List, Dict, Any, Set
from pathlib import Path
from loguru import logger as log


class TestCollector:
    """测试收集器"""
    
    def __init__(self, test_dir: str = "tests"):
        """
        初始化测试收集器
        
        Args:
            test_dir: 测试目录
        """
        self.test_dir = Path(test_dir)
        self.tests = []
        
    def collect_tests(self, markers: List[str] = None, test_type: str = None) -> List[Dict[str, Any]]:
        """
        收集测试用例
        
        Args:
            markers: pytest标记过滤
            test_type: 测试类型 (api, web, etc.)
            
        Returns:
            测试用例列表
        """
        log.info(f"开始收集测试用例 - 目录: {self.test_dir}")
        
        self.tests = []
        
        # 遍历测试文件
        for test_file in self.test_dir.rglob("test_*.py"):
            if self._should_skip_file(test_file):
                continue
            
            # 解析测试文件
            file_tests = self._parse_test_file(test_file)
            
            # 过滤测试
            if markers or test_type:
                file_tests = self._filter_tests(file_tests, markers, test_type)
            
            self.tests.extend(file_tests)
        
        log.info(f"收集到 {len(self.tests)} 个测试用例")
        return self.tests
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        # 跳过__pycache__等目录
        if "__pycache__" in str(file_path):
            return True
        
        # 跳过conftest.py
        if file_path.name == "conftest.py":
            return True
        
        return False
    
    def _parse_test_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        解析测试文件
        
        Args:
            file_path: 测试文件路径
            
        Returns:
            测试用例列表
        """
        tests = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 遍历AST节点
            for node in ast.walk(tree):
                # 查找测试函数
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_info = self._extract_test_info(node, file_path)
                    tests.append(test_info)
                
                # 查找测试类
                elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            test_info = self._extract_test_info(item, file_path, node.name)
                            tests.append(test_info)
        
        except Exception as e:
            log.error(f"解析测试文件失败: {file_path} - {e}")
        
        return tests
    
    def _extract_test_info(self, node: ast.FunctionDef, file_path: Path, class_name: str = None) -> Dict[str, Any]:
        """
        提取测试信息
        
        Args:
            node: AST函数节点
            file_path: 文件路径
            class_name: 类名（如果有）
            
        Returns:
            测试信息字典
        """
        # 构建测试名称
        if class_name:
            test_name = f"{class_name}::{node.name}"
        else:
            test_name = node.name
        
        # 提取装饰器（markers）
        markers = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr'):
                    markers.append(decorator.func.attr)
            elif isinstance(decorator, ast.Attribute):
                markers.append(decorator.attr)
        
        # 提取文档字符串
        docstring = ast.get_docstring(node) or ""
        
        # 生成唯一ID
        test_id = self._generate_test_id(file_path, test_name)
        
        # 相对路径
        rel_path = file_path.relative_to(Path.cwd())
        
        return {
            "test_id": test_id,
            "test_file": str(rel_path),
            "test_name": test_name,
            "full_name": f"{rel_path}::{test_name}",
            "class_name": class_name,
            "function_name": node.name,
            "markers": markers,
            "docstring": docstring,
            "line_number": node.lineno
        }
    
    def _generate_test_id(self, file_path: Path, test_name: str) -> str:
        """生成测试唯一ID"""
        unique_str = f"{file_path}::{test_name}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
    
    def _filter_tests(self, tests: List[Dict[str, Any]], markers: List[str] = None, test_type: str = None) -> List[Dict[str, Any]]:
        """
        过滤测试用例
        
        Args:
            tests: 测试列表
            markers: 标记过滤
            test_type: 测试类型
            
        Returns:
            过滤后的测试列表
        """
        filtered = tests
        
        # 按标记过滤
        if markers:
            filtered = [
                t for t in filtered
                if any(m in t["markers"] for m in markers)
            ]
        
        # 按测试类型过滤
        if test_type:
            filtered = [
                t for t in filtered
                if test_type in t["markers"] or test_type in t["test_file"]
            ]
        
        return filtered
    
    def group_tests_by_file(self) -> Dict[str, List[Dict[str, Any]]]:
        """按文件分组测试"""
        groups = {}
        for test in self.tests:
            file_path = test["test_file"]
            if file_path not in groups:
                groups[file_path] = []
            groups[file_path].append(test)
        return groups
    
    def group_tests_by_marker(self) -> Dict[str, List[Dict[str, Any]]]:
        """按标记分组测试"""
        groups = {}
        for test in self.tests:
            for marker in test["markers"]:
                if marker not in groups:
                    groups[marker] = []
                groups[marker].append(test)
        return groups
    
    def estimate_test_duration(self, test: Dict[str, Any]) -> float:
        """
        估算测试执行时间
        
        Args:
            test: 测试信息
            
        Returns:
            估算时间（秒）
        """
        # 基础时间
        base_time = 5.0
        
        # 根据标记调整
        if "slow" in test["markers"]:
            base_time *= 3
        if "integration" in test["markers"]:
            base_time *= 2
        if "web" in test["markers"]:
            base_time *= 1.5
        if "api" in test["markers"]:
            base_time *= 0.8
        
        return base_time
    
    def balance_tests(self, num_workers: int) -> List[List[Dict[str, Any]]]:
        """
        平衡分配测试到多个工作节点
        
        Args:
            num_workers: 工作节点数量
            
        Returns:
            分配后的测试列表
        """
        if not self.tests:
            return [[] for _ in range(num_workers)]
        
        # 估算每个测试的执行时间
        test_durations = [
            (test, self.estimate_test_duration(test))
            for test in self.tests
        ]
        
        # 按执行时间降序排序
        test_durations.sort(key=lambda x: x[1], reverse=True)
        
        # 初始化工作节点
        workers = [{"tests": [], "total_time": 0} for _ in range(num_workers)]
        
        # 贪心算法分配测试
        for test, duration in test_durations:
            # 找到总时间最少的工作节点
            min_worker = min(workers, key=lambda w: w["total_time"])
            min_worker["tests"].append(test)
            min_worker["total_time"] += duration
        
        # 返回测试列表
        result = [w["tests"] for w in workers]
        
        # 打印分配信息
        for i, worker in enumerate(workers):
            log.info(f"Worker {i}: {len(worker['tests'])} tests, 估算时间: {worker['total_time']:.1f}s")
        
        return result
    
    def create_tasks(self, priority: str = "normal") -> List[Dict[str, Any]]:
        """
        创建分布式任务
        
        Args:
            priority: 任务优先级
            
        Returns:
            任务列表
        """
        tasks = []
        
        for test in self.tests:
            task = {
                "task_id": test["test_id"],
                "test_file": test["test_file"],
                "test_name": test["test_name"],
                "full_name": test["full_name"],
                "markers": test["markers"],
                "priority": priority,
                "timeout": 300,  # 默认5分钟超时
                "retry_count": 0,
                "max_retries": 2,
                "created_at": None  # 将在推送时设置
            }
            
            # 根据标记调整超时时间
            if "slow" in test["markers"]:
                task["timeout"] = 600
            if "integration" in test["markers"]:
                task["timeout"] = 900
            
            tasks.append(task)
        
        return tasks
    
    def save_tests_to_file(self, output_file: str = "collected_tests.json"):
        """保存收集的测试到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.tests, f, indent=2, ensure_ascii=False)
            log.info(f"测试列表已保存到: {output_file}")
        except Exception as e:
            log.error(f"保存测试列表失败: {e}")
    
    def load_tests_from_file(self, input_file: str = "collected_tests.json"):
        """从文件加载测试"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.tests = json.load(f)
            log.info(f"从文件加载 {len(self.tests)} 个测试")
        except Exception as e:
            log.error(f"加载测试列表失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取测试统计信息"""
        stats = {
            "total_tests": len(self.tests),
            "by_file": {},
            "by_marker": {},
            "by_type": {}
        }
        
        # 按文件统计
        for test in self.tests:
            file_path = test["test_file"]
            stats["by_file"][file_path] = stats["by_file"].get(file_path, 0) + 1
        
        # 按标记统计
        for test in self.tests:
            for marker in test["markers"]:
                stats["by_marker"][marker] = stats["by_marker"].get(marker, 0) + 1
        
        return stats


# 全局实例
test_collector = TestCollector()

