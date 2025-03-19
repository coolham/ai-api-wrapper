from unittest.mock import MagicMock, patch
import pytest
import httpx
import os
from ai_api_wrapper.providers.grok_provider import GrokProvider
from ai_api_wrapper.provider import LLMError


@pytest.fixture
def env_file(tmp_path):
    """Create a temporary .env file for testing."""
    env_dir = tmp_path / "test_init_with_env_file"
    env_dir.mkdir()
    env_file = env_dir / ".env"
    env_content = """
GROK_API_KEY=env-file-key
GROK_API_BASE_URL=https://custom.grok.ai/v1
GROK_ORGANIZATION=org-123
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
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv("GROK_API_KEY", "test-api-key")


def test_init_with_env_file(env_file, monkeypatch):
    """Test provider initialization with .env file."""
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.chdir(env_file.parent)
    
    provider = GrokProvider()
    assert provider.client.api_key == "env-file-key"
    assert str(provider.client.base_url).rstrip("/") == "https://custom.grok.ai/v1"
    assert isinstance(provider.http_client, httpx.Client)
    assert provider.client.organization == "org-123"
    assert float(provider.client.timeout) == 45.0
    assert provider.client.max_retries == 3
    assert provider.http_client._verify is False


def test_init_with_env_file_proxy_config(env_file_proxy, monkeypatch):
    """Test proxy configuration from .env file."""
    monkeypatch.chdir(env_file_proxy.parent)
    
    provider = GrokProvider(use_proxy=True)
    assert isinstance(provider.http_client, httpx.Client)
    assert provider.http_client._timeout.read == 45.0
    assert provider.http_client._verify is False
    assert provider.http_client._transport.proxy == "http://env.proxy:8080"


def test_config_precedence(env_file, monkeypatch):
    """Test configuration precedence (config > env vars > .env file)."""
    monkeypatch.chdir(env_file.parent)
    monkeypatch.setenv("GROK_API_KEY", "env-var-key")
    
    # 配置参数应该优先于环境变量和 .env 文件
    provider = GrokProvider(api_key="config-key")
    assert provider.client.api_key == "config-key"


def test_init_with_api_key():
    """Test provider initialization with API key in config."""
    provider = GrokProvider(api_key="test-key")
    assert provider.client.api_key == "test-key"


def test_init_with_env_var(monkeypatch):
    """Test provider initialization with API key in environment variable."""
    monkeypatch.setenv("GROK_API_KEY", "env-var-key")
    provider = GrokProvider()
    assert provider.client.api_key == "env-var-key"


def test_init_without_api_key(monkeypatch):
    """Test provider initialization without API key raises error."""
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    with patch('ai_api_wrapper.providers.grok_provider.load_dotenv', return_value=None):
        with pytest.raises(ValueError) as exc_info:
            GrokProvider()
    assert str(exc_info.value) == "Grok API key is missing. Please provide it in the config or set the GROK_API_KEY environment variable."


def test_chat_completion_success():
    """Test successful chat completion request."""
    provider = GrokProvider()
    
    # 创建模拟响应
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello! How can I help you!"

    with patch.object(
        provider.client.chat.completions,
        "create",
        return_value=mock_response
    ) as mock_create:
        response = provider.chat_completions_create(
            model="grok-1",
            messages=[{"role": "user", "content": "Hi!"}],
            temperature=0.7
        )

        mock_create.assert_called_once_with(
            model="grok-1",
            messages=[{"role": "user", "content": "Hi!"}],
            temperature=0.7
        )

        assert response.choices[0].message.content == "Hello! How can I help you!"


def test_chat_completion_error():
    """Test chat completion request with API error."""
    provider = GrokProvider()

    with patch.object(
        provider.client.chat.completions,
        "create",
        side_effect=Exception("API Error")
    ):
        with pytest.raises(LLMError) as exc_info:
            provider.chat_completions_create(
                model="grok-1",
                messages=[{"role": "user", "content": "Hi!"}]
            )
        assert "Grok API error" in str(exc_info.value)


def test_models_list():
    """Test listing available models."""
    provider = GrokProvider()
    mock_models = [
        {"id": "grok-1", "owned_by": "grok"},
        {"id": "grok-2", "owned_by": "grok"}
    ]

    with patch.object(
        provider.client.models,
        "list",
        return_value=mock_models
    ) as mock_list:
        models = provider.models_list()
        mock_list.assert_called_once()
        assert len(models) == 2
        assert models[0]["id"] == "grok-1"


def test_model_retrieve():
    """Test retrieving specific model information."""
    provider = GrokProvider()
    mock_model = {"id": "grok-1", "owned_by": "grok"}

    with patch.object(
        provider.client.models,
        "retrieve",
        return_value=mock_model
    ) as mock_retrieve:
        model = provider.model_retrieve("grok-1")
        mock_retrieve.assert_called_once_with("grok-1")
        assert model["id"] == "grok-1"


def test_models_list_error():
    """Test error handling when listing models fails."""
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
    """Test error handling when retrieving model fails."""
    provider = GrokProvider()

    with patch.object(
        provider.client.models,
        "retrieve",
        side_effect=Exception("API Error")
    ):
        with pytest.raises(LLMError) as exc_info:
            provider.model_retrieve("grok-1")
        assert "Failed to retrieve Grok model" in str(exc_info.value)


def test_init_with_proxy():
    """Test provider initialization with proxy configuration."""
    provider = GrokProvider(
        api_key="test-key",
        use_proxy=True,
        http_proxy="http://proxy.example.com:8080"
    )
    assert provider.http_client._transport.proxy == "http://proxy.example.com:8080"
    assert provider.http_client._verify is True


def test_init_with_proxy_from_env(monkeypatch):
    """Test provider initialization with proxy from environment variables."""
    monkeypatch.setenv("GROK_HTTP_PROXY", "http://proxy.example.com:8080")
    provider = GrokProvider(
        api_key="test-key",
        use_proxy=True
    )
    assert provider.http_client._transport.proxy == "http://proxy.example.com:8080"
    assert provider.http_client._verify is True


def test_init_with_invalid_proxy():
    """Test provider initialization with invalid proxy configuration."""
    with pytest.raises(LLMError) as exc_info:
        GrokProvider(
            api_key="test-key",
            use_proxy=True,
            http_proxy="invalid:proxy:url"
        )
    assert "Failed to initialize proxy transport" in str(exc_info.value)


def test_init_without_proxy():
    """Test provider initialization without proxy configuration."""
    provider = GrokProvider(api_key="test-key", use_proxy=False)
    assert not hasattr(provider.http_client, "_transport") or provider.http_client._transport is None
    assert provider.http_client._verify is True
