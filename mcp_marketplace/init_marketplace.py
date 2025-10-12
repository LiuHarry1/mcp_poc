#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化 Marketplace 数据
将 packages 目录中的示例包发布到 Marketplace
"""

import json
import requests
import time
from pathlib import Path

MARKETPLACE_URL = "http://localhost:9999"
PACKAGES_DIR = Path("packages")

def wait_for_marketplace():
    """等待 Marketplace 服务器启动"""
    print("⏳ 等待 Marketplace 服务器启动...")
    for i in range(30):  # 最多等待30秒
        try:
            response = requests.get(f"{MARKETPLACE_URL}/", timeout=1)
            if response.ok:
                print("✅ Marketplace 服务器已就绪")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   等待中... ({i+1}/30)")
    
    print("❌ Marketplace 服务器未启动")
    return False

def publish_package(package_file):
    """发布单个包"""
    try:
        with open(package_file, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        print(f"\n📦 发布: {package_data['name']} ({package_data['id']})")
        
        response = requests.post(
            f"{MARKETPLACE_URL}/marketplace/packages",
            json=package_data,
            timeout=10
        )
        
        if response.ok:
            result = response.json()
            print(f"   ✅ 成功! 操作: {result.get('action', 'unknown')}")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 错误: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🏪 初始化 MCP Server Marketplace")
    print("=" * 60)
    
    # 检查 Marketplace 服务器
    if not wait_for_marketplace():
        print("\n💡 请先启动 Marketplace 服务器:")
        print("   python marketplace_server.py")
        return
    
    # 查找所有包配置文件
    package_files = list(PACKAGES_DIR.glob("*-package.json"))
    
    if not package_files:
        print("\n⚠️  没有找到包配置文件")
        return
    
    print(f"\n找到 {len(package_files)} 个包配置文件")
    
    # 发布所有包
    success_count = 0
    for package_file in package_files:
        if publish_package(package_file):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成! 成功发布 {success_count}/{len(package_files)} 个包")
    print("=" * 60)
    print(f"\n📦 访问 Marketplace: {MARKETPLACE_URL}/marketplace/packages")
    print(f"📚 API 文档: {MARKETPLACE_URL}/docs")
    print("\n💡 在前端 UI 中浏览: http://localhost:5173")

if __name__ == "__main__":
    main()

