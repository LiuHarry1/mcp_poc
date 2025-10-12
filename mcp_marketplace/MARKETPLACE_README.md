# 🏪 MCP Server Marketplace 使用指南

## 📖 简介

MCP Server Marketplace 是一个内部的 MCP Server 应用商店，类似于 VS Code Extension Marketplace 或 npm registry。用户可以：

- 🔍 **浏览** - 查看所有可用的 MCP Servers
- 🔎 **搜索** - 按名称、描述、标签搜索
- 📂 **分类** - 按功能分类浏览（文件、计算、搜索等）
- 📥 **安装** - 一键安装想要的 MCP Server
- ⭐ **评分** - 为使用过的 Server 评分和评论

---

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

```bash
# Windows
start_marketplace.bat

# macOS/Linux
chmod +x start_marketplace.sh
./start_marketplace.sh
```

### 方式二：手动启动

1. **启动 Marketplace 服务器**
```bash
python marketplace_server.py
# 运行在 http://localhost:9999
```

2. **初始化示例数据**
```bash
python init_marketplace.py
```

3. **启动 MCP Web Server**
```bash
cd server
python mcp_web_server.py
# 运行在 http://localhost:8000
```

4. **启动前端**
```bash
cd client
npm run dev
# 运行在 http://localhost:5173
```

---

## 🎯 功能使用

### 1. 浏览 Marketplace

访问 http://localhost:5173，点击顶部的 **🏪 Marketplace** 标签页。

你会看到：
- 📊 统计信息卡片（总包数、下载量等）
- 🔍 搜索框
- 📂 分类导航
- 📦 包列表

### 2. 搜索 Server

在搜索框中输入关键词，例如：
- "文件" - 查找文件操作相关的 Server
- "python" - 查找 Python 相关的 Server
- "计算" - 查找计算工具

### 3. 按分类浏览

点击分类按钮过滤：
- 📁 文件操作
- 🧮 计算工具
- 🔍 搜索服务
- 🤖 AI 工具
- 💾 数据库
- 🔌 API 集成
- ⚙️ DevOps
- 💻 代码执行

### 4. 查看包详情

点击任何包卡片，会弹出详情模态框，显示：
- 📝 完整描述
- 🏷️ 标签
- 📦 依赖
- 🔐 需要的环境变量
- ⚙️ 安装配置
- ⭐ 评分和评论

### 5. 安装 Server

方式一：在包卡片上点击 **安装** 按钮

方式二：在详情模态框中点击 **安装** 按钮

安装后会自动：
1. 下载 Server 配置
2. 添加到本地服务器列表
3. 跳转到管理器页面

然后在 **⚙️ 管理器** 页面中点击 **连接** 即可使用。

---

## 📦 发布 MCP Server

### 方式一：使用 CLI 工具（推荐）

1. **初始化包配置**
```bash
python mcp_publish_tool.py init
```

按照提示输入信息，会生成 `mcp_package.json` 文件。

2. **编辑配置文件**

示例配置：
```json
{
  "id": "team-name/server-name",
  "name": "My Awesome Server",
  "description": "一句话描述",
  "long_description": "详细说明（支持 Markdown）",
  "version": "1.0.0",
  "author": "Your Team",
  "category": "file",
  "tags": ["文件", "工具", "python"],
  "type": "stdio",
  "install_config": {
    "command": "python",
    "args": ["my_server.py"]
  },
  "dependencies": [],
  "requires_env": []
}
```

3. **发布到 Marketplace**
```bash
python mcp_publish_tool.py publish
```

### 方式二：使用 API

```python
import requests

package_data = {
    "id": "team/server",
    "name": "My Server",
    # ... 其他字段
}

response = requests.post(
    "http://localhost:9999/marketplace/packages",
    json=package_data
)
```

---

## 🔧 CLI 工具命令

### 初始化包配置
```bash
python mcp_publish_tool.py init
```

### 发布包
```bash
python mcp_publish_tool.py publish
python mcp_publish_tool.py publish --config custom.json
```

### 查看包信息
```bash
python mcp_publish_tool.py info team/server-name
```

### 列出所有包
```bash
python mcp_publish_tool.py list
python mcp_publish_tool.py list --category file
python mcp_publish_tool.py list --query 搜索
```

### 删除包
```bash
python mcp_publish_tool.py delete team/server-name
```

---

## 📋 包配置字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识，格式：`team/name` |
| `name` | string | ✅ | 显示名称 |
| `description` | string | ✅ | 简短描述（一句话） |
| `long_description` | string | ❌ | 详细说明（支持 Markdown） |
| `version` | string | ✅ | 版本号，如 `1.0.0` |
| `author` | string | ✅ | 作者或团队名称 |
| `category` | string | ✅ | 分类：`file`, `compute`, `search`, `ai`, `database`, `api`, `devops`, `code` |
| `tags` | array | ❌ | 标签列表 |
| `type` | string | ✅ | 类型：`stdio`, `rest`, `docker` |
| `install_config` | object | ✅ | 安装配置（根据类型不同） |
| `dependencies` | array | ❌ | Python/Node 依赖 |
| `requires_env` | array | ❌ | 需要的环境变量 |

### install_config 示例

**stdio 类型：**
```json
{
  "command": "python",
  "args": ["server.py"]
}
```

**rest 类型：**
```json
{
  "url": "http://localhost:9000"
}
```

**docker 类型：**
```json
{
  "image": "company/mcp-server:1.0",
  "ports": ["9000:9000"]
}
```

---

## 🔌 API 文档

Marketplace 提供 RESTful API，访问 http://localhost:9999/docs 查看完整文档。

### 主要端点

- `GET /marketplace/packages` - 列出所有包
- `GET /marketplace/packages/{id}` - 获取包详情
- `POST /marketplace/packages` - 发布包
- `DELETE /marketplace/packages/{id}` - 删除包
- `POST /marketplace/packages/{id}/download` - 下载包
- `GET /marketplace/categories` - 获取分类列表
- `GET /marketplace/stats` - 获取统计信息

---

## 📁 目录结构

```
mcp_poc/
├── marketplace_server.py          # Marketplace 后端服务器
├── mcp_publish_tool.py            # CLI 发布工具
├── init_marketplace.py            # 初始化脚本
├── start_marketplace.bat          # 启动脚本 (Windows)
│
├── packages/                      # 包配置文件目录
│   ├── file-server-package.json
│   ├── calc-server-package.json
│   ├── python-executor-package.json
│   ├── rest-test-package.json
│   └── tavily-search-package.json
│
├── marketplace_data/              # Marketplace 数据目录（自动创建）
│   ├── packages.json              # 包数据
│   ├── ratings.json               # 评分数据
│   └── files/                     # 文件存储
│
├── client/                        # 前端
│   └── src/
│       └── components/
│           ├── MarketplaceView.jsx    # Marketplace 视图
│           └── MarketplaceView.css    # 样式
│
└── server/
    └── mcp_web_server.py          # MCP Web API
```

---

## 🎨 自定义和扩展

### 添加新分类

编辑 `marketplace_server.py` 中的 `list_categories` 函数：

```python
categories = [
    {"id": "new-category", "name": "新分类", "icon": "🆕", "description": "描述"},
    # ... 其他分类
]
```

### 添加包图标

在包配置中设置 `icon_url`：

```json
{
  "icon_url": "https://your-cdn.com/icon.png"
}
```

### 自定义样式

编辑 `client/src/components/MarketplaceView.css` 修改主题色、布局等。

---

## ❓ 常见问题

### Q: Marketplace 服务器无法启动？
A: 检查端口 9999 是否被占用：
```bash
netstat -ano | findstr :9999   # Windows
lsof -i :9999                  # macOS/Linux
```

### Q: 安装后找不到 Server？
A: 
1. 确保安装成功（查看提示）
2. 刷新页面
3. 切换到 **⚙️ 管理器** 页面查看

### Q: 如何卸载 Server？
A: 在 **⚙️ 管理器** 页面中点击 **删除** 按钮。

### Q: 如何更新已发布的包？
A: 使用相同的 `id` 重新发布即可更新。

### Q: 支持私有包吗？
A: 当前版本支持团队隔离（通过 `id` 前缀），完整的权限管理需要添加认证系统。

---

## 🚧 后续规划

- [ ] 用户认证和权限管理
- [ ] 包版本历史
- [ ] 依赖自动安装
- [ ] Docker 支持
- [ ] 更新通知
- [ ] 使用统计和分析
- [ ] 包评论系统
- [ ] CI/CD 集成

---

## 📞 支持

如有问题或建议，请联系内部技术团队。

---

**享受使用 MCP Server Marketplace！** 🎉

