"""
配置管理器测试
"""
import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
import yaml
from ai_api_wrapper.utils.config_manager import ConfigManager, get_config_example, show_config_example
from ai_api_wrapper.config.default_config import DEFAULT_CONFIG


class TestConfigManager:
    """配置管理器测试类"""
    
    def setup_method(self):
        """每个测试方法开始前的设置"""
        # 重置配置管理器实例
        ConfigManager.reset()
    
    def test_default_config(self):
        """测试默认配置加载"""
        # 清除环境变量，确保测试的纯粹性
        with patch.dict(os.environ, {}, clear=True):
            # 创建配置管理器实例
            config_manager = ConfigManager()
            
            # 获取配置
            config = config_manager.get_config()
            
            # 验证默认配置是否正确加载
            assert config["http"]["timeout"] == 60.0
            assert config["http"]["verify_ssl"] is True
            assert config["http"]["max_retries"] == 5
            assert config["logging"]["level"] == "DEBUG"
            assert "providers" in config
            assert "openai" in config["providers"]
            assert "grok" in config["providers"]
    
    def test_yaml_config(self):
        """测试 YAML 配置文件加载"""
        # 模拟配置文件内容
        mock_yaml_config = {
            "http": {
                "timeout": 50.0,
                "max_retries": 5
            },
            "logging": {
                "level": "DEBUG"
            },
            "providers": {
                "test_provider": {
                    "base_url": "https://api.test.com",
                    "models": ["test-model-1", "test-model-2"],
                    "default_model": "test-model-1",
                    "use_proxy": True
                }
            }
        }
        
        # 使用模拟的配置文件
        with patch('ai_api_wrapper.utils.config_manager.yaml.safe_load', return_value=mock_yaml_config):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', MagicMock()):
                    # 创建配置管理器实例，使用测试配置文件
                    config_manager = ConfigManager(config_path="test_config.yaml")
                    
                    # 获取配置
                    config = config_manager.get_config()
                    
                    # 验证配置是否正确加载和合并
                    assert config["http"]["timeout"] == 50.0  # 来自测试配置文件
                    assert config["http"]["max_retries"] == 5  # 来自测试配置文件
                    assert config["http"]["verify_ssl"] == True  # 来自默认配置
                    assert config["logging"]["level"] == "DEBUG"  # 来自测试配置文件
                    assert "test_provider" in config["providers"]  # 来自测试配置文件
                    assert config["providers"]["test_provider"]["base_url"] == "https://api.test.com"
    
    def test_env_config(self):
        """测试环境变量配置加载"""
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
            # 创建配置管理器实例
            config_manager = ConfigManager()
            
            # 获取提供商配置
            provider_config = config_manager.get_provider_config("openai")
            
            # 验证环境变量是否正确加载
            assert provider_config["api_key"] == "test-api-key"
            assert provider_config["base_url"] == "https://test-api.openai.com"
            assert provider_config["use_proxy"] == True
            
            # 获取代理配置
            proxy_config = config_manager.get_proxy_config()
            assert "http" in proxy_config
            assert "https" in proxy_config
            assert proxy_config["http"] == "http://test-proxy:7890"
            assert proxy_config["https"] == "https://test-proxy:7890"
    
    def test_config_priority(self):
        """测试配置优先级"""
        # 模拟配置文件内容
        mock_yaml_config = {
            "http": {
                "timeout": 60.0,
                "verify_ssl": False,
                "max_retries": 5
            },
            "providers": {
                "test_provider": {
                    "base_url": "https://override.test.com"
                }
            }
        }
        
        # 模拟环境变量（最高优先级）
        env_vars = {
            "TEST_PROVIDER_BASE_URL": "https://env.test.com"
        }
        
        # 使用模拟的配置文件和环境变量
        with patch('ai_api_wrapper.utils.config_manager.yaml.safe_load', return_value=mock_yaml_config):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', MagicMock()):
                    with patch.dict(os.environ, env_vars):
                        # 创建配置管理器实例，使用测试配置文件
                        config_manager = ConfigManager(config_path="test_config.yaml")
                        
                        # 获取配置
                        config = config_manager.get_config()
                        
                        # 验证配置优先级
                        # 环境变量 > 用户配置 > 默认配置
                        assert config["http"]["timeout"] == 60.0  # 来自配置文件，覆盖默认值
                        assert config["http"]["verify_ssl"] == False  # 来自配置文件，覆盖默认值
                        assert config["http"]["max_retries"] == 5  # 来自配置文件，覆盖默认值
                        
                        # 验证提供商配置优先级
                        provider_config = config_manager.get_provider_config("test_provider")
                        assert provider_config["base_url"] == "https://env.test.com"  # 来自环境变量，覆盖配置文件
    
    def test_provider_config(self):
        """测试获取提供商配置"""
        # 模拟配置文件内容
        mock_yaml_config = {
            "providers": {
                "test_provider": {
                    "base_url": "https://api.test.com",
                    "models": ["test-model-1", "test-model-2"],
                    "default_model": "test-model-1",
                    "use_proxy": True
                }
            }
        }
        
        # 使用模拟的配置文件
        with patch('ai_api_wrapper.utils.config_manager.yaml.safe_load', return_value=mock_yaml_config):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', MagicMock()):
                    # 创建配置管理器实例，使用测试配置文件
                    config_manager = ConfigManager(config_path="test_config.yaml")
                    
                    # 获取提供商配置
                    provider_config = config_manager.get_provider_config("test_provider")
                    
                    # 验证提供商配置
                    assert provider_config["base_url"] == "https://api.test.com"
                    assert provider_config["models"] == ["test-model-1", "test-model-2"]
                    assert provider_config["default_model"] == "test-model-1"
                    assert provider_config["use_proxy"] == True
    
    def test_http_config(self):
        """测试获取 HTTP 配置"""
        # 模拟配置文件内容
        mock_yaml_config = {
            "http": {
                "timeout": 50.0,
                "max_retries": 5
            }
        }
        
        # 使用模拟的配置文件
        with patch('ai_api_wrapper.utils.config_manager.yaml.safe_load', return_value=mock_yaml_config):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', MagicMock()):
                    # 创建配置管理器实例，使用测试配置文件
                    config_manager = ConfigManager(config_path="test_config.yaml")
                    
                    # 获取 HTTP 配置
                    http_config = config_manager.get_http_config()
                    
                    # 验证 HTTP 配置
                    assert http_config["timeout"] == 50.0
                    assert http_config["max_retries"] == 5
                    assert "verify_ssl" in http_config  # 来自默认配置
    
    def test_proxy_config(self):
        """测试获取代理配置"""
        # 模拟环境变量
        env_vars = {
            "HTTP_PROXY": "http://test-proxy:7890",
            "HTTPS_PROXY": "https://test-proxy:7890",
            "TEST_PROVIDER_USE_PROXY": "true"
        }
        
        # 模拟配置
        mock_config = {
            "providers": {
                "test_provider": {
                    "use_proxy": True
                }
            },
            "proxy": {
                "http": "http://test-proxy:7890",
                "https": "https://test-proxy:7890"
            }
        }
        
        # 使用临时环境变量
        with patch.dict(os.environ, env_vars):
            # 创建配置管理器实例
            config_manager = ConfigManager()
            
            # 模拟加载的配置
            config_manager._config = mock_config
            
            # 获取代理配置
            proxy_config = config_manager.get_proxy_config(provider="test_provider")
            
            # 验证代理配置
            assert proxy_config["http"] == "http://test-proxy:7890"
            assert proxy_config["https"] == "https://test-proxy:7890"
    
    def test_proxy_config_disabled(self):
        """测试禁用代理配置"""
        # 模拟环境变量
        env_vars = {
            "HTTP_PROXY": "http://test-proxy:7890",
            "HTTPS_PROXY": "https://test-proxy:7890",
            "TEST_PROVIDER_USE_PROXY": "false"
        }
        
        # 模拟配置
        mock_config = {
            "providers": {
                "test_provider": {
                    "use_proxy": False
                }
            },
            "proxy": {
                "http": "http://test-proxy:7890",
                "https": "https://test-proxy:7890"
            }
        }
        
        # 使用临时环境变量
        with patch.dict(os.environ, env_vars):
            # 创建配置管理器实例
            config_manager = ConfigManager()
            
            # 模拟加载的配置
            config_manager._config = mock_config
            
            # 获取代理配置
            proxy_config = config_manager.get_proxy_config(provider="test_provider")
            
            # 验证代理配置
            assert proxy_config == {}
    
    def test_config_example(self):
        """测试配置示例函数"""
        # 获取配置示例路径
        with patch('pathlib.Path.exists', return_value=True):
            # 模拟配置示例路径
            with patch('ai_api_wrapper.utils.config_manager.PROJECT_ROOT',
                       Path("/fake/path")):
                # 调用函数
                example_path = get_config_example()
                
                # 验证返回值
                assert "advanced_config.yaml" in example_path
    
    def test_show_config_example(self, capsys):
        """测试显示配置示例函数"""
        # 模拟配置示例路径
        with patch('ai_api_wrapper.utils.config_manager.get_config_example',
                  return_value="/fake/path/advanced_config.yaml"):
            # 调用显示配置示例函数
            show_config_example()
            
            # 获取标准输出
            captured = capsys.readouterr()
            
            # 验证输出是否包含配置示例路径
            assert "高级配置示例文件位置" in captured.out
            assert "advanced_config.yaml" in captured.out 