from ai_api_wrapper import UnifiedAIService

# 创建统一服务实例(默认使用OpenAI)
ai = UnifiedAIService()

# 用OpenAI风格的API发送请求
response = ai.chat_completions_create([
    {"role": "system", "content": "你是一位智能助手。"},
    {"role": "user", "content": "解释一下量子计算的基本原理。"}
])

print(response.choices[0].message.content)
