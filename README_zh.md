# AI API Wrapper

一个统一的 AI API 封装库，支持多个 AI 提供商，并提供代理支持。

## 特性

- 🔄 **统一接口**：通过单一、一致的 API 访问不同的 AI 模型
- 🌐 **代理支持**：内置代理支持，特别适合中国大陆用户使用
- 🤖 **多提供商支持**：支持多个 AI 提供商，包括：
  - OpenAI
  - Anthropic
  - Azure OpenAI
  - Google AI
  - DeepSeek
  - 更多提供商正在添加中...

## 安装

```bash
# 使用 poetry 安装
poetry install

# 或使用 pip 安装
pip install ai-api-wrapper
```

## 快速开始

```python
from ai_api_wrapper import Client

# 创建带有代理支持的客户端
proxy_config = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
client = Client(proxy_config=proxy_config)

# 创建聊天完成请求
response = client.chat.completions.create(
    model="deepseek:deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {"role": "user", "content": "你好！"}
    ],
    temperature=0.7
)

# 打印响应
print(response.choices[0].message.content)
```

## 配置

### 环境变量

在项目根目录创建 `.env` 文件，包含以下变量：

```env
# API 密钥
DEEPSEEK_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_api_key_here
AZURE_OPENAI_API_KEY=your_api_key_here

# 基础 URL（可选，如果设置将覆盖 config.json 中的配置）
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_BASE_URL=https://api.openai.com
ANTHROPIC_BASE_URL=https://api.anthropic.com
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com
```

### 配置文件

项目使用单个 `config.json` 文件存储非敏感配置。如果设置了环境变量，其中的 base_url 将覆盖配置文件中的设置：

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

### 安全最佳实践

1. **切勿提交敏感信息**
   - 将所有 API 密钥保存在 `.env` 文件中
   - 将 `.env` 添加到 `.gitignore`
   - 切勿将 API 密钥提交到版本控制系统

2. **配置文件**
   - 将 `config.json` 保持在版本控制中
   - 仅包含非敏感配置
   - 使用环境变量存储敏感数据和自定义 base_url

3. **环境变量**
   - 在本地开发中使用 `.env` 文件
   - 在生产环境中使用系统环境变量
   - 切勿在代码中硬编码 API 密钥或 base_url

## 开发

```bash
# 安装开发依赖
poetry install --with dev

# 运行测试
poetry run pytest

# 代码格式化
poetry run black .
poetry run isort .

# 类型检查
poetry run mypy .
```

## 许可证

GPL v3
