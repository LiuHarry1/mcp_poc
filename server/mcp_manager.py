#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Manager - MCP 服务器管理器

该模块负责：
- MCP 服务器的连接和断开
- 工具的管理和调用
- 配置文件的加载和保存
"""

import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from contextlib import AsyncExitStack

import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from models import MCPServerConfig

# 配置日志
logger = logging.getLogger(__name__)


class MCPManager:
    """MCP 服务器管理器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化 MCPManager
        
        Args:
            config_file: 配置文件路径，默认为 ../mcp_servers_config.json
        """
        self.sessions: Dict[str, Dict] = {}
        self.tools: Dict[str, Dict] = {}
        self.exit_stack = AsyncExitStack()
        self.configs: List[MCPServerConfig] = []
        self.config_file = config_file or Path("../mcp_servers_config.json")
        self.load_configs()
        logger.info("MCPManager 初始化完成")
    
    def load_configs(self):
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.configs = [MCPServerConfig(**cfg) for cfg in data.get('servers', [])]
                logger.info(f"加载了 {len(self.configs)} 个服务器配置")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self.configs = []
        else:
            logger.warning(f"配置文件不存在: {self.config_file}")
    
    def save_configs(self):
        """保存配置到文件"""
        try:
            data = {
                'servers': [cfg.dict() for cfg in self.configs]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("配置文件已保存")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    async def connect_to_server(self, config: MCPServerConfig):
        """
        连接到 MCP 服务器（支持 stdio 和 REST API）
        
        Args:
            config: 服务器配置
            
        Returns:
            连接结果字典
        """
        if config.type == "rest":
            return await self._connect_rest_server(config)
        else:
            return await self._connect_stdio_server(config)
    
    async def _connect_stdio_server(self, config: MCPServerConfig):
        """连接到 stdio 协议的 MCP 服务器"""
        logger.info(f"连接 stdio 服务器: {config.name}")
        
        # 调整命令路径（如果是相对路径）
        args = []
        for arg in config.args or []:
            arg_path = Path(arg)
            if arg_path.exists():
                args.append(str(arg_path))
            elif Path(f"../{arg}").exists():
                args.append(str(Path(f"../{arg}").absolute()))
            else:
                args.append(arg)
        
        server_params = StdioServerParameters(
            command=config.command,
            args=args,
            env=config.env
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        
        await session.initialize()
        
        # 获取服务器的工具列表
        tools_list = await session.list_tools()
        
        # 存储会话和工具
        self.sessions[config.name] = {
            "type": "stdio",
            "session": session
        }
        
        for tool in tools_list.tools:
            tool_key = f"{config.name}:{tool.name}"
            self.tools[tool_key] = {
                "server": config.name,
                "server_type": "stdio",
                "tool": tool
            }
        
        logger.info(f"成功连接 {config.name}，发现 {len(tools_list.tools)} 个工具")
        return {"status": "success", "tools": [t.name for t in tools_list.tools]}
    
    async def _connect_rest_server(self, config: MCPServerConfig):
        """连接到 REST API 的 MCP 服务器"""
        logger.info(f"连接 REST API 服务器: {config.name}")
        base_url = config.url.rstrip('/')
        
        try:
            # 获取工具列表
            response = requests.get(f"{base_url}/mcp/tools", timeout=5)
            response.raise_for_status()
            tools = response.json()
            
            # 存储服务器信息
            self.sessions[config.name] = {
                "type": "rest",
                "base_url": base_url
            }
            
            # 存储工具
            for tool in tools:
                tool_key = f"{config.name}:{tool['name']}"
                self.tools[tool_key] = {
                    "server": config.name,
                    "server_type": "rest",
                    "base_url": base_url,
                    "tool": tool
                }
            
            logger.info(f"成功连接 {config.name}，发现 {len(tools)} 个工具")
            return {"status": "success", "tools": [t["name"] for t in tools]}
            
        except Exception as e:
            error_msg = f"连接 REST API 服务器失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def disconnect_server(self, server_name: str):
        """
        断开服务器连接
        
        Args:
            server_name: 服务器名称
            
        Returns:
            断开结果字典
        """
        if server_name in self.sessions:
            # 移除相关工具
            tools_to_remove = [k for k in self.tools.keys() if k.startswith(f"{server_name}:")]
            for tool_key in tools_to_remove:
                del self.tools[tool_key]
            
            # 移除会话
            del self.sessions[server_name]
            logger.info(f"断开服务器连接: {server_name}")
            return {"status": "success"}
        return {"status": "error", "message": "服务器未连接"}
    
    async def call_tool(self, tool_key: str, arguments: Dict) -> str:
        """
        调用 MCP 工具（支持 stdio 和 REST API）
        
        Args:
            tool_key: 工具键（格式：server:tool）
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_key not in self.tools:
            return f"错误: 工具 {tool_key} 不存在"
        
        tool_info = self.tools[tool_key]
        server_type = tool_info["server_type"]
        
        if server_type == "stdio":
            return await self._call_stdio_tool(tool_info, arguments)
        else:  # rest
            return await self._call_rest_tool(tool_info, arguments)
    
    async def _call_stdio_tool(self, tool_info: Dict, arguments: Dict) -> str:
        """调用 stdio 类型的工具"""
        server_name = tool_info["server"]
        tool_name = tool_info["tool"].name
        session_info = self.sessions[server_name]
        session = session_info["session"]
        
        try:
            result = await session.call_tool(tool_name, arguments)
            if result.content:
                return "\n".join([item.text for item in result.content if hasattr(item, 'text')])
            return "工具执行成功，但没有返回内容"
        except Exception as e:
            logger.error(f"工具调用错误: {e}")
            return f"工具调用错误: {str(e)}"
    
    async def _call_rest_tool(self, tool_info: Dict, arguments: Dict) -> str:
        """调用 REST API 类型的工具"""
        base_url = tool_info["base_url"]
        tool_name = tool_info["tool"]["name"]
        
        try:
            response = requests.post(
                f"{base_url}/mcp/call",
                json={
                    "tool_name": tool_name,
                    "arguments": arguments
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                return result.get("result", "")
            else:
                return f"工具执行失败: {result.get('error', '未知错误')}"
                
        except Exception as e:
            logger.error(f"REST API 调用错误: {e}")
            return f"REST API 调用错误: {str(e)}"
    
    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()
        logger.info("MCPManager 资源已清理")

