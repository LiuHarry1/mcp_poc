#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具管理 API 端点

提供工具列表查询功能
"""

import logging
from fastapi import APIRouter

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/tools", tags=["tools"])

# 全局 MCPManager 实例（将在主应用中注入）
mcp_manager = None


def init_router(manager):
    """初始化路由器，注入 MCPManager 实例"""
    global mcp_manager
    mcp_manager = manager
    return router


@router.get("")
async def get_tools():
    """
    获取所有可用工具
    
    Returns:
        工具列表
    """
    tools = []
    for tool_key, tool_info in mcp_manager.tools.items():
        tool = tool_info["tool"]
        server_type = tool_info["server_type"]
        
        # 根据服务器类型处理工具信息
        if server_type == "stdio":
            tools.append({
                "key": tool_key,
                "name": tool.name,
                "server": tool_info["server"],
                "description": tool.description,
                "parameters": tool.inputSchema
            })
        else:  # rest
            tools.append({
                "key": tool_key,
                "name": tool["name"],
                "server": tool_info["server"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            })
    
    logger.debug(f"返回 {len(tools)} 个工具")
    return {"tools": tools}

