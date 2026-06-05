#!/bin/bash
# 全球情绪温度计 - 启动脚本
# Global Sentiment Thermometer - Start Script

cd "$(dirname "$0")"
echo "🌡️  全球情绪温度计 | Global Sentiment Thermometer"
echo "="*50
echo ""
echo "启动后端服务..."
echo "访问地址: http://localhost:8866"
echo ""
python3 server.py
