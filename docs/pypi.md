# PyPI 发布流程

本文档描述了如何将 ai-api-wrapper 发布到 PyPI 的完整流程。

## 1. 准备工作

### 1.1 环境要求
- Python 3.9 或更高版本
- Poetry 包管理器
- PyPI 账号（如果没有，请在 [PyPI](https://pypi.org/account/register/) 注册）

### 1.2 安装依赖
```bash

# clear cache
poetry cache clear --all pypi

# 安装所有依赖，包括开发依赖
poetry install --with dev
```

## 2. 测试

### 2.1 运行测试
```bash
# 运行所有测试
poetry run pytest

# 运行测试并生成覆盖率报告
poetry run pytest --cov=ai_api_wrapper --cov-report=html
```

### 2.2 代码质量检查
```bash
# 运行类型检查
poetry run mypy .

# 运行代码格式化
poetry run black .
poetry run isort .

# 运行代码检查
poetry run pylint ai_api_wrapper
```

## 3. 版本更新

### 3.1 更新版本号
在 `pyproject.toml` 中更新版本号：
```toml
[tool.poetry]
version = "0.1.1"  # 更新为新版本号
```

### 3.2 更新 CHANGELOG.md
在 CHANGELOG.md 中添加新版本的更新日志：
```markdown
## [0.1.1] - 2024-03-XX
### Added
- 新功能描述
### Changed
- 变更描述
### Fixed
- 修复描述
```

## 4. 构建包

### 4.1 清理构建文件
```bash
# 删除之前的构建文件
rm -rf dist/ build/ *.egg-info/
```

### 4.2 构建包
```bash
# 使用 poetry 构建
poetry build
```

## 5. 发布到 PyPI

### 5.1 配置 PyPI 认证
创建或编辑 `~/.pypirc` 文件：
```ini
[pypi]
username = __token__
password = your-pypi-token
```

或者配置PyPI凭证
```
poetry config pypi-token.pypi 你的PyPI令牌
```

### 5.2 发布到 PyPI
```bash
# 使用 poetry 发布
poetry publish

# 或者使用 twine 发布
poetry run twine upload dist/*
```

## 6. 验证发布

### 6.1 检查 PyPI 页面
访问 [PyPI 项目页面](https://pypi.org/project/ai-api-wrapper/) 确认：
- 版本号是否正确
- 描述是否正确
- 依赖是否正确
- 文档是否正确显示

### 6.2 测试安装
```bash
# 创建新的虚拟环境
python -m venv test_env
source test_env/bin/activate  # Linux/macOS
# 或
.\test_env\Scripts\activate  # Windows

# 安装包
pip install ai-api-wrapper

# 测试导入
python -c "import ai_api_wrapper; print(ai_api_wrapper.__version__)"
```

## 7. 常见问题

### 7.1 发布失败
如果发布失败，检查：
- PyPI 认证是否正确
- 版本号是否已存在
- 包名是否已被使用
- 网络连接是否正常

### 7.2 依赖问题
如果安装时出现依赖问题：
- 检查 `pyproject.toml` 中的依赖版本
- 确保所有依赖都已在 PyPI 上可用
- 检查依赖的兼容性

## 8. 维护建议

### 8.1 版本管理
- 遵循语义化版本控制
- 每次发布前更新 CHANGELOG.md
- 保持向后兼容性

### 8.2 文档更新
- 确保 README.md 和文档是最新的
- 更新示例代码
- 检查所有链接是否有效

### 8.3 依赖更新
- 定期更新依赖版本
- 测试新版本兼容性
- 更新 `pyproject.toml` 中的版本要求
