import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ChatWindow from './components/ChatWindow'
import Sidebar from './components/Sidebar'
import './index.css'

function App() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Olá! Envie um arquivo e me diga o que deseja analisar.' }
  ])
  const [typing, setTyping] = useState(false)
  const [darkMode, setDarkMode] = useState(true)
  const [chats, setChats] = useState([])
  const [chatId, setChatId] = useState(null)

  const token = localStorage.getItem('token')
  const navigate = useNavigate()

  useEffect(() => {
    document.body.className = darkMode ? 'dark' : ''
  }, [darkMode])

  useEffect(() => {
    if (!token) {
      navigate('/')
    }
  }, [token, navigate])

  const toggleTheme = () => {
    setDarkMode(prev => !prev)
  }

  const addMessage = (msg) => {
    setMessages(prev => [...prev, msg])
  }

  const fetchChats = async () => {
    try {
      const response = await fetch('http://192.86.221.214:8000/api/chats/', {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json()
        setChats(data)
      } else {
        const text = await response.text()
        console.error('Resposta não JSON ao buscar chats:', text)
      }

    } catch (err) {
      console.error('Erro ao buscar chats:', err)
    }
  }

  useEffect(() => {
    fetchChats()
  }, [])

  const handleChatSelect = async (id) => {
    setChatId(id)
    try {
      const response = await fetch(`http://192.86.221.214:8000/api/chats/${id}/mensagens/`, {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json()
        setMessages(data)
      } else {
        const text = await response.text()
        console.error('Resposta não JSON ao carregar mensagens:', text)
        setMessages([{ role: 'system', content: '❌ Erro ao carregar este chat.' }])
      }
    } catch (err) {
      console.error('Erro ao carregar mensagens:', err)
      setMessages([{ role: 'system', content: '❌ Erro ao carregar este chat.' }])
    }
  }

  const atualizarTituloLocalmente = (chatIdAtualizado, novoTitulo) => {
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatIdAtualizado ? { ...chat, title: novoTitulo } : chat
      )
    )
  }

  return (
    <div className="app-layout">

      <div className="sidebar">
        <Sidebar
          chats={chats}
          onSelectChat={handleChatSelect}
          currentChatId={chatId}
          onLogout={() => {
            localStorage.removeItem('token')
            localStorage.removeItem('refresh')
            navigate('/')
          }}
        />
      </div>

      <div className="main-content">
        <div className="theme-toggle">
          <button onClick={toggleTheme}>
            {darkMode ? '🔆' : '🌙'}
          </button>
        </div>

        <ChatWindow
          messages={messages}
          addMessage={addMessage}
          setTyping={setTyping}
          typing={typing}
          chatId={chatId}
          setChatId={setChatId}
          setMessages={setMessages}
          onChatCreated={fetchChats}
          setChats={setChats}
          atualizarTituloLocalmente={atualizarTituloLocalmente}
        />
      </div>
    </div>
  )
}

export default App
