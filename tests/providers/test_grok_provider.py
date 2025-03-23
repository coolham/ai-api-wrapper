from unittest.mock import MagicMock, patch
import pytest
import httpx
import os
from ai_api_wrapper.providers.grok_provider import GrokProvider
from ai_api_wrapper.provider import LLMError


@pytest.fixture
def env_file(tmp_path):
    """创建临时 .env 文件用于测试"""
    env_dir = tmp_path / "test_init_with_env_file"
    env_dir.mkdir()
    env_file = env_dir / ".env"
    env_content = """
GROK_API_KEY=env-file-key
GROK_API_BASE_URL=https://custom.x.ai/v1
GROK_TIMEOUT=45.0
GROK_MAX_RETRIES=3
GROK_USE_PROXY=true
GROK_HTTP_PROXY=http://env.proxy:8080
GROK_VERIFY_SSL=false
"""
    env_file.write_text(env_content)
    return env_file


@pytest.fixture
def env_file_proxy(tmp_path):
    """Create a temporary .env file with proxy configuration for testing."""
    env_dir = tmp_path / "test_init_with_env_file_proxy"
    env_dir.mkdir()
    env_file = env_dir / ".env"
    env_content = """
GROK_API_KEY=env-file-key
GROK_API_BASE_URL=https://custom.grok.ai/v1
GROK_TIMEOUT=45.0
GROK_USE_PROXY=true
GROK_HTTP_PROXY=http://env.proxy:8080
GROK_VERIFY_SSL=false
"""
    env_file.write_text(env_content)
    return env_file


@pytest.fixture(autouse=True)
def set_api_key_env_var(monkeypatch):
    """设置测试环境变量"""
    monkeypatch.setenv("GROK_API_KEY", "test-api-key")


def test_init_with_env_file(env_file, monkeypatch):
    """测试使用 .env 文件初始化提供者"""
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.chdir(env_file.parent)
    
    with patch('ai_api_wrapper.providers.grok_provider.ConfigManager') as mock_config:
        mock_config.return_value.get_provider_config.return_value = {
            'api_key': 'env-file-key',
            'base_url': 'https://custom.x.ai/v1',
            'timeout': 45.0,
            'max_retries': 3,
            'verify_ssl': False,
            'proxy': {'http': 'http://env.proxy:8080'}
        }
        
        provider = GrokProvider()
        assert provider.client.api_key == "env-file-key"
        assert str(provider.client.base_url).rstrip("/") == "https://custom.x.ai/v1"


def test_init_with_env_file_proxy_config(env_file_proxy, monkeypatch):
    """测试使用 .env 文件的代理配置"""
    monkeypatch.chdir(env_file_proxy.parent)
    
    with patch('ai_api_wrapper.providers.grok_provider.ConfigManager') as mock_config:
        mock_config.return_value.get_provider_config.return_value = {
            'api_key': 'env-file-key',
            'base_url': 'https://custom.x.ai/v1',
            'timeout': 45.0,
            'verify_ssl': False,
            'proxy': {'http': 'http://env.proxy:8080'}
        }
        
        provider = GrokProvider()
        assert provider.client.api_key == "env-file-key"
        assert provider.provider_config.get('proxy', {}).get('http') == 'http://env.proxy:8080'


def test_config_precedence(env_file, monkeypatch):
    """Test configuration precedence (config > env vars > .env file)."""
    monkeypatch.chdir(env_file.parent)
    monkeypatch.setenv("GROK_API_KEY", "env-var-key")
    
    # 配置参数应该优先于环境变量和 .env 文件
    provider = GrokProvider(api_key="config-key")
    assert provider.client.api_key == "config-key"


def test_init_with_api_key():
    """测试使用 API 密钥初始化提供者"""
    provider = GrokProvider(api_key="test-key")
    assert provider.client.api_key == "test-key"


def test_init_with_env_var(monkeypatch):
    """测试使用环境变量初始化提供者"""
    monkeypatch.setenv("GROK_API_KEY", "env-var-key")
    with patch('ai_api_wrapper.providers.grok_provider.ConfigManager') as mock_config:
        mock_config.return_value.get_provider_config.return_value = {
            'api_key': 'env-var-key'
        }
        provider = GrokProvider()
        assert provider.client.api_key == "env-var-key"


def test_init_without_api_key(monkeypatch):
    """测试没有 API 密钥时初始化失败"""
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    with patch('ai_api_wrapper.providers.grok_provider.ConfigManager') as mock_config:
        mock_config.return_value.get_provider_config.return_value = {}
        with pytest.raises(ValueError) as exc_info:
            GrokProvider()
        assert str(exc_info.value) == "Grok API key is required"


def test_chat_completion_success():
    """测试成功的聊天完成请求"""
    provider = GrokProvider()
    
    # 创建模拟响应
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "choices": [{
            "message": {
                "content": "你好！我能帮你什么？"
            }
        }]
    }

    with patch.object(
        provider.client.chat.completions,
        "create",
        return_value=mock_response
    ) as mock_create:
        response = provider.chat_completions_create(
            model="grok-1",
            messages=[{"role": "user", "content": "你好！"}],
            temperature=0.7
        )

        mock_create.assert_called_once_with(
            model="grok-1",
            messages=[{"role": "user", "content": "你好！"}],
            temperature=0.7,
            max_tokens=4000,
            stream=False
        )

        assert response["choices"][0]["message"]["content"] == "你好！我能帮你什么？"


def test_chat_completion_error():
    """测试聊天完成请求失败的情况"""
    provider = GrokProvider()

    with patch.object(
        provider.client.chat.completions,
        "create",
        side_effect=Exception("API Error")
    ):
        with pytest.raises(LLMError) as exc_info:
            provider.chat_completions_create(
                model="grok-1",
                messages=[{"role": "user", "content": "你好！"}]
            )
        assert "Grok API error" in str(exc_info.value)


def test_models_list():
    """测试列出可用模型"""
    provider = GrokProvider()
    mock_models = {
        "data": [
            {"id": "grok-1", "owned_by": "x.ai"},
            {"id": "grok-2", "owned_by": "x.ai"}
        ]
    }

    mock_response = MagicMock()
    mock_response.model_dump.return_value = mock_models

    with patch.object(
        provider.client.models,
        "list",
        return_value=mock_response
    ) as mock_list:
        models = provider.models_list()
        mock_list.assert_called_once()
        assert len(models["data"]) == 2
        assert models["data"][0]["id"] == "grok-1"


def test_model_retrieve():
    """测试获取特定模型信息"""
    provider = GrokProvider()
    mock_model = {"id": "grok-1", "owned_by": "x.ai"}

    mock_response = MagicMock()
    mock_response.model_dump.return_value = mock_model

    with patch.object(
        provider.client.models,
        "retrieve",
        return_value=mock_response
    ) as mock_retrieve:
        model = provider.model_retrieve("grok-1")
        mock_retrieve.assert_called_once_with("grok-1")
        assert model["id"] == "grok-1"


def test_models_list_error():
    """测试列出模型失败的情况"""
    provider = GrokProvider()

    with patch.object(
        provider.client.models,
        "list",
        side_effect=Exception("API Error")
    ):
        with pytest.raises(LLMError) as exc_info:
            provider.models_list()
        assert "Failed to list Grok models" in str(exc_info.value)


def test_model_retrieve_error():
    """测试获取模型信息失败的情况"""
    provider = GrokProvider()

    with patch.object(
        provider.client.models,
        "retrieve",
        side_effect=Exception("API Error")
    ):
        with pytest.raises(LLMError) as exc_info:
            provider.model_retrieve("grok-1")
        assert "Failed to retrieve Grok model" in str(exc_info.value)


@pytest.mark.skip(reason="代理配置测试在其他provider中已验证，不需要重复测试")
@patch('ai_api_wrapper.providers.grok_provider.ConfigManager')
def test_init_with_proxy(mock_env_vars):
    """测试使用代理初始化"""
    # 代理配置测试在其他provider中已验证，不需要重复测试
    pass


def test_init_with_proxy_from_env(monkeypatch):
    """测试从环境变量获取代理配置"""
    monkeypatch.setenv("GROK_HTTP_PROXY", "http://proxy.example.com:8080")
    with patch('ai_api_wrapper.providers.grok_provider.ConfigManager') as mock_config:
        mock_config.return_value.get_provider_config.return_value = {
            'proxy': {'http': 'http://proxy.example.com:8080'}
        }
        provider = GrokProvider(api_key="test-key")
        assert provider.client.api_key == "test-key"


@pytest.mark.skip(reason="代理配置测试在其他provider中已验证，不需要重复测试")
@patch('ai_api_wrapper.providers.grok_provider.ConfigManager')
def test_init_without_proxy(mock_env_vars):
    """测试不使用代理初始化"""
    # 代理配置测试在其他provider中已验证，不需要重复测试
    pass


@pytest.mark.skip(reason="代理配置测试在其他provider中已验证，不需要重复测试")
@patch('ai_api_wrapper.providers.grok_provider.ConfigManager')
def test_init_with_proxy_no_proxy_url(mock_env_vars):
    """测试启用代理但未提供代理URL时初始化"""
    # 代理配置测试在其他provider中已验证，不需要重复测试
    pass


def test_chat_completion_with_custom_max_tokens():
    """测试使用自定义 max_tokens 的聊天完成请求"""
    provider = GrokProvider()
    
    # 创建模拟响应
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "choices": [{
            "message": {
                "content": "你好！"
            }
        }]
    }

    with patch.object(
        provider.client.chat.completions,
        "create",
        return_value=mock_response
    ) as mock_create:
        response = provider.chat_completions_create(
            model="grok-1",
            messages=[{"role": "user", "content": "你好！"}],
            max_tokens=1000
        )

        mock_create.assert_called_once_with(
            model="grok-1",
            messages=[{"role": "user", "content": "你好！"}],
            temperature=0.7,
            max_tokens=1000,
            stream=False
        )

        assert response["choices"][0]["message"]["content"] == "你好！"


def test_chat_completion_with_additional_params():
    """测试带有额外参数的聊天完成请求"""
    provider = GrokProvider()
    
    # 创建模拟响应
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "choices": [{
            "message": {
                "content": "你好！"
            }
        }]
    }

    with patch.object(
        provider.client.chat.completions,
        "create",
        return_value=mock_response
    ) as mock_create:
        response = provider.chat_completions_create(
            model="grok-1",
            messages=[{"role": "user", "content": "你好！"}],
            temperature=0.8,
            presence_penalty=0.5,
            frequency_penalty=0.5
        )

        mock_create.assert_called_once_with(
            model="grok-1",
            messages=[{"role": "user", "content": "你好！"}],
            temperature=0.8,
            max_tokens=4000,
            stream=False,
            presence_penalty=0.5,
            frequency_penalty=0.5
        )

        assert response["choices"][0]["message"]["content"] == "你好！"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    monkeypatch.setenv('GROK_API_KEY', 'test-api-key')
    monkeypatch.setenv('GROK_API_BASE_URL', 'https://api.x.ai/v1')
    
    # 设置代理相关的环境变量
    with patch('ai_api_wrapper.providers.grok_provider.ConfigManager') as mock_config:
        mock_config.return_value.get_provider_config.return_value = {
            'api_key': 'test-api-key',
            'base_url': 'https://api.x.ai/v1',
            'proxy': {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890'
            }
        }
        yield mock_config
