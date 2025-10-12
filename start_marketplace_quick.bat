@echo off
REM MCP Server Marketplace 快捷启动脚本 (Windows)
REM 自动切换到 mcp_marketplace 目录并启动

cd /d "%~dp0\mcp_marketplace"
call start_marketplace.bat

