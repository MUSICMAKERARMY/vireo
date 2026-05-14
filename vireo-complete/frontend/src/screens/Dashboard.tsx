import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useChatStore } from '../store/chatStore';
import { useSocket } from '../hooks/useSocket';

const Dashboard = () => {
  const chats = useChatStore((s) => s.chats);
  const fetchChats = useChatStore((s) => s.fetchChats);
  const onlineUsers = useChatStore((s) => s.onlineUsers);
  const navigate = useNavigate();

  useSocket(); // activate socket listeners

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchChats();
  }, [fetchChats, navigate]);

  const getOtherParticipant = (chat: any) => {
    // For direct chats, find the participant who isn't the current user
    const currentUserId = chat.participants?.find((p: any) => p.userId !== 'me')?.userId; // Replace with actual current user ID from auth store
    // Simple: return the first participant that is not the logged in user
    return chat.participants?.find((p: any) => p.userId !== chat.participants[0].userId)?.user;
  };

  return (
    <div className="h-screen flex">
      <div className="w-80 bg-surface border-r border-white/5 p-4">
        <h2 className="text-lg font-heading text-primary mb-4">Chats</h2>
        {chats.map((chat) => {
          const other = getOtherParticipant(chat);
          const isOnline = other ? onlineUsers.includes(other.id) : false;
          return (
            <Link
              key={chat.id}
              to={`/chat/${chat.id}`}
              className="flex items-center p-3 hover:bg-glass rounded-lg mb-1"
            >
              <span className="relative mr-3">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                  {other?.username?.[0]?.toUpperCase() || 'C'}
                </div>
                <span
                  className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-surface ${
                    isOnline ? 'bg-green-500' : 'bg-gray-500'
                  }`}
                />
              </span>
              <span>{other?.username || chat.name || 'Chat'}</span>
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