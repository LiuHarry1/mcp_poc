import { useState, useEffect } from 'react'
import ServerList from './components/ServerList'
import ToolList from './components/ToolList'
import ChatBox from './components/ChatBox'
import MarketplaceView from './components/MarketplaceView'
import './App.css'

function App() {
  const [servers, setServers] = useState([])
  const [connectedServers, setConnectedServers] = useState([])
  const [tools, setTools] = useState([])
  const [activeTab, setActiveTab] = useState('marketplace') // 'marketplace' or 'manager'

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

  const handleInstallFromMarketplace = () => {
    // 安装完成后刷新服务器列表并切换到管理页面
    loadServers()
    setActiveTab('manager')
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>🚀 MCP Web Manager</h1>
        </div>
        <div className="header-right">
          <div className="tab-nav">
            <button 
              className={`tab-btn ${activeTab === 'marketplace' ? 'active' : ''}`}
              onClick={() => setActiveTab('marketplace')}
            >
              🏪 Marketplace
            </button>
            <button 
              className={`tab-btn ${activeTab === 'manager' ? 'active' : ''}`}
              onClick={() => setActiveTab('manager')}
            >
              ⚙️ 管理器
            </button>
          </div>
        </div>
      </header>

      <div className="main-content">
        {activeTab === 'marketplace' ? (
          <MarketplaceView onInstall={handleInstallFromMarketplace} />
        ) : (
          <>
            <div className="sidebar">
              <ServerList 
                servers={servers}
                connectedServers={connectedServers}
                onUpdate={handleServerUpdate}
              />
              
              <ToolList tools={tools} />
            </div>

            <ChatBox />
          </>
        )}
      </div>
    </div>
  )
}

export default App

