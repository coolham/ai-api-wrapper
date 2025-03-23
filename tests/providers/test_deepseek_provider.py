from unittest.mock import MagicMock, patch
import pytest
import httpx
import os
from ai_api_wrapper.providers.deepseek_provider import DeepseekProvider
from ai_api_wrapper.provider import LLMError
from unittest.mock import Mock


@pytest.fixture
def env_file(tmp_path):
    """创建临时 .env 文件用于测试"""
    env_dir = tmp_path / "test_init_with_env_file"
    env_dir.mkdir()
    env_file = env_dir / ".env"
    env_content = """
DEEPSEEK_API_KEY=env-file-key
DEEPSEEK_API_BASE_URL=https://custom.deepseek.com
DEEPSEEK_TIMEOUT=45.0
DEEPSEEK_MAX_RETRIES=3
DEEPSEEK_USE_PROXY=true
DEEPSEEK_HTTP_PROXY=http://env.proxy:8080
DEEPSEEK_VERIFY_SSL=false
"""
    env_file.write_text(env_content)
    return env_file


@pytest.fixture(autouse=True)
def set_api_key_env_var(monkeypatch):
    """设置测试环境变量"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-api-key")


def test_init_with_env_file(env_file, monkeypatch):
    """测试使用 .env 文件初始化提供者"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 45.0,
            "max_retries": 3,
            "verify_ssl": False,
            "api_key": "env-file-key",
            "proxy": {
                "http": "http://env.proxy:8080"
            }
        }
        mock_config_manager.return_value = config_manager_instance
        
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.chdir(env_file.parent)
        
        with patch('openai.OpenAI') as mock_openai:
            client_instance = MagicMock()
            client_instance.api_key = "env-file-key"
            client_instance.base_url = "https://api.deepseek.com"
            mock_openai.return_value = client_instance
            
            provider = DeepseekProvider()
            assert provider.api_key == "env-file-key"
            assert provider.base_url == "https://api.deepseek.com"


def test_init_with_api_key():
    """测试使用 API 密钥初始化提供者"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "max_retries": 3,
            "verify_ssl": True
        }
        mock_config_manager.return_value = config_manager_instance
        
        with patch('openai.OpenAI') as mock_openai:
            client_instance = MagicMock()
            client_instance.api_key = "test-key"
            mock_openai.return_value = client_instance
            
            provider = DeepseekProvider(api_key="test-key")
            assert provider.api_key == "test-key"


def test_init_with_env_var(monkeypatch):
    """测试使用环境变量初始化提供者"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "max_retries": 3,
            "verify_ssl": True,
            "api_key": "env-var-key"
        }
        mock_config_manager.return_value = config_manager_instance
        
        monkeypatch.setenv("DEEPSEEK_API_KEY", "env-var-key")
        
        with patch('openai.OpenAI') as mock_openai:
            client_instance = MagicMock()
            client_instance.api_key = "env-var-key"
            mock_openai.return_value = client_instance
            
            provider = DeepseekProvider()
            assert provider.api_key == "env-var-key"


def test_init_without_api_key(monkeypatch):
    """测试没有 API 密钥时初始化失败"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {}
        mock_config_manager.return_value = config_manager_instance
        
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(ValueError) as exc_info:
            DeepseekProvider()
        assert str(exc_info.value) == "Deepseek API key is required"


@pytest.fixture
def mock_config():
    """模拟配置数据"""
    return {
        "base_url": "https://api.deepseek.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": True,
        "api_key": "test-api-key",
        "max_tokens": 4000,
    }


@pytest.fixture
def mock_config_with_proxy():
    """模拟带有代理的配置数据"""
    return {
        "base_url": "https://api.deepseek.com",
        "timeout": 30.0,
        "max_retries": 3,
        "verify_ssl": True,
        "api_key": "test-api-key",
        "max_tokens": 4000,
        "proxy": {
            "http": "http://proxy.example.com:8080",
            "https": "http://proxy.example.com:8080"
        }
    }


@pytest.mark.skip(reason="OpenAI客户端初始化需要真实的httpx.Client实例，无法使用mock")
def test_init_with_proxy():
    """测试使用代理配置初始化提供者"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "proxy": {
                "http": "http://proxy.example.com:8080",
                "https": "http://proxy.example.com:8080"
            }
        }
        mock_config_manager.return_value = config_manager_instance
        
        # 直接mock _configure_http_client方法
        with patch.object(DeepseekProvider, '_configure_http_client') as mock_method:
            http_client = MagicMock()
            mock_method.return_value = http_client
            
            # 模拟OpenAI类
            with patch('openai.OpenAI') as mock_openai:
                # 创建provider
                provider = DeepseekProvider()
                
                # 验证_configure_http_client被调用
                mock_method.assert_called_once()
                
                # 验证OpenAI被调用，包含http_client参数
                mock_openai.assert_called_once()
                call_args = mock_openai.call_args[1]
                assert 'http_client' in call_args
                assert call_args['http_client'] == http_client


@pytest.mark.skip(reason="OpenAI客户端初始化需要真实的httpx.Client实例，无法使用mock")
def test_init_without_proxy():
    """测试不使用代理配置初始化提供者"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key"
            # 没有代理配置
        }
        mock_config_manager.return_value = config_manager_instance
        
        # 直接mock _configure_http_client方法
        with patch.object(DeepseekProvider, '_configure_http_client') as mock_method:
            mock_method.return_value = None
            
            # 模拟OpenAI类
            with patch('openai.OpenAI') as mock_openai:
                # 创建provider
                provider = DeepseekProvider()
                
                # 验证_configure_http_client被调用
                mock_method.assert_called_once()
                
                # 验证OpenAI被调用，不包含http_client参数
                mock_openai.assert_called_once()
                call_args = mock_openai.call_args[1]
                assert 'http_client' not in call_args


@pytest.mark.skip(reason="OpenAI客户端初始化需要真实的httpx.Client实例，无法使用mock")
def test_init_with_proxy_from_env(monkeypatch):
    """测试从环境变量获取代理配置"""
    monkeypatch.setenv("DEEPSEEK_HTTP_PROXY", "http://proxy.example.com:8080")
    
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "proxy": {
                "http": "http://proxy.example.com:8080",
                "https": "http://proxy.example.com:8080"
            }
        }
        mock_config_manager.return_value = config_manager_instance
        
        # 直接mock _configure_http_client方法
        with patch.object(DeepseekProvider, '_configure_http_client') as mock_method:
            http_client = MagicMock()
            mock_method.return_value = http_client
            
            # 模拟OpenAI类
            with patch('openai.OpenAI') as mock_openai:
                # 创建provider
                provider = DeepseekProvider()
                
                # 验证_configure_http_client被调用
                mock_method.assert_called_once()
                
                # 验证OpenAI被调用，包含http_client参数
                mock_openai.assert_called_once()
                call_args = mock_openai.call_args[1]
                assert 'http_client' in call_args
                assert call_args['http_client'] == http_client


def test_chat_completion_success():
    """测试成功的聊天完成请求"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "max_tokens": 4000
        }
        mock_config_manager.return_value = config_manager_instance
        
        provider = DeepseekProvider()
        
        # 创建模拟响应
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "choices": [{"message": {"content": "你好！我能帮你什么？"}}]
        }

        with patch.object(
            provider.client.chat.completions,
            "create",
            return_value=mock_response
        ) as mock_create:
            response = provider.chat_completions_create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "你好！"}],
                temperature=0.7
            )

            mock_create.assert_called_once_with(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "你好！"}],
                temperature=0.7,
                max_tokens=4000,
                stream=False
            )

            assert response["choices"][0]["message"]["content"] == "你好！我能帮你什么？"


def test_chat_completion_error():
    """测试聊天完成请求失败的情况"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "max_tokens": 4000
        }
        mock_config_manager.return_value = config_manager_instance
        
        provider = DeepseekProvider()

        with patch.object(
            provider.client.chat.completions,
            "create",
            side_effect=Exception("API Error")
        ):
            with pytest.raises(LLMError) as exc_info:
                provider.chat_completions_create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": "你好！"}]
                )
            assert "Deepseek API error" in str(exc_info.value)


def test_models_list():
    """测试列出可用模型"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "max_tokens": 4000
        }
        mock_config_manager.return_value = config_manager_instance
        
        provider = DeepseekProvider()
        mock_models = {
            "data": [
                {"id": "deepseek-chat", "owned_by": "deepseek"},
                {"id": "deepseek-reasoner", "owned_by": "deepseek"}
            ]
        }

        with patch.object(
            provider.client.models,
            "list",
            return_value=MagicMock(model_dump=lambda: mock_models)
        ) as mock_list:
            models = provider.models_list()
            mock_list.assert_called_once()
            assert len(models["data"]) == 2
            assert models["data"][0]["id"] == "deepseek-chat"


def test_model_retrieve():
    """测试获取特定模型信息"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "max_tokens": 4000
        }
        mock_config_manager.return_value = config_manager_instance
        
        provider = DeepseekProvider()
        mock_model = {"id": "deepseek-chat", "owned_by": "deepseek"}

        with patch.object(
            provider.client.models,
            "retrieve",
            return_value=MagicMock(model_dump=lambda: mock_model)
        ) as mock_retrieve:
            model = provider.model_retrieve("deepseek-chat")
            mock_retrieve.assert_called_once_with("deepseek-chat")
            assert model["id"] == "deepseek-chat"


def test_models_list_error():
    """测试列出模型失败的情况"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "max_tokens": 4000
        }
        mock_config_manager.return_value = config_manager_instance
        
        provider = DeepseekProvider()

        with patch.object(
            provider.client.models,
            "list",
            side_effect=Exception("API Error")
        ):
            with pytest.raises(LLMError) as exc_info:
                provider.models_list()
            assert "Failed to list Deepseek models" in str(exc_info.value)


def test_model_retrieve_error():
    """测试获取模型信息失败的情况"""
    with patch('ai_api_wrapper.providers.deepseek_provider.ConfigManager') as mock_config_manager:
        # 创建配置管理器的模拟实例
        config_manager_instance = Mock()
        config_manager_instance.get_provider_config.return_value = {
            "base_url": "https://api.deepseek.com",
            "timeout": 30.0,
            "verify_ssl": True,
            "api_key": "test-key",
            "max_tokens": 4000
        }
        mock_config_manager.return_value = config_manager_instance
        
        provider = DeepseekProvider()

        with patch.object(
            provider.client.models,
            "retrieve",
            side_effect=Exception("API Error")
        ):
            with pytest.raises(LLMError) as exc_info:
                provider.model_retrieve("deepseek-chat")
            assert "Failed to retrieve Deepseek model" in str(exc_info.value)
