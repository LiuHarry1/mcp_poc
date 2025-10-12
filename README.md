# 🚀 MCP Web Manager with Marketplace

一个现代化的 MCP (Model Context Protocol) 管理平台，包含**内部 MCP Server Marketplace**，支持浏览、安装和管理 MCP 服务器，并通过 AI 智能调用工具。

## 🆕 新功能：MCP Server Marketplace

🏪 **内部应用商店** - 类似 VS Code Extension Marketplace
- 📦 浏览所有可用的 MCP Servers
- 🔍 搜索和按分类过滤
- 📥 一键安装想要的 Server
- ⭐ 评分和评论系统
- 📝 发布自己的 MCP Server

## ⚡ 快速开始

### 方式一：启动 Marketplace（推荐）

```bash
# Windows
cd mcp_marketplace
start_marketplace.bat

# macOS/Linux
cd mcp_marketplace
chmod +x start_marketplace.sh
./start_marketplace.sh
```

然后访问：**http://localhost:5173** 

### 方式二：仅启动基础功能

```bash
# 1. 安装前端依赖（首次使用）
cd client
npm install
cd ..

# 2. 启动应用
start.bat

# 3. 访问界面
# 前端: http://localhost:5173
# 后端: http://localhost:8000/docs
```

---

## 📁 项目结构

```
mcp_poc/
├── mcp_marketplace/                      # 🆕 Marketplace 模块
│   ├── marketplace_server.py             # Marketplace 后端服务器
│   ├── mcp_publish_tool.py              # CLI 发布工具
│   ├── init_marketplace.py              # 初始化脚本
│   ├── test_marketplace.py              # 功能测试脚本
│   ├── start_marketplace.bat            # Windows 启动脚本
│   ├── start_marketplace.sh             # Unix 启动脚本
│   │
│   ├── packages/                        # 包配置文件
│   │   ├── file-server-package.json
│   │   ├── calc-server-package.json
│   │   ├── python-executor-package.json
│   │   ├── rest-test-package.json
│   │   └── tavily-search-package.json
│   │
│   ├── marketplace_data/                # 数据存储（自动生成）
│   │   ├── packages.json
│   │   ├── ratings.json
│   │   └── files/
│   │
│   ├── README.md                        # Marketplace 说明
│   ├── MARKETPLACE_README.md            # 详细功能文档
│   ├── QUICKSTART.md                    # 快速开始指南
│   ├── DEMO_GUIDE.md                    # 演示指南
│   └── IMPLEMENTATION_SUMMARY.md        # 实现总结
│
├── client/                              # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── MarketplaceView.jsx      # 🆕 Marketplace 视图
│   │   │   ├── ServerList.jsx
│   │   │   ├── ToolList.jsx
│   │   │   └── ChatBox.jsx
│   │   └── App.jsx                      # 主应用
│   └── package.json
│
├── server/                              # Python 后端
│   ├── mcp_web_server.py                # FastAPI 服务器
│   └── requirements.txt                 # 依赖
│
├── mcp_server_file.py                   # 文件工具服务器
├── mcp_server_calc.py                   # 计算工具服务器
├── mcp_server_python_executor.py        # Python 执行器
├── mcp_server_rest.py                   # REST API 示例
│
├── README.md                            # 本文件
├── UI_使用指南.md                        # UI 使用文档
└── 后端开发文档.md                       # 后端开发文档
```

---

## 🎯 核心功能

### 🏪 MCP Server Marketplace（新功能）

- **浏览商店** - 查看所有可用的 MCP Servers
- **搜索过滤** - 按名称、描述、标签搜索
- **分类导航** - 按功能分类（文件、计算、搜索、AI等）
- **一键安装** - 自动配置和安装 Server
- **评分系统** - 为 Server 评分和评论
- **发布工具** - CLI 工具快速发布 Server

### 🔌 双协议支持

1. **stdio 协议** - 本地进程通信
2. **REST API 协议** - HTTP 服务通信

### 💬 智能对话

- 集成通义千问大模型
- 自动工具选择和调用
- Markdown 格式渲染

### ⚙️ 可视化管理

- 动态添加/删除服务器
- 实时连接/断开
- 工具自动发现

---

## 🛠️ 技术栈

**前端**: React 18 + Vite  
**后端**: FastAPI + Python 3.11  
**通信**: REST API + WebSocket  
**AI**: 通义千问（Qwen）  
**协议**: MCP stdio + REST API

---

## 📚 文档

- **🚀 快速开始指南**: [mcp_marketplace/QUICKSTART.md](mcp_marketplace/QUICKSTART.md) - 30秒上手
- **🏪 Marketplace 详细文档**: [mcp_marketplace/MARKETPLACE_README.md](mcp_marketplace/MARKETPLACE_README.md) - 完整功能介绍
- **📖 演示指南**: [mcp_marketplace/DEMO_GUIDE.md](mcp_marketplace/DEMO_GUIDE.md) - 完整演示流程
- **UI 使用指南**: [UI_使用指南.md](UI_使用指南.md)
- **后端开发文档**: [后端开发文档.md](后端开发文档.md)

---

## 🎉 30秒快速体验

```bash
# Windows
cd mcp_marketplace
start_marketplace.bat

# macOS/Linux
cd mcp_marketplace
chmod +x start_marketplace.sh
./start_marketplace.sh
```

然后访问 **http://localhost:5173** 开始浏览 Marketplace！

### 推荐体验流程

1. 🏪 浏览 Marketplace，查看 5 个示例 Server
2. 📥 安装 "文件操作服务器"
3. 🔌 在管理器页面连接 Server
4. 💬 在聊天框中让 AI 创建文件：`创建一个文件 test.txt，内容是 "Hello!"`

---

## 🛠️ 发布你的 MCP Server

```bash
cd mcp_marketplace

# 1. 初始化包配置
python mcp_publish_tool.py init

# 2. 编辑生成的 mcp_package.json

# 3. 发布到 Marketplace
python mcp_publish_tool.py publish
```

详见 [mcp_marketplace/MARKETPLACE_README.md](mcp_marketplace/MARKETPLACE_README.md)

---

## 📊 服务端口

- **Marketplace API**: http://localhost:9999
- **MCP Web API**: http://localhost:8000
- **Web UI**: http://localhost:5173

---

## 💡 示例问题（安装对应 Server 后）

### 文件操作
```
创建一个文件 test.txt，内容是 "Hello from MCP!"
读取 data.txt 的内容并告诉我
```

### 数学计算
```
计算 sqrt(16) + pow(2, 3)
计算这些数字的统计信息：[10, 20, 30, 40, 50]
```

### Python 执行
```
用 Python 生成一个斐波那契数列前10项
生成 10 个随机数，计算它们的平均值
```

### 组合使用（多个 Server）
```
用 Python 生成 10 个随机数，计算它们的统计信息，然后保存到 random_stats.txt
计算 100 到 200 之间所有数字的平方，然后统计这些平方数的平均值和总和，保存到文件
```

---

## 🌟 特色亮点

✅ **应用商店模式** - 像 VS Code 一样浏览和安装扩展  
✅ **零配置安装** - 一键安装，自动配置  
✅ **内部生态** - 团队共享和复用工具  
✅ **智能 AI 集成** - 自动工具调用  
✅ **双协议支持** - stdio 和 REST API  
✅ **实时统计** - 下载量、评分、热门排行

---

## 🔗 相关资源

- **官方 MCP Servers**: https://www.mcpservers.cn/servers
- **MCP 协议文档**: https://modelcontextprotocol.io
- **GitHub MCP Servers**: https://github.com/modelcontextprotocol/servers

---

**环境**: Python 3.11 (conda: mcp_env)  
**许可**: MIT License  
**贡献**: 欢迎提交 PR 和 Issue