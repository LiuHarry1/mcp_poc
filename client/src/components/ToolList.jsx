function ToolList({ tools }) {
  return (
    <div className="tool-section">
      <div className="section-header">
        <h2>🛠️ 可用工具</h2>
        <span className="badge">{tools.length}</span>
      </div>

      <div className="tool-list">
        {tools.length === 0 ? (
          <div className="empty-state">
            <p className="hint">连接服务器后显示工具</p>
          </div>
        ) : (
          tools.map(tool => (
            <div key={tool.key} className="tool-item">
              <div className="tool-name">🔧 {tool.name}</div>
              <div className="tool-server">📡 {tool.server}</div>
              <div className="tool-description">{tool.description}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ToolList

