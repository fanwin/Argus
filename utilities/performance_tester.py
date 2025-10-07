"""
Performance Testing Utilities
性能测试工具类 - 提供Web性能、API性能和负载测试功能
"""

import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utilities.logger import log
from utilities.config_reader import config


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PerformanceReport:
    """性能测试报告数据类"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    percentile_95: float
    percentile_99: float
    throughput: float  # requests per second
    error_rate: float
    errors: List[str]


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.config = config.get_api_config()
    
    def measure_api_performance(
        self, 
        url: str, 
        method: str = "GET", 
        headers: Dict = None, 
        data: Dict = None,
        timeout: int = 30
    ) -> PerformanceMetrics:
        """测量单个API请求的性能"""
        start_time = time.time()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            return PerformanceMetrics(
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code < 400
            )
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return PerformanceMetrics(
                response_time=response_time,
                status_code=0,
                success=False,
                error_message=str(e)
            )
    
    def load_test_api(
        self,
        url: str,
        concurrent_users: int = 10,
        total_requests: int = 100,
        method: str = "GET",
        headers: Dict = None,
        data: Dict = None
    ) -> PerformanceReport:
        """API负载测试"""
        log.info(f"开始API负载测试: {url}")
        log.info(f"并发用户: {concurrent_users}, 总请求数: {total_requests}")
        
        metrics = []
        start_time = time.time()
        
        def make_request():
            return self.measure_api_performance(url, method, headers, data)
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(total_requests)]
            
            for future in as_completed(futures):
                try:
                    metric = future.result()
                    metrics.append(metric)
                except Exception as e:
                    log.error(f"请求执行失败: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return self._generate_performance_report(metrics, total_duration)
    
    def measure_page_load_performance(self, selenium_wrapper, url: str) -> Dict[str, float]:
        """测量页面加载性能"""
        log.info(f"测量页面加载性能: {url}")
        
        # 导航到页面并测量时间
        start_time = time.time()
        selenium_wrapper.driver.get(url)
        
        # 等待页面完全加载
        WebDriverWait(selenium_wrapper.driver, 30).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        end_time = time.time()
        page_load_time = (end_time - start_time) * 1000
        
        # 获取浏览器性能指标
        performance_metrics = selenium_wrapper.driver.execute_script("""
            var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
            var timing = performance.timing || {};
            return {
                navigationStart: timing.navigationStart,
                domainLookupStart: timing.domainLookupStart,
                domainLookupEnd: timing.domainLookupEnd,
                connectStart: timing.connectStart,
                connectEnd: timing.connectEnd,
                requestStart: timing.requestStart,
                responseStart: timing.responseStart,
                responseEnd: timing.responseEnd,
                domLoading: timing.domLoading,
                domInteractive: timing.domInteractive,
                domContentLoadedEventStart: timing.domContentLoadedEventStart,
                domContentLoadedEventEnd: timing.domContentLoadedEventEnd,
                loadEventStart: timing.loadEventStart,
                loadEventEnd: timing.loadEventEnd
            };
        """)
        
        # 计算各个阶段的时间
        if performance_metrics['navigationStart']:
            dns_time = performance_metrics['domainLookupEnd'] - performance_metrics['domainLookupStart']
            tcp_time = performance_metrics['connectEnd'] - performance_metrics['connectStart']
            request_time = performance_metrics['responseStart'] - performance_metrics['requestStart']
            response_time = performance_metrics['responseEnd'] - performance_metrics['responseStart']
            dom_processing_time = performance_metrics['domInteractive'] - performance_metrics['domLoading']
            
            return {
                'total_page_load_time': page_load_time,
                'dns_lookup_time': dns_time,
                'tcp_connection_time': tcp_time,
                'request_time': request_time,
                'response_time': response_time,
                'dom_processing_time': dom_processing_time,
                'dom_content_loaded_time': performance_metrics['domContentLoadedEventEnd'] - performance_metrics['navigationStart'],
                'load_event_time': performance_metrics['loadEventEnd'] - performance_metrics['navigationStart']
            }
        else:
            return {'total_page_load_time': page_load_time}
    
    def stress_test_api(
        self,
        url: str,
        duration_seconds: int = 60,
        initial_users: int = 1,
        max_users: int = 50,
        ramp_up_time: int = 30
    ) -> List[PerformanceReport]:
        """API压力测试 - 逐步增加负载"""
        log.info(f"开始API压力测试: {url}")
        log.info(f"测试时长: {duration_seconds}秒, 最大用户数: {max_users}")
        
        reports = []
        user_increment = max(1, (max_users - initial_users) // (ramp_up_time // 5))
        current_users = initial_users
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # 运行当前用户数的负载测试
            requests_per_batch = min(50, current_users * 5)
            report = self.load_test_api(
                url=url,
                concurrent_users=current_users,
                total_requests=requests_per_batch
            )
            
            report.concurrent_users = current_users
            reports.append(report)
            
            log.info(f"用户数: {current_users}, 平均响应时间: {report.avg_response_time:.2f}ms")
            
            # 增加用户数
            if current_users < max_users:
                current_users = min(max_users, current_users + user_increment)
            
            time.sleep(5)  # 短暂休息
        
        return reports
    
    def _generate_performance_report(self, metrics: List[PerformanceMetrics], duration: float) -> PerformanceReport:
        """生成性能测试报告"""
        if not metrics:
            return PerformanceReport(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [])
        
        successful_metrics = [m for m in metrics if m.success]
        failed_metrics = [m for m in metrics if not m.success]
        
        response_times = [m.response_time for m in successful_metrics]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            
            # 计算百分位数
            sorted_times = sorted(response_times)
            percentile_95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
            percentile_99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = 0
            percentile_95 = percentile_99 = 0
        
        throughput = len(metrics) / duration if duration > 0 else 0
        error_rate = len(failed_metrics) / len(metrics) * 100 if metrics else 0
        
        errors = [m.error_message for m in failed_metrics if m.error_message]
        
        return PerformanceReport(
            total_requests=len(metrics),
            successful_requests=len(successful_metrics),
            failed_requests=len(failed_metrics),
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            median_response_time=median_response_time,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            throughput=throughput,
            error_rate=error_rate,
            errors=errors
        )
    
    def benchmark_api_endpoints(self, endpoints: List[Dict]) -> Dict[str, PerformanceReport]:
        """批量测试多个API端点的性能"""
        log.info(f"开始批量API性能测试，共{len(endpoints)}个端点")
        
        results = {}
        
        for endpoint in endpoints:
            url = endpoint.get('url')
            name = endpoint.get('name', url)
            method = endpoint.get('method', 'GET')
            headers = endpoint.get('headers', {})
            data = endpoint.get('data', {})
            concurrent_users = endpoint.get('concurrent_users', 10)
            total_requests = endpoint.get('total_requests', 100)
            
            log.info(f"测试端点: {name}")
            
            try:
                report = self.load_test_api(
                    url=url,
                    concurrent_users=concurrent_users,
                    total_requests=total_requests,
                    method=method,
                    headers=headers,
                    data=data
                )
                results[name] = report
                
            except Exception as e:
                log.error(f"端点 {name} 测试失败: {e}")
        
        return results
    
    def save_performance_report(self, report: PerformanceReport, filename: str):
        """保存性能测试报告到文件"""
        import json
        from pathlib import Path
        
        reports_dir = Path("reports/performance")
        reports_dir.mkdir(exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_requests': report.total_requests,
            'successful_requests': report.successful_requests,
            'failed_requests': report.failed_requests,
            'avg_response_time': report.avg_response_time,
            'min_response_time': report.min_response_time,
            'max_response_time': report.max_response_time,
            'median_response_time': report.median_response_time,
            'percentile_95': report.percentile_95,
            'percentile_99': report.percentile_99,
            'throughput': report.throughput,
            'error_rate': report.error_rate,
            'errors': report.errors
        }
        
        with open(reports_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        log.info(f"性能测试报告已保存: {reports_dir / filename}")


# 性能测试装饰器
def performance_test(threshold_ms: float = 1000):
    """性能测试装饰器 - 用于标记和验证性能要求"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000
            
            if execution_time > threshold_ms:
                log.warning(f"性能警告: {func.__name__} 执行时间 {execution_time:.2f}ms 超过阈值 {threshold_ms}ms")
            else:
                log.info(f"性能正常: {func.__name__} 执行时间 {execution_time:.2f}ms")
            
            return result
        return wrapper
    return decorator
