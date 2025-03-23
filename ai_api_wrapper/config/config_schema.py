"""
配置模式定义
用于验证配置的正确性
"""
from typing import Dict, List, Any, Optional, Union


class HTTPConfig:
    """HTTP 客户端配置模式"""
    timeout: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True
    backoff_factor: float = 0.5


class LoggingConfig:
    """日志配置模式"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/ai_api_wrapper.log"
    max_size: int = 10485760
    backup_count: int = 5


class CacheConfig:
    """缓存配置模式"""
    enabled: bool = True
    ttl: int = 3600
    max_size: int = 1000
    directory: str = ".cache"


class ConcurrencyConfig:
    """并发配置模式"""
    max_requests: int = 10
    rate_limit: int = 60


class ErrorHandlingConfig:
    """错误处理配置模式"""
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    max_retries: int = 3


class ModelDefaultsConfig:
    """模型默认配置模式"""
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class ProviderConfig:
    """提供商配置模式"""
    base_url: str
    models: List[str]
    default_model: str
    use_proxy: bool = False
    api_key: Optional[str] = None


class Config:
    """总配置模式"""
    http: HTTPConfig
    logging: LoggingConfig
    cache: CacheConfig
    concurrency: ConcurrencyConfig
    error_handling: ErrorHandlingConfig
    model_defaults: ModelDefaultsConfig
    providers: Dict[str, ProviderConfig]


def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置是否符合模式
    
    Args:
        config: 配置字典
        
    Returns:
        bool: 验证是否通过
    """
    # 简单验证，确保必要的配置项存在
    required_sections = ["http", "logging", "providers"]
    for section in required_sections:
        if section not in config:
            return False
    
    # 验证 providers 配置
    if not isinstance(config["providers"], dict):
        return False
    
    for provider_name, provider_config in config["providers"].items():
        if not isinstance(provider_config, dict):
            return False
        if "base_url" not in provider_config:
            return False
    
    return True 