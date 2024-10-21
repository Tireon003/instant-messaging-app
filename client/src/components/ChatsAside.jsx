import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';


export const ChatsAside = () => {
  const [username, setUsername] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [chats, setChats] = useState([]);
  const navigate = useNavigate();
  const token = Cookies.get('access_token');

  useEffect(() => {
    const getCurrentUser = () => {
      try {
        const decodedToken = jwtDecode(token);
        setCurrentUser(decodedToken);
        console.log("CurrentUser updated:", decodedToken);
      } catch (error) {
        console.error("Error decoding JWT:", error);
        document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
      }
    };

    const fetchChats = async () => {
      try {
        const response = await axios.get(
          `${window.CONSTS.SERVER_URL}/api/chats/`,
          {
              withCredentials: true,
              headers: {
                  'Authorization': 'Bearer ' + token,
              }
          }
        );

        setChats(response.data);
      } catch (err) {
        console.error('Ошибка при получении чатов:', err);
        // Здесь можно добавить дополнительную логику обработки ошибок
      }
    };

    getCurrentUser();
    fetchChats()
  }, []);

  // Макет функции для создания нового чата
  const createChat = async (username) => {
    if (username.trim() === currentUser?.name) {
        alert("Невозможно начать чат с самим собой!")
        return
    }
    try {
      const response = await axios.post(
        `${window.CONSTS.SERVER_URL}/api/chats?with_user=${username}`,
        {},
        {
            withCredentials: true,
            headers: {
                'Authorization': 'Bearer ' + token,
            }
        }
      );

      // Если запрос успешен, обновляем список чатов (используем response.data для реальных данных)
      const newChat = response.data; // Предположим, что API возвращает новый чат
      setChats([...chats, newChat]);
      setUsername("")
      console.log('Новый чат создан:', newChat);
      alert(`Чат с пользователем ${username} успешно создан`)
    } catch (error) {
      console.error('Ошибка при создании чата:', error);
      alert(`Чат  пользователем не был создан!`)
    }
  };

  const handleChatClick = (chatId, recipientName, recipientId) => {
      navigate(`/chat/${chatId}?recipient_name=${encodeURIComponent(recipientName)}&id=${encodeURIComponent(recipientId)}`);
  };

  const handleCreateChat = () => {
    if (username.trim()) {
      createChat(username); // Вызываем функцию создания чата
      setUsername(''); // Очищаем поле ввода
    } else {
      console.log('Введите имя пользователя');
    }
  };

  const handleLogout = async () => {
    await axios.post(`${window.CONSTS.SERVER_URL}/api/auth/logout`,
    {},
    {
        withCredentials: true,
        headers: {
            'Authorization': 'Bearer ' + token,
        }
    })
    .then(res => {
        if (res.status === 200) {
            window.location.reload();
        }
    })
    .catch(err => {
        if (err.status === 401) {
            console.log("You are not authenticated")
        }
    })
  }

  return (
    <div className="max-w-64 min-w-64 grow border-solid border-2 border-neutral-400 flex flex-col">
      {/* Модуль для создания нового чата */}
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

      {/* Список чатов с прокруткой */}
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
