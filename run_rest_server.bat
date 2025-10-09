@echo off
echo ========================================
echo MCP REST API Server 启动脚本
echo ========================================
echo.

REM 激活 conda 环境
call conda activate mcp_env

echo 启动 MCP REST API Server...
echo.
echo ================================================
echo   服务地址: http://localhost:9000
echo   API 文档: http://localhost:9000/docs
echo   工具列表: http://localhost:9000/mcp/tools
echo   调用工具: POST http://localhost:9000/mcp/call
echo ================================================
echo.
echo 按 Ctrl+C 停止服务器
echo.

python mcp_server_rest.py

pause

