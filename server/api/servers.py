#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器管理 API 端点

提供服务器配置的 CRUD 操作和连接管理
"""

import logging
from fastapi import APIRouter, HTTPException

from models import MCPServerConfig

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/servers", tags=["servers"])

# 全局 MCPManager 实例（将在主应用中注入）
mcp_manager = None


def init_router(manager):
    """初始化路由器，注入 MCPManager 实例"""
    global mcp_manager
    mcp_manager = manager
    return router


@router.get("")
async def get_servers():
    """
    获取所有服务器配置
    
    Returns:
        服务器列表和已连接的服务器列表
    """
    return {
        "servers": [cfg.dict() for cfg in mcp_manager.configs],
        "connected": list(mcp_manager.sessions.keys())
    }


@router.post("")
async def add_server(config: MCPServerConfig):
    """
    添加新的服务器配置
    
    Args:
        config: 服务器配置
        
    Returns:
        添加结果
    """
    if any(cfg.name == config.name for cfg in mcp_manager.configs):
        raise HTTPException(status_code=400, detail="服务器名称已存在")
    
    mcp_manager.configs.append(config)
    mcp_manager.save_configs()
    logger.info(f"添加服务器配置: {config.name}")
    return {"status": "success", "config": config.dict()}


@router.delete("/{server_name}")
async def delete_server(server_name: str):
    """
    删除服务器配置
    
    Args:
        server_name: 服务器名称
        
    Returns:
        删除结果
    """
    # 如果服务器已连接，先断开
    if server_name in mcp_manager.sessions:
        await mcp_manager.disconnect_server(server_name)
    
    # 从配置列表中移除
    mcp_manager.configs = [cfg for cfg in mcp_manager.configs if cfg.name != server_name]
    mcp_manager.save_configs()
    logger.info(f"删除服务器配置: {server_name}")
    return {"status": "success"}


@router.post("/{server_name}/connect")
async def connect_server(server_name: str):
    """
    连接到服务器
    
    Args:
        server_name: 服务器名称
        
    Returns:
        连接结果
    """
    config = next((cfg for cfg in mcp_manager.configs if cfg.name == server_name), None)
    if not config:
        raise HTTPException(status_code=404, detail="服务器配置不存在")
    
    try:
        result = await mcp_manager.connect_to_server(config)
        return result
    except Exception as e:
        logger.error(f"连接服务器失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接失败: {str(e)}")


@router.post("/{server_name}/disconnect")
async def disconnect_server(server_name: str):
    """
    断开服务器连接
    
    Args:
        server_name: 服务器名称
        
    Returns:
        断开结果
    """
    result = await mcp_manager.disconnect_server(server_name)
    return result

