import { useState } from 'react'
import AddServerModal from './AddServerModal'

function ServerList({ servers, connectedServers, onUpdate }) {
  const [showModal, setShowModal] = useState(false)

  const connectServer = async (serverName) => {
    try {
      const response = await fetch(`/api/servers/${serverName}/connect`, {
        method: 'POST',
      })
      if (response.ok) {
        const result = await response.json()
        onUpdate()
        // 可选：显示连接成功消息
        console.log(`已连接到 ${serverName}，工具:`, result.tools)
      } else {
        const error = await response.json()
        const errorMsg = typeof error.detail === 'string' 
          ? error.detail 
          : JSON.stringify(error.detail)
        alert(`连接失败: ${errorMsg}`)
      }
    } catch (error) {
      const errorMsg = error.message || '未知错误'
      alert(`连接失败: ${errorMsg}`)
      console.error('连接错误:', error)
    }
  }

  const disconnectServer = async (serverName) => {
    try {
      const response = await fetch(`/api/servers/${serverName}/disconnect`, {
        method: 'POST',
      })
      if (response.ok) {
        onUpdate()
      }
    } catch (error) {
      alert(`断开失败: ${error.message}`)
    }
  }

  const deleteServer = async (serverName) => {
    if (!confirm(`确定要删除服务器 "${serverName}" 吗？`)) {
      return
    }

    try {
      const response = await fetch(`/api/servers/${serverName}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        onUpdate()
      }
    } catch (error) {
      alert(`删除失败: ${error.message}`)
    }
  }

  return (
    <div className="server-section">
      <div className="section-header">
        <h2>📡 MCP 服务器</h2>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          + 添加服务器
        </button>
      </div>

      <div className="server-list">
        {servers.length === 0 ? (
          <div className="empty-state">
            <p>暂无服务器配置</p>
            <p className="hint">点击上方按钮添加服务器</p>
          </div>
        ) : (
          servers.map(server => {
            const isConnected = connectedServers.includes(server.name)
            const serverType = server.type || 'stdio'
            
            let displayInfo = ''
            if (serverType === 'rest') {
              displayInfo = `REST API: ${server.url || ''}`
            } else {
              const cmd = server.command || ''
              const args = Array.isArray(server.args) ? server.args.join(' ') : ''
              displayInfo = `${cmd} ${args}`.trim()
            }
            
            return (
              <div key={server.name} className={`server-item ${isConnected ? 'connected' : ''}`}>
                <div className="server-name">
                  <span className={`status-indicator ${isConnected ? 'connected' : ''}`}></span>
                  {server.name}
                  <span className="server-type-badge">{serverType === 'rest' ? 'REST' : 'stdio'}</span>
                </div>
                <div className="server-command">
                  {displayInfo}
                </div>
                <div className="server-actions">
                  {isConnected ? (
                    <button 
                      className="btn btn-sm btn-secondary"
                      onClick={() => disconnectServer(server.name)}
                    >
                      断开
                    </button>
                  ) : (
                    <button 
                      className="btn btn-sm btn-success"
                      onClick={() => connectServer(server.name)}
                    >
                      连接
                    </button>
                  )}
                  <button 
                    className="btn btn-sm btn-danger"
                    onClick={() => deleteServer(server.name)}
                  >
                    删除
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>

      {showModal && (
        <AddServerModal 
          onClose={() => setShowModal(false)}
          onAdd={() => {
            setShowModal(false)
            onUpdate()
          }}
        />
      )}
    </div>
  )
}

export default ServerList

