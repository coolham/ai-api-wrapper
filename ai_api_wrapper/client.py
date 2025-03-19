from typing import Dict, Any, List, Optional, Tuple
from .provider import Provider, ProviderFactory
from .utils.tools import Tools
from .utils.config_manager import ConfigManager
from .utils.logger import logger


class Models:
    """模型管理类"""
    def __init__(self, client):
        self.client = client
    
    def list(self, provider: str, **kwargs):
        """获取模型列表
        
        Args:
            provider: 服务提供商
            **kwargs: 请求参数
            
        Returns:
            dict: 响应结果
        """
        provider_instance = self.client._get_provider(provider)
        return provider_instance.models_list(**kwargs)
    
    def retrieve(self, model: str, **kwargs):
        """获取模型信息
        
        Args:
            model: 模型名称
            **kwargs: 请求参数
            
        Returns:
            dict: 响应结果
        """
        provider, model_name = self.client._parse_model_name(model)
        provider_instance = self.client._get_provider(provider)
        return provider_instance.model_retrieve(model_name, **kwargs)

class ChatCompletions:
    """聊天补全接口"""
    def __init__(self, client):
        self.client = client

    def _extract_thinking_content(self, response):
        """提取思考内容"""
        if hasattr(response, "choices") and response.choices:
            message = response.choices[0].message
            if hasattr(message, "content") and message.content:
                content = message.content.strip()
                if content.startswith("<think>") and "</think>" in content:
                    start_idx = len("<think>")
                    end_idx = content.find("</think>")
                    thinking_content = content[start_idx:end_idx].strip()
                    message.reasoning_content = thinking_content
                    message.content = content[end_idx + len("</think>"):].strip()
        return response

    def _tool_runner(self, provider, model_name: str, messages: list, tools: any, max_turns: int, **kwargs):
        """处理工具执行循环"""
        if isinstance(tools, Tools):
            tools_instance = tools
            kwargs["tools"] = tools_instance.tools()
        else:
            if not all(callable(tool) for tool in tools):
                raise ValueError("One or more tools is not callable")
            tools_instance = Tools(tools)
            kwargs["tools"] = tools_instance.tools()

        turns = 0
        intermediate_responses = []
        intermediate_messages = []

        while turns < max_turns:
            response = provider.chat_completions_create(model_name, messages, **kwargs)
            response = self._extract_thinking_content(response)
            intermediate_responses.append(response)

            tool_calls = getattr(response.choices[0].message, "tool_calls", None) if hasattr(response, "choices") else None
            intermediate_messages.append(response.choices[0].message)

            if not tool_calls:
                response.intermediate_responses = intermediate_responses[:-1]
                response.choices[0].intermediate_messages = intermediate_messages
                return response

            results, tool_messages = tools_instance.execute_tool(tool_calls)
            intermediate_messages.extend(tool_messages)
            messages.extend([response.choices[0].message, *tool_messages])
            turns += 1

        response.intermediate_responses = intermediate_responses[:-1]
        response.choices[0].intermediate_messages = intermediate_messages
        return response

    def create(self, **kwargs):
        """创建聊天补全
        
        Args:
            **kwargs: 请求参数
            
        Returns:
            dict: 响应结果
        """
        model = kwargs.get("model")
        if not model:
            raise ValueError("Model name is required")
            
        provider, model_name = self.client._parse_model_name(model)
        provider_instance = self.client._get_provider(provider)
        
        # 更新模型名称
        kwargs["model"] = model_name
        
        # 提取工具相关参数
        max_turns = kwargs.pop("max_turns", None)
        tools = kwargs.get("tools", None)
        
        # 检查是否需要工具执行
        if max_turns is not None and tools is not None:
            return self._tool_runner(
                provider_instance,
                model_name,
                kwargs.get("messages", []).copy(),
                tools,
                max_turns,
                **kwargs
            )
        
        # 默认行为
        response = provider_instance.chat_completions_create(**kwargs)
        return self._extract_thinking_content(response)

class Chat:
    """聊天接口"""
    def __init__(self, client):
        self.client = client
    
    @property
    def completions(self) -> ChatCompletions:
        """获取聊天补全接口"""
        return ChatCompletions(self.client)

class Client:
    """AI API 客户端"""
    
    def __init__(self, proxy_config: Optional[Dict[str, str]] = None):
        """初始化客户端
        
        Args:
            proxy_config: 代理配置，格式为 {"http": "http://proxy:port", "https": "https://proxy:port"}
        """
        self.providers = {}  # 存储所有提供者实例
        self.config_manager = ConfigManager()
        self.proxy_config = proxy_config
        logger.info("Client initialized with proxy config: %s", proxy_config)
        
    def _get_provider(self, provider_name: str) -> Provider:
        """获取指定的提供者实例
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            Provider: 提供者实例
        """
        if provider_name not in self.providers:
            logger.info(f"Creating new provider instance for: {provider_name}")
          
            # 获取提供商配置
            provider_config = self.config_manager.get_provider_config(provider_name)
            logger.info(f"Provider config for {provider_name}: {provider_config}")
            
            # 添加代理配置
            if self.proxy_config:
                provider_config["proxy"] = self.proxy_config
                logger.info(f"Added proxy config to provider {provider_name}: {self.proxy_config}")
            
            # 创建提供者实例
            self.providers[provider_name] = ProviderFactory.create_provider(provider_name, provider_config)
            logger.info(f"Provider instance created for: {provider_name}")
        else:
            logger.info(f"Using existing provider instance for: {provider_name}")
            
        return self.providers[provider_name]
    
    def _parse_model_name(self, model: str) -> Tuple[str, str]:
        """解析模型名称
        
        Args:
            model: 模型名称，格式为 "provider:model"
            
        Returns:
            Tuple[str, str]: (provider, model_name)
        """
        parts = model.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid model format: {model}")
        return parts[0], parts[1]
    
    @property
    def chat(self) -> Chat:
        """获取聊天接口"""
        return Chat(self)
    
    @property
    def models(self) -> Models:
        """获取模型接口"""
        return Models(self)
