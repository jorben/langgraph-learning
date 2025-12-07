#!/bin/bash

# Example 02 运行脚本
# 智能客服路由系统

echo "=== 启动智能客服路由系统 ==="

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "提示：建议在虚拟环境中运行"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告：未找到 .env 文件"
    echo "请将 .env.example 复制为 .env 并填入您的 API 密钥"
fi

# 运行主程序
uv run python main.py