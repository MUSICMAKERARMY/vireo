import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const nav = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('accessToken', res.data.accessToken);
      localStorage.setItem('refreshToken', res.data.refreshToken);
      nav('/dashboard');
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-surface">
      <form onSubmit={handleSubmit} className="glass p-8 rounded-2xl w-96">
        <h1 className="text-2xl font-heading text-primary mb-6">Vireo Login</h1>
        <input className="w-full p-3 mb-4 rounded bg-surface border border-white/10" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input className="w-full p-3 mb-6 rounded bg-surface border border-white/10" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <button className="w-full py-3 bg-primary text-surface font-bold rounded-full hover:bg-primary-dark transition" type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
