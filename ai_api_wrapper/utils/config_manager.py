import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
from dotenv import load_dotenv, find_dotenv
from ai_api_wrapper.utils.logger import logger
from ai_api_wrapper.config.default_config import DEFAULT_CONFIG
from ai_api_wrapper.config.config_schema import validate_config


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()


class ConfigManager:
    """配置管理器"""
    _instance = None
    _config: Dict[str, Any] = {}
    _initialized = False
    _user_config_path = None
    
    def __new__(cls, config_path: Optional[Union[str, Path]] = None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        elif config_path is not None and config_path != cls._instance._user_config_path:
            # 如果配置路径变更，重置实例
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        if not self._initialized or config_path != self._user_config_path:
            self._user_config_path = config_path
            # 重置配置
            self._config = {}
            self._load_config()
            self._initialized = True
    
    def _log_warning(self, message: str):
        """记录警告日志"""
        logger.warning(message)
    
    def _log_error(self, message: str):
        """记录错误日志"""
        logger.error(message)
    
    def _log_info(self, message: str):
        """记录信息日志"""
        logger.info(message)

    @classmethod
    def reset(cls):
        """重置配置管理器实例，主要用于测试"""
        cls._instance = None
        cls._config = {}
        cls._initialized = False
        cls._user_config_path = None
    
    def _load_config(self):
        """加载配置"""
        try:
            # 1. 加载默认配置
            self._config = DEFAULT_CONFIG.copy()
            self._log_info("Loaded default config")
            
            # 2. 加载用户自定义配置（如果存在）
            if self._user_config_path:
                user_config_path = Path(self._user_config_path)
                if user_config_path.exists():
                    self._log_info(f"Loading user config from {user_config_path}")
                    user_config = self._load_yaml_config(user_config_path)
                    if user_config:
                        self._log_info(f"Loaded user config: {user_config}")
                        self._merge_config(user_config)
                else:
                    self._log_warning(f"User config file not found: {user_config_path}")
            
            # 3. 加载环境变量配置
            self._load_env_config()
            
            # 4. 验证配置
            if not validate_config(self._config):
                self._log_warning("Config validation failed, using default config")
                self._config = DEFAULT_CONFIG.copy()
                self._load_env_config()
            
        except Exception as e:
            self._log_error(f"Failed to load configuration: {str(e)}")
            # 回退到默认配置
            self._config = DEFAULT_CONFIG.copy()
            self._load_env_config()
    
    def _load_yaml_config(self, path: Path) -> Dict[str, Any]:
        """加载 YAML 配置文件
        
        Args:
            path: YAML 文件路径
            
        Returns:
            Dict[str, Any]: 加载的配置
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    return {}
                return config
        except Exception as e:
            self._log_error(f"Failed to load YAML config: {str(e)}")
            return {}
    
    def _load_env_config(self):
        """从环境变量加载配置"""
        # 加载 .env 文件
        load_dotenv(find_dotenv(usecwd=True))
        
        # 获取所有环境变量
        env_config = {}
        
        # 处理 AI 服务配置
        for provider in ['openai', 'anthropic', 'grok', 'deepseek', 'openrouter', 'test_provider']:
            provider_config = {}
            
            # API 密钥
            api_key = os.getenv(f'{provider.upper()}_API_KEY')
            if api_key:
                if "providers" not in env_config:
                    env_config["providers"] = {}
                if provider not in env_config["providers"]:
                    env_config["providers"][provider] = {}
                env_config["providers"][provider]["api_key"] = api_key
            
            # 基础 URL
            base_url = os.getenv(f'{provider.upper()}_BASE_URL')
            if base_url:
                if "providers" not in env_config:
                    env_config["providers"] = {}
                if provider not in env_config["providers"]:
                    env_config["providers"][provider] = {}
                env_config["providers"][provider]["base_url"] = base_url
            
            # 代理设置
            use_proxy = os.getenv(f'{provider.upper()}_USE_PROXY')
            if use_proxy is not None:
                use_proxy = use_proxy.lower() == 'true'
                if "providers" not in env_config:
                    env_config["providers"] = {}
                if provider not in env_config["providers"]:
                    env_config["providers"][provider] = {}
                env_config["providers"][provider]["use_proxy"] = use_proxy
        
        # 全局代理设置
        http_proxy = os.getenv('HTTP_PROXY')
        https_proxy = os.getenv('HTTPS_PROXY')
        if http_proxy or https_proxy:
            if "proxy" not in env_config:
                env_config["proxy"] = {}
            if http_proxy:
                env_config["proxy"]["http"] = http_proxy
            if https_proxy:
                env_config["proxy"]["https"] = https_proxy
                
        # HTTP设置
        timeout = os.getenv('HTTP_TIMEOUT')
        if timeout:
            try:
                timeout_value = float(timeout)
                if "http" not in env_config:
                    env_config["http"] = {}
                env_config["http"]["timeout"] = timeout_value
            except ValueError:
                self._log_warning(f"Invalid HTTP_TIMEOUT value: {timeout}")
        
        # 合并环境变量配置
        if env_config:
            self._log_info(f"Loaded env config: {env_config}")
            self._merge_config(env_config)
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """递归合并配置
        
        Args:
            new_config: 新配置
        """
        self._log_info(f"Merging new config: {new_config}")
        for key, value in new_config.items():
            if key in self._config:
                if isinstance(self._config[key], dict) and isinstance(value, dict):
                    self._merge_config_recursive(self._config[key], value)
                else:
                    self._config[key] = value
            else:
                self._config[key] = value
    
    def _merge_config_recursive(self, target: Dict[str, Any], source: Dict[str, Any]):
        """递归合并字典
        
        Args:
            target: 目标字典
            source: 源字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config_recursive(target[key], value)
            else:
                target[key] = value
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置
        
        Returns:
            Dict[str, Any]: 完整配置
        """
        return self._config.copy()
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取指定提供商的配置
        
        Args:
            provider: 提供商名称
            
        Returns:
            Dict[str, Any]: 提供商配置
        """
        if "providers" not in self._config or provider not in self._config["providers"]:
            return {}
        return self._config["providers"][provider].copy()
    
    def get_http_config(self) -> Dict[str, Any]:
        """获取 HTTP 配置
        
        Returns:
            Dict[str, Any]: HTTP 配置
        """
        return self._config.get("http", {}).copy()
    
    def get_proxy_config(self, provider: str = None) -> Dict[str, str]:
        """获取代理配置
        
        Args:
            provider: 提供商名称，如果指定，将会检查该提供商是否使用代理
            
        Returns:
            Dict[str, str]: 代理配置
        """
        # 检查提供商是否使用代理
        if provider:
            provider_config = self.get_provider_config(provider)
            if not provider_config.get("use_proxy", False):
                return {}
        
        # 获取全局代理配置
        proxy_config = self._config.get("proxy", {})
        return proxy_config.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取指定键的配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self._config[key] = value


# 配置工具函数
def get_config_example() -> str:
    """获取配置示例文件路径
    
    Returns:
        str: 配置示例文件路径
    """
    return str(PROJECT_ROOT / "examples" / "config_examples" / "advanced_config.yaml")


def show_config_example():
    """显示配置示例文件位置"""
    example_path = get_config_example()
    print(f"高级配置示例文件位置：{example_path}")
    print("您可以复制该文件并修改为自己的配置文件。") 