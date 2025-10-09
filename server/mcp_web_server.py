#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Web Server - 提供 REST API 和 WebSocket 服务
"""

import asyncio
import json
import sys
import io
import os
from typing import List, Dict, Optional
from pathlib import Path
from contextlib import AsyncExitStack

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import dashscope
from dashscope import Generation

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置通义千问API
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-f256c03643e9491fb1ebc278dd958c2d")
dashscope.api_key = DASHSCOPE_API_KEY

# 创建 FastAPI 应用
app = FastAPI(title="MCP Web API", description="MCP 服务器管理和聊天 API")

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

# 数据模型
class MCPServerConfig(BaseModel):
    name: str
    type: str = "stdio"  # "stdio" 或 "rest"
    command: Optional[str] = None  # stdio 类型需要
    args: Optional[List[str]] = None  # stdio 类型需要
    url: Optional[str] = None  # rest 类型需要
    env: Optional[Dict[str, str]] = None

class ChatMessage(BaseModel):
    message: str

class MCPManager:
    """MCP 服务器管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, Dict] = {}
        self.exit_stack = AsyncExitStack()
        self.configs: List[MCPServerConfig] = []
        self.load_configs()
    
    def load_configs(self):
        """从文件加载配置"""
        config_file = Path("../mcp_servers_config.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.configs = [MCPServerConfig(**cfg) for cfg in data.get('servers', [])]
    
    def save_configs(self):
        """保存配置到文件"""
        config_file = Path("../mcp_servers_config.json")
        data = {
            'servers': [cfg.dict() for cfg in self.configs]
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    async def connect_to_server(self, config: MCPServerConfig):
        """连接到 MCP 服务器（支持 stdio 和 REST API）"""
        
        if config.type == "rest":
            # REST API 类型服务器
            return await self._connect_rest_server(config)
        else:
            # stdio 类型服务器
            return await self._connect_stdio_server(config)
    
    async def _connect_stdio_server(self, config: MCPServerConfig):
        """连接到 stdio 协议的 MCP 服务器"""
        # 调整命令路径（如果是相对路径）
        args = []
        for arg in config.args:
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
        
        return {"status": "success", "tools": [t.name for t in tools_list.tools]}
    
    async def _connect_rest_server(self, config: MCPServerConfig):
        """连接到 REST API 的 MCP 服务器"""
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
            
            return {"status": "success", "tools": [t["name"] for t in tools]}
            
        except Exception as e:
            raise Exception(f"连接 REST API 服务器失败: {str(e)}")
    
    async def disconnect_server(self, server_name: str):
        """断开服务器连接"""
        if server_name in self.sessions:
            # 移除相关工具
            tools_to_remove = [k for k in self.tools.keys() if k.startswith(f"{server_name}:")]
            for tool_key in tools_to_remove:
                del self.tools[tool_key]
            
            # 移除会话
            del self.sessions[server_name]
            return {"status": "success"}
        return {"status": "error", "message": "服务器未连接"}
    
    def get_tools_for_qwen(self) -> List[Dict]:
        """将 MCP 工具转换为通义千问的函数调用格式"""
        qwen_tools = []
        
        for tool_key, tool_info in self.tools.items():
            tool = tool_info["tool"]
            
            # 处理 stdio 和 rest 两种类型的工具
            if tool_info["server_type"] == "stdio":
                description = tool.description
                parameters = tool.inputSchema
            else:  # rest
                description = tool["description"]
                parameters = tool["parameters"]
            
            qwen_tool = {
                "type": "function",
                "function": {
                    "name": tool_key,
                    "description": description,
                    "parameters": parameters
                }
            }
            qwen_tools.append(qwen_tool)
        
        return qwen_tools
    
    async def call_tool(self, tool_key: str, arguments: Dict) -> str:
        """调用 MCP 工具（支持 stdio 和 REST API）"""
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
            return f"REST API 调用错误: {str(e)}"
    
    async def chat(self, user_message: str, max_iterations: int = 10):
        """使用通义千问进行对话"""
        messages = [
            {
                "role": "system",
                "content": "你是一个智能助手，可以使用各种工具来帮助用户。当需要使用工具时，请调用相应的函数。"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        tools = self.get_tools_for_qwen()
        
        for iteration in range(max_iterations):
            try:
                response = Generation.call(
                    model="qwen-plus",
                    messages=messages,
                    tools=tools if tools else None,
                    result_format='message'
                )
                
                if response.status_code != 200:
                    yield {"type": "error", "content": f"API错误: {response.message}"}
                    break
                
                assistant_message = response.output.choices[0].message
                
                # 检查是否需要调用工具
                tool_calls = None
                try:
                    tool_calls = assistant_message.tool_calls if hasattr(assistant_message, 'tool_calls') else None
                except:
                    tool_calls = None
                
                if tool_calls:
                    # 构建消息
                    content = ""
                    try:
                        content = assistant_message.content if hasattr(assistant_message, 'content') else ""
                    except:
                        content = ""
                    
                    msg = {
                        "role": "assistant",
                        "content": content or ""
                    }
                    
                    # 转换工具调用
                    tool_calls_list = []
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            tool_calls_list.append(tc)
                        else:
                            tool_calls_list.append({
                                'id': tc.id if hasattr(tc, 'id') else 'unknown',
                                'type': 'function',
                                'function': {
                                    'name': tc.function.name if hasattr(tc.function, 'name') else tc.function.get('name'),
                                    'arguments': tc.function.arguments if hasattr(tc.function, 'arguments') else tc.function.get('arguments')
                                }
                            })
                    msg['tool_calls'] = tool_calls_list
                    messages.append(msg)
                    
                    # 执行工具调用
                    for tool_call in tool_calls:
                        if isinstance(tool_call, dict):
                            function_name = tool_call['function']['name']
                            arguments = json.loads(tool_call['function']['arguments'])
                            tool_call_id = tool_call.get('id', 'unknown')
                        else:
                            function_name = tool_call.function.name
                            arguments = json.loads(tool_call.function.arguments)
                            tool_call_id = tool_call.id
                        
                        yield {
                            "type": "tool_call",
                            "tool": function_name,
                            "arguments": arguments
                        }
                        
                        tool_result = await self.call_tool(function_name, arguments)
                        
                        yield {
                            "type": "tool_result",
                            "tool": function_name,
                            "result": tool_result
                        }
                        
                        messages.append({
                            "role": "tool",
                            "content": tool_result,
                            "tool_call_id": tool_call_id
                        })
                else:
                    # 最终答案
                    final_response = ""
                    try:
                        final_response = assistant_message.content if hasattr(assistant_message, 'content') else ""
                    except:
                        final_response = ""
                    
                    yield {
                        "type": "response",
                        "content": final_response
                    }
                    return
                    
            except Exception as e:
                yield {"type": "error", "content": f"错误: {str(e)}"}
                break
        
        yield {"type": "error", "content": "达到最大迭代次数"}
    
    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()

# 全局管理器实例
mcp_manager = MCPManager()

# API 端点
@app.get("/")
async def root():
    """根端点"""
    return {"message": "MCP Web API", "version": "1.0.0"}

@app.get("/api/servers")
async def get_servers():
    """获取所有服务器配置"""
    return {
        "servers": [cfg.dict() for cfg in mcp_manager.configs],
        "connected": list(mcp_manager.sessions.keys())
    }

@app.post("/api/servers")
async def add_server(config: MCPServerConfig):
    """添加新的服务器配置"""
    if any(cfg.name == config.name for cfg in mcp_manager.configs):
        raise HTTPException(status_code=400, detail="服务器名称已存在")
    
    mcp_manager.configs.append(config)
    mcp_manager.save_configs()
    return {"status": "success", "config": config.dict()}

@app.delete("/api/servers/{server_name}")
async def delete_server(server_name: str):
    """删除服务器配置"""
    if server_name in mcp_manager.sessions:
        await mcp_manager.disconnect_server(server_name)
    
    mcp_manager.configs = [cfg for cfg in mcp_manager.configs if cfg.name != server_name]
    mcp_manager.save_configs()
    return {"status": "success"}

@app.post("/api/servers/{server_name}/connect")
async def connect_server(server_name: str):
    """连接到服务器"""
    config = next((cfg for cfg in mcp_manager.configs if cfg.name == server_name), None)
    if not config:
        raise HTTPException(status_code=404, detail="服务器配置不存在")
    
    try:
        result = await mcp_manager.connect_to_server(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接失败: {str(e)}")

@app.post("/api/servers/{server_name}/disconnect")
async def disconnect_server(server_name: str):
    """断开服务器连接"""
    result = await mcp_manager.disconnect_server(server_name)
    return result

@app.get("/api/tools")
async def get_tools():
    """获取所有可用工具"""
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
    return {"tools": tools}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 聊天端点"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            # 流式返回聊天响应
            async for chunk in mcp_manager.chat(user_message):
                await websocket.send_json(chunk)
                
    except WebSocketDisconnect:
        print("WebSocket 连接断开")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    await mcp_manager.cleanup()

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Web API Server 启动中...")
    print("=" * 60)
    print(f"\nAPI 地址: http://localhost:8000")
    print(f"API 文档: http://localhost:8000/docs")
    print(f"WebSocket: ws://localhost:8000/ws/chat")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

