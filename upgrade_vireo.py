#!/usr/bin/env python3
"""
Vireo Feature Upgrade: Online status, typing indicators, read receipts.
Run from your VireoProject folder.
"""
import os

BASE = "vireo-complete/frontend/src"

# ==================== FILES TO UPDATE ====================

FILES = {}

# --- Zustand Chat Store ---
FILES["store/chatStore.ts"] = r'''import { create } from 'zustand';
import { ChatService } from '../services/chatService';

interface ChatState {
  chats: any[];
  activeChatId: string | null;
  onlineUsers: string[];
  typingUsers: Record<string, string>; // chatId -> username
  setActiveChat: (id: string) => void;
  fetchChats: () => Promise<void>;
  addMessage: (message: any) => void;
  setOnlineUsers: (ids: string[]) => void;
  addOnlineUser: (id: string) => void;
  removeOnlineUser: (id: string) => void;
  setTypingUser: (chatId: string, username: string | null) => void;
  updateMessageStatus: (messageId: string, status: string) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  activeChatId: null,
  onlineUsers: [],
  typingUsers: {},

  setActiveChat: (id) => set({ activeChatId: id }),

  fetchChats: async () => {
    const data = await ChatService.getChats();
    set({ chats: data });
  },

  addMessage: (message) => {
    const { chats } = get();
    const updated = chats.map((chat) => {
      if (chat.id === message.chatId) {
        // Add message if not already present
        const exists = chat.messages?.some((m: any) => m.id === message.id);
        if (!exists) {
          return {
            ...chat,
            messages: [...(chat.messages || []), message],
          };
        }
      }
      return chat;
    });
    set({ chats: updated });
  },

  setOnlineUsers: (ids) => set({ onlineUsers: ids }),

  addOnlineUser: (id) =>
    set((state) => ({
      onlineUsers: state.onlineUsers.includes(id)
        ? state.onlineUsers
        : [...state.onlineUsers, id],
    })),

  removeOnlineUser: (id) =>
    set((state) => ({
      onlineUsers: state.onlineUsers.filter((uid) => uid !== id),
    })),

  setTypingUser: (chatId, username) =>
    set((state) => ({
      typingUsers: {
        ...state.typingUsers,
        [chatId]: username || '',
      },
    })),

  updateMessageStatus: (messageId, status) =>
    set((state) => ({
      chats: state.chats.map((chat) => ({
        ...chat,
        messages: chat.messages?.map((msg: any) =>
          msg.id === messageId ? { ...msg, status } : msg
        ),
      })),
    })),
}));
'''

# --- Socket hook ---
FILES["hooks/useSocket.ts"] = r'''import { useEffect, useRef } from 'react';
import { getSocket } from '../socket/socketClient';
import { useChatStore } from '../store/chatStore';

export const useSocket = () => {
  const {
    addMessage,
    addOnlineUser,
    removeOnlineUser,
    setTypingUser,
    updateMessageStatus,
    activeChatId,
  } = useChatStore();
  const socketRef = useRef(getSocket());
  const typingTimeouts = useRef<Record<string, NodeJS.Timeout>>({});

  useEffect(() => {
    const socket = socketRef.current;

    // Online/offline
    socket.on('user_online', (userId: string) => {
      addOnlineUser(userId);
    });
    socket.on('user_offline', (userId: string) => {
      removeOnlineUser(userId);
    });

    // New message
    socket.on('new_message', (msg: any) => {
      addMessage(msg);
      // Auto-mark as seen if the chat is active
      if (msg.chatId === useChatStore.getState().activeChatId) {
        socket.emit('message_seen', { messageId: msg.id, chatId: msg.chatId });
      }
    });

    // Message status updates (delivered/seen)
    socket.on('message_status', ({ messageId, status }: any) => {
      updateMessageStatus(messageId, status);
    });

    // Typing indicators
    socket.on('user_typing', ({ chatId, userId }: any) => {
      const chat = useChatStore.getState().chats.find((c) => c.id === chatId);
      if (chat) {
        const participant = chat.participants?.find((p: any) => p.userId === userId);
        const username = participant?.user?.username || 'Someone';
        setTypingUser(chatId, username);

        // Clear typing after 2 seconds
        if (typingTimeouts.current[chatId]) clearTimeout(typingTimeouts.current[chatId]);
        typingTimeouts.current[chatId] = setTimeout(() => {
          setTypingUser(chatId, null);
        }, 2000);
      }
    });

    socket.on('user_stop_typing', ({ chatId }: any) => {
      setTypingUser(chatId, null);
    });

    return () => {
      socket.off('user_online');
      socket.off('user_offline');
      socket.off('new_message');
      socket.off('message_status');
      socket.off('user_typing');
      socket.off('user_stop_typing');
    };
  }, [addMessage, addOnlineUser, removeOnlineUser, setTypingUser, updateMessageStatus]);

  return socketRef.current;
};
'''

# --- Dashboard with online dots ---
FILES["screens/Dashboard.tsx"] = r'''import React, { useEffect, useState } from 'react';
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
'''

# --- ChatWindow with typing indicator and read receipts ---
FILES["screens/ChatWindow.tsx"] = r'''import React, { useState, useEffect, useRef } from 'react';
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
'''

# ==================== WRITE FILES ====================

def write_files():
    for relative_path, content in FILES.items():
        full_path = os.path.join(BASE, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        print(f"  ✅ {relative_path}")

if __name__ == '__main__':
    write_files()
    print("\n🎉 All files updated! Now run:")
    print("  git add .")
    print("  git commit -m 'add online status, typing indicators, read receipts'")
    print("  git push")
    print("Then Vercel will auto-deploy. Enjoy your upgraded Vireo!")