"""
Client 配置集成测试
"""
import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch
import yaml
from ai_api_wrapper import Client


class TestClientConfig:
    """Client 配置集成测试类"""
    
    def test_client_with_default_config(self):
        """测试使用默认配置创建客户端"""
        # 清除环境变量，确保测试的纯粹性
        with patch.dict(os.environ, {}, clear=True):
            # 创建客户端实例
            client = Client()
            
            # 验证客户端是否正确初始化
            assert client is not None
            assert hasattr(client, 'config_manager')
            assert client.config_manager is not None
    
    def test_client_with_yaml_config(self):
        """测试使用 YAML 配置文件创建客户端"""
        # 获取测试配置文件路径
        test_config_path = Path(__file__).parent / "test_config.yaml"
        
        # 清除环境变量，确保测试的纯粹性
        with patch.dict(os.environ, {}, clear=True):
            # 创建客户端实例，使用测试配置文件
            client = Client(config_path=test_config_path)
            
            # 验证客户端是否正确初始化
            assert client is not None
            assert hasattr(client, 'config_manager')
            
            # 验证配置是否正确加载
            config = client.config_manager.get_config()
            assert config["http"]["timeout"] == 50.0
            assert config["http"]["max_retries"] == 5
            assert config["logging"]["level"] == "DEBUG"
    
    def test_client_with_env_vars(self):
        """测试使用环境变量创建客户端"""
        # 模拟环境变量
        env_vars = {
            "OPENAI_API_KEY": "test-api-key",
            "OPENAI_BASE_URL": "https://test-api.openai.com",
            "OPENAI_USE_PROXY": "true",
            "HTTP_PROXY": "http://test-proxy:7890",
            "HTTPS_PROXY": "https://test-proxy:7890"
        }
        
        # 使用临时环境变量
        with patch.dict(os.environ, env_vars):
            # 创建客户端实例
            client = Client()
            
            # 验证客户端是否正确初始化
            assert client is not None
            assert hasattr(client, 'config_manager')
            
            # 验证环境变量是否正确加载
            config = client.config_manager.get_config()
            assert config["providers"]["openai"]["api_key"] == "test-api-key"
            assert config["providers"]["openai"]["base_url"] == "https://test-api.openai.com"
            assert config["providers"]["openai"]["use_proxy"] == True
            assert config["proxy"]["http"] == "http://test-proxy:7890"
            assert config["proxy"]["https"] == "https://test-proxy:7890"
    
    def test_client_config_priority(self):
        """测试客户端配置优先级"""
        # 创建临时 YAML 配置文件
        temp_config = {
            "http": {
                "timeout": 60.0
            },
            "providers": {
                "openai": {
                    "base_url": "https://override.openai.com"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as temp:
            temp_path = temp.name
            yaml.dump(temp_config, temp)
        
        try:
            # 模拟环境变量（最高优先级）
            env_vars = {
                "OPENAI_BASE_URL": "https://env.openai.com",
                "OPENAI_API_KEY": "env-api-key"
            }
            
            # 使用临时环境变量和配置文件
            with patch.dict(os.environ, env_vars):
                # 创建客户端实例，使用临时配置文件
                client = Client(config_path=temp_path)
                
                # 验证客户端是否正确初始化
                assert client is not None
                assert hasattr(client, 'config_manager')
                
                # 验证配置优先级
                config = client.config_manager.get_config()
                assert config["http"]["timeout"] == 60.0  # 来自临时配置文件
                assert config["providers"]["openai"]["base_url"] == "https://env.openai.com"  # 来自环境变量
                assert config["providers"]["openai"]["api_key"] == "env-api-key"  # 来自环境变量
        finally:
            # 删除临时文件
            os.unlink(temp_path) 