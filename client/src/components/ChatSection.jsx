import { useParams } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import {useUser} from "../hooks/useUser.js";
import {fetchChatHistory, refreshMessagesStatus} from "../api/chats.js";
import {fetchRecipientStatus} from "../api/users.js";
import {useRecipient} from "../hooks/useRecipient.js";
import Message from "./ui/Message.jsx";


export const ChatSection = () => {
  const {chatId } = useParams();
  const [currentUser, token] = useUser();
  const { recipientId, recipientName } = useRecipient();
  const wsUrl = `${window.CONSTS.WS_SERVER_URL}/api/chats/${chatId}/ws?to_user=${recipientId}&token=${token}`;
  const {
      sendMessage,
      lastMessage,
      readyState,
  } = useWebSocket(
      wsUrl,
      {
          onOpen: () => console.debug('WS connection established'),
          shouldReconnect: (closeEvent) => true,
          reconnectAttempts: 5,
          reconnectInterval: 1000,
      });
  const [isOnline, setIsOnline] = useState("offline");
  const [chatHistory, setChatHistory] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [unreadMessages, setUnreadMessages] = useState([]);
  const chatRef = useRef(null);

  useEffect(() => {
      const fetchData = async () => {
          const history = await fetchChatHistory(chatId, token);
          setChatHistory(history);
      }

      if (chatId) fetchData();
  }, [chatId, token]);

  useEffect(() => {
      console.debug("Обработка последнего сообщения из ws")
      if (readyState === ReadyState.OPEN && lastMessage !== null) {
          const messageObj = JSON.parse(lastMessage.data)
          if (messageObj["chat_id"] === parseInt(chatId)) {
              setChatHistory((prev) => prev.concat(messageObj));
          }
      }
  }, [chatId, lastMessage, readyState]);

  useEffect(() => {
      const checkUserStatus = async () => {
          const status = await fetchRecipientStatus(recipientId);
          setIsOnline(status);
      }
      if (recipientId) checkUserStatus();
      const intervalId = setInterval(checkUserStatus, 10000);
      return () => clearInterval(intervalId);
  }, [recipientId]);

    useEffect(() => {
        const checkMessagesIsRead = async () => {
            const currentUnreadMessages = chatHistory.filter(message =>
                message["is_read"] === false && message["owner"] === currentUser["sub"]
            );
            const listsAreDifferent =
                currentUnreadMessages.length !== unreadMessages.length ||
                currentUnreadMessages.some(
                    newMessage => !unreadMessages.some(oldMessage => oldMessage["id"] === newMessage["id"])
                );
            if (listsAreDifferent) {
                setUnreadMessages(currentUnreadMessages);
            }
            if (unreadMessages.length > 0) {
                const messageIds = unreadMessages.map(msg => msg["id"]);
                const readStatus = await refreshMessagesStatus(messageIds);
                const hasReadUpdates = Object.values(readStatus).some(status => status === true);
                if (hasReadUpdates) {
                    setChatHistory(prevChatHistory => prevChatHistory.map(
                        message => ({
                            ...message,
                            is_read: readStatus[message["id"]] ? readStatus[message["id"]] : message["is_read"]
                        }))
                    );
                } else {
                    console.debug("Нет обновлений статуса прочтения, chatHistory не будет изменен.");
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
      console.debug(`Отправлено сообщение с текстом: ${message}`)
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
                  <Message
                      currentUser={currentUser}
                      recipientName={recipientName}
                      messageData={item}
                  />
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
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(newMessage)}
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
