#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - 计算工具服务器
提供数学计算和数据处理工具
"""

import asyncio
import sys
import io
import json
from typing import Any, List

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建服务器实例
app = Server("calc-tools-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="calculator",
            description="执行数学计算，支持基本运算和数学函数",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如: '2 + 2', 'sqrt(16)', 'pow(2, 3)'"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="statistics",
            description="计算数字列表的统计信息（平均值、最大值、最小值、总和）",
            inputSchema={
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "数字列表"
                    }
                },
                "required": ["numbers"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """执行工具调用"""
    
    if name == "calculator":
        expression = arguments.get("expression", "")
        try:
            # 安全的数学计算环境
            import math
            safe_dict = {
                "sqrt": math.sqrt,
                "pow": math.pow,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "abs": abs,
                "round": round,
                "pi": math.pi,
                "e": math.e
            }
            
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return [TextContent(type="text", text=f"计算结果: {expression} = {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"计算错误: {str(e)}")]
    
    elif name == "statistics":
        numbers = arguments.get("numbers", [])
        try:
            if not numbers:
                return [TextContent(type="text", text="错误: 数字列表为空")]
            
            total = sum(numbers)
            avg = total / len(numbers)
            max_val = max(numbers)
            min_val = min(numbers)
            
            result = {
                "总和": total,
                "平均值": avg,
                "最大值": max_val,
                "最小值": min_val,
                "数量": len(numbers)
            }
            
            result_text = "统计结果:\n" + "\n".join([f"{k}: {v}" for k, v in result.items()])
            return [TextContent(type="text", text=result_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"统计计算错误: {str(e)}")]
    
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

