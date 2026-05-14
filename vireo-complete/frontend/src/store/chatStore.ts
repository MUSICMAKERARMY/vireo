import { create } from 'zustand';
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
