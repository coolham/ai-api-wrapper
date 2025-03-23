"""
默认配置文件
包含所有 AI API 包装器的默认配置参数
"""
from typing import Dict, Any, Union, List

# 类型提示以帮助mypy理解字典结构
ConfigDict = Dict[str, Any]

DEFAULT_CONFIG: ConfigDict = {
    # HTTP 客户端设置
    "http": {
        "timeout": 30.0,            # HTTP 请求超时时间（秒）
        "max_retries": 3,           # 最大重试次数
        "verify_ssl": True,         # 是否验证 SSL 证书
        "backoff_factor": 0.5,      # 重试等待时间指数因子
    },
    
    # 日志设置
    "logging": {
        "level": "INFO",            # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
        "file": "logs/ai_api_wrapper.log",  # 日志文件路径
        "max_size": 10485760,       # 日志文件最大大小（字节）
        "backup_count": 5,          # 日志文件备份数量
    },
    
    # 缓存设置
    "cache": {
        "enabled": True,            # 是否启用缓存
        "ttl": 3600,                # 缓存过期时间（秒）
        "max_size": 1000,           # 最大缓存条目数
        "directory": ".cache",      # 缓存目录
    },
    
    # 并发设置
    "concurrency": {
        "max_requests": 10,         # 最大并发请求数
        "rate_limit": 60,           # 请求速率限制（次/分钟）
    },
    
    # 错误处理设置
    "error_handling": {
        "retry_delay": 1.0,         # 错误重试延迟（秒）
        "retry_multiplier": 2.0,    # 错误重试延迟倍数
        "max_retries": 3,           # 最大重试次数
    },
    
    # 模型默认设置
    "model_defaults": {
        "max_tokens": 4000,         # 默认最大 token 数
        "temperature": 0.7,         # 默认温度值
        "top_p": 1.0,               # 默认 top_p 值
        "frequency_penalty": 0.0,   # 默认频率惩罚值
        "presence_penalty": 0.0,    # 默认存在惩罚值
    },
    
    # 消息处理设置
    "message_handling": {
        "max_length": 4096,         # 最大消息长度
        "truncate_messages": True,  # 是否截断过长的消息
    },
    
    # 性能设置
    "performance": {
        "enable_compression": True, # 是否启用压缩
        "compression_level": 6,     # 压缩级别（1-9）
    },
    
    # 安全设置
    "security": {
        "api_key_rotation_interval": 3600,  # API 密钥轮换间隔（秒）
        "enable_rate_limiting": True,       # 是否启用速率限制
    },
    
    # 提供商设置
    "providers": {
        # OpenAI 设置
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-3.5-turbo", "gpt-4"],
            "default_model": "gpt-3.5-turbo",
        },
        
        # Anthropic 设置
        "anthropic": {
            "base_url": "https://api.anthropic.com",
            "models": ["claude-2", "claude-instant-1"],
            "default_model": "claude-2",
        },
        
        # Grok 设置
        "grok": {
            "base_url": "https://api.x.ai/v1",
            "models": ["grok-1", "grok-2"],
            "default_model": "grok-2",
        },
        
        # DeepSeek 设置
        "deepseek": {
            "base_url": "https://api.deepseek.com",
            "models": ["deepseek-chat"],
            "default_model": "deepseek-chat",
        },
        
        # OpenRouter 设置
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "models": ["openai/gpt-3.5-turbo", "anthropic/claude-2"],
            "default_model": "openai/gpt-3.5-turbo",
        },
    }
}

# 导出常量，以兼容之前引用advanced_settings的代码
HTTP_TIMEOUT = DEFAULT_CONFIG["http"]["timeout"]
HTTP_MAX_RETRIES = DEFAULT_CONFIG["http"]["max_retries"]
HTTP_VERIFY_SSL = DEFAULT_CONFIG["http"]["verify_ssl"]

LOG_LEVEL = DEFAULT_CONFIG["logging"]["level"]
LOG_FORMAT = DEFAULT_CONFIG["logging"]["format"]

CACHE_ENABLED = DEFAULT_CONFIG["cache"]["enabled"]
CACHE_TTL = DEFAULT_CONFIG["cache"]["ttl"]

MAX_CONCURRENT_REQUESTS = DEFAULT_CONFIG["concurrency"]["max_requests"]
REQUEST_RATE_LIMIT = DEFAULT_CONFIG["concurrency"]["rate_limit"]

ERROR_RETRY_DELAY = DEFAULT_CONFIG["error_handling"]["retry_delay"]
ERROR_RETRY_MULTIPLIER = DEFAULT_CONFIG["error_handling"]["retry_multiplier"]

DEFAULT_MODEL = DEFAULT_CONFIG["providers"]["openai"]["default_model"]
DEFAULT_MAX_TOKENS = DEFAULT_CONFIG["model_defaults"]["max_tokens"]
DEFAULT_TEMPERATURE = DEFAULT_CONFIG["model_defaults"]["temperature"]

MAX_MESSAGE_LENGTH = DEFAULT_CONFIG["message_handling"]["max_length"]
TRUNCATE_MESSAGES = DEFAULT_CONFIG["message_handling"]["truncate_messages"]

ENABLE_COMPRESSION = DEFAULT_CONFIG["performance"]["enable_compression"]
COMPRESSION_LEVEL = DEFAULT_CONFIG["performance"]["compression_level"]

API_KEY_ROTATION_INTERVAL = DEFAULT_CONFIG["security"]["api_key_rotation_interval"]
ENABLE_RATE_LIMITING = DEFAULT_CONFIG["security"]["enable_rate_limiting"] 