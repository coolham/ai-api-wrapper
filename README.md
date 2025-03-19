# AI API Wrapper

A unified API wrapper for various AI providers, with built-in proxy support.

## Features

- 🔄 **Unified Interface**: Access different AI models through a single, consistent API
- 🌐 **Proxy Support**: Built-in proxy support, perfect for users in mainland China
- 🤖 **Multiple Providers**: Support for various AI providers including:
  - OpenAI
  - Anthropic
  - Azure OpenAI
  - Google AI
  - DeepSeek
  - More providers coming soon...

## Installation

```bash
# Using poetry
poetry install

# Or using pip
pip install ai-api-wrapper
```

## Quick Start

```python
from ai_api_wrapper import Client

# Create a client with proxy support
proxy_config = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
client = Client(proxy_config=proxy_config)

# Create a chat completion
response = client.chat.completions.create(
    model="deepseek:deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7
)

# Print the response
print(response.choices[0].message.content)
```

## Configuration

### Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# API Keys
DEEPSEEK_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_api_key_here
AZURE_OPENAI_API_KEY=your_api_key_here

# Base URLs (Optional, will override config.json if set)
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_BASE_URL=https://api.openai.com
ANTHROPIC_BASE_URL=https://api.anthropic.com
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com
```

### Configuration File

The project uses a single `config.json` file for non-sensitive configurations. Base URLs in this file will be overridden by environment variables if set:

```json
{
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": true,
        "models": {
            "deepseek-chat": {
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "deepseek-coder": {
                "max_tokens": 4000,
                "temperature": 0.7
            }
        }
    },
    "openai": {
        "base_url": "https://api.openai.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": true
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": true
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": true
    },
    "azure": {
        "base_url": "https://your-resource.openai.azure.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": true
    },
    "logging": {
        "level": "INFO",
        "file": "app.log"
    }
}
```

### Security Best Practices

1. **Never commit sensitive information**
   - Keep all API keys in `.env` file
   - Add `.env` to your `.gitignore`
   - Never commit API keys to version control

2. **Configuration file**
   - Keep `config.json` in version control
   - Only include non-sensitive configurations
   - Use environment variables for sensitive data and custom base URLs

3. **Environment variables**
   - Use `.env` file for local development
   - Use system environment variables in production
   - Never hardcode API keys or base URLs in your code

## Development

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

## License

GPL v3


# 配置系统说明

## 配置文件结构

项目使用分层的JSON配置文件系统：

1. `default.json`：默认配置文件
   - 包含所有可能的配置项
   - 定义默认值和基本结构
   - 可以提交到版本控制
   - **不应包含任何敏感信息**（API密钥、密码等）

2. `local.json`：本地配置文件
   - 包含敏感信息（API密钥、密码等）
   - 覆盖默认配置
   - **不应提交到版本控制**
   - 应添加到 `.gitignore` 文件中

## 安全最佳实践

1. **敏感信息仅存储在 `local.json` 中**
   - API 密钥
   - 数据库凭据
   - JWT 密钥
   - 任何其他密码或密钥

2. **禁止在 `default.json` 中存储任何真实的敏感信息**
   - 在 `default.json` 中，将所有密钥字段设置为空字符串 `""`
   - 仅使用 `default.json` 定义配置结构

3. **版本控制注意事项**
   - 始终将 `local.json` 添加到 `.gitignore`
   - 仅提交 `default.json` 到仓库
   - 提供 `local.json.template` 文件，用于新开发人员设置

## 配置项说明

### AI服务配置

```json
{
    "ai_services": {
        "service_name": {
            "enabled": true,
            "default_provider": "official",
            "default_model": "model-name",
            "providers": {
                "provider_name": {
                    "name": "显示名称",
                    "enabled": true,
                    "api_key": "",  // 在 default.json 中留空，在 local.json 中填写实际值
                    "base_url": "API基础URL",
                    "models": {
                        "model_name": {
                            "internal_name": "提供商特定的模型名称",
                            "max_tokens": 4000,
                            "temperature": 0.7
                        }
                    }
                }
            }
        }
    }
}
```

### 其他配置

- `database`：数据库配置（密码仅存储在 local.json）
- `redis`：Redis配置（密码仅存储在 local.json）
- `jwt_secret`：JWT密钥（仅存储在 local.json）
- `logging`：日志配置

## 使用方法

1. 复制`local.json.template`为`local.json`
2. 在`local.json`中填入实际的配置值（API密钥等）
3. 不要修改`default.json`中的默认值（除非添加新功能）
4. 使用`ConfigManager`类访问配置：

```python
from utils.config_manager import ConfigManager

config = ConfigManager()

# 获取提供商配置
provider_config = config.get_provider_config('deepseek', 'siliconflow')

# 获取模型配置
model_config = config.get_model_config('deepseek', 'siliconflow', 'deepseek-chat')

# 获取已启用的服务
enabled_services = config.get_enabled_services()
```

## Test

python -m pytest tests/ -v


## 注意事项

1. 不要在代码中硬编码任何敏感信息
2. 不要提交`local.json`到版本控制
3. 保持配置文件的结构与`default.json`一致
4. 使用有意义的配置项名称
5. 及时更新文档 
6. 