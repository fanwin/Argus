"""
配置读取工具类
支持多环境配置切换和配置文件读取
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from utilities.logger import log


class ConfigReader:
    """配置读取器类"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置读取器"""
        self.config_dir = Path("configs")
        self.current_env = None
        
    def load_config(self, environment: str = None) -> Dict[str, Any]:
        """
        加载指定环境的配置
        
        Args:
            environment: 环境名称 (dev/staging/prod)
            
        Returns:
            配置字典
        """
        if environment is None:
            environment = os.getenv("TEST_ENV", "dev")
            
        config_file = self.config_dir / f"{environment}.yaml"
        
        if not config_file.exists():
            log.error(f"配置文件不存在: {config_file}")
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            log.info(f"成功加载配置文件: {config_file}")
            self._config = config
            self.current_env = environment
            
            # 从环境变量覆盖配置
            self._override_from_env(config)
            
            return config
            
        except yaml.YAMLError as e:
            log.error(f"解析配置文件失败: {e}")
            raise
        except Exception as e:
            log.error(f"读取配置文件失败: {e}")
            raise
    
    def _override_from_env(self, config: Dict[str, Any]):
        """从环境变量覆盖配置"""
        # API配置覆盖
        if api_url := os.getenv("API_BASE_URL"):
            config.setdefault("api", {})["base_url"] = api_url

        if api_token := os.getenv("API_TOKEN"):
            config.setdefault("api", {}).setdefault("auth", {})["token"] = api_token

        if api_username := os.getenv("API_USERNAME"):
            config.setdefault("api", {}).setdefault("auth", {})["username"] = api_username

        if api_password := os.getenv("API_PASSWORD"):
            config.setdefault("api", {}).setdefault("auth", {})["password"] = api_password

        if api_key := os.getenv("API_KEY"):
            config.setdefault("api", {}).setdefault("auth", {})["api_key"] = api_key

        if jwt_secret := os.getenv("JWT_SECRET"):
            config.setdefault("api", {}).setdefault("auth", {})["jwt_secret"] = jwt_secret

        if http_proxy := os.getenv("HTTP_PROXY"):
            config.setdefault("api", {}).setdefault("proxy", {})["http"] = http_proxy

        if https_proxy := os.getenv("HTTPS_PROXY"):
            config.setdefault("api", {}).setdefault("proxy", {})["https"] = https_proxy

        # Web配置覆盖
        if web_url := os.getenv("WEB_BASE_URL"):
            config.setdefault("web", {})["base_url"] = web_url

        if browser := os.getenv("BROWSER"):
            config.setdefault("web", {})["browser"] = browser

        if headless := os.getenv("HEADLESS"):
            config.setdefault("web", {})["headless"] = headless.lower() == "true"

        if window_size := os.getenv("WINDOW_SIZE"):
            config.setdefault("web", {})["window_size"] = window_size

        # 数据库配置覆盖
        if db_host := os.getenv("DB_HOST"):
            config.setdefault("database", {})["host"] = db_host

        if db_port := os.getenv("DB_PORT"):
            config.setdefault("database", {})["port"] = int(db_port)

        if db_name := os.getenv("DB_NAME"):
            config.setdefault("database", {})["name"] = db_name

        if db_username := os.getenv("DB_USERNAME"):
            config.setdefault("database", {})["username"] = db_username

        if db_password := os.getenv("DB_PASSWORD"):
            config.setdefault("database", {})["password"] = db_password

    def validate_config(self) -> bool:
        """
        验证配置的有效性

        Returns:
            配置是否有效
        """
        if not self._config:
            log.error("配置未加载")
            return False

        try:
            # 验证API配置
            api_config = self._config.get("api", {})
            if not api_config.get("base_url"):
                log.warning("API base_url 未配置")

            # 验证Web配置
            web_config = self._config.get("web", {})
            if not web_config.get("base_url"):
                log.warning("Web base_url 未配置")

            # 验证浏览器配置
            browser = web_config.get("browser", "chrome")
            if browser not in ["chrome", "firefox", "edge", "safari"]:
                log.error(f"不支持的浏览器类型: {browser}")
                return False

            # 验证认证配置
            auth_config = api_config.get("auth", {})
            auth_type = auth_config.get("type", "").lower()
            if auth_type and auth_type not in ["bearer", "basic", "oauth2", "api_key", "jwt"]:
                log.error(f"不支持的认证类型: {auth_type}")
                return False

            log.info("配置验证通过")
            return True

        except Exception as e:
            log.error(f"配置验证失败: {e}")
            return False
            
        if db_user := os.getenv("DB_USER"):
            config.setdefault("database", {})["username"] = db_user
            
        if db_password := os.getenv("DB_PASSWORD"):
            config.setdefault("database", {})["password"] = db_password
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """获取当前配置"""
        return self._config
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("api", {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取Web配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("web", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("database", {})
    
    def get_test_data_config(self) -> Dict[str, Any]:
        """获取测试数据配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("test_data", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("logging", {})
    
    def get_reporting_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("reporting", {})
    
    def get_concurrency_config(self) -> Dict[str, Any]:
        """获取并发配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("concurrency", {})
    
    def get_retry_config(self) -> Dict[str, Any]:
        """获取重试配置"""
        if not self._config:
            raise RuntimeError("配置未加载，请先调用load_config()")
        return self._config.get("retry", {})
    
    def get_current_environment(self) -> Optional[str]:
        """获取当前环境"""
        return self.current_env


# 创建全局配置实例
config = ConfigReader()
