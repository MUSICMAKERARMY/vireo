import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import { getSocket } from '../socket/socketClient';

const ChatWindow = () => {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<any[]>([]);
  const [newMsg, setNewMsg] = useState('');
  const socketRef = useRef(getSocket());

  useEffect(() => {
    api.get(`/messages/${id}`).then(res => setMessages(res.data)).catch(() => {});
    socketRef.current.on('new_message', (msg) => {
      if (msg.chatId === id) setMessages(prev => [...prev, msg]);
    });
    return () => { socketRef.current.off('new_message'); };
  }, [id]);

  const send = () => {
    if (!newMsg.trim()) return;
    socketRef.current.emit('send_message', { chatId: id, body: newMsg, type: 'TEXT' });
    setNewMsg('');
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map(m => (
          <div key={m.id} className="mb-2">
            <span className="font-bold text-primary">{m.sender?.username}: </span>
            {m.body}
          </div>
        ))}
      </div>
      <div className="p-4 border-t border-white/5 flex">
        <input className="flex-1 p-3 bg-surface rounded-l-full" value={newMsg} onChange={e => setNewMsg(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} placeholder="Type a message..." />
        <button className="px-6 bg-primary text-surface rounded-r-full" onClick={send}>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;
