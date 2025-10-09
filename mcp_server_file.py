#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - 文件工具服务器
提供文件读取和写入工具
"""

import asyncio
import sys
import io
from pathlib import Path
from typing import Any, List

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建服务器实例
app = Server("file-tools-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="read_file",
            description="读取指定文件的内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="write_file",
            description="写入内容到指定文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要写入的文件路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的内容"
                    }
                },
                "required": ["file_path", "content"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """执行工具调用"""
    
    if name == "read_file":
        file_path = arguments.get("file_path")
        try:
            path = Path(file_path)
            if not path.exists():
                return [TextContent(type="text", text=f"错误: 文件不存在: {file_path}")]
            
            content = path.read_text(encoding="utf-8")
            return [TextContent(type="text", text=f"文件内容:\n{content}")]
        except Exception as e:
            return [TextContent(type="text", text=f"读取文件时出错: {str(e)}")]
    
    elif name == "write_file":
        file_path = arguments.get("file_path")
        content = arguments.get("content")
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return [TextContent(type="text", text=f"成功写入文件: {file_path}")]
        except Exception as e:
            return [TextContent(type="text", text=f"写入文件时出错: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    """运行服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

