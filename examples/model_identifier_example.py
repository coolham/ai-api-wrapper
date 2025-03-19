import sys
from dotenv import load_dotenv, find_dotenv
import ai_api_wrapper as ai
import time

# 加载环境变量
load_dotenv(find_dotenv())

# 创建客户端
client = ai.Client(default_service="deepseek")

# 准备消息
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "请介绍一下你自己。"}
]

# 测试不同的模型标识方式
models = [
    "deepseek:deepseek-r1",           # Deepseek 官方服务
    "deepseek:deepseek-coder",        # Deepseek 官方服务
    "openrouter:deepseek-r1",         # OpenRouter 提供的 Deepseek 服务
    "openrouter:gpt-4o",             # OpenRouter 提供的 OpenAI 服务
    "openrouter:claude-3",           # OpenRouter 提供的 Anthropic 服务
    "grok:grok-2-1212"              # Grok 官方服务
]

for model in models:
    print(f"\nTesting model: {model}")
    print("-" * 50)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        print(f"Content:\n{response['choices'][0]['message']['content']}\n")
    except Exception as e:
        print(f"Error with {model}: {str(e)}")

# 尝试获取可用模型列表
print("\nListing available models:")
print("-" * 50)
try:
    # 列出 Deepseek 的模型
    print("\nDeepseek models:")
    models = client.models.list(provider="deepseek")
    for model_info in models['data']:
        print(f"- {model_info['id']}")
    
    # 列出 OpenRouter 的模型
    print("\nOpenRouter models:")
    models = client.models.list(provider="openrouter")
    for model_info in models['data']:
        print(f"- {model_info['id']}")
        
    # 列出 Grok 的模型
    print("\nGrok models:")
    models = client.models.list(provider="grok")
    for model_info in models['data']:
        print(f"- {model_info['id']}")
except Exception as e:
    print(f"Error listing models: {str(e)}") 