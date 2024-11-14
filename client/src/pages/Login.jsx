import { useState } from 'react';
import { Link } from 'react-router-dom';
import {loginUser} from "../api/auth.js";

function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
      e.preventDefault();
      await loginUser(formData["username"], formData["password"]);
  };

  return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex shadow-md h-52 max-h-52 w-72 mx-auto border-sky-400 rounded-lg box-border justify-center flex-col items-center border-solid border-2">
          <h2 className="mb-2">
            Вход в аккаунт
          </h2>
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
              required
            />
            <input
              name="password"
              type="password"
              placeholder="  Password"
              value={formData.password}
              onChange={handleChange}
              className="mt-2 border border-blue-500 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <button
                className="mt-4 h-8 px-2 min-w-48 bg-blue-400 rounded-md text-white"
                type="submit"
            >
              Войти
            </button>
          </form>
          <p className="mt-2">
            Нет аккаунта?
            <Link
                className="underline hover:text-sky-500"
                to="/register"
            >
              Зарегистрироваться
            </Link>
          </p>
        </div>
    </div>
  );
}

export default Login;
