import sys
from dotenv import load_dotenv, find_dotenv
import ai_api_wrapper as ai
import time
import base64
from pathlib import Path

# 加载环境变量
load_dotenv(find_dotenv())

# 创建客户端
client = ai.Client()

def encode_image(image_path):
    """将图片转换为 base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 准备消息
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What's the latest news about Grok AI?"}
]

# 使用 Grok 模型
model = "grok:grok-2-1212"  # 使用新的三层标识方式
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
    models = client.models.list(provider="grok")  # 指定提供者
    for model_info in models['data']:
        print(f"- {model_info['id']}")
except Exception as e:
    print(f"Error listing models: {str(e)}")

# 演示多轮对话
print("\nTesting multi-turn conversation:")
print("-" * 50)
conversation_messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "你好，请介绍一下你自己。"}
]

try:
    # 第一轮对话
    response = client.chat.completions.create(
        model="grok:grok-2-1212",
        messages=conversation_messages,
        temperature=0.7
    )
    print(f"Assistant: {response['choices'][0]['message']['content']}\n")
    
    # 添加助手的回复到对话历史
    conversation_messages.append(response['choices'][0]['message'])
    
    # 第二轮对话
    conversation_messages.append({"role": "user", "content": "你能帮我写一个Python函数吗？"})
    response = client.chat.completions.create(
        model="grok:grok-2-1212",
        messages=conversation_messages,
        temperature=0.7
    )
    print(f"Assistant: {response['choices'][0]['message']['content']}\n")
    
    # 添加助手的回复到对话历史
    conversation_messages.append(response['choices'][0]['message'])
    
    # 第三轮对话
    conversation_messages.append({"role": "user", "content": "这个函数的时间复杂度是多少？"})
    response = client.chat.completions.create(
        model="grok:grok-2-1212",
        messages=conversation_messages,
        temperature=0.7
    )
    print(f"Assistant: {response['choices'][0]['message']['content']}\n")
except Exception as e:
    print(f"Error in conversation: {str(e)}")

# 演示流式输出
print("\nTesting streaming output:")
print("-" * 50)
stream_messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "请写一首关于春天的诗。"}
]

try:
    print("Assistant: ", end="", flush=True)
    response = client.chat.completions.create(
        model="grok:grok-2-1212",
        messages=stream_messages,
        temperature=0.7
    )
    
    # 模拟流式输出
    content = response['choices'][0]['message']['content']
    for char in content:
        print(char, end="", flush=True)
        time.sleep(0.05)  # 添加小延迟使输出更自然
    print("\n")
except Exception as e:
    print(f"Error in streaming: {str(e)}")

# 演示使用不同温度设置
print("\nTesting different temperature settings:")
print("-" * 50)
temp_messages = [
    {"role": "system", "content": "You are a creative AI assistant."},
    {"role": "user", "content": "请用三个词描述人工智能的未来。"}
]

try:
    # 使用较低的温度（更保守的回答）
    print("Low temperature (0.2):")
    response = client.chat.completions.create(
        model="grok:grok-2-1212",
        messages=temp_messages,
        temperature=0.2
    )
    print(f"Assistant: {response['choices'][0]['message']['content']}\n")
    
    # 使用较高的温度（更有创造性的回答）
    print("High temperature (0.8):")
    response = client.chat.completions.create(
        model="grok:grok-2-1212",
        messages=temp_messages,
        temperature=0.8
    )
    print(f"Assistant: {response['choices'][0]['message']['content']}\n")
except Exception as e:
    print(f"Error in temperature test: {str(e)}")

# 演示图片识别功能
print("\nTesting image recognition:")
print("-" * 50)

# 准备测试图片路径
image_path = Path("examples/test_images/test.jpg")
if not image_path.exists():
    print(f"测试图片不存在: {image_path}")
else:
    try:
        # 将图片转换为 base64
        base64_image = encode_image(image_path)
        
        # 准备包含图片的消息
        vision_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请描述这张图片的内容。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # 使用 Grok Vision 模型
        print("使用 Grok Vision 模型分析图片...")
        response = client.chat.completions.create(
            model="grok:grok-2-vision-1212",
            messages=vision_messages,
            max_tokens=1000
        )
        print(f"图片描述:\n{response['choices'][0]['message']['content']}\n")
        
        # 测试图片问答
        print("测试图片问答...")
        vision_messages[0]["content"][0]["text"] = "这张图片中的主要颜色是什么？"
        response = client.chat.completions.create(
            model="grok:grok-2-vision-1212",
            messages=vision_messages,
            max_tokens=1000
        )
        print(f"问答结果:\n{response['choices'][0]['message']['content']}\n")
        
    except Exception as e:
        print(f"图片识别测试出错: {str(e)}")

# 演示使用不同的服务提供商
print("\nTesting different service providers:")
print("-" * 50)
test_messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What's the difference between different service providers?"}
]

