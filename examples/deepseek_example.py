import sys
from dotenv import load_dotenv, find_dotenv
import ai_api_wrapper as ai

# 加载环境变量
load_dotenv(find_dotenv())

# 代理配置（如果需要）
proxy_config = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# 创建客户端（可以选择是否使用代理）
# client = ai.Client(proxy_config=proxy_config)  # 使用代理
client = ai.Client()  # 不使用代理

# 准备消息
messages = [
    {"role": "system", "content": "Talk using Pirate English."},
    {"role": "user", "content": "Tell me a joke in 1 line."},
]

# 使用 DeepSeek 模型进行测试
models = [
    "deepseek:deepseek-chat",
    "deepseek:deepseek-reasoner"
]

for model in models:
    print(f"\nTesting model: {model}")
    print("-" * 50)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.75
        )
        if isinstance(response, dict):
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
            print(f"Content:\n{content}\n")
        else:
            print(f"Content:\n{response.choices[0].message.content}\n")
            if hasattr(response.choices[0].message, 'reasoning_content'):
                print(f"Reasoning content:\n{response.choices[0].message.reasoning_content}\n")
    except Exception as e:
        print(f"Error with {model}: {str(e)}") 