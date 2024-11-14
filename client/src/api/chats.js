import axios from "axios";

export async function fetchChatHistory(chatId, token) {
    let chatHistory;
    await axios.get(`${window.CONSTS.SERVER_URL}/api/chats/${chatId}/history`, {
        withCredentials: true,
        headers: {
            'Authorization': 'Bearer ' + token,
        }
    }).then(response => {
        chatHistory = response.data;
    }).catch(error => {
        chatHistory = [];
        console.error(`В процессе получения истории чата возникла ошибка: ${error}`)
    })
    return chatHistory;
}

export async function fetchUserChats(token) {
    let chatsList;
    await axios.get(
        `${window.CONSTS.SERVER_URL}/api/chats/`,
        {
            withCredentials: true,
            headers: {
                'Authorization': 'Bearer ' + token,
            }
        }
    ).then(response => {
        chatsList = response.data;
    }).catch(error => {
        chatsList = [];
        if (error.status === 401) {
            console.error(`Пользователь не авторизован.`);
        } else {
            console.error(`В процессе получения списка чатов возникла ошибка: ${error}`)
        }
    })
    return chatsList;
}

export async function createNewChat(username, token) {
    let newChat;
    await axios.post(
        `${window.CONSTS.SERVER_URL}/api/chats?with_user=${username}`,
        {},
        {
            withCredentials: true,
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        }
    ).then(response => {
        newChat = response.data;
    }).catch(error => {
        newChat = null;
        if (error.status === 422) {
            console.error(`Ошибка при указании данных для создания чата. Детали ошибки: ${error}`);
        } else if (error.status === 404) {
            console.error(`Пользователь с именем ${username} не найден.`);
        } else if (error.status === 401) {
            console.error(`Пользователь не авторизован.`);
        } else {
            console.error(`В процессе выполнения запроса произошла ошибка: ${error}`)
        }
    });
    return newChat;
}

export async function refreshMessagesStatus(messageIds) {
    let refreshedMessagesStatus = null;
    await axios.post(
        `${window.CONSTS.SERVER_URL}/api/chats/get_read_status`,
        messageIds,
    ).then(response => {
        refreshedMessagesStatus = response.data;
    }).catch(error => {
        console.error(`В процессе выполнения запроса произошла ошибка: ${error}`)
    });
    return refreshedMessagesStatus;
}