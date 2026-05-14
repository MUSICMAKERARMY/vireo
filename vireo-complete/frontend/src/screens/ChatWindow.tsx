import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import Parse from '../services/parse';
import { getSocket } from '../socket/socketClient';
import { useChatStore } from '../store/chatStore';

const ChatWindow = () => {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<any[]>([]);
  const [newMsg, setNewMsg] = useState('');
  const socketRef = useRef(getSocket());
  const typingUser = useChatStore((s) => s.typingUsers[id || ''] || '');
  const onlineUsers = useChatStore((s) => s.onlineUsers);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  const currentUser = Parse.User.current();
  const otherParticipant = // find the other user in chat (for direct chat)
    // This would typically come from the chat object, but we can get from messages[0]?.sender
    messages.find((m) => m.get('sender')?.id !== currentUser?.id)?.get('sender');

  const isOnline = otherParticipant && onlineUsers.includes(otherParticipant.id);

  useEffect(() => {
    if (!id) return;

    const fetchMessages = async () => {
      const chat = new Parse.Object('Chat');
      chat.id = id;
      const query = new Parse.Query('Message');
      query.equalTo('chat', chat);
      query.include('sender');
      query.ascending('createdAt');
      const results = await query.find();
      setMessages(results);
    };
    fetchMessages();

    const socket = socketRef.current;

    const handleNewMessage = (msg: any) => {
      if (msg.chatId === id) {
        // Add to local state
        setMessages((prev) => {
          if (prev.some((m) => m.id === msg.id)) return prev;
          return [...prev, msg];
        });
        // Mark as seen
        socket.emit('message_seen', { messageId: msg.id, chatId: id });
      }
    };

    socket.on('new_message', handleNewMessage);

    return () => {
      socket.off('new_message', handleNewMessage);
    };
  }, [id]);

  const handleTyping = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewMsg(e.target.value);
    // Emit typing events
    const socket = socketRef.current;
    socket.emit('typing_start', id);
    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      socket.emit('typing_stop', id);
    }, 1000);
  };

  const sendMessage = async () => {
    if (!newMsg.trim() || !id) return;
    const message = new Parse.Object('Message');
    const chat = new Parse.Object('Chat');
    chat.id = id;
    message.set('body', newMsg);
    message.set('chat', chat);
    message.set('sender', currentUser);
    message.set('type', 'TEXT');
    message.set('status', 'SENT');
    await message.save();
    setNewMsg('');
    // Emit via socket for real-time delivery to others
    socketRef.current.emit('send_message', {
      chatId: id,
      body: newMsg,
      type: 'TEXT',
      replyToId: null,
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SENT': return <span className="text-xs text-gray-400">✓</span>;
      case 'DELIVERED': return <span className="text-xs text-gray-400">✓✓</span>;
      case 'SEEN': return <span className="text-xs text-blue-400">✓✓</span>;
      default: return null;
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Chat header */}
      <div className="p-3 border-b border-white/5 flex items-center">
        <div className="w-8 h-8 rounded-full bg-primary/20 mr-3 flex items-center justify-center text-primary">
          {otherParticipant?.get('username')?.[0]?.toUpperCase() || '?'}
        </div>
        <div>
          <div className="font-semibold">{otherParticipant?.get('username') || 'Chat'}</div>
          {typingUser ? (
            <div className="text-xs text-primary animate-pulse">{typingUser} is typing...</div>
          ) : (
            <div className="text-xs text-gray-400">
              {isOnline ? 'Online' : 'Offline'}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg) => {
          const isMine = msg.get('sender')?.id === currentUser?.id;
          return (
            <div key={msg.id} className={`mb-2 flex ${isMine ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] p-2 rounded-xl ${isMine ? 'bg-primary/20' : 'bg-glass'}`}>
                {!isMine && (
                  <div className="text-xs text-primary mb-1">
                    {msg.get('sender')?.get('username')}
                  </div>
                )}
                <div>{msg.get('body')}</div>
                <div className="flex justify-end items-center gap-1 mt-1">
                  {isMine && getStatusIcon(msg.get('status'))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/5 flex">
        <input
          className="flex-1 p-3 bg-surface rounded-l-full text-white"
          value={newMsg}
          onChange={handleTyping}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <button
          className="px-6 bg-primary text-surface rounded-r-full"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
