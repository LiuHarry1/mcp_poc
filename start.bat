@echo off
echo ========================================
echo MCP Web Manager - React 版本
echo ========================================
echo.

REM 激活 conda 环境
echo 正在激活 conda 环境 (mcp_env)...
call conda activate mcp_env

if errorlevel 1 (
    echo 错误: 无法激活 conda 环境
    pause
    exit /b 1
)

REM 启动后端服务器（后台运行）
echo.
echo [1/2] 启动后端服务器...
cd server
start "MCP Backend" cmd /k "conda activate mcp_env && python mcp_web_server.py"
cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端开发服务器
echo.
echo [2/2] 启动前端开发服务器...
cd client
echo.
echo ================================================
echo   前端地址: http://localhost:3000
echo   后端API: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo ================================================
echo.
npm run dev

pause

