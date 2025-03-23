"""
默认配置文件
包含所有 AI API 包装器的默认配置参数
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Union, List, Optional

from ai_api_wrapper.utils.constants import PROJECT_ROOT

# 类型提示以帮助mypy理解字典结构
ConfigDict = Dict[str, Any]

# HTTP 客户端设置
HTTP_TIMEOUT = 60.0
HTTP_MAX_RETRIES = 5
HTTP_RETRY_CODES = [408, 429, 500, 502, 503, 504]
HTTP_BACKOFF_FACTOR = 0.5
HTTP_RETRY_JITTER = True
HTTP_VERIFY_SSL = True  # 是否验证 SSL 证书

# 日志设置
LOG_LEVEL = "INFO"
LOG_TO_FILE = False
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "logs")
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
LOG_ROTATION = "500 MB"
LOG_RETENTION = "10 days"

# 缓存设置
CACHE_ENABLED = False
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")
CACHE_TTL = 3600  # 秒
CACHE_MAX_SIZE = 1024  # MB

# 并发设置
MAX_CONCURRENT_REQUESTS = 10
POOL_MAX_SIZE = 100
POOL_TIMEOUT = 60
REQUEST_RATE_LIMIT = 60  # 每分钟请求数

# 错误处理设置
RAISE_FOR_STATUS = True
AUTO_RETRY = True
RETRY_STATUSES = [429, 500, 502, 503, 504]
MAX_RETRIES = 3
RETRY_BACKOFF = 0.5
ERROR_RETRY_DELAY = 1.0  # 初始延迟时间（秒）
ERROR_RETRY_MULTIPLIER = 2.0  # 延迟时间倍数

# 模型默认设置
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TOP_P = 1.0
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0

# 消息处理设置
MAX_MESSAGES_PER_REQUEST = 100
TRIM_MESSAGES_STRATEGY = "sliding_window"  # 或 "summarize"
TOKEN_LIMIT_BUFFER = 200
MAX_MESSAGE_LENGTH = 4000  # 单个消息的最大长度
TRUNCATE_MESSAGES = True  # 是否截断过长的消息

# 性能设置
ENABLE_STREAMING = True
BATCH_SIZE = 10
CONNECTION_POOL_SIZE = 10
KEEP_ALIVE_TIMEOUT = 60
ENABLE_COMPRESSION = True  # 是否启用压缩
COMPRESSION_LEVEL = 6  # 压缩级别 (1-9, 1最快，9最小)

# 安全设置
VALIDATE_API_KEYS = True
MASK_SENSITIVE_DATA = True
ALLOWED_ORIGINS = ["*"]
RATE_LIMIT_ENABLED = False
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 60  # 秒
API_KEY_ROTATION_INTERVAL = 86400  # API 密钥轮换间隔（秒）
ENABLE_RATE_LIMITING = True  # 是否启用速率限制

# 服务提供商设置
OPENAI_DEFAULT_CONFIG = {
    "BASE_URL": None,  # 默认使用 OpenAI 官方 API 端点
    "MODEL_MAPPING": {
        "gpt-3.5-turbo": "gpt-3.5-turbo-0125",
        "gpt-4": "gpt-4-0125-preview",
        "gpt-4-turbo": "gpt-4-0125-preview",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
    "default_model": "gpt-3.5-turbo",  # 默认模型
}

GEMINI_DEFAULT_CONFIG = {
    "API_BASE": "https://generativelanguage.googleapis.com/v1beta",
    "MODEL_MAPPING": {
        "gemini-pro": "models/gemini-pro:generateContent",
        "gemini-pro-vision": "models/gemini-pro-vision:generateContent",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

DATABRICKS_DEFAULT_CONFIG = {
    "API_BASE": "https://common-gpu-serving.databricks.com/serving-endpoints",
    "MODEL_MAPPING": {
        "databricks-dbrx-instruct": "dbrx-instruct",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

ANTHROPIC_DEFAULT_CONFIG = {
    "API_BASE": "https://api.anthropic.com/v1/messages",
    "MODEL_MAPPING": {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-2.1": "claude-2.1",
        "claude-2.0": "claude-2.0",
        "claude-instant-1.2": "claude-instant-1.2",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

MISTRAL_DEFAULT_CONFIG = {
    "API_BASE": "https://api.mistral.ai/v1",
    "MODEL_MAPPING": {
        "mistral-tiny": "mistral-tiny-2312",
        "mistral-small": "mistral-small-2312",
        "mistral-medium": "mistral-medium-2312",
        "mistral-large": "mistral-large-2402",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

ZHIPU_DEFAULT_CONFIG = {
    "API_BASE": "https://open.bigmodel.cn/api/paas/v4",
    "MODEL_MAPPING": {
        "glm-4": "glm-4",
        "glm-3-turbo": "glm-3-turbo",
        "glm-4v": "glm-4v",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

BAIDU_DEFAULT_CONFIG = {
    "API_BASE": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
    "MODEL_MAPPING": {
        "ernie-4.0": "completions_pro",
        "ernie-3.5": "completions",
        "ernie-speed": "ernie-speed",
        "ernie-bot-8k": "ernie_bot_8k",
        "ernie-bot": "ernie_bot",
        "ernie-bot-turbo": "ernie_bot_turbo",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

DEEPSEEK_DEFAULT_CONFIG = {
    "API_BASE": "https://api.deepseek.com/v1",
    "MODEL_MAPPING": {
        "deepseek-chat": "deepseek-chat",
        "deepseek-coder": "deepseek-coder",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

GROQ_DEFAULT_CONFIG = {
    "BASE_URL": "https://api.groq.com/openai/v1",
    "MODEL_MAPPING": {
        "llama2-70b": "llama2-70b-4096",
        "llama3-8b": "llama3-8b-8192",
        "llama3-70b": "llama3-70b-8192",
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gemma-7b": "gemma-7b-it",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

GROK_DEFAULT_CONFIG = {
    "BASE_URL": os.environ.get("GROK_BASE_URL") or "https://api.openai.com/v1",
    "MODEL_MAPPING": {
        "grok-1": "grok-1",
        "grok-1.5": "grok-1.5",
        "grok-1.5-mini": "grok-1.5-mini",
        "grok-2": "grok-2-8k",
        "grok-2-1212": "grok-2-1212",
    },
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

OPENROUTER_DEFAULT_CONFIG = {
    "BASE_URL": "https://openrouter.ai/api/v1",
    "DEFAULT_TIMEOUT": HTTP_TIMEOUT,
    "MAX_RETRIES": 3,
}

DEFAULT_CONFIG: ConfigDict = {
    # HTTP 客户端设置
    "http": {
        "timeout": HTTP_TIMEOUT,            # HTTP 请求超时时间（秒）
        "max_retries": HTTP_MAX_RETRIES,    # 最大重试次数
        "verify_ssl": HTTP_VERIFY_SSL,      # 是否验证 SSL 证书
        "backoff_factor": HTTP_BACKOFF_FACTOR,  # 重试等待时间指数因子
        "retry_codes": HTTP_RETRY_CODES,    # 需要重试的状态码
        "retry_jitter": HTTP_RETRY_JITTER,  # 是否在重试时间上添加随机抖动
    },
    
    # 代理设置
    "proxy": {"http": None, "https": None, "all": None},

    # 日志设置
    "logging": {
        "level": LOG_LEVEL,                # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
        "format": LOG_FORMAT,              # 日志格式
        "to_file": LOG_TO_FILE,            # 是否输出到文件
        "file_path": LOG_FILE_PATH,        # 日志文件路径
        "rotation": LOG_ROTATION,          # 日志滚动大小
        "retention": LOG_RETENTION,        # 日志保留时间
    },
    
    # 缓存设置
    "cache": {
        "enabled": CACHE_ENABLED,          # 是否启用缓存
        "ttl": CACHE_TTL,                  # 缓存有效期（秒）
        "dir": CACHE_DIR,                  # 缓存目录
        "max_size": CACHE_MAX_SIZE,        # 最大缓存大小（MB）
    },
    
    # 并发设置
    "concurrency": {
        "max_requests": MAX_CONCURRENT_REQUESTS,   # 最大并发请求数
        "rate_limit": REQUEST_RATE_LIMIT,          # 速率限制（每分钟请求数）
        "pool_max_size": POOL_MAX_SIZE,            # 连接池最大大小
        "pool_timeout": POOL_TIMEOUT,              # 连接池超时时间
    },
    
    # 错误处理设置
    "error_handling": {
        "retry_delay": ERROR_RETRY_DELAY,         # 重试延迟时间（秒）
        "retry_multiplier": ERROR_RETRY_MULTIPLIER, # 重试延迟乘数
        "raise_for_status": RAISE_FOR_STATUS,      # 是否在HTTP状态码不是200时抛出异常
        "auto_retry": AUTO_RETRY,                  # 是否自动重试
        "retry_statuses": RETRY_STATUSES,          # 需要重试的状态码
        "max_retries": MAX_RETRIES,                # 最大重试次数
        "retry_backoff": RETRY_BACKOFF,            # 重试延迟增长因子
    },
    
    # 模型默认设置
    "model_defaults": {
        "temperature": DEFAULT_TEMPERATURE,        # 温度值，控制随机性
        "max_tokens": DEFAULT_MAX_TOKENS,         # 生成的最大令牌数
        "top_p": DEFAULT_TOP_P,                    # Top-p 采样参数
        "frequency_penalty": DEFAULT_FREQUENCY_PENALTY,   # 频率惩罚
        "presence_penalty": DEFAULT_PRESENCE_PENALTY,     # 存在惩罚
    },
    
    # 消息处理设置
    "message_handling": {
        "max_length": MAX_MESSAGE_LENGTH,         # 消息最大长度
        "truncate_messages": TRUNCATE_MESSAGES,    # 是否截断过长消息
        "max_messages_per_request": MAX_MESSAGES_PER_REQUEST,  # 最大消息数
        "trim_strategy": TRIM_MESSAGES_STRATEGY,   # 消息裁剪策略
        "token_limit_buffer": TOKEN_LIMIT_BUFFER,  # 令牌限制缓冲
    },
    
    # 性能设置
    "performance": {
        "enable_compression": ENABLE_COMPRESSION,  # 是否启用压缩
        "compression_level": COMPRESSION_LEVEL,    # 压缩级别
        "enable_streaming": ENABLE_STREAMING,      # 是否启用流式响应
        "batch_size": BATCH_SIZE,                  # 批处理大小
        "connection_pool_size": CONNECTION_POOL_SIZE,  # 连接池大小
        "keep_alive_timeout": KEEP_ALIVE_TIMEOUT,  # 连接保持时间
    },
    
    # 安全设置
    "security": {
        "api_key_rotation_interval": API_KEY_ROTATION_INTERVAL,  # API 密钥轮换间隔（秒）
        "enable_rate_limiting": ENABLE_RATE_LIMITING,            # 是否启用速率限制
        "validate_api_keys": VALIDATE_API_KEYS,                  # 是否验证API密钥
        "mask_sensitive_data": MASK_SENSITIVE_DATA,              # 是否掩码敏感数据
        "allowed_origins": ALLOWED_ORIGINS,                      # 允许的源
        "rate_limit": {
            "enabled": RATE_LIMIT_ENABLED,                       # 是否启用
            "requests": RATE_LIMIT_REQUESTS,                     # 请求数
            "period": RATE_LIMIT_PERIOD,                         # 周期（秒）
        },
    },
    
    # 提供商配置
    "providers": {
        "openai": OPENAI_DEFAULT_CONFIG,
        "gemini": GEMINI_DEFAULT_CONFIG,
        "anthropic": ANTHROPIC_DEFAULT_CONFIG,
        "databricks": DATABRICKS_DEFAULT_CONFIG,
        "mistral": MISTRAL_DEFAULT_CONFIG,
        "zhipu": ZHIPU_DEFAULT_CONFIG,
        "baidu": BAIDU_DEFAULT_CONFIG,
        "deepseek": DEEPSEEK_DEFAULT_CONFIG,
        "groq": GROQ_DEFAULT_CONFIG,
        "grok": GROK_DEFAULT_CONFIG,
        "openrouter": OPENROUTER_DEFAULT_CONFIG,
    },
}

# 导出一些常用的配置值以便直接导入
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

def get_default_config() -> Dict[str, Any]:
    """Return default configuration."""
    return DEFAULT_CONFIG.copy() 