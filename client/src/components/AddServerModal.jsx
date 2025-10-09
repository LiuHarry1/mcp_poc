import { useState } from 'react'

function AddServerModal({ onClose, onAdd }) {
  const [formData, setFormData] = useState({
    name: '',
    type: 'stdio',
    command: '',
    args: '',
    url: '',
    env: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()

    let config = {
      name: formData.name,
      type: formData.type
    }

    if (formData.type === 'stdio') {
      // stdio 类型配置
      const args = formData.args.split('\n').map(a => a.trim()).filter(a => a)
      
      let env = null
      if (formData.env.trim()) {
        try {
          env = JSON.parse(formData.env)
        } catch (e) {
          alert('环境变量 JSON 格式错误')
          return
        }
      }

      config.command = formData.command
      config.args = args
      config.env = env
    } else {
      // rest 类型配置
      config.url = formData.url
    }

    try {
      const response = await fetch('/api/servers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })

      if (!response.ok) {
        const error = await response.json()
        const errorMsg = typeof error.detail === 'string' 
          ? error.detail 
          : JSON.stringify(error.detail)
        throw new Error(errorMsg || '添加失败')
      }

      onAdd()
    } catch (error) {
      const errorMsg = error.message || '添加失败'
      alert(errorMsg)
      console.error('添加服务器错误:', error)
    }
  }

  return (
    <div className="modal show">
      <div className="modal-content">
        <div className="modal-header">
          <h2>添加 MCP 服务器</h2>
          <span className="close" onClick={onClose}>&times;</span>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>服务器名称 *</label>
              <input 
                type="text" 
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="例如: file-server"
              />
            </div>

            <div className="form-group">
              <label>服务器类型 *</label>
              <select 
                value={formData.type}
                onChange={(e) => setFormData({...formData, type: e.target.value})}
                className="form-select"
              >
                <option value="stdio">stdio 协议（本地进程）</option>
                <option value="rest">REST API（HTTP 服务）</option>
              </select>
            </div>

            {formData.type === 'stdio' ? (
              <>
                <div className="form-group">
                  <label>命令 *</label>
                  <input 
                    type="text" 
                    required
                    value={formData.command}
                    onChange={(e) => setFormData({...formData, command: e.target.value})}
                    placeholder="例如: python"
                  />
                </div>

                <div className="form-group">
                  <label>参数（每行一个）*</label>
                  <textarea 
                    required
                    rows="3"
                    value={formData.args}
                    onChange={(e) => setFormData({...formData, args: e.target.value})}
                    placeholder="例如:&#10;mcp_server_file.py"
                  />
                </div>

                <div className="form-group">
                  <label>环境变量（JSON格式，可选）</label>
                  <textarea 
                    rows="2"
                    value={formData.env}
                    onChange={(e) => setFormData({...formData, env: e.target.value})}
                    placeholder='例如: {"PATH": "/usr/bin"}'
                  />
                </div>
              </>
            ) : (
              <div className="form-group">
                <label>服务器 URL *</label>
                <input 
                  type="url" 
                  required
                  value={formData.url}
                  onChange={(e) => setFormData({...formData, url: e.target.value})}
                  placeholder="例如: http://localhost:9000"
                />
                <small style={{color: '#64748b', fontSize: '12px', marginTop: '5px', display: 'block'}}>
                  REST API 服务器的基础 URL（会自动调用 /mcp/tools 和 /mcp/call 端点）
                </small>
              </div>
            )}

            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                取消
              </button>
              <button type="submit" className="btn btn-primary">
                添加
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default AddServerModal

