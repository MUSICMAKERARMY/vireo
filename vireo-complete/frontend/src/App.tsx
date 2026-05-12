import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './screens/Login';
import Dashboard from './screens/Dashboard';
import ChatWindow from './screens/ChatWindow';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat/:id" element={<ChatWindow />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
