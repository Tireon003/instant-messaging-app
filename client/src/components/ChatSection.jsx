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
  const [isOnline, setIsOnline] = useState("offline");
  const [currentUser, setCurrentUser] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const chatRef = useRef(null);
  const [unreadMessages, setUnreadMessages] = useState([]);


  useEffect(() => {
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
      console.log("Получение последнего сообщения сокета")
    if (readyState == ReadyState.OPEN && lastMessage !== null) {
        const messageObj = JSON.parse(lastMessage.data)
        console.log(messageObj)
        if (messageObj.chat_id == chatId) {
            setChatHistory((prev) => prev.concat(messageObj));
        }
    }
  }, [lastMessage, readyState]);

  useEffect(() => {
    const checkUserStatus = async () => {
      try {
        const response = await axios.get(`${window.CONSTS.SERVER_URL}/api/chats/user_network_status?recipient_id=${recipientId}`);
        setIsOnline(response.data.status);
      } catch (error) {
        console.error('Ошибка при проверке статуса пользователя', error);
      }
    };
    checkUserStatus();
    const intervalId = setInterval(checkUserStatus, 10000);
    return () => clearInterval(intervalId);
  }, [recipientId]);

    useEffect(() => {
        const checkMessagesIsRead = async () => {
            console.log("Проверяем, есть ли непрочитанные сообщения")
            const currentUnreadMessages = chatHistory.filter(message =>
                message.is_read === false && message.owner === currentUser.sub
            );
            const listsAreDifferent =
                currentUnreadMessages.length !== unreadMessages.length ||
                currentUnreadMessages.some(
                    newMessage => !unreadMessages.some(oldMessage => oldMessage.id === newMessage.id)
                );
            if (listsAreDifferent) {
                setUnreadMessages(currentUnreadMessages);
            }
            if (unreadMessages.length > 0) {
                const messageIds = unreadMessages.map(msg => msg.id);
                try {
                    const response = await axios.post(`${window.CONSTS.SERVER_URL}/api/chats/get_read_status`, messageIds);
                    const readStatus = response.data;
                    const hasReadUpdates = Object.values(readStatus).some(status => status === true);

                    if (hasReadUpdates) {
                        setChatHistory(prevChatHistory =>
                            prevChatHistory.map(message => ({
                                ...message,
                                is_read: readStatus[message.id] ? readStatus[message.id] : message.is_read
                            }))
                        );
                    } else {
                        console.log("Нет обновлений статуса прочтения, chatHistory не будет изменен.");
                    }
                } catch (error) {
                    console.error('Error fetching message read status:', error);
                }
            }
        };
        checkMessagesIsRead();
        const intervalCheckRead = setInterval(checkMessagesIsRead, 3000);
        return () => clearInterval(intervalCheckRead);
    }, [currentUser, unreadMessages, chatHistory]);

  useEffect(() => {
      chatRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end'});
  }, [chatHistory])

  const handleSendMessage = (message) => {
      sendMessage(message)
      console.log(`Я отправил ${message}`)
      setNewMessage("")
  };

  return (
  <div className="box-content flex flex-col border-solid border-neutral-400 border-2 w-full h-full">
    {chatId ? (
      <div className="flex flex-col h-full">
        <div className="flex justify-between items-center bg-white shadow">
          <h2 className="text-lg py-2 pl-4 flex items-center">{recipientName}</h2>
          <span className="text-sm text-gray-500 pr-4">{isOnline}</span>
        </div>
        {/* Контейнер с прокруткой для сообщений */}
        <div className="overflow-y-auto grow p-2 flex flex-col">
          {chatHistory ? (
            <>
              <div ref={chatRef} className="flex flex-col space-y-2">
                {chatHistory.map((item) => (
                  <div
                    key={item.id}
                    className={`max-w-[400px] p-1 mx-2 border flex flex-col ${
                      currentUser?.sub === item.owner
                        ? 'self-end bg-blue-100'
                        : 'self-start bg-gray-100'
                    }`}
                  >
                    <p className="text-sm">{item.owner === currentUser?.sub ? currentUser.name : recipientName}</p>
                    <p className="text-sm max-w-[380px]">{item.content}</p>
                    <div className="flex items-center justify-between space-x-2">
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
                        <div>
                            {item.owner === currentUser?.sub ? (
                                <small className="flex items-center mt-2">
                                    {item.is_read ? (
                                        <svg className="h-5 w-5 text-green-500"  width="24" height="24" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">  <path stroke="none" d="M0 0h24v24H0z"/>  <path d="M7 12l5 5l10 -10" />  <path d="M2 12l5 5m5 -5l5 -5" /></svg>
                                    ) : (
                                        <svg className="h-5 w-5 text-gray-400"  width="24" height="24" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">  <path stroke="none" d="M0 0h24v24H0z"/>  <path d="M5 12l5 5l10 -10" /></svg>
                                    )
                                    }
                                </small>
                            ) : (
                                <div></div>
                            )}
                        </div>
                    </div>
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
