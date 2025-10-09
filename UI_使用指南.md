# 🚀 MCP Web Manager - UI 使用指南

## ⚡ 快速开始

### 一键启动

```bash
start.bat
```

### 访问界面

```
前端: http://localhost:3000
后端: http://localhost:8000/docs
```

---

## 📖 完整使用指南

### 1️⃣ 添加 MCP 服务器

#### 方法 1: stdio 协议（本地进程）

1. 点击 **"+ 添加服务器"**
2. 填写：
   - **名称**: `file-server`
   - **类型**: 选择 **"stdio 协议（本地进程）"**
   - **命令**: `python`
   - **参数**（每行一个）:
     ```
     mcp_server_file.py
     ```
   - **环境变量**（可选）: 
     ```json
     {"PATH": "/usr/bin"}
     ```
3. 点击 **"添加"**

#### 方法 2: REST API（HTTP 服务）

1. 点击 **"+ 添加服务器"**
2. 填写：
   - **名称**: `rest-demo`
   - **类型**: 选择 **"REST API（HTTP 服务）"**
   - **服务器 URL**: `http://localhost:9000`
3. 点击 **"添加"**

### 2️⃣ 连接服务器

1. 在服务器列表中找到服务器
2. 点击 **"连接"** 按钮
3. 等待状态指示器变绿 🟢
4. 工具列表会自动更新

### 3️⃣ 开始对话

在聊天框输入问题：

```
计算 sqrt(256)
创建文件 test.txt，内容是 "Hello"
将 "hello" 转为大写
```

按 **Enter** 发送（或点击发送按钮）

---

## 🎯 界面说明

### 左侧边栏

#### 📡 MCP 服务器区域

**服务器卡片**:
```
┌─────────────────────────────┐
│ 🟢 file-server [stdio]      │
│ python mcp_server_file.py   │
│ [断开] [删除]               │
└─────────────────────────────┘
```

**状态指示器**:
- 🟢 绿色（跳动）= 已连接
- 🔴 灰色 = 未连接

**类型徽章**:
- `[stdio]` = 本地进程
- `[REST]` = HTTP 服务

**操作按钮**:
- **连接** - 连接到服务器
- **断开** - 断开连接
- **删除** - 删除配置

#### 🛠️ 可用工具区域

显示所有已连接服务器的工具：
```
🔧 read_file
📡 file-server
读取指定文件的内容
```

### 右侧聊天区域

#### 💬 消息类型

- **用户消息** - 蓝色气泡，右对齐
- **助手消息** - 灰色气泡，左对齐，支持 Markdown
- **系统消息** - 黄色背景，居中
- **工具调用** - 紫色边框，显示工具和参数
- **工具结果** - 绿色边框，显示执行结果

#### ⌨️ 输入操作

- **Enter** - 发送消息
- **Shift+Enter** - 换行
- **发送按钮** - 点击发送

---

## 💡 使用示例

### 示例 1: 文件操作

```
你: 创建文件 hello.txt，内容是 "Hello MCP!"

🔧 调用工具: file-server:write_file
{"file_path": "hello.txt", "content": "Hello MCP!"}

✅ 工具结果: 成功写入文件: hello.txt

助手: 已成功创建文件 hello.txt
```

### 示例 2: 数学计算

```
你: 计算 sqrt(144) + pow(2, 3)

🔧 调用工具: calc-server:calculator
{"expression": "sqrt(144) + pow(2, 3)"}

✅ 工具结果: 计算结果: ... = 20.0

助手: 计算结果是 20.0
```

### 示例 3: REST API 工具

```
你: 将 "hello world" 转换为大写

🔧 调用工具: rest-demo:uppercase
{"text": "hello world"}

✅ 工具结果: HELLO WORLD

助手: 已转换为大写：HELLO WORLD
```

### 示例 4: 组合使用

```
你: 将 "hello" 转为大写并保存到 result.txt

步骤1: 调用 rest-demo:uppercase
步骤2: 调用 file-server:write_file

助手: 已完成！已将 "HELLO" 保存到 result.txt
```

---

## 🌐 在线 MCP 服务器资源

### MCP 服务器市场

1. **MCP.so** - 16,000+ 服务器
   - https://mcp.so/zh

2. **MCPServers.cn** - 中文社区
   - https://www.mcpservers.cn

3. **MCP.pizza** - 开发者工具
   - https://www.mcp.pizza

### 热门服务器

#### 开发工具类
```json
{
  "name": "github",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {"GITHUB_TOKEN": "your-token"}
}
```

#### 搜索工具类
```json
{
  "name": "brave-search",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {"BRAVE_API_KEY": "your-key"}
}
```

#### 数据库类
```json
{
  "name": "sqlite",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/db.sqlite"]
}
```

---

## 🎨 Markdown 支持

助手回复支持 Markdown 格式：

### 支持的语法

- **粗体**: `**文本**`
- *斜体*: `*文本*`
- 列表: `- 项目`
- 代码: `` `代码` ``
- 代码块: ` ```代码``` `
- 链接: `[文本](URL)`
- 标题: `# ## ###`

### 示例效果

AI 返回的 Markdown:
```markdown
今天的天气：
- **气温**: 25°C
- **状况**: 晴朗
```

显示效果：
- **气温**: 25°C
- **状况**: 晴朗

---

## ⚙️ 配置文件

### mcp_servers_config.json

所有服务器配置自动保存：

```json
{
  "servers": [
    {
      "name": "file-server",
      "type": "stdio",
      "command": "python",
      "args": ["mcp_server_file.py"],
      "env": null
    },
    {
      "name": "rest-demo",
      "type": "rest",
      "url": "http://localhost:9000",
      "env": null
    }
  ]
}
```

---

## 🐛 故障排除

### 问题 1: WebSocket 未连接

**症状**: 显示 "❌ WebSocket 未连接"

**解决**:
1. 确认后端运行在 8000 端口
2. 刷新页面（Ctrl + Shift + R）
3. 查看浏览器控制台（F12）
4. 重启服务（`start.bat`）

### 问题 2: 服务器连接失败

**stdio 服务器**:
- 检查命令和文件路径是否正确
- 确认 Python 环境已激活
- 查看后端终端日志

**REST 服务器**:
- 确认 URL 可访问（浏览器打开测试）
- 检查 REST Server 是否运行
- 访问 `{url}/mcp/tools` 测试

### 问题 3: 工具调用失败

**检查**:
1. 服务器状态是否为绿色🟢
2. 工具列表是否显示
3. 浏览器控制台是否有错误
4. 后端日志是否有错误

### 问题 4: 页面显示异常

**解决**:
```
按 Ctrl + Shift + R 强制刷新
```

---

## 🔧 高级功能

### 快捷键

- `Enter` - 发送消息
- `Shift + Enter` - 换行
- `Ctrl + Shift + R` - 刷新页面

### 消息操作

- **清空对话** - 点击聊天框顶部的"清空对话"按钮

### 多服务器使用

可以同时连接多个服务器，AI 会自动选择合适的工具。

---

## 📱 响应式设计

- **桌面端**: 左右分栏布局
- **平板端**: 自适应调整
- **移动端**: 垂直堆叠布局

---

## 🎉 快速参考

### 启动应用
```bash
start.bat
# http://localhost:3000
```

### 添加服务器
```
+ 添加服务器 → 填写配置 → 添加
```

### 连接服务器
```
服务器卡片 → 连接按钮 → 等待绿色🟢
```

### 开始对话
```
输入问题 → Enter 发送
```

---

**享受 MCP Web Manager！** 🚀

