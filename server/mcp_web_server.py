#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Web Server - 主应用入口

该模块负责：
- FastAPI 应用初始化
- 中间件配置
- 路由注册
- 应用生命周期管理
"""

import sys
import io
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mcp_manager import MCPManager
from chatbot import ChatBot
from api import (
    init_servers_router,
    init_tools_router,
    init_chat_router
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 创建 FastAPI 应用
app = FastAPI(
    title="MCP Web API",
    description="MCP 服务器管理和聊天 API",
    version="1.0.0"
)

# 配置 CORS - 允许 React 开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 开发服务器
        "http://localhost:5173",  # Vite 开发服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局管理器实例
mcp_manager = MCPManager()
chatbot = ChatBot(mcp_manager)

# 注册路由
app.include_router(init_servers_router(mcp_manager))
app.include_router(init_tools_router(mcp_manager))
app.include_router(init_chat_router(chatbot))


@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "MCP Web API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/chat"
    }


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("应用正在关闭，清理资源...")
    await mcp_manager.cleanup()
    logger.info("资源清理完成")


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Web API Server 启动中...")
    print("=" * 60)
    print(f"\nAPI 地址: http://localhost:8000")
    print(f"API 文档: http://localhost:8000/docs")
    print(f"WebSocket: ws://localhost:8000/ws/chat")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
