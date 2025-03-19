from abc import ABC, abstractmethod
from pathlib import Path
import importlib
import os
import functools


class LLMError(Exception):
    """Custom exception for LLM errors."""

    def __init__(self, message):
        super().__init__(message)


class Provider(ABC):
    """Base class for AI providers."""
    
    @property
    def provider(self):
        """Return self as the provider."""
        return self
    
    @abstractmethod
    def chat_completions_create(self, model, messages):
        """Abstract method for chat completion calls, to be implemented by each provider."""
        pass


class ProviderFactory:
    """Factory to dynamically load provider instances based on naming conventions."""

    PROVIDERS_DIR = Path(__file__).parent / "providers"
    
    # 定义每个提供商支持的配置字段
    PROVIDER_CONFIG_FIELDS = {
        "openai": ["api_key", "base_url", "timeout", "max_retries"],
        "deepseek": ["api_key", "base_url", "timeout", "max_retries"],
        "grok": ["api_key", "base_url", "timeout", "max_retries", "verify_ssl"],
        "openrouter": ["api_key", "base_url", "timeout", "max_retries", "verify_ssl"]
    }

    @classmethod
    def create_provider(cls, provider_key, config):
        """Dynamically load and create an instance of a provider based on the naming convention."""
        # 过滤配置字段
        supported_fields = cls.PROVIDER_CONFIG_FIELDS.get(provider_key, [])
        filtered_config = {k: v for k, v in config.items() if k in supported_fields}
        
        # Convert provider_key to the expected module and class names
        provider_class_name = f"{provider_key.capitalize()}Provider"
        provider_module_name = f"{provider_key}_provider"

        module_path = f"ai_api_wrapper.providers.{provider_module_name}"

        # Lazily load the module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(
                f"Could not import module {module_path}: {str(e)}. Please ensure the provider is supported by doing ProviderFactory.get_supported_providers()"
            )

        # Instantiate the provider class
        provider_class = getattr(module, provider_class_name)
        return provider_class(**filtered_config)

    @classmethod
    @functools.cache
    def get_supported_providers(cls):
        """List all supported provider names based on files present in the providers directory."""
        provider_files = Path(cls.PROVIDERS_DIR).glob("*_provider.py")
        return {file.stem.replace("_provider", "") for file in provider_files}
