#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 包 - 包含所有 REST API 和 WebSocket 端点

该包包含以下模块：
- servers: 服务器管理端点
- tools: 工具查询端点
- chat: 聊天 WebSocket 端点
"""

from .servers import init_router as init_servers_router
from .tools import init_router as init_tools_router
from .chat import init_router as init_chat_router

__all__ = [
    "init_servers_router",
    "init_tools_router",
    "init_chat_router"
]

