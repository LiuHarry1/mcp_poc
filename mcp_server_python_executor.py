#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - Python 代码执行器
安全地执行 Python 代码片段
"""

import asyncio
import sys
import io
import traceback
from typing import Any, List
from contextlib import redirect_stdout, redirect_stderr

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建服务器实例
app = Server("python-executor-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="execute_python",
            description="执行 Python 代码并返回结果。支持标准库和常用计算。注意：为了安全，某些危险操作会被限制。",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 Python 代码"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "执行超时时间（秒），默认 5 秒",
                        "default": 5
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="evaluate_expression",
            description="计算 Python 表达式并返回结果。适合快速计算数学表达式或简单求值。",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的 Python 表达式，如 '2 + 2', '[x**2 for x in range(10)]'"
                    }
                },
                "required": ["expression"]
            }
        )
    ]


def create_safe_globals():
    """创建安全的全局变量环境"""
    import math
    import json
    import re
    from datetime import datetime, timedelta
    from collections import Counter, defaultdict
    
    # 允许的内置函数
    safe_builtins = {
        'abs': abs,
        'all': all,
        'any': any,
        'bin': bin,
        'bool': bool,
        'chr': chr,
        'dict': dict,
        'divmod': divmod,
        'enumerate': enumerate,
        'filter': filter,
        'float': float,
        'format': format,
        'hex': hex,
        'int': int,
        'isinstance': isinstance,
        'len': len,
        'list': list,
        'map': map,
        'max': max,
        'min': min,
        'oct': oct,
        'ord': ord,
        'pow': pow,
        'range': range,
        'reversed': reversed,
        'round': round,
        'set': set,
        'sorted': sorted,
        'str': str,
        'sum': sum,
        'tuple': tuple,
        'type': type,
        'zip': zip,
    }
    
    return {
        '__builtins__': safe_builtins,
        'math': math,
        'json': json,
        're': re,
        'datetime': datetime,
        'timedelta': timedelta,
        'Counter': Counter,
        'defaultdict': defaultdict,
    }


async def execute_code_with_timeout(code: str, timeout: float) -> str:
    """在单独的线程中执行代码，带超时控制"""
    import concurrent.futures
    
    def run_code():
        # 捕获标准输出和错误输出
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # 创建安全的执行环境
            safe_globals = create_safe_globals()
            local_vars = {}
            
            # 重定向输出
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # 执行代码
                exec(code, safe_globals, local_vars)
            
            # 获取输出
            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()
            
            result_parts = []
            
            if stdout_text:
                result_parts.append(f"标准输出:\n{stdout_text}")
            
            if stderr_text:
                result_parts.append(f"错误输出:\n{stderr_text}")
            
            # 如果有定义的变量，也显示出来
            if local_vars:
                vars_str = "\n".join([f"{k} = {repr(v)}" for k, v in local_vars.items() if not k.startswith('_')])
                if vars_str:
                    result_parts.append(f"定义的变量:\n{vars_str}")
            
            if not result_parts:
                return "代码执行成功（无输出）"
            
            return "\n\n".join(result_parts)
            
        except Exception as e:
            error_msg = f"执行错误:\n{type(e).__name__}: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            return error_msg
    
    # 使用线程池执行代码
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(executor, run_code),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return f"执行超时（超过 {timeout} 秒）"


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """执行工具调用"""
    
    if name == "execute_python":
        code = arguments.get("code", "")
        timeout = arguments.get("timeout", 5)
        
        if not code.strip():
            return [TextContent(type="text", text="错误: 代码不能为空")]
        
        try:
            result = await execute_code_with_timeout(code, timeout)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            return [TextContent(type="text", text=f"执行失败: {str(e)}")]
    
    elif name == "evaluate_expression":
        expression = arguments.get("expression", "")
        
        if not expression.strip():
            return [TextContent(type="text", text="错误: 表达式不能为空")]
        
        try:
            # 创建安全环境
            safe_globals = create_safe_globals()
            
            # 计算表达式
            result = eval(expression, safe_globals, {})
            
            return [TextContent(type="text", text=f"表达式: {expression}\n结果: {repr(result)}")]
        except Exception as e:
            error_msg = f"计算错误: {type(e).__name__}: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
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

