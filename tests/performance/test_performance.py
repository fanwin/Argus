"""
性能测试案例
展示性能测试功能：负载测试、压力测试、API性能测试等
"""

import pytest
import allure
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from utilities.performance_tester import PerformanceTester, performance_test
from utilities.api_client import APIClient
from utilities.logger import log


@allure.epic("性能测试")
@allure.feature("系统性能验证")
class TestPerformance:
    """性能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_performance_test(self):
        """设置性能测试环境"""
        self.performance_tester = PerformanceTester()
        self.api_client = APIClient()
        
        # 使用httpbin.org作为测试目标
        self.test_urls = {
            "simple_get": "https://httpbin.org/get",
            "json_response": "https://httpbin.org/json",
            "delay_1s": "https://httpbin.org/delay/1",
            "delay_2s": "https://httpbin.org/delay/2",
            "large_response": "https://httpbin.org/base64/SFRUUEJJTiBpcyBhd2Vzb21l" * 10
        }
        
        log.info("性能测试环境初始化完成")
    
    @allure.story("API性能基准测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.performance
    @pytest.mark.api
    def test_api_performance_baseline(self):
        """测试API性能基准"""
        
        with allure.step("单个API请求性能测试"):
            url = self.test_urls["simple_get"]
            
            # 测量单个请求性能
            metrics = self.performance_tester.measure_api_performance(url)
            
            # 验证性能指标
            assert metrics.response_time < 5000, f"响应时间过长: {metrics.response_time}ms"
            assert metrics.status_code == 200, f"状态码异常: {metrics.status_code}"
            
            log.info(f"API性能基准 - 响应时间: {metrics.response_time}ms, 状态码: {metrics.status_code}")
            
            # 添加性能数据到报告
            allure.attach(
                f"响应时间: {metrics.response_time}ms\n状态码: {metrics.status_code}\n响应大小: {metrics.response_size}字节",
                name="API性能基准数据",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("API负载测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.performance
    @pytest.mark.slow
    def test_api_load_testing(self):
        """测试API负载能力"""
        
        with allure.step("执行负载测试"):
            url = self.test_urls["simple_get"]
            concurrent_users = 5  # 并发用户数
            total_requests = 20   # 总请求数
            
            log.info(f"开始负载测试: {concurrent_users}并发用户, {total_requests}总请求")
            
            # 执行负载测试
            report = self.performance_tester.load_test_api(
                url=url,
                concurrent_users=concurrent_users,
                total_requests=total_requests
            )
            
            # 验证负载测试结果
            assert report.success_rate >= 0.9, f"成功率过低: {report.success_rate:.2%}"
            assert report.avg_response_time < 10000, f"平均响应时间过长: {report.avg_response_time}ms"
            
            log.info(f"负载测试完成 - 成功率: {report.success_rate:.2%}, 平均响应时间: {report.avg_response_time}ms")
        
        with allure.step("分析性能数据"):
            # 生成详细的性能报告
            performance_summary = f"""
负载测试报告:
- 并发用户数: {concurrent_users}
- 总请求数: {total_requests}
- 成功请求数: {report.successful_requests}
- 失败请求数: {report.failed_requests}
- 成功率: {report.success_rate:.2%}
- 平均响应时间: {report.avg_response_time:.2f}ms
- 最小响应时间: {report.min_response_time:.2f}ms
- 最大响应时间: {report.max_response_time:.2f}ms
- 95%响应时间: {report.percentile_95:.2f}ms
- 99%响应时间: {report.percentile_99:.2f}ms
- 吞吐量: {report.throughput:.2f} 请求/秒
            """
            
            allure.attach(
                performance_summary,
                name="负载测试详细报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 保存性能测试报告
            self.performance_tester.save_performance_report(report, "load_test_report.json")
    
    @allure.story("压力测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.performance
    @pytest.mark.slow
    def test_stress_testing(self):
        """测试系统压力极限"""
        
        with allure.step("执行压力测试"):
            url = self.test_urls["simple_get"]
            
            # 逐步增加负载的压力测试
            stress_reports = self.performance_tester.stress_test_api(
                url=url,
                max_users=10,
                duration_seconds=30,
                user_increment=2
            )
            
            assert len(stress_reports) > 0, "压力测试应该产生报告"
            
            log.info(f"压力测试完成，生成了 {len(stress_reports)} 个阶段报告")
        
        with allure.step("分析压力测试结果"):
            # 分析不同负载下的性能表现
            performance_degradation = []
            
            for i, report in enumerate(stress_reports):
                user_count = getattr(report, 'concurrent_users', i + 1)
                performance_degradation.append({
                    'users': user_count,
                    'avg_response_time': report.avg_response_time,
                    'success_rate': report.success_rate,
                    'throughput': report.throughput
                })
            
            # 检查性能退化
            if len(performance_degradation) >= 2:
                first_stage = performance_degradation[0]
                last_stage = performance_degradation[-1]
                
                response_time_increase = (last_stage['avg_response_time'] - first_stage['avg_response_time']) / first_stage['avg_response_time']
                success_rate_decrease = first_stage['success_rate'] - last_stage['success_rate']
                
                log.info(f"性能退化分析: 响应时间增加 {response_time_increase:.2%}, 成功率下降 {success_rate_decrease:.2%}")
                
                # 性能退化警告
                if response_time_increase > 2.0:  # 响应时间增加超过200%
                    log.warning(f"响应时间严重退化: {response_time_increase:.2%}")
                
                if success_rate_decrease > 0.1:  # 成功率下降超过10%
                    log.warning(f"成功率显著下降: {success_rate_decrease:.2%}")
            
            # 生成压力测试报告
            stress_summary = "压力测试阶段报告:\n"
            for stage in performance_degradation:
                stress_summary += f"用户数: {stage['users']}, 响应时间: {stage['avg_response_time']:.2f}ms, 成功率: {stage['success_rate']:.2%}, 吞吐量: {stage['throughput']:.2f}\n"
            
            allure.attach(
                stress_summary,
                name="压力测试阶段报告",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("批量API性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.performance
    def test_batch_api_performance(self):
        """测试多个API端点的性能"""
        
        with allure.step("准备API端点列表"):
            endpoints = [
                {
                    "name": "简单GET请求",
                    "url": self.test_urls["simple_get"],
                    "method": "GET",
                    "concurrent_users": 3,
                    "total_requests": 10
                },
                {
                    "name": "JSON响应",
                    "url": self.test_urls["json_response"],
                    "method": "GET",
                    "concurrent_users": 3,
                    "total_requests": 10
                },
                {
                    "name": "1秒延迟",
                    "url": self.test_urls["delay_1s"],
                    "method": "GET",
                    "concurrent_users": 2,
                    "total_requests": 6
                }
            ]
            
            log.info(f"准备测试 {len(endpoints)} 个API端点")
        
        with allure.step("执行批量性能测试"):
            results = self.performance_tester.benchmark_api_endpoints(endpoints)
            
            assert len(results) > 0, "批量测试应该产生结果"
            
            log.info(f"批量测试完成，测试了 {len(results)} 个端点")
        
        with allure.step("分析批量测试结果"):
            performance_comparison = []
            
            for endpoint_name, report in results.items():
                performance_comparison.append({
                    'name': endpoint_name,
                    'avg_response_time': report.avg_response_time,
                    'success_rate': report.success_rate,
                    'throughput': report.throughput,
                    'percentile_95': report.percentile_95
                })
            
            # 按响应时间排序
            performance_comparison.sort(key=lambda x: x['avg_response_time'])
            
            # 生成性能对比报告
            comparison_report = "API性能对比报告:\n"
            comparison_report += f"{'端点名称':<20} {'平均响应时间(ms)':<15} {'成功率':<10} {'吞吐量':<15} {'95%响应时间(ms)':<15}\n"
            comparison_report += "-" * 80 + "\n"
            
            for perf in performance_comparison:
                comparison_report += f"{perf['name']:<20} {perf['avg_response_time']:<15.2f} {perf['success_rate']:<10.2%} {perf['throughput']:<15.2f} {perf['percentile_95']:<15.2f}\n"
            
            allure.attach(
                comparison_report,
                name="API性能对比报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 找出性能最好和最差的端点
            fastest_endpoint = performance_comparison[0]
            slowest_endpoint = performance_comparison[-1]
            
            log.info(f"性能最佳端点: {fastest_endpoint['name']} ({fastest_endpoint['avg_response_time']:.2f}ms)")
            log.info(f"性能最差端点: {slowest_endpoint['name']} ({slowest_endpoint['avg_response_time']:.2f}ms)")
    
    @allure.story("性能装饰器测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.performance
    def test_performance_decorator(self):
        """测试性能装饰器功能"""
        
        @performance_test(threshold_ms=1000)
        def fast_operation():
            """快速操作"""
            time.sleep(0.1)
            return "快速操作完成"
        
        @performance_test(threshold_ms=500)
        def slow_operation():
            """慢速操作"""
            time.sleep(0.8)
            return "慢速操作完成"
        
        with allure.step("测试快速操作性能"):
            result = fast_operation()
            assert result == "快速操作完成"
            log.info("快速操作性能测试完成")
        
        with allure.step("测试慢速操作性能"):
            result = slow_operation()
            assert result == "慢速操作完成"
            log.info("慢速操作性能测试完成（可能有性能警告）")
    
    @allure.story("内存和资源监控")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.performance
    def test_resource_monitoring(self):
        """测试资源使用监控"""
        import psutil
        import os
        
        with allure.step("监控系统资源"):
            # 获取当前进程信息
            process = psutil.Process(os.getpid())
            
            # 记录初始资源使用
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu = process.cpu_percent()
            
            log.info(f"初始内存使用: {initial_memory:.2f}MB")
            log.info(f"初始CPU使用: {initial_cpu:.2f}%")
        
        with allure.step("执行资源密集型操作"):
            # 模拟一些内存和CPU密集型操作
            data_list = []
            for i in range(10000):
                data_list.append(f"测试数据_{i}" * 10)
            
            # 执行一些计算
            result = sum(len(item) for item in data_list)
            
            time.sleep(1)  # 等待资源统计更新
        
        with allure.step("检查资源使用变化"):
            # 记录操作后资源使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()
            
            memory_increase = final_memory - initial_memory
            cpu_change = final_cpu - initial_cpu
            
            log.info(f"最终内存使用: {final_memory:.2f}MB (增加: {memory_increase:.2f}MB)")
            log.info(f"最终CPU使用: {final_cpu:.2f}% (变化: {cpu_change:.2f}%)")
            
            # 资源使用报告
            resource_report = f"""
资源使用监控报告:
- 初始内存: {initial_memory:.2f}MB
- 最终内存: {final_memory:.2f}MB
- 内存增加: {memory_increase:.2f}MB
- 初始CPU: {initial_cpu:.2f}%
- 最终CPU: {final_cpu:.2f}%
- CPU变化: {cpu_change:.2f}%
- 处理数据量: {len(data_list)} 条记录
- 计算结果: {result}
            """
            
            allure.attach(
                resource_report,
                name="资源使用监控报告",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 清理内存
            del data_list
    
    @allure.story("网络性能测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.performance
    @pytest.mark.network
    def test_network_performance(self):
        """测试网络性能"""
        
        with allure.step("测试不同响应大小的性能"):
            # 测试不同大小的响应
            response_sizes = [
                ("小响应", self.test_urls["simple_get"]),
                ("JSON响应", self.test_urls["json_response"]),
                ("大响应", self.test_urls["large_response"])
            ]
            
            network_performance = []
            
            for size_name, url in response_sizes:
                try:
                    metrics = self.performance_tester.measure_api_performance(url)
                    
                    network_performance.append({
                        'size': size_name,
                        'response_time': metrics.response_time,
                        'response_size': metrics.response_size,
                        'throughput': metrics.response_size / (metrics.response_time / 1000) if metrics.response_time > 0 else 0  # 字节/秒
                    })
                    
                    log.info(f"{size_name} - 响应时间: {metrics.response_time}ms, 大小: {metrics.response_size}字节")
                    
                except Exception as e:
                    log.warning(f"{size_name}测试失败: {e}")
        
        with allure.step("分析网络性能"):
            if network_performance:
                # 生成网络性能报告
                network_report = "网络性能测试报告:\n"
                network_report += f"{'响应类型':<15} {'响应时间(ms)':<15} {'响应大小(字节)':<15} {'吞吐量(字节/秒)':<20}\n"
                network_report += "-" * 70 + "\n"
                
                for perf in network_performance:
                    network_report += f"{perf['size']:<15} {perf['response_time']:<15.2f} {perf['response_size']:<15} {perf['throughput']:<20.2f}\n"
                
                allure.attach(
                    network_report,
                    name="网络性能测试报告",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # 计算平均网络性能
                avg_response_time = statistics.mean([p['response_time'] for p in network_performance])
                total_data_transferred = sum([p['response_size'] for p in network_performance])
                
                log.info(f"平均响应时间: {avg_response_time:.2f}ms")
                log.info(f"总数据传输: {total_data_transferred}字节")
            else:
                log.warning("网络性能测试未产生有效数据")
