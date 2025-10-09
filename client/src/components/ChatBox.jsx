import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'

function ChatBox() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [ws, setWs] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    let websocket = null
    let reconnectTimeout = null
    
    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/chat`
      
      console.log('正在连接 WebSocket:', wsUrl)
      
      websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        console.log('✅ WebSocket 连接已建立')
        setWs(websocket)
      }
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      }
      
      websocket.onerror = (error) => {
        console.error('❌ WebSocket 错误:', error)
      }
      
      websocket.onclose = (event) => {
        console.log('WebSocket 连接已关闭, code:', event.code, 'reason:', event.reason)
        setWs(null)
        
        // 3秒后自动重连
        console.log('将在 3 秒后重新连接...')
        reconnectTimeout = setTimeout(() => {
          console.log('尝试重新连接 WebSocket...')
          connect()
        }, 3000)
      }
    }
    
    connect()
    
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
      if (websocket) {
        websocket.close()
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'tool_call':
        setMessages(prev => [...prev, {
          type: 'tool_call',
          tool: data.tool,
          arguments: data.arguments
        }])
        break
      case 'tool_result':
        setMessages(prev => [...prev, {
          type: 'tool_result',
          tool: data.tool,
          result: data.result
        }])
        break
      case 'response':
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: data.content
        }])
        break
      case 'error':
        setMessages(prev => [...prev, {
          type: 'system',
          content: `❌ 错误: ${data.content}`
        }])
        break
    }
  }

  const sendMessage = () => {
    console.log('发送消息按钮被点击')
    console.log('输入内容:', input)
    console.log('WebSocket 状态:', ws ? ws.readyState : 'null')
    
    if (!input.trim()) {
      console.log('输入为空，不发送')
      return
    }
    
    if (!ws) {
      console.error('WebSocket 未连接')
      setMessages(prev => [...prev, {
        type: 'system',
        content: '❌ WebSocket 未连接，请刷新页面重试'
      }])
      return
    }
    
    if (ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket 未就绪，状态:', ws.readyState)
      setMessages(prev => [...prev, {
        type: 'system',
        content: '❌ WebSocket 连接未就绪，请稍后重试'
      }])
      return
    }

    console.log('发送消息到服务器:', input)
    
    // 添加用户消息
    setMessages(prev => [...prev, {
      type: 'user',
      content: input
    }])

    // 发送到服务器
    try {
      ws.send(JSON.stringify({ message: input }))
      console.log('消息已发送')
    } catch (error) {
      console.error('发送消息失败:', error)
      setMessages(prev => [...prev, {
        type: 'system',
        content: `❌ 发送失败: ${error.message}`
      }])
    }

    // 清空输入框
    setInput('')
  }

  const clearChat = () => {
    setMessages([])
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>💬 智能助手</h2>
        <button className="btn btn-sm btn-secondary" onClick={clearChat}>
          清空对话
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>👋 欢迎使用 MCP Web Manager!</h3>
            <p>请先在左侧配置并连接 MCP 服务器，然后就可以开始对话了。</p>
            <ul>
              <li>✅ 配置 MCP 服务器</li>
              <li>✅ 连接到服务器</li>
              <li>✅ 开始智能对话</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx}>
              {msg.type === 'user' && (
                <div className="message user">{msg.content}</div>
              )}
              {msg.type === 'assistant' && (
                <div className="message assistant">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
              {msg.type === 'system' && (
                <div className="message system">{msg.content}</div>
              )}
              {msg.type === 'tool_call' && (
                <div className="tool-call">
                  <div className="tool-call-header">🔧 调用工具: {msg.tool}</div>
                  <pre className="tool-call-args">
                    {JSON.stringify(msg.arguments, null, 2)}
                  </pre>
                </div>
              )}
              {msg.type === 'tool_result' && (
                <div className="tool-result">
                  <div className="tool-result-header">✅ 工具结果: {msg.tool}</div>
                  <div className="tool-result-content">{msg.result}</div>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你的问题...（支持 Shift+Enter 换行，Enter 发送）"
          rows="3"
        />
        <button className="btn btn-primary" onClick={sendMessage}>
          发送
        </button>
      </div>
    </div>
  )
}

export default ChatBox

