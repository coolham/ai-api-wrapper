import httpx
from typing import Dict, Any, List, Optional
from ai_api_wrapper.provider import Provider, LLMError
from ai_api_wrapper.providers.message_converter import OpenAICompliantMessageConverter
from ai_api_wrapper.utils.config_manager import ConfigManager


class OpenrouterProvider(Provider):
    """OpenRouter API 提供者"""
    
    def __init__(self, **kwargs):
        """初始化 OpenRouter 提供者"""
        self.config_manager = ConfigManager()
        self.provider_config = self.config_manager.get_provider_config('openrouter')
        
        # 从配置中获取基本设置
        self.base_url = self.provider_config.get('base_url', 'https://openrouter.ai/api/v1')
        self.timeout = self.provider_config.get('timeout', 30.0)
        self.max_retries = self.provider_config.get('max_retries', 3)
        self.verify_ssl = self.provider_config.get('verify_ssl', True)
        
        # 从环境变量或 kwargs 获取 API 密钥
        self.api_key = kwargs.get('api_key') or self.provider_config.get('api_key')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        # 创建 HTTP 客户端
        try:
            client_kwargs = {
                "base_url": self.base_url,
                "timeout": self.timeout,
                "verify": self.verify_ssl
            }
            
            self.http_client = httpx.Client(**client_kwargs)
            
            # 设置请求头
            self.http_client.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/xingshizai/ai-api-wrapper",  # OpenRouter 要求
                "X-Title": "AI API Wrapper",  # OpenRouter 要求
                "Content-Type": "application/json"
            })
        except Exception as e:
            raise LLMError(f"Failed to initialize HTTP client: {str(e)}")
        
        # 创建消息转换器
        self.message_converter = OpenAICompliantMessageConverter()
    
    def chat_completions_create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建聊天完成"""
        try:
            # 获取模型配置
            model_config = self.config_manager.get_model_config('openrouter', model)
            
            # 使用模型配置中的默认值（如果未提供）
            if max_tokens is None:
                max_tokens = model_config.get('max_tokens', 4000)
            
            # 转换消息格式
            converted_messages = self.message_converter.convert_request(messages)
            
            # 准备请求数据
            data = {
                "model": model,
                "messages": converted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 添加服务特定参数
            if "service" in model_config:
                data["service"] = model_config["service"]
            
            # 添加其他参数
            for key, value in kwargs.items():
                if key not in ["service"]:  # 排除已处理的参数
                    data[key] = value
            
            # 发送请求
            response = self.http_client.post("/chat/completions", json=data)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            raise LLMError(f"OpenRouter API error: {str(e)}")
    
    def models_list(self) -> Dict[str, Any]:
        """列出可用模型"""
        try:
            response = self.http_client.get("/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise LLMError(f"Failed to list OpenRouter models: {str(e)}")
    
    def model_retrieve(self, model: str) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            response = self.http_client.get(f"/models/{model}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise LLMError(f"Failed to retrieve OpenRouter model {model}: {str(e)}")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'http_client'):
            self.http_client.close()
