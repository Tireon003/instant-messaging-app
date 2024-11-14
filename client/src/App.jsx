import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Cookies from 'js-cookie';

function App() {
  const token = Cookies.get('access_token');
  console.log(token)

  return (
    <Router>
      <Routes>
        <Route path="/register" element={token ? <Navigate to="/chat" /> : <Register />} />
        <Route path="/login" element={token ? <Navigate to="/chat" /> : <Login />} />
        <Route path="/chat/:chatId" element={token ? <Chat /> : <Navigate to="/login" />} />
        <Route path="/chat" element={token ? <Chat /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
