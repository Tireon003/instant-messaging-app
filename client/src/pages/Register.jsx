import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import Cookies from 'js-cookie';

function Register() {
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post(`${window.CONSTS.SERVER_URL}/api/auth/generate_registration_code`,
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
        alert(`Для завершения регистрации следует отправить телеграм-боту (@msg_notificator_bot) код регистрации: ${response.data.code}. Код активен в течение 10 минут.`)
        navigate('/login');
    })
    .catch(err => {
        if (err.status == 400) {
            alert("Данное имя пользователя занято! Введите другой и повторите снова.")
        }
    });
  };

  return (
      <div className="flex items-center justify-center  h-screen">
        <div className="h-52 max-h-52 w-64 flex shadow-md mx-auto border-sky-400 rounded-lg box-border justify-center flex-col items-center h-screen border-solid border-2">
          <h2 className="mb-2">Регистрация</h2>
          <form
            onSubmit={handleSubmit}
            className="flex flex-col items-center"
          >
            <input
              name="username"
              placeholder="  Username"
              value={formData.username}
              onChange={handleChange}
              className="mt-2 border border-blue-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required />
            <input
              name="password"
              type="password"
              placeholder="  Password"
              value={formData.password}
              onChange={handleChange}
              className="mt-2 border border-blue-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required />
            <button className="mt-4 h-8 px-2 bg-blue-400 rounded-md text-white" type="submit">Получить код регистрации</button>
          </form>
          <p className="mt-2">Уже есть аккаунт? <Link className="underline hover:text-sky-500" to="/login">Войти</Link></p>
        </div>
      </div>
  );
}

export default Register;
