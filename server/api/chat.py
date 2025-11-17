#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天 API 端点

提供 WebSocket 聊天服务
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(tags=["chat"])

# 全局 ChatBot 实例（将在主应用中注入）
chatbot = None


def init_router(bot):
    """初始化路由器，注入 ChatBot 实例"""
    global chatbot
    chatbot = bot
    return router


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket 聊天端点
    
    提供实时聊天功能，支持工具调用
    """
    await websocket.accept()
    logger.info("WebSocket 连接已建立")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "content": "消息不能为空"
                })
                continue
            
            logger.info(f"收到用户消息: {user_message[:50]}...")
            
            # 使用 ChatBot 进行对话
            async for chunk in chatbot.chat(user_message):
                await websocket.send_json(chunk)
                
    except WebSocketDisconnect:
        logger.info("WebSocket 连接断开")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass

