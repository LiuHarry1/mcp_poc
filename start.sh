#!/bin/bash

# MCP Server Marketplace 快捷启动脚本
# 自动切换到 mcp_marketplace 目录并启动

cd "$(dirname "$0")/mcp_marketplace"
chmod +x start_marketplace.sh
./start_marketplace.sh

