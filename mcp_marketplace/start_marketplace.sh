#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "========================================"
echo "🏪 启动 MCP Server Marketplace"
echo "========================================"
echo ""

echo "[1/3] 启动 Marketplace 服务器..."
python3 marketplace_server.py > marketplace.log 2>&1 &
MARKETPLACE_PID=$!
echo "   Marketplace PID: $MARKETPLACE_PID"

sleep 3

echo "[2/3] 初始化示例数据..."
python3 init_marketplace.py

echo ""
echo "[3/3] 启动前端和后端..."
cd ../server
python3 mcp_web_server.py > ../mcp_marketplace/web_server.log 2>&1 &
WEB_SERVER_PID=$!
echo "   Web Server PID: $WEB_SERVER_PID"
cd ../mcp_marketplace

cd ../client
npm run dev > ../mcp_marketplace/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ../mcp_marketplace

echo ""
echo "========================================"
echo "✅ 所有服务已启动"
echo "========================================"
echo ""
echo "📦 Marketplace API: http://localhost:9999"
echo "🌐 Web UI: http://localhost:5173"
echo "🔧 MCP Web API: http://localhost:8000"
echo ""
echo "进程ID:"
echo "  Marketplace: $MARKETPLACE_PID"
echo "  Web Server: $WEB_SERVER_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "停止服务: kill $MARKETPLACE_PID $WEB_SERVER_PID $FRONTEND_PID"
echo ""

