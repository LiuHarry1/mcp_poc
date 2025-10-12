# 🏪 MCP Server Marketplace

内部 MCP Server 应用商店 - 浏览、安装和分享 MCP Servers

## 📁 目录结构

```
mcp_marketplace/
├── marketplace_server.py          # Marketplace 后端服务器 (Port 9999)
├── mcp_publish_tool.py            # CLI 发布工具
├── init_marketplace.py            # 数据初始化脚本
├── test_marketplace.py            # 功能测试脚本
│
├── start_marketplace.bat          # Windows 启动脚本
├── start_marketplace.sh           # macOS/Linux 启动脚本
│
├── packages/                      # 示例包配置文件
│   ├── file-server-package.json
│   ├── calc-server-package.json
│   ├── python-executor-package.json
│   ├── rest-test-package.json
│   └── tavily-search-package.json
│
├── marketplace_data/              # 数据存储（自动生成）
│   ├── packages.json
│   ├── ratings.json
│   └── files/
│
├── README.md                      # 本文件
├── MARKETPLACE_README.md          # 详细功能文档
├── QUICKSTART.md                  # 快速开始指南
├── DEMO_GUIDE.md                  # 演示指南
└── IMPLEMENTATION_SUMMARY.md      # 实现总结
```

## 🚀 快速开始

### 启动 Marketplace

**Windows:**
```bash
cd mcp_marketplace
start_marketplace.bat
```

**macOS/Linux:**
```bash
cd mcp_marketplace
chmod +x start_marketplace.sh
./start_marketplace.sh
```

### 访问界面
http://localhost:5173

---

## 📦 核心组件

### 1. Marketplace Server (`marketplace_server.py`)
- FastAPI 后端服务器
- 端口：9999
- 提供包注册、搜索、下载等 API
- API 文档：http://localhost:9999/docs

### 2. CLI 工具 (`mcp_publish_tool.py`)

**初始化包配置：**
```bash
python mcp_publish_tool.py init
```

**发布包：**
```bash
python mcp_publish_tool.py publish
```

**列出所有包：**
```bash
python mcp_publish_tool.py list
```

**查看包详情：**
```bash
python mcp_publish_tool.py info <package-id>
```

**删除包：**
```bash
python mcp_publish_tool.py delete <package-id>
```

### 3. 初始化脚本 (`init_marketplace.py`)
自动将 `packages/` 目录中的示例包发布到 Marketplace

```bash
python init_marketplace.py
```

### 4. 测试脚本 (`test_marketplace.py`)
测试 Marketplace 所有功能是否正常

```bash
python test_marketplace.py
```

### 5. Registry Manager (`registry_manager.py`) 🆕

支持从 Git Repository 安装 Server，类似 npm、pip、Homebrew。

**初始化注册仓库：**
```bash
python registry_manager.py init https://github.com/company/mcp-registry.git
```

**列出所有 Server：**
```bash
python registry_manager.py list
```

**从注册仓库安装：**
```bash
python registry_manager.py install company/file-server
```

**直接从 Git 安装：**
```bash
python registry_manager.py install-git https://github.com/user/mcp-server.git
```

详见 [REGISTRY_QUICKSTART.md](REGISTRY_QUICKSTART.md)

---

## 🎯 主要功能

- **📦 包管理** - 注册、搜索、下载 MCP Servers
- **🔍 搜索过滤** - 按名称、描述、标签搜索
- **📂 分类系统** - 8个功能分类
- **⭐ 评分系统** - 用户评价和反馈
- **📊 统计分析** - 下载量、评分、热门排行
- **🔌 多协议** - 支持 stdio、REST API
- **🆕 Git Repository** - 支持从 Git 仓库安装 Server（类似 npm、pip）

---

## 📚 详细文档

- **[QUICKSTART.md](QUICKSTART.md)** - 30秒快速开始
- **[MARKETPLACE_README.md](MARKETPLACE_README.md)** - 完整功能文档
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - 演示指南
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - 实现总结
- **🆕 [REGISTRY_GUIDE.md](REGISTRY_GUIDE.md)** - Git Repository 注册方式详解
- **🆕 [REGISTRY_QUICKSTART.md](REGISTRY_QUICKSTART.md)** - Git Registry 快速开始

---

## 🛠️ 技术栈

- **FastAPI** - 后端框架
- **Pydantic** - 数据验证
- **Click** - CLI 框架
- **JSON** - 数据存储

---

## 📊 服务端口

- **Marketplace API**: http://localhost:9999
- **MCP Web Server**: http://localhost:8000 (在父目录)
- **Frontend**: http://localhost:5173 (在父目录)

---

## 🎉 开始使用

1. 启动服务：`./start_marketplace.sh`
2. 访问界面：http://localhost:5173
3. 浏览 Marketplace 标签页
4. 安装想要的 MCP Server
5. 享受！

更多信息请参考 [QUICKSTART.md](QUICKSTART.md)

