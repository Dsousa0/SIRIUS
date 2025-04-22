import React, { useState, useEffect, useRef } from 'react' 
import Message from './Message'

function ChatWindow({ messages, addMessage, setTyping, typing, chatId, setChatId, setMessages, onChatCreated, atualizarTituloLocalmente }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const [fileId, setFileId] = useState(null)
  const [fileName, setFileName] = useState('')
  const token = localStorage.getItem('token')
  
  const criarChat = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chats/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ title: 'Novo chat' }),
      })

      const text = await response.text()

      try {
        const data = JSON.parse(text)

        if (data.id) {
          setChatId(data.id)
          if (onChatCreated) onChatCreated()
          return data.id
        } else {
          console.error('Erro no retorno do chat:', data)
        }

      } catch {
        console.error('Resposta não JSON ao criar chat:', text)
      }

    } catch (err) {
      console.error('Erro ao criar chat:', err)
    }
  }

  const salvarMensagem = async (chat_id, role, content) => {
    try {
      await fetch(`http://localhost:8000/api/chats/${chat_id}/mensagens/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role, content })
      })
    } catch (err) {
      console.error('Erro ao salvar mensagem:', err)
    }
  }

  const handleSend = async () => {
    if (!input.trim()) return
    addMessage({ role: 'user', content: input })

    let activeChatId = chatId
    const isPrimeiraPergunta = messages.filter(m => m.role === 'user').length === 0

    if (!activeChatId) {
      activeChatId = await criarChat()
    }

    await salvarMensagem(activeChatId, 'user', input)

    if (isPrimeiraPergunta && input.length > 3) {
      try {
        const titulo = input.slice(0, 40)
        await fetch(`http://localhost:8000/api/chats/${activeChatId}/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ title: titulo })
        })
        if (typeof atualizarTituloLocalmente === 'function') {
          atualizarTituloLocalmente(activeChatId, input)
        }
      } catch (err) {
        console.error('Erro ao atualizar título do chat:', err)
      }
    }
    
    setTyping(true)
    
    try {
      let response
      if (fileId) {
        response = await fetch('http://localhost:8000/api/analyze/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ file_id: fileId, prompt: input }),
        })
    } else { 
      response = await fetch('http://localhost:8000/api/chat-livre/',{
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt: input, chat_id: activeChatId }),
      })
    }
      const contentType = response.headers.get('content-type')

      if (contentType && contentType.includes('application/json')) {
        const data = await response.json()
        setTyping(false)

        if (data.insights) {
          addMessage({ role: 'assistant', content: data.insights })
          await salvarMensagem(activeChatId, 'assistant', data.insights)
        } else if (data.response) {
          addMessage({ role: 'assistant', content: data.response })
          await salvarMensagem(activeChatId, 'assistant', data.response)
        }else if (data.error) {
          addMessage({ role: 'assistant', content: `❌ ${data.error}` })
        } else {
          addMessage({ role: 'assistant', content: '❌ Erro ao processar os dados.' })
        }

        setInput('')
      } else {
        const text = await response.text()
        console.error('Resposta não JSON (análise):', text)
        setTyping(false)
        addMessage({ role: 'assistant', content: '❌ Resposta inesperada do servidor.' })
      }

    } catch (error) {
      console.error('Erro ao chamar /api/analyze/ ou /chat-livre/:', error)
      setTyping(false)
      addMessage({ role: 'assistant', content: '❌ Erro de conexão com o servidor.' })
    }
  }

  const handleFileUpload = async (e) => {
    const selected = e.target.files[0]
    if (!selected) return

    setFileName(selected.name)

    const formData = new FormData()
    formData.append('arquivo', selected)

    try {
      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      })

      const data = await response.json()

      if (data.file_id) {
        setFileId(data.file_id)
        addMessage({
          role: 'system',
          content: `✅ Arquivo "${selected.name}" enviado com sucesso! Pronto para análise.`,
        })
      } else {
        addMessage({ role: 'system', content: '⚠️ Arquivo enviado, mas resposta inesperada do servidor.' })
      }
    } catch (error) {
      console.error('Erro no upload:', error)
      addMessage({ role: 'system', content: '❌ Erro ao enviar o arquivo para o servidor.' })
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, typing])

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <Message key={index} role={msg.role} content={msg.content} />
        ))}
        {typing && (
          <div className="message assistant">
            <div className="bubble typing">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-bar">
        <div className="file-upload">
          <label className="custom-file-upload">
          📁 Escolher arquivo
            <input type="file" onChange={handleFileUpload} />
          </label>
          {fileName && <span className="file-name">{fileName}</span>}
        </div>

        <input
          type="text"
          placeholder="Digite sua pergunta..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Enviar</button>
        <button
          onClick={() => {
            setMessages([])
            setChatId(null)
            setFileId(null)
            setFileName('')
          }}
          style={{ backgroundColor: '#6c757d', marginLeft: '8px' }}
        >
          ➕ Novo Chat
        </button>
      </div>
    </div>
  )
}

export default ChatWindow
