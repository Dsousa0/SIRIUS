import React from 'react'

function Sidebar({ onSelectChat, currentChatId, chats, onLogout }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>🧑‍💻 Meus Chats</h3>
        <button className="logout-button" onClick={onLogout}>⬅️Sair</button>
      </div>
      <ul className="chat-list">
        {chats.map((chat) => (
          <li
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={chat.id === currentChatId ? 'active' : ''}
          >
            {chat.title || `Chat #${chat.id}`}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Sidebar
