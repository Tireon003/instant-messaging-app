import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {useUser} from "../hooks/useUser.js";
import {createNewChat, fetchUserChats} from "../api/chats.js";
import {logoutUser} from "../api/auth.js";


export const ChatsAside = () => {
  const [username, setUsername] = useState('');
  const [currentUser, token] = useUser();
  const [chats, setChats] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
      const fetchChats = async () => {
          const chats = await fetchUserChats(token);
          setChats(chats);
      };

      fetchChats();
  }, [token]);

  const createChat = async (username, token) => {
      if (username === currentUser?.name) {
          alert("Невозможно начать чат с самим собой!")
          return
      }
      const newChat = await createNewChat(username, token);
      if (newChat !== null) {
          setChats([...chats, {
              chat_id: newChat["id"],
              recipient_name: username,
              recipient_id: newChat["user_2"]
          }]);
          alert(`Чат с пользователем ${username} успешно создан`)
      } else {
          alert("Ошибка при создании нового чата.")
      }
  };

  const handleChatClick = (chatId, recipientName, recipientId) => {
      navigate(`/chat/${chatId}?recipient_name=${encodeURIComponent(recipientName)}&id=${encodeURIComponent(recipientId)}`);
  };

  const handleCreateChat = async () => {
      if (username.trim()) {
          await createChat(username.trim(), token);
          setUsername('');
      } else {
          alert('Введите имя пользователя и повторите снова.');
      }
  };

  const handleLogout = async () => {
      await logoutUser(token);
  }

  return (
    <div className="max-w-64 min-w-64 grow border-solid border-2 border-neutral-400 flex flex-col">
      <div className="p-2 border-b-2 border-neutral-400">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Введите username"
          className="p-1 border rounded-lg w-52"
        />
        <button
          onClick={handleCreateChat}
          className="ml-2 p-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          +
        </button>
      </div>
      <ul className="overflow-y-auto flex-grow">
        {chats.map((chat) => (
          <li
            className="cursor-pointer rounded-md border-2 border-neutral-300 mt-2 mx-2 hover:bg-neutral-200 h-12 text-center flex items-center justify-center list-none"
            key={chat.id}
            onClick={() => handleChatClick(chat?.chat_id, chat?.recipient_name, chat?.recipient_id)}
          >
            {chat?.recipient_name}
          </li>
        ))}
      </ul>
      <div className="h-16 flex justify-between items-center border-t-2 border-neutral-200">
          <h2
            className="ml-2"
          >{currentUser?.name}</h2>
          <button
            className="text-white w-20 h-10 bg-blue-500 rounded-md mr-2 hover:bg-blue-600"
            onClick={handleLogout}
          >
          Log out
          </button>
      </div>
    </div>
  );
};
