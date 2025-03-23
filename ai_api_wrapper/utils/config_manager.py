import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, TypedDict, cast
from dotenv import load_dotenv, find_dotenv
from ai_api_wrapper.utils.logger import logger
from ai_api_wrapper.config.default_config import DEFAULT_CONFIG
from ai_api_wrapper.config.config_schema import validate_config


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = get_project_root()


class ConfigManager:
    """配置管理器"""
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _initialized = False
    _user_config_path: Optional[Union[str, Path]] = None
    
    def __new__(cls, config_path: Optional[Union[str, Path]] = None) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        elif config_path is not None and config_path != cls._instance._user_config_path:
            # 如果传入了新的配置路径，重置配置管理器
            cls._instance._initialized = False
        
        return cls._instance

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，支持 YAML 和 JSON 格式
        """
        if ConfigManager._initialized and config_path == ConfigManager._user_config_path:
            return
            
        self._user_config_path = config_path
        self._load_config()
        ConfigManager._initialized = True
    
    def _log_info(self, message: str) -> None:
        """记录日志信息"""
        logger.info(message)
    
    def _log_warning(self, message: str) -> None:
        """记录警告信息"""
        logger.warning(message)
    
    def _log_error(self, message: str) -> None:
        """记录错误信息"""
        logger.error(message)
        
    def _load_config(self) -> None:
        """加载配置"""
        # 加载默认配置
        self._config = DEFAULT_CONFIG.copy()
        self._log_info("Loaded default config")
        
        # 加载环境变量
        self._load_env_config()
        
        # 如果指定了用户配置文件，则加载用户配置
        if self._user_config_path:
            try:
                user_config = self._load_user_config()
                if user_config:
                    self._merge_config(user_config)
                    self._log_info(f"Loaded user config from {self._user_config_path}")
            except Exception as e:
                self._log_error(f"Error loading user config: {e}")
        
        # 验证配置
        try:
            validate_config(self._config)
        except Exception as e:
            self._log_warning(f"Config validation failed, using default config")
            self._config = DEFAULT_CONFIG.copy()
    
    def _load_user_config(self) -> Dict[str, Any]:
        """加载用户配置文件"""
        if not self._user_config_path:
            return {}
            
        config_path = Path(self._user_config_path)
        if not config_path.exists():
            self._log_warning(f"Config file not found: {config_path}")
            return {}
            
        try:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    result = yaml.safe_load(f)
                    if result is None:
                        return {}
                    return cast(Dict[str, Any], result)
            elif config_path.suffix.lower() == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    return cast(Dict[str, Any], json.load(f))
            else:
                self._log_error(f"Unsupported config file format: {config_path.suffix}")
                return {}
        except Exception as e:
            self._log_error(f"Error loading config file: {e}")
            return {}
    
    def _load_env_config(self) -> None:
        """从环境变量加载配置"""
        # 加载 .env 文件
        dotenv_path = find_dotenv()
        if dotenv_path:
            load_dotenv(dotenv_path)
            
        # 提取环境变量配置
        env_config: Dict[str, Any] = {}
        
        # API 密钥
        providers = {}
        
        # OpenAI
        if os.environ.get('OPENAI_API_KEY'):
            openai_config = {
                'api_key': os.environ.get('OPENAI_API_KEY'),
                'base_url': os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com'),
                'use_proxy': os.environ.get('OPENAI_USE_PROXY', 'true').lower() in ['true', 'yes', '1']
            }
            providers['openai'] = openai_config
            
        # Anthropic
        if os.environ.get('ANTHROPIC_API_KEY'):
            anthropic_config = {
                'api_key': os.environ.get('ANTHROPIC_API_KEY'),
                'base_url': os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com'),
                'use_proxy': os.environ.get('ANTHROPIC_USE_PROXY', 'true').lower() in ['true', 'yes', '1']
            }
            providers['anthropic'] = anthropic_config
            
        # Grok
        if os.environ.get('GROK_API_KEY'):
            grok_config = {
                'api_key': os.environ.get('GROK_API_KEY'),
                'base_url': os.environ.get('GROK_BASE_URL', 'https://api.x.ai/v1'),
                'use_proxy': os.environ.get('GROK_USE_PROXY', 'true').lower() in ['true', 'yes', '1']
            }
            providers['grok'] = grok_config
        
        # DeepSeek
        if os.environ.get('DEEPSEEK_API_KEY'):
            use_proxy_str = os.environ.get('DEEPSEEK_USE_PROXY', 'true').lower()
            use_proxy: bool = use_proxy_str in ['true', 'yes', '1']
            deepseek_config = {
                'api_key': os.environ.get('DEEPSEEK_API_KEY'),
                'base_url': os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                'use_proxy': use_proxy
            }
            providers['deepseek'] = deepseek_config
        
        # OpenRouter
        if os.environ.get('OPENROUTER_API_KEY'):
            openrouter_config = {
                'api_key': os.environ.get('OPENROUTER_API_KEY'),
                'base_url': os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
                'use_proxy': os.environ.get('OPENROUTER_USE_PROXY', 'true').lower() in ['true', 'yes', '1']
            }
            providers['openrouter'] = openrouter_config
            
        # 添加服务提供商配置
        if providers:
            env_config['providers'] = providers
            
        # 代理配置
        proxy = {}
        if os.environ.get('HTTP_PROXY'):
            proxy['http'] = os.environ.get('HTTP_PROXY')
        if os.environ.get('HTTPS_PROXY'):
            proxy['https'] = os.environ.get('HTTPS_PROXY')
        if os.environ.get('ALL_PROXY'):
            proxy['all'] = os.environ.get('ALL_PROXY')
            
        if proxy:
            env_config['proxy'] = proxy
            
        # 记录环境变量配置
        if env_config:
            self._log_info(f"Loaded env config: {env_config}")
            self._merge_config(env_config)
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """合并配置"""
        self._log_info(f"Merging new config: {new_config}")
        self._config = self._merge_config_recursive(self._config, new_config)
        
    def _merge_config_recursive(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置字典"""
        merged = base.copy()
        
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_config_recursive(base[key], value)
            else:
                merged[key] = value
                
        return merged
        
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return dict(self._config)
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取提供商配置"""
        providers = self._config.get('providers', {})
        if provider in providers:
            return dict(providers[provider].copy())
        return {}
    
    def get_http_config(self) -> Dict[str, Any]:
        """获取 HTTP 配置"""
        return dict(self._config.get('http', {}))
    
    def get_proxy_config(self, provider: Optional[str] = None) -> Dict[str, str]:
        """获取代理配置"""
        proxy_config = self._config.get('proxy', {}).copy()
        
        # 如果指定了服务提供商，检查服务提供商是否使用代理
        if provider:
            provider_config = self.get_provider_config(provider)
            use_proxy = provider_config.get('use_proxy', True)
            
            if not use_proxy:
                return {}
        
        # 转换为字符串键值对的字典
        return {k: str(v) for k, v in proxy_config.items() if v is not None}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        config = self._config
        
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
                
        return config
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    @classmethod
    def reset(cls) -> None:
        """重置配置管理器实例"""
        cls._instance = None
        cls._initialized = False


def get_config_example() -> Dict[str, Any]:
    """获取配置示例"""
    return {
        "http": {
            "timeout": 60.0,
            "max_retries": 3,
            "verify_ssl": True,
        },
        "proxy": {
            "http": "http://localhost:8888",
            "https": "http://localhost:8888",
        },
        "logging": {
            "level": "INFO",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            "to_file": True,
            "file_path": "logs/ai_api_wrapper.log",
        },
        "providers": {
            "openai": {
                "api_key": "YOUR_OPENAI_API_KEY",
                "base_url": "https://api.openai.com/v1",
                "use_proxy": True,
            },
            "grok": {
                "api_key": "YOUR_GROK_API_KEY", 
                "base_url": "https://api.x.ai/v1",
                "use_proxy": True,
            },
        }
    }
    
def show_config_example() -> None:
    """显示配置示例"""
    config_example = get_config_example()
    print("\n=== 配置文件示例 (.env) ===")
    print("# OpenAI 配置")
    print("OPENAI_API_KEY=sk-your-api-key")
    print("OPENAI_BASE_URL=https://api.openai.com")
    print("OPENAI_USE_PROXY=true")
    print("\n# Anthropic 配置")
    print("ANTHROPIC_API_KEY=sk-ant-your-api-key")
    print("ANTHROPIC_BASE_URL=https://api.anthropic.com")
    print("ANTHROPIC_USE_PROXY=true")
    print("\n# 代理配置")
    print("HTTP_PROXY=http://localhost:8888")
    print("HTTPS_PROXY=http://localhost:8888")
    print("\n=== 配置文件示例 (YAML) ===")
    print(yaml.dump(config_example, default_flow_style=False, sort_keys=False)) 