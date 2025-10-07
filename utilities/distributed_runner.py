"""
分布式测试运行器
支持跨多台机器分布式执行测试
"""

import os
import json
import time
import socket
import hashlib
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import redis
from loguru import logger as log


class DistributedTestRunner:
    """分布式测试运行器"""
    
    def __init__(self, redis_host: str = None, redis_port: int = None, redis_password: str = None):
        """
        初始化分布式测试运行器
        
        Args:
            redis_host: Redis服务器地址
            redis_port: Redis端口
            redis_password: Redis密码
        """
        self.redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        self.redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = redis_password or os.getenv("REDIS_PASSWORD", "")
        
        # 连接Redis
        self.redis_client = self._connect_redis()
        
        # 节点信息
        self.node_id = self._generate_node_id()
        self.node_info = {
            "node_id": self.node_id,
            "hostname": socket.gethostname(),
            "ip": self._get_local_ip(),
            "status": "idle",
            "started_at": datetime.now().isoformat(),
            "tests_executed": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
        
        # 任务队列键
        self.task_queue_key = "argus:distributed:task_queue"
        self.result_queue_key = "argus:distributed:result_queue"
        self.node_registry_key = "argus:distributed:nodes"
        self.lock_key_prefix = "argus:distributed:lock:"
        
        # 心跳线程
        self.heartbeat_thread = None
        self.running = False
        
        log.info(f"分布式测试运行器初始化完成 - 节点ID: {self.node_id}")
    
    def _connect_redis(self) -> redis.Redis:
        """连接Redis服务器"""
        try:
            client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password if self.redis_password else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            client.ping()
            log.info(f"成功连接到Redis服务器: {self.redis_host}:{self.redis_port}")
            return client
        except Exception as e:
            log.error(f"连接Redis失败: {e}")
            raise
    
    def _generate_node_id(self) -> str:
        """生成唯一的节点ID"""
        hostname = socket.gethostname()
        timestamp = str(time.time())
        unique_str = f"{hostname}_{timestamp}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
    def _get_local_ip(self) -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def register_node(self):
        """注册节点到集群"""
        try:
            node_key = f"{self.node_registry_key}:{self.node_id}"
            self.redis_client.hset(node_key, mapping=self.node_info)
            self.redis_client.expire(node_key, 300)  # 5分钟过期
            log.info(f"节点已注册: {self.node_id}")
        except Exception as e:
            log.error(f"注册节点失败: {e}")
    
    def unregister_node(self):
        """注销节点"""
        try:
            node_key = f"{self.node_registry_key}:{self.node_id}"
            self.redis_client.delete(node_key)
            log.info(f"节点已注销: {self.node_id}")
        except Exception as e:
            log.error(f"注销节点失败: {e}")
    
    def update_node_status(self, status: str, **kwargs):
        """更新节点状态"""
        try:
            self.node_info["status"] = status
            self.node_info["last_update"] = datetime.now().isoformat()
            self.node_info.update(kwargs)
            
            node_key = f"{self.node_registry_key}:{self.node_id}"
            self.redis_client.hset(node_key, mapping=self.node_info)
            self.redis_client.expire(node_key, 300)
        except Exception as e:
            log.error(f"更新节点状态失败: {e}")
    
    def start_heartbeat(self, interval: int = 30):
        """启动心跳线程"""
        def heartbeat():
            while self.running:
                try:
                    self.update_node_status(self.node_info["status"])
                    time.sleep(interval)
                except Exception as e:
                    log.error(f"心跳发送失败: {e}")
        
        self.running = True
        self.heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        self.heartbeat_thread.start()
        log.info("心跳线程已启动")
    
    def stop_heartbeat(self):
        """停止心跳线程"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        log.info("心跳线程已停止")
    
    def push_task(self, task: Dict[str, Any]):
        """推送任务到队列"""
        try:
            task_json = json.dumps(task)
            self.redis_client.rpush(self.task_queue_key, task_json)
            log.info(f"任务已推送: {task.get('task_id', 'unknown')}")
        except Exception as e:
            log.error(f"推送任务失败: {e}")
            raise
    
    def push_tasks(self, tasks: List[Dict[str, Any]]):
        """批量推送任务"""
        try:
            pipeline = self.redis_client.pipeline()
            for task in tasks:
                task_json = json.dumps(task)
                pipeline.rpush(self.task_queue_key, task_json)
            pipeline.execute()
            log.info(f"批量推送 {len(tasks)} 个任务")
        except Exception as e:
            log.error(f"批量推送任务失败: {e}")
            raise
    
    def pop_task(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """从队列获取任务"""
        try:
            result = self.redis_client.blpop(self.task_queue_key, timeout=timeout)
            if result:
                _, task_json = result
                task = json.loads(task_json)
                log.debug(f"获取任务: {task.get('task_id', 'unknown')}")
                return task
            return None
        except Exception as e:
            log.error(f"获取任务失败: {e}")
            return None
    
    def push_result(self, result: Dict[str, Any]):
        """推送测试结果"""
        try:
            result_json = json.dumps(result)
            self.redis_client.rpush(self.result_queue_key, result_json)
            log.debug(f"结果已推送: {result.get('task_id', 'unknown')}")
        except Exception as e:
            log.error(f"推送结果失败: {e}")
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """获取所有测试结果"""
        try:
            results = []
            while True:
                result_json = self.redis_client.lpop(self.result_queue_key)
                if not result_json:
                    break
                results.append(json.loads(result_json))
            return results
        except Exception as e:
            log.error(f"获取结果失败: {e}")
            return []
    
    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """获取分布式锁"""
        lock_key = f"{self.lock_key_prefix}{lock_name}"
        try:
            return self.redis_client.set(
                lock_key,
                self.node_id,
                nx=True,
                ex=timeout
            )
        except Exception as e:
            log.error(f"获取锁失败: {e}")
            return False
    
    def release_lock(self, lock_name: str):
        """释放分布式锁"""
        lock_key = f"{self.lock_key_prefix}{lock_name}"
        try:
            # 只有持有锁的节点才能释放
            if self.redis_client.get(lock_key) == self.node_id:
                self.redis_client.delete(lock_key)
        except Exception as e:
            log.error(f"释放锁失败: {e}")
    
    def get_active_nodes(self) -> List[Dict[str, Any]]:
        """获取所有活跃节点"""
        try:
            nodes = []
            pattern = f"{self.node_registry_key}:*"
            for key in self.redis_client.scan_iter(match=pattern):
                node_info = self.redis_client.hgetall(key)
                if node_info:
                    nodes.append(node_info)
            return nodes
        except Exception as e:
            log.error(f"获取活跃节点失败: {e}")
            return []
    
    def get_queue_size(self) -> int:
        """获取任务队列大小"""
        try:
            return self.redis_client.llen(self.task_queue_key)
        except Exception as e:
            log.error(f"获取队列大小失败: {e}")
            return 0
    
    def clear_queue(self):
        """清空任务队列"""
        try:
            self.redis_client.delete(self.task_queue_key)
            self.redis_client.delete(self.result_queue_key)
            log.info("任务队列已清空")
        except Exception as e:
            log.error(f"清空队列失败: {e}")
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个测试任务
        
        Args:
            task: 任务信息
            
        Returns:
            执行结果
        """
        task_id = task.get("task_id", "unknown")
        test_file = task.get("test_file", "")
        test_name = task.get("test_name", "")
        
        log.info(f"开始执行任务: {task_id} - {test_file}::{test_name}")
        
        start_time = time.time()
        result = {
            "task_id": task_id,
            "node_id": self.node_id,
            "test_file": test_file,
            "test_name": test_name,
            "status": "unknown",
            "start_time": datetime.now().isoformat(),
            "duration": 0,
            "error": None
        }
        
        try:
            # 更新节点状态
            self.update_node_status("running", current_task=task_id)
            
            # 执行pytest命令
            import subprocess
            cmd = [
                "pytest",
                f"{test_file}::{test_name}",
                "-v",
                "--tb=short",
                f"--alluredir=reports/allure-results/{self.node_id}",
                f"--html=reports/node-{self.node_id}-{task_id}.html",
                "--self-contained-html"
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=task.get("timeout", 300)
            )
            
            result["status"] = "passed" if process.returncode == 0 else "failed"
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            result["return_code"] = process.returncode
            
            # 更新节点统计
            if result["status"] == "passed":
                self.node_info["tests_passed"] += 1
            else:
                self.node_info["tests_failed"] += 1
            self.node_info["tests_executed"] += 1
            
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "测试执行超时"
            log.error(f"任务超时: {task_id}")
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            log.error(f"任务执行失败: {task_id} - {e}")
        finally:
            result["duration"] = time.time() - start_time
            result["end_time"] = datetime.now().isoformat()
            self.update_node_status("idle")
        
        log.info(f"任务完成: {task_id} - 状态: {result['status']} - 耗时: {result['duration']:.2f}s")
        return result
    
    def run_worker(self, max_tasks: int = None):
        """
        运行工作节点
        
        Args:
            max_tasks: 最大执行任务数，None表示无限制
        """
        log.info(f"工作节点启动: {self.node_id}")
        
        # 注册节点
        self.register_node()
        
        # 启动心跳
        self.start_heartbeat()
        
        tasks_executed = 0
        
        try:
            while True:
                # 检查是否达到最大任务数
                if max_tasks and tasks_executed >= max_tasks:
                    log.info(f"已达到最大任务数: {max_tasks}")
                    break
                
                # 获取任务
                task = self.pop_task(timeout=5)
                
                if task:
                    # 执行任务
                    result = self.execute_task(task)
                    
                    # 推送结果
                    self.push_result(result)
                    
                    tasks_executed += 1
                else:
                    # 没有任务，等待
                    log.debug("等待新任务...")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            log.info("收到中断信号，停止工作节点")
        finally:
            # 停止心跳
            self.stop_heartbeat()
            
            # 注销节点
            self.unregister_node()
            
            log.info(f"工作节点已停止: {self.node_id} - 执行任务数: {tasks_executed}")


# 全局实例
distributed_runner = DistributedTestRunner()

