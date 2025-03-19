"""
OpenRouter Provider 使用示例

这个示例展示了如何使用 ai_api_wrapper 库通过 OpenRouter 访问各种 AI 模型。
OpenRouter 是一个统一的 API 网关，让你可以访问多个 AI 提供商（如 DeepSeek、Anthropic、OpenAI 等）的模型。

使用前准备：
1. 注册 OpenRouter 账号：https://openrouter.ai/
2. 获取 API Key：在 OpenRouter 控制台生成
3. 安装依赖：pip install ai-api-wrapper
4. 在项目根目录的 .env 文件中配置 OPENROUTER_API_KEY

注意：确保 .env 文件中包含 OPENROUTER_API_KEY 配置
"""

import os
from dotenv import load_dotenv
from ai_api_wrapper import Client
from ai_api_wrapper.provider import LLMError
from ai_api_wrapper.utils.logger import logger


def get_openrouter_api_key():
    """
    从环境变量或 .env 文件获取 OpenRouter API Key
    """
    # 加载 .env 文件
    load_dotenv()
    
    # 获取 API Key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("请在 .env 文件中配置 OPENROUTER_API_KEY")
    return api_key


def chat_with_ai():
    """
    基础聊天示例
    展示如何使用 OpenRouter 进行简单的对话
    """
    try:
        # 获取 API Key
        api_key = get_openrouter_api_key()
        
        # 初始化 Client 实例
        client = Client()

        # 准备对话消息
        # messages 是一个列表，每个消息都是一个字典，包含 role 和 content
        # role 可以是 "system"、"user" 或 "assistant"
        messages = [
            {"role": "system", "content": "你是一个专业的 Python 编程助手，擅长解释代码和提供编程建议。"},
            {"role": "user", "content": "请解释一下 Python 中的装饰器是什么，并给出一个简单的例子。"}
        ]

        # 发送聊天请求
        # temperature: 控制输出的随机性，0.0 最确定，1.0 最随机
        # max_tokens: 控制输出的最大长度
        response = client.chat.completions.create(
            model="openrouter:gpt-4o",  # 使用 gpt-4o 的模型
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        # 处理响应
        print("\n=== AI 助手回答 ===")
        if isinstance(response, dict):
            print(response.get("content", "无响应内容"))
            usage = response.get("usage", {})
            print(f"\nToken 使用情况：")
            print(f"- 提示词 tokens: {usage.get('prompt_tokens', 0)}")
            print(f"- 回复 tokens: {usage.get('completion_tokens', 0)}")
            print(f"- 总 tokens: {usage.get('total_tokens', 0)}")
        else:
            print(response.choices[0].message.content)
            print(f"\nToken 使用情况：")
            print(f"- 提示词 tokens: {response.usage.prompt_tokens}")
            print(f"- 回复 tokens: {response.usage.completion_tokens}")
            print(f"- 总 tokens: {response.usage.total_tokens}")
        print("==================\n")

    except LLMError as e:
        logger.error(f"聊天请求失败: {str(e)}")
    except ValueError as e:
        logger.error(f"配置错误: {str(e)}")
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")


def explore_available_models():
    """
    探索可用模型示例
    展示如何获取 OpenRouter 支持的所有模型列表
    """
    try:
        # 获取 API Key
        api_key = get_openrouter_api_key()
        
        # 初始化 Client 实例
        client = Client()

        # 获取可用模型列表
        models = client.models.list(provider="openrouter")

        # 按提供商分组显示模型
        print("\n=== OpenRouter 可用模型列表 ===")
        if isinstance(models, dict):
            models_data = models.get("data", [])
        else:
            models_data = models.data

        providers = {}
        for model in models_data:
            provider = model.get("provider") if isinstance(model, dict) else model.provider
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)

        for provider, provider_models in providers.items():
            print(f"\n{provider} 的模型:")
            for model in provider_models:
                if isinstance(model, dict):
                    print(f"- {model.get('id')}")
                    print(f"  名称: {model.get('name')}")
                    print(f"  上下文长度: {model.get('context_length')}")
                    print(f"  支持函数调用: {'是' if model.get('supports_function_calling') else '否'}")
                else:
                    print(f"- {model.id}")
                    print(f"  名称: {model.name}")
                    print(f"  上下文长度: {model.context_length}")
                    print(f"  支持函数调用: {'是' if model.supports_function_calling else '否'}")
        print("\n==============================\n")

    except LLMError as e:
        logger.error(f"获取模型列表失败: {str(e)}")
    except ValueError as e:
        logger.error(f"配置错误: {str(e)}")
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")


def get_model_details():
    """
    获取模型详情示例
    展示如何获取特定模型的详细信息
    """
    try:
        # 获取 API Key
        api_key = get_openrouter_api_key()
        
        # 初始化 Client 实例
        client = Client(default_service="openrouter")

        # 获取特定模型信息
        model_id = "openrouter:mistralai/mistral-small"
        model_info = client.models.retrieve(model_id)

        # 打印模型详细信息
        print("\n=== 模型详细信息 ===")
        if isinstance(model_info, dict):
            print(f"模型 ID: {model_info.get('id')}")
            print(f"名称: {model_info.get('name')}")
            print(f"提供商: {model_info.get('provider')}")
            print(f"上下文长度: {model_info.get('context_length')}")
            print(f"支持函数调用: {'是' if model_info.get('supports_function_calling') else '否'}")
        else:
            print(f"模型 ID: {model_info.id}")
            print(f"名称: {model_info.name}")
            print(f"提供商: {model_info.provider}")
            print(f"上下文长度: {model_info.context_length}")
            print(f"支持函数调用: {'是' if model_info.supports_function_calling else '否'}")
        print("==================\n")

    except LLMError as e:
        logger.error(f"获取模型信息失败: {str(e)}")
    except ValueError as e:
        logger.error(f"配置错误: {str(e)}")
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")


def main():
    """
    主函数：运行所有示例
    """
    print("开始运行 OpenRouter Provider 示例...\n")
    
    try:
        # 运行基础聊天示例
        print("1. 测试基础聊天功能")
        chat_with_ai()
        
        # 运行模型列表示例
        print("2. 获取可用模型列表")
        explore_available_models()
        
        # 运行模型详情示例
        print("3. 获取模型详细信息")
        # get_model_details()
        
        print("示例运行完成！")
    except ValueError as e:
        logger.error(f"程序运行失败: {str(e)}")
        print("\n请确保在 .env 文件中正确配置了 OPENROUTER_API_KEY")


if __name__ == "__main__":
    main()
