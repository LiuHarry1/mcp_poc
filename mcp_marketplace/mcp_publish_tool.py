#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server 发布工具
用于将 MCP Server 发布到内部 Marketplace
"""

import click
import json
import requests
import os
from pathlib import Path
from datetime import datetime

MARKETPLACE_URL = os.getenv("MARKETPLACE_URL", "http://localhost:9999")


@click.group()
def cli():
    """🏪 MCP Server Marketplace 发布工具"""
    pass


@cli.command()
@click.option('--config', default='mcp_package.json', help='包配置文件路径')
def publish(config):
    """
    发布 MCP Server 到 Marketplace
    
    示例：
        python mcp_publish_tool.py publish
        python mcp_publish_tool.py publish --config my_package.json
    """
    
    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"❌ 配置文件不存在: {config}")
        click.echo(f"💡 运行 'python mcp_publish_tool.py init' 创建配置文件")
        return
    
    # 读取配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            package_config = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"❌ 配置文件格式错误: {e}")
        return
    
    # 验证必需字段
    required_fields = ['id', 'name', 'description', 'version', 'author', 'category', 'type', 'install_config']
    missing_fields = [field for field in required_fields if field not in package_config]
    
    if missing_fields:
        click.echo(f"❌ 配置文件缺少必需字段: {', '.join(missing_fields)}")
        return
    
    # 显示包信息
    click.echo("\n📦 包信息:")
    click.echo(f"   ID: {package_config['id']}")
    click.echo(f"   名称: {package_config['name']}")
    click.echo(f"   版本: {package_config['version']}")
    click.echo(f"   作者: {package_config['author']}")
    click.echo(f"   分类: {package_config['category']}")
    
    # 确认发布
    if not click.confirm(f"\n🚀 确定要发布到 {MARKETPLACE_URL} 吗？"):
        click.echo("❌ 已取消")
        return
    
    # 发布到 Marketplace
    click.echo(f"\n📤 正在发布...")
    try:
        response = requests.post(
            f"{MARKETPLACE_URL}/marketplace/packages",
            json=package_config,
            timeout=10
        )
        
        if response.ok:
            result = response.json()
            click.echo(f"\n✅ 发布成功！")
            click.echo(f"   操作: {result.get('action', 'unknown')}")
            click.echo(f"   访问: {MARKETPLACE_URL}/marketplace/packages/{package_config['id']}")
        else:
            error_detail = response.json().get('detail', response.text)
            click.echo(f"\n❌ 发布失败: {error_detail}")
            
    except requests.exceptions.ConnectionError:
        click.echo(f"\n❌ 无法连接到 Marketplace: {MARKETPLACE_URL}")
        click.echo(f"💡 请确保 Marketplace 服务器正在运行")
    except Exception as e:
        click.echo(f"\n❌ 发布失败: {str(e)}")


@cli.command()
@click.option('--output', default='mcp_package.json', help='输出配置文件路径')
def init(output):
    """
    初始化 MCP Server 包配置
    
    示例：
        python mcp_publish_tool.py init
        python mcp_publish_tool.py init --output my_package.json
    """
    
    click.echo("🎯 初始化 MCP Server 包配置\n")
    click.echo("请按照提示输入信息...\n")
    
    # 基本信息
    config = {
        "id": click.prompt("📦 包ID (格式: team/name, 如: ai-team/file-server)", type=str),
        "name": click.prompt("📝 显示名称", type=str),
        "description": click.prompt("📄 简短描述 (一句话)", type=str),
        "long_description": click.prompt("📖 详细说明 (可选，支持 Markdown)", default="", type=str),
        "version": click.prompt("🔢 版本号", default="1.0.0", type=str),
        "author": click.prompt("👤 作者/团队", type=str),
    }
    
    # 分类
    click.echo("\n📂 选择分类:")
    categories = [
        ("file", "📁 文件操作"),
        ("compute", "🧮 计算工具"),
        ("search", "🔍 搜索服务"),
        ("ai", "🤖 AI 工具"),
        ("database", "💾 数据库"),
        ("api", "🔌 API 集成"),
        ("devops", "⚙️ DevOps"),
        ("code", "💻 代码执行"),
    ]
    for i, (cat_id, cat_name) in enumerate(categories, 1):
        click.echo(f"  {i}. {cat_name}")
    
    cat_choice = click.prompt("选择分类 (输入数字)", type=int, default=1)
    if 1 <= cat_choice <= len(categories):
        config['category'] = categories[cat_choice - 1][0]
    else:
        config['category'] = 'api'
    
    # 标签
    tags_input = click.prompt("\n🏷️  标签 (逗号分隔, 如: python,工具,文件)", default="", type=str)
    config['tags'] = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    
    # 类型和安装配置
    click.echo("\n🔧 选择类型:")
    click.echo("  1. stdio - 标准输入输出协议 (推荐)")
    click.echo("  2. rest - REST API 协议")
    
    type_choice = click.prompt("选择类型 (输入数字)", type=int, default=1)
    
    if type_choice == 2:
        config['type'] = 'rest'
        config['install_config'] = {
            "url": click.prompt("🌐 REST API URL", type=str)
        }
    else:
        config['type'] = 'stdio'
        command = click.prompt("⚙️  启动命令", default="python", type=str)
        args_input = click.prompt("📋 命令参数 (逗号分隔)", default="server.py", type=str)
        args = [arg.strip() for arg in args_input.split(',') if arg.strip()]
        
        config['install_config'] = {
            "command": command,
            "args": args
        }
    
    # 依赖
    deps_input = click.prompt("\n📦 Python 依赖 (逗号分隔, 可选)", default="", type=str)
    config['dependencies'] = [dep.strip() for dep in deps_input.split(',') if dep.strip()]
    
    # 环境变量
    env_input = click.prompt("🔐 需要的环境变量 (逗号分隔, 可选)", default="", type=str)
    config['requires_env'] = [env.strip() for env in env_input.split(',') if env.strip()]
    
    # 初始化元数据
    config['package_url'] = ""
    config['readme_url'] = ""
    config['icon_url'] = ""
    config['downloads'] = 0
    config['rating'] = 5.0
    
    # 保存配置
    output_path = Path(output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    click.echo(f"\n✅ 配置文件已创建: {output_path}")
    click.echo(f"💡 运行 'python mcp_publish_tool.py publish --config {output}' 发布到 Marketplace")


@cli.command()
@click.argument('package_id')
def info(package_id):
    """
    查看 Marketplace 中的包信息
    
    示例：
        python mcp_publish_tool.py info company/file-server
    """
    
    click.echo(f"🔍 查询包信息: {package_id}\n")
    
    try:
        response = requests.get(
            f"{MARKETPLACE_URL}/marketplace/packages/{package_id}",
            timeout=10
        )
        
        if response.ok:
            pkg = response.json()
            
            click.echo("📦 包信息:")
            click.echo(f"   ID: {pkg['id']}")
            click.echo(f"   名称: {pkg['name']}")
            click.echo(f"   描述: {pkg['description']}")
            click.echo(f"   版本: {pkg['version']}")
            click.echo(f"   作者: {pkg['author']}")
            click.echo(f"   分类: {pkg['category']}")
            click.echo(f"   类型: {pkg['type']}")
            click.echo(f"   标签: {', '.join(pkg.get('tags', []))}")
            click.echo(f"   下载量: {pkg.get('downloads', 0)}")
            click.echo(f"   评分: {pkg.get('rating', 0)} ⭐")
            click.echo(f"   创建时间: {pkg.get('created_at', 'N/A')}")
            click.echo(f"   更新时间: {pkg.get('updated_at', 'N/A')}")
            
            if pkg.get('long_description'):
                click.echo(f"\n📖 详细说明:\n{pkg['long_description']}")
            
        else:
            click.echo(f"❌ 包不存在: {package_id}")
            
    except requests.exceptions.ConnectionError:
        click.echo(f"❌ 无法连接到 Marketplace: {MARKETPLACE_URL}")
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}")


@cli.command()
@click.option('--category', help='按分类过滤')
@click.option('--query', help='搜索关键词')
def list(category, query):
    """
    列出 Marketplace 中的所有包
    
    示例：
        python mcp_publish_tool.py list
        python mcp_publish_tool.py list --category file
        python mcp_publish_tool.py list --query 搜索
    """
    
    click.echo("📋 Marketplace 包列表\n")
    
    try:
        params = {}
        if category:
            params['category'] = category
        if query:
            params['query'] = query
        
        response = requests.get(
            f"{MARKETPLACE_URL}/marketplace/packages",
            params=params,
            timeout=10
        )
        
        if response.ok:
            data = response.json()
            packages = data.get('packages', [])
            
            if not packages:
                click.echo("没有找到包")
                return
            
            click.echo(f"找到 {len(packages)} 个包:\n")
            
            for pkg in packages:
                click.echo(f"📦 {pkg['name']} ({pkg['id']})")
                click.echo(f"   版本: {pkg['version']} | 分类: {pkg['category']} | 下载: {pkg.get('downloads', 0)} | 评分: {pkg.get('rating', 0)}⭐")
                click.echo(f"   {pkg['description']}")
                click.echo()
        else:
            click.echo(f"❌ 查询失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        click.echo(f"❌ 无法连接到 Marketplace: {MARKETPLACE_URL}")
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}")


@cli.command()
@click.argument('package_id')
def delete(package_id):
    """
    从 Marketplace 删除包
    
    示例：
        python mcp_publish_tool.py delete company/file-server
    """
    
    click.echo(f"🗑️  删除包: {package_id}\n")
    
    if not click.confirm(f"⚠️  确定要删除 {package_id} 吗？此操作不可撤销！"):
        click.echo("❌ 已取消")
        return
    
    try:
        response = requests.delete(
            f"{MARKETPLACE_URL}/marketplace/packages/{package_id}",
            timeout=10
        )
        
        if response.ok:
            click.echo(f"✅ 包已删除: {package_id}")
        else:
            click.echo(f"❌ 删除失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        click.echo(f"❌ 无法连接到 Marketplace: {MARKETPLACE_URL}")
    except Exception as e:
        click.echo(f"❌ 删除失败: {str(e)}")


if __name__ == '__main__':
    cli()

