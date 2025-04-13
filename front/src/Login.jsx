import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [transicao, setTransicao] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    document.body.className = 'dark'
  }, [])

  const handleLogin = async () => {
    setErro('')

    try {
      const response = await fetch('http://localhost:8000/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ username: email, password: senha }),
      })

      const text = await response.text()
      const data = JSON.parse(text)

      if (response.ok && data.access && data.refresh) {
        localStorage.setItem('token', data.access)
        localStorage.setItem('refresh', data.refresh)
        setTransicao(true)
        setTimeout(() => {
          navigate('/chat')
        }, 700)
      } else {
        setErro('❌ Credenciais inválidas ou erro no retorno.')
      }

    } catch (err) {
      console.error('Erro ao logar:', err)
      setErro('❌ Erro de conexão com o servidor.')
    }
  }

  return (
    <>
      <div className={`login-container ${transicao ? 'fade-out' : ''}`} 
       onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
       tabIndex={0}
      >
      <img src="/SIRIUS LOGO.png" alt="Logo" className="login-imagem" />
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Usuário"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
        />
        <input
          type="password"
          placeholder="Senha"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
        />
        <button onClick={handleLogin}>Entrar</button>
        {erro && <p className="erro">{erro}</p>}
      </div>
    </>
  )
}

export default Login
