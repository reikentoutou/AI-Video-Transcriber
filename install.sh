#!/bin/bash

# AI视频转录器安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="venv"

echo "🚀 AI视频转录器安装脚本"
echo "=========================="

# 检查Python版本
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python版本: $python_version"

# 创建并配置虚拟环境
echo ""
echo "配置 Python 虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "✅ 已创建虚拟环境: $VENV_DIR"
else
    echo "✅ 虚拟环境已存在: $VENV_DIR"
fi

# 安装Python依赖（在 venv 内，避免 PEP 668 系统环境限制）
echo ""
echo "安装Python依赖..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt
echo "✅ Python依赖安装完成"

# 检查FFmpeg
echo ""
echo "检查FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg已安装"
else
    echo "⚠️  FFmpeg未安装，正在尝试安装..."
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            echo "❌ 无法自动安装FFmpeg，请手动安装"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ 请先安装Homebrew，然后运行: brew install ffmpeg"
        fi
    else
        echo "❌ 不支持的操作系统，请手动安装FFmpeg"
    fi
fi

# 创建必要的目录
echo ""
echo "创建必要的目录..."
mkdir -p temp static
echo "✅ 目录创建完成"

# 设置权限
chmod +x start.py

echo ""
echo "🎉 安装完成!"
echo ""
echo "使用方法:"
echo "  1. (可选) 配置OpenAI API密钥以启用智能摘要功能"
echo "     export OPENAI_API_KEY=your_api_key_here"
echo ""
echo "  2. 启动服务:"
echo "     source venv/bin/activate"
echo "     python start.py"
echo "     # 或直接: ./venv/bin/python start.py"
echo ""
echo "  3. 打开浏览器访问: http://localhost:8000"
echo ""
echo "支持的视频平台:"
echo "  - YouTube"
echo "  - Bilibili"
echo "  - 其他yt-dlp支持的平台"
