import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [chats, setChats] = useState<any[]>([]);

  useEffect(() => {
    api.get('/chats').then(res => setChats(res.data)).catch(() => {});
  }, []);

  return (
    <div className="h-screen flex">
      <div className="w-80 bg-surface border-r border-white/5 p-4">
        <h2 className="text-lg font-heading text-primary mb-4">Chats</h2>
        {chats.map(chat => (
          <Link key={chat.id} to={`/chat/${chat.id}`} className="block p-3 hover:bg-glass rounded-lg mb-1">
            {chat.name || chat.participants?.map(p => p.user.username).join(', ')}
          </Link>
        ))}
      </div>
      <div className="flex-1 flex items-center justify-center text-white/40">
        Select a chat to start messaging
      </div>
    </div>
  );
};

export default Dashboard;
