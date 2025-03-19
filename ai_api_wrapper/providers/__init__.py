"""Provider registry module."""

from ai_api_wrapper.providers.grok_provider import GrokProvider
from ai_api_wrapper.providers.deepseek_provider import DeepseekProvider


# 注册提供商
PROVIDERS = {
    "grok": GrokProvider,
    "deepseek": DeepseekProvider,
}
