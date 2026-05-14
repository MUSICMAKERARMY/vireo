import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Parse from '../services/parse';
import { useChatStore } from '../store/chatStore';
import { useSocket } from '../hooks/useSocket';

const Dashboard = () => {
  const [chats, setChats] = useState<any[]>([]);
  const navigate = useNavigate();
  const onlineUsers = useChatStore((s) => s.onlineUsers);
  useSocket(); // activate socket listeners

  const fetchChats = async () => {
    const currentUser = Parse.User.current();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    const query = new Parse.Query('Chat');
    query.equalTo('participants', currentUser);
    query.include('participants.user');
    const results = await query.find();
    setChats(results);
  };

  useEffect(() => {
    fetchChats();
  }, []);

  const getOtherParticipant = (chat: any) => {
    const currentUser = Parse.User.current();
    return chat.get('participants')?.find(
      (p: any) => p.get('user').id !== currentUser?.id
    )?.get('user');
  };

  return (
    <div className="h-screen flex">
      <div className="w-80 bg-surface border-r border-white/5 p-4">
        <h2 className="text-lg font-heading text-primary mb-4">Chats</h2>
        {chats.map((chat) => {
          const other = getOtherParticipant(chat);
          const isOnline = other && onlineUsers.includes(other.id);
          return (
            <Link
              key={chat.id}
              to={`/chat/${chat.id}`}
              className="flex items-center p-3 hover:bg-glass rounded-lg mb-1"
            >
              <span className="relative mr-3">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                  {other?.get('username')?.[0]?.toUpperCase() || '?'}
                </div>
                <span
                  className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-surface ${
                    isOnline ? 'bg-green-500' : 'bg-gray-500'
                  }`}
                />
              </span>
              <span>{other?.get('username') || chat.id}</span>
            </Link>
          );
        })}
      </div>
      <div className="flex-1 flex items-center justify-center text-white/40">
        Select a chat to start messaging
      </div>
    </div>
  );
};

export default Dashboard;
