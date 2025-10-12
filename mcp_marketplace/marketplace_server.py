#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server Marketplace - 内部 MCP Server 应用商店
提供浏览、搜索、下载、安装 MCP Server 的功能
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# 创建 FastAPI 应用
app = FastAPI(
    title="MCP Server Marketplace",
    description="内部 MCP Server 应用商店",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class MCPServerPackage(BaseModel):
    """MCP Server 包信息"""
    id: str                          # 唯一标识，如 "company/file-server"
    name: str                        # 显示名称
    description: str                 # 简短描述
    long_description: Optional[str] = ""  # 详细说明（Markdown）
    version: str                     # 版本号，如 "1.0.0"
    author: str                      # 作者/团队
    category: str                    # 分类：file, compute, search, ai, database, api, devops
    tags: List[str]                  # 标签
    
    # 安装信息
    type: str                        # "stdio", "rest", "docker"
    install_config: dict             # 安装配置
    # stdio: {"command": "python", "args": ["server.py"]}
    # rest: {"url": "http://internal-server"}
    # docker: {"image": "company/mcp-server:1.0"}
    
    # 资源
    package_url: Optional[str] = ""  # 下载链接（内部存储）
    readme_url: Optional[str] = ""   # README 文件
    icon_url: Optional[str] = ""     # 图标
    
    # 依赖
    dependencies: Optional[List[str]] = []  # Python/Node 依赖
    requires_env: Optional[List[str]] = []  # 需要的环境变量
    
    # 元数据
    downloads: int = 0               # 下载次数
    rating: float = 5.0              # 评分
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PackageRating(BaseModel):
    """包评分"""
    package_id: str
    rating: int  # 1-5
    comment: Optional[str] = ""
    user: str


class MarketplaceDB:
    """简单的文件数据库（生产环境建议用 PostgreSQL）"""
    
    def __init__(self, data_dir="marketplace_data"):
        self.data_dir = Path(data_dir)
        self.packages_file = self.data_dir / "packages.json"
        self.ratings_file = self.data_dir / "ratings.json"
        self.files_dir = self.data_dir / "files"
        
        # 创建目录
        self.data_dir.mkdir(exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        # 加载包数据
        if self.packages_file.exists():
            with open(self.packages_file, 'r', encoding='utf-8') as f:
                self.packages = json.load(f)
        else:
            self.packages = {}
            self.save_packages()
        
        # 加载评分数据
        if self.ratings_file.exists():
            with open(self.ratings_file, 'r', encoding='utf-8') as f:
                self.ratings = json.load(f)
        else:
            self.ratings = {}
            self.save_ratings()
    
    def save_packages(self):
        """保存包数据"""
        with open(self.packages_file, 'w', encoding='utf-8') as f:
            json.dump(self.packages, f, indent=2, ensure_ascii=False)
    
    def save_ratings(self):
        """保存评分数据"""
        with open(self.ratings_file, 'w', encoding='utf-8') as f:
            json.dump(self.ratings, f, indent=2, ensure_ascii=False)
    
    def add_package(self, package: MCPServerPackage):
        """添加或更新包"""
        now = datetime.now().isoformat()
        package_dict = package.dict()
        
        if package.id in self.packages:
            # 更新：保留 created_at
            package_dict['created_at'] = self.packages[package.id].get('created_at', now)
        else:
            # 新增
            package_dict['created_at'] = now
        
        package_dict['updated_at'] = now
        self.packages[package.id] = package_dict
        self.save_packages()
        return package_dict
    
    def get_package(self, package_id: str):
        """获取包详情"""
        return self.packages.get(package_id)
    
    def delete_package(self, package_id: str):
        """删除包"""
        if package_id in self.packages:
            del self.packages[package_id]
            self.save_packages()
            return True
        return False
    
    def search_packages(self, query: str = None, category: str = None, tags: List[str] = None):
        """搜索包"""
        results = list(self.packages.values())
        
        if query:
            query = query.lower()
            results = [p for p in results 
                      if query in p['name'].lower() 
                      or query in p['description'].lower()
                      or query in p.get('long_description', '').lower()]
        
        if category:
            results = [p for p in results if p['category'] == category]
        
        if tags:
            results = [p for p in results 
                      if any(tag in p.get('tags', []) for tag in tags)]
        
        # 按下载量和评分排序
        results.sort(key=lambda x: (x.get('downloads', 0), x.get('rating', 0)), reverse=True)
        
        return results
    
    def increment_download(self, package_id: str):
        """增加下载次数"""
        if package_id in self.packages:
            self.packages[package_id]['downloads'] = self.packages[package_id].get('downloads', 0) + 1
            self.save_packages()
            return True
        return False
    
    def add_rating(self, rating: PackageRating):
        """添加评分"""
        if rating.package_id not in self.ratings:
            self.ratings[rating.package_id] = []
        
        self.ratings[rating.package_id].append(rating.dict())
        self.save_ratings()
        
        # 更新包的平均评分
        if rating.package_id in self.packages:
            all_ratings = [r['rating'] for r in self.ratings[rating.package_id]]
            avg_rating = sum(all_ratings) / len(all_ratings)
            self.packages[rating.package_id]['rating'] = round(avg_rating, 1)
            self.save_packages()
    
    def get_ratings(self, package_id: str):
        """获取包的评分"""
        return self.ratings.get(package_id, [])


# 初始化数据库
db = MarketplaceDB()


# API 端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "MCP Server Marketplace API",
        "version": "1.0.0",
        "endpoints": {
            "packages": "/marketplace/packages",
            "categories": "/marketplace/categories",
            "docs": "/docs"
        }
    }


@app.get("/marketplace/packages")
async def list_packages(
    query: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    列出所有包（支持搜索和过滤）
    
    - query: 搜索关键词
    - category: 分类过滤
    - tags: 标签过滤（逗号分隔）
    - limit: 返回数量限制
    """
    tag_list = tags.split(',') if tags else None
    packages = db.search_packages(query, category, tag_list)
    
    # 限制返回数量
    if limit:
        packages = packages[:limit]
    
    return {
        "total": len(packages),
        "packages": packages
    }


@app.get("/marketplace/packages/{package_id:path}")
async def get_package_detail(package_id: str):
    """获取包详情"""
    package = db.get_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # 获取评分
    ratings = db.get_ratings(package_id)
    
    return {
        **package,
        "ratings_count": len(ratings),
        "recent_ratings": ratings[-5:]  # 最近5条评分
    }


@app.post("/marketplace/packages")
async def publish_package(package: MCPServerPackage):
    """
    发布新包或更新现有包
    注意：生产环境需要添加认证和权限验证
    """
    try:
        result = db.add_package(package)
        return {
            "status": "success",
            "action": "updated" if package.id in db.packages else "created",
            "package": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish package: {str(e)}")


@app.delete("/marketplace/packages/{package_id:path}")
async def delete_package(package_id: str):
    """删除包"""
    if db.delete_package(package_id):
        return {"status": "success", "message": "Package deleted"}
    else:
        raise HTTPException(status_code=404, detail="Package not found")


@app.post("/marketplace/packages/{package_id:path}/download")
async def download_package(package_id: str):
    """
    下载包（记录下载次数）
    返回安装配置信息
    """
    package = db.get_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # 增加下载次数
    db.increment_download(package_id)
    
    return {
        "status": "success",
        "package_id": package_id,
        "name": package['name'],
        "version": package['version'],
        "type": package['type'],
        "install_config": package['install_config'],
        "dependencies": package.get('dependencies', []),
        "requires_env": package.get('requires_env', []),
        "package_url": package.get('package_url', ''),
        "downloads": package.get('downloads', 0) + 1
    }


@app.post("/marketplace/packages/{package_id:path}/rate")
async def rate_package(package_id: str, rating: PackageRating):
    """为包评分"""
    package = db.get_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    db.add_rating(rating)
    return {"status": "success", "message": "Rating added"}


@app.get("/marketplace/categories")
async def list_categories():
    """获取所有分类"""
    categories = [
        {"id": "file", "name": "文件操作", "icon": "📁", "description": "文件读写、管理工具"},
        {"id": "compute", "name": "计算工具", "icon": "🧮", "description": "数学计算、数据处理"},
        {"id": "search", "name": "搜索服务", "icon": "🔍", "description": "网络搜索、信息检索"},
        {"id": "ai", "name": "AI 工具", "icon": "🤖", "description": "AI 模型、智能助手"},
        {"id": "database", "name": "数据库", "icon": "💾", "description": "数据库操作、查询工具"},
        {"id": "api", "name": "API 集成", "icon": "🔌", "description": "第三方 API 集成"},
        {"id": "devops", "name": "DevOps", "icon": "⚙️", "description": "开发运维工具"},
        {"id": "code", "name": "代码执行", "icon": "💻", "description": "代码执行、脚本运行"},
    ]
    
    # 统计每个分类的包数量
    for cat in categories:
        cat['count'] = len([p for p in db.packages.values() if p['category'] == cat['id']])
    
    return {"categories": categories}


@app.get("/marketplace/stats")
async def get_stats():
    """获取 Marketplace 统计信息"""
    packages = list(db.packages.values())
    
    return {
        "total_packages": len(packages),
        "total_downloads": sum(p.get('downloads', 0) for p in packages),
        "categories_count": len(set(p['category'] for p in packages)),
        "average_rating": round(sum(p.get('rating', 0) for p in packages) / len(packages), 1) if packages else 0,
        "popular_packages": sorted(packages, key=lambda x: x.get('downloads', 0), reverse=True)[:5],
        "recent_packages": sorted(packages, key=lambda x: x.get('created_at', ''), reverse=True)[:5],
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🏪 MCP Server Marketplace 启动中...")
    print("=" * 60)
    print(f"\n📦 Marketplace API: http://localhost:9999")
    print(f"📚 API 文档: http://localhost:9999/docs")
    print(f"💾 数据目录: ./marketplace_data/")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(app, host="0.0.0.0", port=9999, log_level="info")

