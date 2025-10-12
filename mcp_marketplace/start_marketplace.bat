@echo off
chcp 65001 >nul
echo ========================================
echo 🏪 启动 MCP Server Marketplace
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 启动 Marketplace 服务器...
start "MCP Marketplace" cmd /k "python marketplace_server.py"

timeout /t 3 >nul

echo [2/3] 初始化示例数据...
python init_marketplace.py

echo.
echo [3/3] 启动前端和后端...
start "MCP Web Server" cmd /k "cd ..\server && python mcp_web_server.py"
start "MCP Frontend" cmd /k "cd ..\client && npm run dev"

echo.
echo ========================================
echo ✅ 所有服务已启动
echo ========================================
echo.
echo 📦 Marketplace API: http://localhost:9999
echo 🌐 Web UI: http://localhost:5173
echo 🔧 MCP Web API: http://localhost:8000
echo.
echo 按任意键关闭此窗口...
pause >nul

