#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from typing import List, Dict, Optional
from pydantic import BaseModel


class MCPServerConfig(BaseModel):
    """MCP 服务器配置"""
    name: str
    type: str = "stdio"  # "stdio" 或 "rest"
    command: Optional[str] = None  # stdio 类型需要
    args: Optional[List[str]] = None  # stdio 类型需要
    url: Optional[str] = None  # rest 类型需要
    env: Optional[Dict[str, str]] = None


class ChatMessage(BaseModel):
    """聊天消息模型"""
    message: str

