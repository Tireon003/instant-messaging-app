import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import Cookies from 'js-cookie';

function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post(`${window.CONSTS.SERVER_URL}/api/auth/login`,
    new URLSearchParams({
          username: formData.username,
          password: formData.password,
          grant_type: 'password'
        }), {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    .then((response) => {
        alert("Вы успешно авторизованы! Нажмите ОК для перехода к чатам.")
        window.location.reload();
    })
    .catch(err => alert("Не удалось войти, возможно вы указали неверные имя пользователя и/или пароль"));
  };

  return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex shadow-md h-52 max-h-52 w-72 mx-auto border-sky-400 rounded-lg box-border justify-center flex-col items-center h-screen border-solid border-2">
          <h2 className="mb-2">Вход в аккаунт</h2>
          <form onSubmit={handleSubmit} className="flex flex-col items-center">
            <input
              name="username"
              placeholder="  Username"
              value={formData.username}
              onChange={handleChange}
              className="mt-2 border border-blue-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              name="password"
              type="password"
              placeholder="  Password"
              value={formData.password}
              onChange={handleChange}
              className="mt-2 border border-blue-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required />
            <button  className="mt-4 h-8 px-2 min-w-48 bg-blue-400 rounded-md text-white" type="submit">Войти</button>
          </form>
          <p className="mt-2">Нет аккаунта? <Link className="underline hover:text-sky-500" to="/register">Зарегистрироваться</Link></p>
        </div>
    </div>
  );
}

export default Login;
