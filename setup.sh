#!/bin/bash
# ============================================
# AI数字分身 - 一键安装启动脚本
# 用法: bash setup.sh
# ============================================

set -e

echo "🤖 ============================================"
echo "   AI数字分身 - 安装向导"
echo "=============================================="
echo ""

# 检查Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 已安装: $(python3 --version)"
else
    echo "❌ 需要Python3.10+，请先安装Python"
    exit 1
fi

# 创建虚拟环境（可选但推荐）
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 正在创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo ""
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装依赖包..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"

# 检查.env文件
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，正在从模板创建..."
    cp .env.example .env
    echo "✅ .env 文件已创建，请编辑填入你的API Key："
    echo ""
    echo "   nano .env"
    echo ""
    echo "   推荐API获取（便宜好用）："
    echo "   🟢 DeepSeek: https://platform.deepseek.com/ (¥1起)"
    echo "   🟢 通义千问: https://dashscope.aliyun.com/"
    echo "   🟢 智谱AI: https://open.bigmodel.cn/"
    echo ""
    echo "   编辑好 .env 后，重新运行此脚本即可启动。"
    exit 0
else
    echo "✅ .env 文件已存在"
fi

# 启动应用
echo ""
echo "🚀 启动AI数字分身..."
echo ""
echo "   访问地址: http://localhost:8501"
echo "   按 Ctrl+C 停止运行"
echo ""
streamlit run app/main.py --server.port 8501
