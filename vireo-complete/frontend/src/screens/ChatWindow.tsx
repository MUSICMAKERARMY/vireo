import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import { getSocket } from '../socket/socketClient';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';

const ChatWindow = () => {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<any[]>([]);
  const [newMsg, setNewMsg] = useState('');
  const socketRef = useRef(getSocket());
  const typingUser = useChatStore((s) => s.typingUsers[id || ''] || '');
  const onlineUsers = useChatStore((s) => s.onlineUsers);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();
  const currentUserId = useAuthStore((s) => s.userId);   // ✅ real user ID

  const otherParticipant = useChatStore((s) => {
    const chat = s.chats.find((c) => c.id === id);
    if (!chat) return null;
    return chat.participants?.find((p: any) => p.userId !== currentUserId)?.user;
  });
  const isOnline = otherParticipant && onlineUsers.includes(otherParticipant.id);

  useEffect(() => {
    if (!id) return;

    const fetchMessages = async () => {
      const { data } = await api.get(`/messages/${id}`);
      setMessages(data);
    };
    fetchMessages();

    const socket = socketRef.current;
    const handleNewMessage = (msg: any) => {
      if (msg.chatId === id) {
        setMessages((prev) => {
          if (prev.some((m) => m.id === msg.id)) return prev;
          return [...prev, msg];
        });
        socket.emit('message_seen', { messageId: msg.id, chatId: id });
      }
    };
    socket.on('new_message', handleNewMessage);
    return () => { socket.off('new_message', handleNewMessage); };
  }, [id]);

  const handleTyping = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewMsg(e.target.value);
    const socket = socketRef.current;
    socket.emit('typing_start', id);
    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      socket.emit('typing_stop', id);
    }, 1000);
  };

  const sendMessage = () => {
    if (!newMsg.trim() || !id) return;
    const socket = socketRef.current;
    // Send message through socket – backend will create it
    socket.emit('send_message', {
      chatId: id,
      body: newMsg,
      type: 'TEXT',
      replyToId: null,
    });
    setNewMsg('');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SENT': return '✓';
      case 'DELIVERED': return '✓✓';
      case 'SEEN': return '✓✓'; // blue color would be nice, but text works
      default: return '';
    }
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="p-3 border-b border-white/5 flex items-center">
        <div className="w-8 h-8 rounded-full bg-primary/20 mr-3 flex items-center justify-center text-primary">
          {otherParticipant?.username?.[0]?.toUpperCase() || '?'}
        </div>
        <div>
          <div className="font-semibold">{otherParticipant?.username || 'Chat'}</div>
          {typingUser ? (
            <div className="text-xs text-primary animate-pulse">{typingUser} is typing...</div>
          ) : (
            <div className="text-xs text-gray-400">{isOnline ? 'Online' : 'Offline'}</div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg) => {
          const isMine = msg.senderId === currentUserId || msg.sender?.id === currentUserId;
          return (
            <div key={msg.id} className={`mb-2 flex ${isMine ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] p-2 rounded-xl ${isMine ? 'bg-primary/20' : 'bg-glass'}`}>
                {!isMine && (
                  <div className="text-xs text-primary mb-1">{msg.sender?.username}</div>
                )}
                <div>{msg.body}</div>
                <div className="flex justify-end items-center gap-1 mt-1">
                  {isMine && <span className="text-xs text-gray-400">{getStatusIcon(msg.status)}</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-4 border-t border-white/5 flex">
        <input
          className="flex-1 p-3 bg-surface rounded-l-full"
          value={newMsg}
          onChange={handleTyping}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <button className="px-6 bg-primary text-surface rounded-r-full" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;