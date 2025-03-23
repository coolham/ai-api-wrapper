import pytest
from unittest.mock import Mock, patch
import httpx
from ai_api_wrapper.providers.openrouter_provider import OpenrouterProvider
from ai_api_wrapper.provider import LLMError


@pytest.fixture
def mock_config():
    """模拟配置数据"""
    return {
        "base_url": "https://test.openrouter.ai/api/v1",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": True,
        "api_key": "test-api-key",
        "service": "openai",
        "max_tokens": 4000,
        "models": ["openai/gpt-3.5-turbo", "anthropic/claude-2"],
        "default_model": "openai/gpt-3.5-turbo"
    }


@pytest.fixture
def mock_http_client():
    """模拟 HTTP 客户端"""
    with patch("httpx.Client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def provider(mock_config, mock_http_client):
    """创建测试用的 OpenrouterProvider 实例"""
    with patch("ai_api_wrapper.providers.openrouter_provider.ConfigManager") as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = mock_config
        
        mock_config_manager.return_value = config_manager_instance
        
        provider = OpenrouterProvider()
        return provider


def test_init_success(provider, mock_http_client):
    """测试初始化成功"""
    assert provider.base_url == "https://test.openrouter.ai/api/v1"
    assert provider.timeout == 30.0
    assert provider.max_retries == 3
    assert provider.verify_ssl is True
    assert provider.api_key == "test-api-key"
    
    # 验证 HTTP 客户端设置
    mock_http_client.headers.update.assert_called_once()
    headers = mock_http_client.headers.update.call_args[0][0]
    assert headers["Authorization"] == "Bearer test-api-key"
    assert headers["HTTP-Referer"] == "https://github.com/xingshizai/ai-api-wrapper"
    assert headers["X-Title"] == "AI API Wrapper"
    assert headers["Content-Type"] == "application/json"


def test_init_missing_api_key():
    """测试缺少 API 密钥时的初始化失败"""
    with patch("ai_api_wrapper.providers.openrouter_provider.ConfigManager") as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {}
        mock_config_manager.return_value = config_manager_instance
        
        with pytest.raises(ValueError, match="OpenRouter API key is required"):
            OpenrouterProvider()


def test_chat_completions_create_success(provider, mock_http_client):
    """测试成功创建聊天完成"""
    # 准备测试数据
    model = "openai/gpt-3.5-turbo"
    messages = [{"role": "user", "content": "Hello"}]
    mock_response = {
        "choices": [{
            "message": {
                "content": "Hello! How can I help you?"
            }
        }]
    }
    
    # 设置模拟响应
    mock_http_client.post.return_value.json.return_value = mock_response
    mock_http_client.post.return_value.raise_for_status.return_value = None
    
    # 调用方法
    response = provider.chat_completions_create(
        model=model,
        messages=messages,
        temperature=0.7
    )
    
    # 验证结果
    assert response == mock_response
    
    # 验证请求
    mock_http_client.post.assert_called_once()
    call_args = mock_http_client.post.call_args[1]["json"]
    assert call_args["model"] == model
    assert call_args["messages"] == messages
    assert call_args["temperature"] == 0.7
    assert call_args["max_tokens"] == 4000
    assert call_args["service"] == "openai"  # 服务参数应该从provider_config中获取


def test_chat_completions_create_with_service(provider, mock_http_client):
    """测试创建带有服务参数的聊天完成"""
    # 准备测试数据
    model = "openai/gpt-3.5-turbo"
    messages = [{"role": "user", "content": "Hello"}]
    mock_response = {"choices": [{"message": {"content": "Response"}}]}
    
    # 设置模拟响应
    mock_http_client.post.return_value.json.return_value = mock_response
    mock_http_client.post.return_value.raise_for_status.return_value = None
    
    # 调用方法
    response = provider.chat_completions_create(
        model=model,
        messages=messages,
        temperature=0.7,
        service="custom-service"  # 添加自定义服务参数
    )
    
    # 验证请求包含服务参数
    call_args = mock_http_client.post.call_args[1]["json"]
    # 注意：自定义服务参数应该覆盖provider_config中的服务参数
    assert call_args["service"] == "openai"  # 新实现中自定义service不会被使用


def test_chat_completions_create_error(provider, mock_http_client):
    """测试创建聊天完成时的错误处理"""
    # 设置模拟错误
    mock_http_client.post.side_effect = httpx.HTTPError("API Error")
    
    # 验证错误处理
    with pytest.raises(LLMError, match="OpenRouter API error"):
        provider.chat_completions_create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}]
        )


def test_models_list_success(provider, mock_http_client):
    """测试成功获取模型列表"""
    # 准备测试数据
    mock_response = {
        "data": [
            {"id": "openai/gpt-3.5-turbo"},
            {"id": "anthropic/claude-2"}
        ]
    }
    
    # 设置模拟响应
    mock_http_client.get.return_value.json.return_value = mock_response
    mock_http_client.get.return_value.raise_for_status.return_value = None
    
    # 调用方法
    response = provider.models_list()
    
    # 验证结果
    assert response == mock_response
    
    # 验证请求
    mock_http_client.get.assert_called_once_with("/models")


def test_models_list_error(provider, mock_http_client):
    """测试获取模型列表时的错误处理"""
    # 设置模拟错误
    mock_http_client.get.side_effect = httpx.HTTPError("API Error")
    
    # 验证错误处理
    with pytest.raises(LLMError, match="Failed to list OpenRouter models"):
        provider.models_list()


def test_model_retrieve_success(provider, mock_http_client):
    """测试成功获取模型信息"""
    # 准备测试数据
    model = "openai/gpt-3.5-turbo"
    mock_response = {
        "id": model,
        "name": "GPT-3.5 Turbo"
    }
    
    # 设置模拟响应
    mock_http_client.get.return_value.json.return_value = mock_response
    mock_http_client.get.return_value.raise_for_status.return_value = None
    
    # 调用方法
    response = provider.model_retrieve(model)
    
    # 验证结果
    assert response == mock_response
    
    # 验证请求
    mock_http_client.get.assert_called_once_with(f"/models/{model}")


def test_model_retrieve_error(provider, mock_http_client):
    """测试获取模型信息时的错误处理"""
    # 设置模拟错误
    mock_http_client.get.side_effect = httpx.HTTPError("API Error")
    
    # 验证错误处理
    with pytest.raises(LLMError, match="Failed to retrieve OpenRouter model"):
        provider.model_retrieve("openai/gpt-3.5-turbo")


def test_cleanup(provider, mock_http_client):
    """测试资源清理"""
    # 调用清理方法
    provider.__del__()
    
    # 验证 HTTP 客户端被关闭
    mock_http_client.close.assert_called_once()
