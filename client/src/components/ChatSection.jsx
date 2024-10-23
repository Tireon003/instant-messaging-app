import { useParams, useLocation } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import Cookies from 'js-cookie';
import {jwtDecode} from 'jwt-decode';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import axios from 'axios';


export const ChatSection = () => {
  const { chatId } = useParams();
  const token = Cookies.get('access_token');
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const recipientName = queryParams.get('recipient_name');
  const recipientId = queryParams.get('id');
  const wsUrl = `${window.CONSTS.WS_SERVER_URL}/api/chats/${chatId}/ws?to_user=${recipientId}&token=${token}`;
  const {
      sendMessage,
      lastMessage,
      readyState
  } = useWebSocket(wsUrl, {
    onOpen: () => console.log('opened'),
    //Will attempt to reconnect on all close events, such as server shutting down
    //shouldReconnect: (closeEvent) => true,
  });

  const [currentUser, setCurrentUser] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [messageHistory, setMessageHistory] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const chatRef = useRef(null);


  useEffect(() => {
    // Декодирование токена и установка текущего пользователя
    const getCurrentUser = () => {
      try {
        const decodedToken = jwtDecode(token);
        setCurrentUser(decodedToken);
      } catch (error) {
      }
    };

    getCurrentUser();
  }, [token]);

  useEffect(() => {
      const fetchChatHistory = async () => {
        try {
          const response = await axios.get(`${window.CONSTS.SERVER_URL}/api/chats/${chatId}/history`, {
            withCredentials: true,
            headers: {
              'Authorization': 'Bearer ' + token,
            }
          });
          setChatHistory(response.data);
        } catch (error) {
          console.error('Ошибка при загрузке истории чата:', error);
        }
      };

      fetchChatHistory();
    }, [chatId, token]);

  useEffect(() => {
    if (lastMessage !== null) {
        const messageObj = JSON.parse(lastMessage.data)
        if (messageObj.chat_id === chatId) {
            setMessageHistory((prev) => prev.concat(messageObj));
        }
    }
  }, [lastMessage]);

  useEffect(() => {
      chatRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end'});
  }, [chatHistory, messageHistory])

  const handleSendMessage = (message) => {
      sendMessage(message)
      console.log(`Я отправил ${message}`)
      setNewMessage("")
  };

  return (
  <div className="box-content flex flex-col border-solid border-neutral-400 border-2 w-full h-full">
    {chatId ? (
      <div className="flex flex-col h-full">
        <h2 className="text-lg py-2 pl-4 bg-white shadow flex items-center">{recipientName}</h2>

        {/* Контейнер с прокруткой для сообщений */}
        <div className="overflow-y-auto grow p-2 flex flex-col">
          {chatHistory.length > 0 || messageHistory.length ? (
            <>
              <div ref={chatRef} className="flex flex-col space-y-2">
                {[...chatHistory, ...messageHistory].map((item) => (
                  <div
                    key={item.timestamp}
                    className={`max-w-[400px] p-1 mx-2 border flex flex-col ${
                      currentUser?.sub === item.owner
                        ? 'self-end bg-blue-100'
                        : 'self-start bg-gray-100'
                    }`}
                  >
                    <p className="text-sm">{item.owner === currentUser?.sub ? currentUser.name : recipientName}</p>
                    <p className="text-sm max-w-[380px]">{item.content}</p>
                    <small className="text-gray-500 mt-2">
                      {new Date(item.timestamp).toLocaleDateString('default', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                      })}{' '}
                      {new Date(item.timestamp).toLocaleTimeString('default', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false,
                      })}
                    </small>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex justify-center items-center h-full">
              <h2>История сообщений пуста. Начните диалог первым!</h2>
            </div>
          )}
        </div>

        {/* Блок для отправки нового сообщения */}
        <div className="p-2 border-t flex items-center space-x-2 bg-gray-50">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Введите сообщение..."
            className="flex-grow p-2 border rounded-lg"
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(newMessage)}
          />
          <button
            onClick={() => handleSendMessage(newMessage)}
            className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600"
          >
            Отправить
          </button>
        </div>
      </div>
    ) : (
      <div className="flex justify-center items-center h-full">
        <h2>Выберите чат...</h2>
      </div>
    )}
  </div>
);

};
