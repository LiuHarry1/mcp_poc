#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot 模块 - 处理 AI 聊天和工具调用逻辑

该模块负责：
- 与通义千问 API 交互
- 工具调用的解析和执行
- 对话流程管理
"""

import json
import os
import logging
from typing import List, Dict, AsyncGenerator, Optional, Any, Protocol
import dashscope
from dashscope import Generation

# 配置日志
logger = logging.getLogger(__name__)


class MCPManagerProtocol(Protocol):
    """MCPManager 协议接口，用于类型提示"""
    
    @property
    def tools(self) -> Dict[str, Dict[str, Any]]:
        """工具字典"""
        ...
    
    async def call_tool(self, tool_key: str, arguments: Dict[str, Any]) -> str:
        """调用工具"""
        ...


class ChatBot:
    """AI 聊天机器人，支持工具调用"""
    
    # 默认 API Key（应该从环境变量读取）
    DEFAULT_API_KEY = "sk-f256c03643e9491fb1ebc278dd958c2d"
    
    # 默认模型
    DEFAULT_MODEL = "qwen-plus"
    
    # 默认最大迭代次数
    DEFAULT_MAX_ITERATIONS = 10
    
    def __init__(self, mcp_manager: MCPManagerProtocol, api_key: Optional[str] = None):
        """
        初始化 ChatBot
        
        Args:
            mcp_manager: MCPManager 实例，用于调用工具
            api_key: 通义千问 API Key，如果为 None 则从环境变量读取
        """
        self.mcp_manager = mcp_manager
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", self.DEFAULT_API_KEY)
        dashscope.api_key = self.api_key
        
        # 系统提示词
        self.system_prompt = (
            "你是一个智能助手，可以使用各种工具来帮助用户。"
            "当需要使用工具时，请调用相应的函数。"
            "请用中文回答用户的问题。"
        )
        
        logger.info("ChatBot 初始化完成")
    
    def _get_tools_for_qwen(self) -> List[Dict[str, Any]]:
        """
        将 MCP 工具转换为通义千问的函数调用格式
        
        Returns:
            通义千问工具列表
        """
        qwen_tools = []
        
        if not self.mcp_manager.tools:
            logger.debug("没有可用的工具")
            return qwen_tools
        
        for tool_key, tool_info in self.mcp_manager.tools.items():
            try:
                tool = tool_info["tool"]
                server_type = tool_info.get("server_type", "stdio")
                
                # 处理 stdio 和 rest 两种类型的工具
                if server_type == "stdio":
                    description = getattr(tool, "description", "")
                    parameters = getattr(tool, "inputSchema", {})
                else:  # rest
                    description = tool.get("description", "")
                    parameters = tool.get("parameters", {})
                
                qwen_tool = {
                    "type": "function",
                    "function": {
                        "name": tool_key,
                        "description": description,
                        "parameters": parameters
                    }
                }
                qwen_tools.append(qwen_tool)
            except Exception as e:
                logger.warning(f"转换工具 {tool_key} 失败: {e}")
                continue
        
        logger.debug(f"转换了 {len(qwen_tools)} 个工具")
        return qwen_tools
    
    def _parse_tool_calls(self, assistant_message: Any) -> Optional[List[Dict[str, Any]]]:
        """
        解析工具调用信息
        
        Args:
            assistant_message: 助手消息对象
            
        Returns:
            工具调用列表，如果没有则返回 None
        """
        try:
            tool_calls = getattr(assistant_message, 'tool_calls', None)
            if not tool_calls:
                return None
            
            # 转换为统一格式
            tool_calls_list = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    tool_calls_list.append(tc)
                else:
                    # 处理对象类型的 tool_call
                    function = getattr(tc, 'function', None)
                    if function:
                        func_name = getattr(function, 'name', None) or (function.get('name') if isinstance(function, dict) else None)
                        func_args = getattr(function, 'arguments', None) or (function.get('arguments') if isinstance(function, dict) else None)
                        
                        tool_calls_list.append({
                            'id': getattr(tc, 'id', 'unknown'),
                            'type': 'function',
                            'function': {
                                'name': func_name,
                                'arguments': func_args
                            }
                        })
            
            return tool_calls_list if tool_calls_list else None
        except Exception as e:
            logger.error(f"解析工具调用失败: {e}")
            return None
    
    def _get_message_content(self, message: Any) -> str:
        """
        安全获取消息内容
        
        Args:
            message: 消息对象
            
        Returns:
            消息内容字符串
        """
        try:
            if hasattr(message, 'content'):
                content = message.content
                return content if isinstance(content, str) else str(content)
            return ""
        except Exception as e:
            logger.warning(f"获取消息内容失败: {e}")
            return ""
    
    async def chat(
        self, 
        user_message: str, 
        max_iterations: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        使用通义千问进行对话，支持工具调用
        
        Args:
            user_message: 用户消息
            max_iterations: 最大迭代次数（防止无限循环）
            system_prompt: 自定义系统提示词
            
        Yields:
            消息字典，包含 type 和 content/tool/arguments/result 等字段
        """
        if not user_message or not user_message.strip():
            yield {
                "type": "error",
                "content": "消息不能为空"
            }
            return
        
        max_iter = max_iterations or self.DEFAULT_MAX_ITERATIONS
        
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": system_prompt or self.system_prompt
            },
            {
                "role": "user",
                "content": user_message.strip()
            }
        ]
        
        tools = self._get_tools_for_qwen()
        logger.info(f"开始对话，可用工具数: {len(tools)}")
        
        for iteration in range(max_iter):
            try:
                logger.debug(f"第 {iteration + 1} 次迭代")
                
                # 调用通义千问 API
                response = Generation.call(
                    model=self.DEFAULT_MODEL,
                    messages=messages,
                    tools=tools if tools else None,
                    result_format='message'
                )
                
                if response.status_code != 200:
                    error_msg = f"API错误: {response.message}"
                    logger.error(error_msg)
                    yield {
                        "type": "error",
                        "content": error_msg
                    }
                    break
                
                if not response.output or not response.output.choices:
                    error_msg = "API 返回格式错误"
                    logger.error(error_msg)
                    yield {
                        "type": "error",
                        "content": error_msg
                    }
                    break
                
                assistant_message = response.output.choices[0].message
                
                # 检查是否需要调用工具
                tool_calls = self._parse_tool_calls(assistant_message)
                
                if tool_calls:
                    logger.debug(f"检测到 {len(tool_calls)} 个工具调用")
                    
                    # 构建助手消息
                    content = self._get_message_content(assistant_message)
                    msg: Dict[str, Any] = {
                        "role": "assistant",
                        "content": content or ""
                    }
                    
                    # 添加工具调用信息
                    msg['tool_calls'] = tool_calls
                    messages.append(msg)
                    
                    # 执行工具调用
                    for tool_call in tool_calls:
                        try:
                            # 解析工具调用信息
                            if isinstance(tool_call, dict):
                                function_name = tool_call['function']['name']
                                arguments_str = tool_call['function']['arguments']
                                tool_call_id = tool_call.get('id', 'unknown')
                            else:
                                function_name = tool_call.function.name
                                arguments_str = tool_call.function.arguments
                                tool_call_id = tool_call.id
                            
                            # 解析参数
                            try:
                                if isinstance(arguments_str, str):
                                    arguments = json.loads(arguments_str)
                                else:
                                    arguments = arguments_str
                            except json.JSONDecodeError as e:
                                error_msg = f"工具参数解析失败: {arguments_str}"
                                logger.error(f"{error_msg}, 错误: {e}")
                                yield {
                                    "type": "error",
                                    "content": error_msg
                                }
                                continue
                            
                            logger.info(f"调用工具: {function_name}")
                            
                            # 发送工具调用通知
                            yield {
                                "type": "tool_call",
                                "tool": function_name,
                                "arguments": arguments
                            }
                            
                            # 调用工具
                            tool_result = await self.mcp_manager.call_tool(function_name, arguments)
                            
                            # 发送工具结果
                            yield {
                                "type": "tool_result",
                                "tool": function_name,
                                "result": tool_result
                            }
                            
                            # 添加工具结果到消息历史
                            messages.append({
                                "role": "tool",
                                "content": tool_result,
                                "tool_call_id": tool_call_id
                            })
                        except Exception as e:
                            error_msg = f"工具调用失败: {str(e)}"
                            logger.error(error_msg, exc_info=True)
                            yield {
                                "type": "error",
                                "content": error_msg
                            }
                else:
                    # 最终答案
                    final_response = self._get_message_content(assistant_message)
                    logger.info("生成最终回答")
                    
                    yield {
                        "type": "response",
                        "content": final_response
                    }
                    return
                    
            except Exception as e:
                error_msg = f"对话处理错误: {str(e)}"
                logger.error(error_msg, exc_info=True)
                yield {
                    "type": "error",
                    "content": error_msg
                }
                break
        
        logger.warning(f"达到最大迭代次数 ({max_iter})")
        yield {
            "type": "error",
            "content": "达到最大迭代次数，请简化您的问题"
        }

