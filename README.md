# 🚀 MCP Web Manager

一个现代化的 MCP (Model Context Protocol) 管理平台，支持动态配置 MCP 服务器并通过 AI 智能调用工具。

## ⚡ 快速开始

### 1. 安装依赖（首次使用）

```bash
# 安装前端依赖
cd client
npm install
cd ..
```

### 2. 启动应用

```bash
start.bat
```

### 3. 访问界面

```
前端: http://localhost:3000
后端: http://localhost:8000/docs
```

---

## 📁 项目结构

```
mcp_test/
├── client/                 # React 前端
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   └── App.jsx        # 主应用
│   └── package.json
│
├── server/                # Python 后端
│   ├── mcp_web_server.py  # FastAPI 服务器
│   └── requirements.txt   # 依赖
│
├── mcp_server_file.py     # 文件工具服务器
├── mcp_server_calc.py     # 计算工具服务器
├── mcp_server_rest.py     # REST API 示例
│
├── start.bat              # 启动脚本
├── run_rest_server.bat    # REST Server 启动
│
├── UI_使用指南.md          # UI 使用文档
└── 后端开发文档.md         # 后端开发文档
```

---

## 🎯 核心功能

### 双协议支持

1. **stdio 协议** - 本地进程通信
2. **REST API 协议** - HTTP 服务通信

### 智能对话

- 集成通义千问大模型
- 自动工具选择和调用
- Markdown 格式渲染

### 可视化管理

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

- **UI 使用指南**: [UI_使用指南.md](UI_使用指南.md)
- **后端开发文档**: [后端开发文档.md](后端开发文档.md)

---

## 🎉 开始使用

```bash
# 1. 安装依赖（首次）
cd client && npm install

# 2. 启动应用
cd .. && start.bat

# 3. 访问
# http://localhost:3000
```

---

**环境**: Python 3.11 (conda: mcp_env)  
**许可**: MIT License


https://www.mcpservers.cn/servers?tab=official-servers


question for demo.

读取 data.txt 文件的内容，然后计算里面所有数字的统计信息，最后用 Python 生成一个可视化报告
搜索最新的人工智能新闻，然后用 Python 提取关键信息，最后保存到 ai_news.txt 文件

计算 sqrt(16) + pow(2, 3)，然后把结果保存到 result.txt，再读取确认一下

生成一个斐波那契数列的 Python 代码，执行它，然后对结果进行统计分析


"用 Python 生成 10 个随机数，计算它们的统计信息，然后保存到 random_stats.txt"


"计算 100 到 200 之间所有数字的平方，然后统计这些平方数的平均值和总和"

"搜索最新的 MCP 协议信息，用 Python 提取关键数据，进行统计分析，然后生成报告保存到文件"