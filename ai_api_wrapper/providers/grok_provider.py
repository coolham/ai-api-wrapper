import httpx
from typing import Dict, Any, List, Optional
from ai_api_wrapper.provider import Provider, LLMError
from ai_api_wrapper.providers.message_converter import OpenAICompliantMessageConverter
from ai_api_wrapper.utils.config_manager import ConfigManager
from ai_api_wrapper.utils.logger import logger
from ai_api_wrapper.config.default_config import (
    HTTP_TIMEOUT,
    HTTP_MAX_RETRIES,
    HTTP_VERIFY_SSL
)
from openai import OpenAI
import os


class GrokProvider(Provider):
    """Grok API 提供者"""
    
    def __init__(self, **kwargs):
        """初始化 Grok 提供者"""
        logger.info("Initializing GrokProvider")
        self.config_manager = ConfigManager()
        self.provider_config = self.config_manager.get_provider_config('grok')
        
        # 从配置中获取基本设置
        self.base_url = self.provider_config.get('base_url', 'https://api.x.ai/v1')
        self.timeout = self.provider_config.get('timeout', HTTP_TIMEOUT)
        self.max_retries = self.provider_config.get('max_retries', HTTP_MAX_RETRIES)
        self.verify_ssl = self.provider_config.get('verify_ssl', HTTP_VERIFY_SSL)
        logger.debug(f"Provider settings - base_url: {self.base_url}, timeout: {self.timeout}, max_retries: {self.max_retries}, verify_ssl: {self.verify_ssl}")
        
        # 从环境变量或 kwargs 获取 API 密钥
        self.api_key = kwargs.get('api_key') or self.provider_config.get('api_key')
        if not self.api_key:
            logger.error("Grok API key is missing")
            raise ValueError("Grok API key is required")
        logger.debug("API key loaded successfully")
        
        # 初始化 OpenAI 客户端
        client_kwargs = {
            "api_key": self.api_key,
            "base_url": self.base_url
        }
        
        # 配置 HTTP 客户端
        http_client = self._configure_http_client()
        if http_client:
            client_kwargs["http_client"] = http_client
        
        # 初始化 OpenAI 客户端
        try:
            self.client = OpenAI(**client_kwargs)
            logger.debug("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise LLMError(f"Failed to initialize OpenAI client: {str(e)}")
        
        # 创建消息转换器
        self.message_converter = OpenAICompliantMessageConverter()
        logger.debug("Message converter initialized")
    
    def _configure_http_client(self) -> Optional[httpx.Client]:
        """配置 HTTP 客户端，处理代理设置

        Returns:
            配置好的 httpx.Client 实例，如果不使用代理则返回 None
        """
        # 检查是否使用代理
        proxy_config = self.provider_config.get('proxy')
        if not proxy_config:
            return None
            
        # 获取代理 URL
        https_proxy = proxy_config.get('https', '')
        http_proxy = proxy_config.get('http', '')
        
        # 优先使用 HTTP 代理
        proxy_url = http_proxy or https_proxy
        
        if not proxy_url:
            return None
            
        # 确保 proxy_url 使用 http:// 前缀
        if not proxy_url.startswith('http://') and not proxy_url.startswith('https://'):
            proxy_url = f"http://{proxy_url}"
            
        try:
            logger.debug(f"Using proxy server: {proxy_url}")
            
            # 创建 httpx 客户端
            return httpx.Client(
                proxy=proxy_url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
        except Exception as e:
            logger.error(f"Proxy configuration failed: {str(e)}")
            return None
    
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
            logger.info(f"Creating chat completion for model: {model}")
            logger.debug(f"Input messages: {messages}")
            
            # 使用默认值或者从配置中获取max_tokens
            if max_tokens is None:
                # 从provider_config中尝试获取默认的max_tokens
                max_tokens = self.provider_config.get('max_tokens', 4000)
                logger.debug(f"Using default max_tokens: {max_tokens}")
            
            # 转换消息格式
            converted_messages = self.message_converter.convert_request(messages)
            logger.debug(f"Converted messages: {converted_messages}")
            
            # 准备请求数据
            request_data = {
                "model": model,
                "messages": converted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,  # 确保不启用流式响应
                **kwargs
            }
            logger.debug(f"Request data: {request_data}")
            
            # 发送请求
            logger.debug(f"Sending request to {self.base_url}/chat/completions")
            try:
                response = self.client.chat.completions.create(
                    model=request_data["model"],
                    messages=request_data["messages"],
                    temperature=request_data["temperature"],
                    max_tokens=request_data["max_tokens"],
                    stream=request_data.get("stream", False),
                    **{k: v for k, v in request_data.items() if k not in ["model", "messages", "temperature", "max_tokens", "stream"]}
                )
                logger.debug("Request successful")
                
                result = response.model_dump()
                logger.debug(f"Response: {result}")
                return result
            except Exception as e:
                logger.error(f"OpenAI client error: {str(e)}")
                raise LLMError(f"OpenAI client error: {str(e)}")
        except Exception as e:
            logger.error(f"Grok API error: {str(e)}")
            raise LLMError(f"Grok API error: {str(e)}")
    
    def models_list(self) -> Dict[str, Any]:
        """列出可用模型"""
        try:
            logger.info("Fetching available models")
            response = self.client.models.list()
            result = response.model_dump()
            logger.debug(f"Successfully retrieved {len(result.get('data', []))} models")
            return result
        except Exception as e:
            logger.error(f"Failed to list Grok models: {str(e)}")
            raise LLMError(f"Failed to list Grok models: {str(e)}")
    
    def model_retrieve(self, model: str) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            logger.info(f"Retrieving information for model: {model}")
            response = self.client.models.retrieve(model)
            result = response.model_dump()
            logger.debug(f"Successfully retrieved model info for: {model}")
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve Grok model {model}: {str(e)}")
            raise LLMError(f"Failed to retrieve Grok model {model}: {str(e)}")
    
    def __del__(self):
        """清理资源"""
        logger.debug("Cleaning up GrokProvider")
