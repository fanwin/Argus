"""
API客户端工具类
封装requests库，提供统一的API测试接口
"""

import json
import time
from typing import Dict, Any, Optional, Union
import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from utilities.logger import log
from utilities.config_reader import config


class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str = None, headers: Dict[str, str] = None):
        """
        初始化API客户端

        Args:
            base_url: API基础URL
            headers: 默认请求头
        """
        self.session = requests.Session()
        self._initialized = False
        self._base_url = base_url
        self._headers = headers

        # 延迟初始化，等待配置加载
        if base_url is not None:
            self._initialize_with_config()

    def _initialize_with_config(self):
        """使用配置初始化客户端"""
        if self._initialized:
            return

        try:
            # 从配置获取API设置
            api_config = config.get_api_config()

            self.base_url = self._base_url or api_config.get("base_url", "")
            self.timeout = api_config.get("timeout", 30)
            self.retry_count = api_config.get("retry_count", 3)
            self.retry_delay = api_config.get("retry_delay", 1)

            # 设置默认请求头
            default_headers = api_config.get("headers", {})
            if self._headers:
                default_headers.update(self._headers)
            self.session.headers.update(default_headers)

            # 设置认证
            self._setup_auth(api_config.get("auth", {}))

            self._initialized = True
            log.info(f"API客户端初始化完成，基础URL: {self.base_url}")

        except RuntimeError:
            # 配置未加载，使用默认值
            self.base_url = self._base_url or ""
            self.timeout = 30
            self.retry_count = 3
            self.retry_delay = 1

            if self._headers:
                self.session.headers.update(self._headers)

            self._initialized = True
            log.debug("API客户端使用默认配置初始化")
    
    def _setup_auth(self, auth_config: Dict[str, Any]):
        """设置认证"""
        auth_type = auth_config.get("type", "").lower()
        
        if auth_type == "bearer" and auth_config.get("token"):
            self.session.headers["Authorization"] = f"Bearer {auth_config['token']}"
            log.debug("设置Bearer Token认证")
            
        elif auth_type == "basic" and auth_config.get("username") and auth_config.get("password"):
            self.session.auth = HTTPBasicAuth(auth_config["username"], auth_config["password"])
            log.debug("设置Basic认证")
            
        elif auth_type == "oauth2":
            # OAuth2认证需要额外配置
            log.debug("OAuth2认证需要额外配置")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        # 确保已初始化
        self._initialize_with_config()

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # 设置超时
        kwargs.setdefault("timeout", self.timeout)
        
        # 重试机制
        last_exception = None
        for attempt in range(self.retry_count + 1):
            try:
                log.debug(f"发送{method.upper()}请求: {url} (尝试 {attempt + 1}/{self.retry_count + 1})")
                
                response = self.session.request(method, url, **kwargs)
                
                log.info(f"{method.upper()} {url} - 状态码: {response.status_code}")
                log.debug(f"响应头: {dict(response.headers)}")
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                log.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry_count + 1}): {e}")
                
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    break
        
        log.error(f"请求最终失败: {last_exception}")
        raise last_exception
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Union[Dict, str] = None, json_data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """发送POST请求"""
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = data
        return self._make_request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, data: Union[Dict, str] = None, json_data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """发送PUT请求"""
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = data
        return self._make_request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Union[Dict, str] = None, json_data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """发送PATCH请求"""
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = data
        return self._make_request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def set_auth_token(self, token: str):
        """设置认证令牌"""
        self.session.headers["Authorization"] = f"Bearer {token}"
        log.debug("更新Bearer Token")
    
    def remove_auth(self):
        """移除认证"""
        self.session.headers.pop("Authorization", None)
        self.session.auth = None
        log.debug("移除认证信息")
    
    def update_headers(self, headers: Dict[str, str]):
        """更新请求头"""
        self.session.headers.update(headers)
        log.debug(f"更新请求头: {headers}")
    
    def get_response_json(self, response: requests.Response) -> Dict[str, Any]:
        """获取响应JSON数据"""
        try:
            return response.json()
        except json.JSONDecodeError as e:
            log.error(f"解析JSON响应失败: {e}")
            log.debug(f"响应内容: {response.text}")
            raise
    
    def assert_status_code(self, response: requests.Response, expected_code: int):
        """断言状态码"""
        actual_code = response.status_code
        if actual_code != expected_code:
            log.error(f"状态码断言失败: 期望 {expected_code}, 实际 {actual_code}")
            log.debug(f"响应内容: {response.text}")
            raise AssertionError(f"期望状态码 {expected_code}, 实际 {actual_code}")
        log.debug(f"状态码断言成功: {actual_code}")
    
    def assert_response_contains(self, response: requests.Response, expected_text: str):
        """断言响应包含指定文本"""
        response_text = response.text
        if expected_text not in response_text:
            log.error(f"响应内容断言失败: 未找到 '{expected_text}'")
            log.debug(f"响应内容: {response_text}")
            raise AssertionError(f"响应中未找到 '{expected_text}'")
        log.debug(f"响应内容断言成功: 找到 '{expected_text}'")


# 创建全局API客户端实例
api_client = APIClient()
