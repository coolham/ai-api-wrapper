#!/bin/bash

# 设置环境变量
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 运行单元测试
echo "运行单元测试..."
pytest tests/providers/deepseek/test_deepseek_provider.py -v -m unit

# 运行所有测试并生成覆盖率报告
echo "运行所有测试并生成覆盖率报告..."
pytest -v --cov=ai_api_wrapper --cov-report=html

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "测试通过！"
    echo "覆盖率报告已生成在 htmlcov/index.html"
else
    echo "测试失败！"
    exit 1
fi 