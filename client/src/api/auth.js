import axios from "axios";

export async function logoutUser(token) {
    await axios.post(`${window.CONSTS.SERVER_URL}/api/auth/logout`,
        {},
        {
            withCredentials: true,
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        }
    ).then(response => {
        if (response.status === 200) {
            window.location.reload();
        }
    }).catch(error => {
        if (error.status === 401) {
            console.log("Неавторизованный пользователь")
        }
    });
}

export async function loginUser(username, password) {
    await axios.post(`${window.CONSTS.SERVER_URL}/api/auth/login`,
        new URLSearchParams({
            username: username,
            password: password,
            grant_type: 'password'
        }),
        {
            withCredentials: true,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }
    ).then(() => {
        alert("Вы успешно авторизованы! Нажмите ОК для перехода к чатам.")
        window.location.reload();
    }).catch(err => {
        console.error(`При входе возникла ошибка: ${err}`);
        alert("Не удалось войти, возможно вы указали неверные имя пользователя и/или пароль");
    });
}

export async function registerUser(username, password) {
    let code = null;
    await axios.post(`${window.CONSTS.SERVER_URL}/api/auth/generate_registration_code`,
        new URLSearchParams({
            username: username,
            password: password,
            grant_type: 'password'
        }),
        {
            withCredentials: true,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }
    ).then((response) => {
        code = response.data["code"]
    })
    return code;
}