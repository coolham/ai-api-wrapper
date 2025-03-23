# AI API 包装器配置指南

## 配置概述

AI API 包装器的配置系统支持多种配置方式，您可以根据自己的需求选择最适合的配置方法。配置按照以下优先级从高到低加载：

1. **环境变量**：最高优先级，适合基础配置和敏感信息
2. **用户自定义 YAML 配置文件**：适合高级自定义配置
3. **默认配置**：内置在包中，无需修改

## 基础配置：环境变量

基础配置使用环境变量或 `.env` 文件进行设置，主要用于 API 密钥、基础 URL 和代理开关等基本设置。

### 创建 `.env` 文件

在项目根目录创建 `.env` 文件，内容示例：

```dotenv
# API 密钥配置
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROK_API_KEY=your_grok_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 基础 URL 配置（可选）
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_BASE_URL=https://api.anthropic.com
GROK_BASE_URL=https://api.x.ai/v1
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# 代理配置
# 设置为 true 表示使用全局代理
OPENAI_USE_PROXY=false
ANTHROPIC_USE_PROXY=false
GROK_USE_PROXY=true
DEEPSEEK_USE_PROXY=false
OPENROUTER_USE_PROXY=false

# 全局代理设置
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 高级配置：YAML 文件

如果需要更高级的配置选项，您可以使用 YAML 配置文件。首先获取配置示例：

```python
import ai_api_wrapper as ai

# 显示配置示例文件位置
ai.show_config_example()

# 获取配置示例文件路径
example_path = ai.get_config_example()
```

### 使用自定义配置文件

1. 复制示例配置文件：

```bash
cp "示例配置文件路径" my_config.yaml
```

2. 修改配置文件，根据需要自定义选项。

3. 在代码中使用自定义配置文件：

```python
from pathlib import Path
import ai_api_wrapper as ai

# 创建客户端，使用自定义配置文件
client = ai.Client(config_path=Path("my_config.yaml"))
```

## 高级配置选项说明

YAML 配置文件中可以设置以下高级选项：

### HTTP 客户端设置

```yaml
http:
  timeout: 30.0              # HTTP 请求超时时间（秒）
  max_retries: 3             # 最大重试次数
  verify_ssl: true           # 是否验证 SSL 证书
  backoff_factor: 0.5        # 重试等待时间指数因子
```

### 日志设置

```yaml
logging:
  level: "INFO"              # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日志格式
  file: "logs/ai_api_wrapper.log"  # 日志文件路径
  max_size: 10485760         # 日志文件最大大小（字节，约10MB）
  backup_count: 5            # 日志文件备份数量
```

### 缓存设置

```yaml
cache:
  enabled: true              # 是否启用缓存
  ttl: 3600                  # 缓存过期时间（秒）
  max_size: 1000             # 最大缓存条目数
  directory: ".cache"        # 缓存目录
```

### 并发设置

```yaml
concurrency:
  max_requests: 10           # 最大并发请求数
  rate_limit: 60             # 请求速率限制（次/分钟）
```

### 错误处理设置

```yaml
error_handling:
  retry_delay: 1.0           # 错误重试延迟（秒）
  retry_multiplier: 2.0      # 错误重试延迟倍数
  max_retries: 3             # 最大重试次数
```

### 模型默认设置

```yaml
model_defaults:
  max_tokens: 4000           # 默认最大 token 数
  temperature: 0.7           # 默认温度值
  top_p: 1.0                 # 默认 top_p 值
  frequency_penalty: 0.0     # 默认频率惩罚值
  presence_penalty: 0.0      # 默认存在惩罚值
```

### 提供商特定设置

```yaml
providers:
  # OpenAI 设置
  openai:
    models:
      - "gpt-3.5-turbo"
      - "gpt-4"
    default_model: "gpt-3.5-turbo"
  
  # 其他提供商配置...
```

## 配置验证

配置加载时会进行基本验证，确保必要的配置项存在且格式正确。如果验证失败，将回退到默认配置。

## 工具函数

包中提供了几个配置相关的工具函数：

- `get_config_example()`：获取配置示例文件路径
- `show_config_example()`：显示配置示例文件位置

## 最佳实践

1. API 密钥等敏感信息使用环境变量或 `.env` 文件配置
2. 高级设置使用 YAML 配置文件
3. 不要手动修改包内的默认配置文件
4. 将 `.env` 和自定义配置文件添加到 `.gitignore` 中，避免提交敏感信息 