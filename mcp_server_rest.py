#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - REST API 版本
通过 FastAPI 暴露 MCP 工具，支持 HTTP REST API 调用
"""

import sys
import io
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 创建 FastAPI 应用
app = FastAPI(
    title="MCP REST API Server",
    description="基于 REST API 的 MCP 工具服务器",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolCallResponse(BaseModel):
    success: bool
    result: str
    error: str = None

# MCP 工具实现
class MCPTools:
    """MCP 工具集合"""
    
    @staticmethod
    def get_tools() -> List[ToolDefinition]:
        """获取所有可用工具"""
        return [
            ToolDefinition(
                name="echo",
                description="回显输入的文本",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "要回显的文本"
                        }
                    },
                    "required": ["text"]
                }
            ),
            ToolDefinition(
                name="uppercase",
                description="将文本转换为大写",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "要转换的文本"
                        }
                    },
                    "required": ["text"]
                }
            ),
            ToolDefinition(
                name="reverse",
                description="反转文本",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "要反转的文本"
                        }
                    },
                    "required": ["text"]
                }
            ),
            ToolDefinition(
                name="word_count",
                description="统计文本中的单词数量",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "要统计的文本"
                        }
                    },
                    "required": ["text"]
                }
            )
        ]
    
    @staticmethod
    def call_tool(tool_name: str, arguments: Dict[str, Any]) -> ToolCallResponse:
        """执行工具调用"""
        try:
            if tool_name == "echo":
                text = arguments.get("text", "")
                return ToolCallResponse(
                    success=True,
                    result=f"回显: {text}"
                )
            
            elif tool_name == "uppercase":
                text = arguments.get("text", "")
                return ToolCallResponse(
                    success=True,
                    result=text.upper()
                )
            
            elif tool_name == "reverse":
                text = arguments.get("text", "")
                return ToolCallResponse(
                    success=True,
                    result=text[::-1]
                )
            
            elif tool_name == "word_count":
                text = arguments.get("text", "")
                words = text.split()
                return ToolCallResponse(
                    success=True,
                    result=f"文本包含 {len(words)} 个单词"
                )
            
            else:
                return ToolCallResponse(
                    success=False,
                    result="",
                    error=f"未知工具: {tool_name}"
                )
                
        except Exception as e:
            return ToolCallResponse(
                success=False,
                result="",
                error=f"工具执行错误: {str(e)}"
            )

# API 端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "name": "MCP REST API Server",
        "version": "1.0.0",
        "protocol": "REST API",
        "endpoints": {
            "tools": "/mcp/tools",
            "call": "/mcp/call"
        }
    }

@app.get("/mcp/tools", response_model=List[ToolDefinition])
async def list_tools():
    """列出所有可用的工具"""
    return MCPTools.get_tools()

@app.post("/mcp/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """调用指定的工具"""
    return MCPTools.call_tool(request.tool_name, request.arguments)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    print("=" * 60)
    print("MCP REST API Server 启动中...")
    print("=" * 60)
    print(f"\n服务地址: http://localhost:9000")
    print(f"API 文档: http://localhost:9000/docs")
    print(f"工具列表: http://localhost:9000/mcp/tools")
    print(f"调用工具: POST http://localhost:9000/mcp/call")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")

