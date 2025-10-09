import { useState, useEffect } from 'react'
import ServerList from './components/ServerList'
import ToolList from './components/ToolList'
import ChatBox from './components/ChatBox'
import './App.css'

function App() {
  const [servers, setServers] = useState([])
  const [connectedServers, setConnectedServers] = useState([])
  const [tools, setTools] = useState([])

  const loadServers = async () => {
    try {
      const response = await fetch('/api/servers')
      const data = await response.json()
      setServers(data.servers)
      setConnectedServers(data.connected)
    } catch (error) {
      console.error('加载服务器失败:', error)
    }
  }

  const loadTools = async () => {
    try {
      const response = await fetch('/api/tools')
      const data = await response.json()
      setTools(data.tools)
    } catch (error) {
      console.error('加载工具失败:', error)
    }
  }

  useEffect(() => {
    loadServers()
    loadTools()
  }, [])

  const handleServerUpdate = () => {
    loadServers()
    loadTools()
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>🚀 MCP Web Manager</h1>
        </div>
        <div className="header-right">
          <span>动态配置 MCP 服务器并进行智能对话</span>
        </div>
      </header>

      <div className="main-content">
        <div className="sidebar">
          <ServerList 
            servers={servers}
            connectedServers={connectedServers}
            onUpdate={handleServerUpdate}
          />
          
          <ToolList tools={tools} />
        </div>

        <ChatBox />
      </div>
    </div>
  )
}

export default App

