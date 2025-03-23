# 帮助文档

## 如何执行测试用例

使用pytest执行测试用例有多种方法，以下是常用方法：

### 单独执行某个文件的测试用例

1. **直接指定文件路径**:
```bash
pytest path/to/test_file.py
```

2. **使用Python模块路径**:
```bash
pytest tests/config/test_config_manager.py
```

3. **使用-k参数按名称筛选测试**:
```bash
pytest -k "test_file_name"
```

4. **执行特定测试文件中的特定测试函数**:
```bash
pytest path/to/test_file.py::test_function_name
```

5. **执行特定测试类中的特定方法**:
```bash
pytest path/to/test_file.py::TestClass::test_method_name
```

6. **使用-v参数获取详细输出**:
```bash
pytest path/to/test_file.py -v
```

7. **在PowerShell中使用分号分隔命令**:
```powershell
cd tests/config; python -m pytest test_config_manager.py -v
```

以上方法可根据需要组合使用，例如您可以添加-v参数查看详细测试过程。

### 执行目录下的所有测试用例

1. **直接指定目录路径**:
```bash
pytest tests/providers/
```
这将执行指定目录下所有的测试文件，pytest会自动查找并运行以`test_`开头的Python文件或以`_test.py`结尾的文件中的测试用例。

2. **结合-v参数获取详细输出**:
```bash
pytest tests/providers/ -v
```

3. **使用通配符匹配多个文件**:
```bash
pytest tests/providers/*.py
```

4. **在特定目录下执行同时过滤测试名称**:
```bash
pytest tests/providers/ -k "test_init"
```
