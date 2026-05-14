import { useEffect, useRef } from 'react';
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
  const typingTimeouts = useRef<Record<string, NodeJS.Timeout>>({});

  useEffect(() => {
    const socket = getSocket();

    socket.on('user_online', (userId: string) => {
      addOnlineUser(userId);
    });

    socket.on('user_offline', (userId: string) => {
      removeOnlineUser(userId);
    });

    socket.on('new_message', (msg: any) => {
      addMessage(msg);
      // Auto‑mark as seen if chat is open
      if (msg.chatId === useChatStore.getState().activeChatId) {
        socket.emit('message_seen', { messageId: msg.id, chatId: msg.chatId });
      }
    });

    socket.on('message_status', ({ messageId, status }: any) => {
      updateMessageStatus(messageId, status);
    });

    socket.on('user_typing', ({ chatId, userId }: any) => {
      const chat = useChatStore.getState().chats.find((c) => c.id === chatId);
      if (chat) {
        const participant = chat.participants?.find((p: any) => p.userId === userId);
        const username = participant?.user?.username || 'Someone';
        setTypingUser(chatId, username);
        if (typingTimeouts.current[chatId]) clearTimeout(typingTimeouts.current[chatId]);
        typingTimeouts.current[chatId] = setTimeout(() => {
          setTypingUser(chatId, null);
        }, 2000);
      }
    });

    socket.on('user_stop_typing', ({ chatId }: any) => {
      setTypingUser(chatId, null);
      if (typingTimeouts.current[chatId]) {
        clearTimeout(typingTimeouts.current[chatId]);
        delete typingTimeouts.current[chatId];
      }
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
};