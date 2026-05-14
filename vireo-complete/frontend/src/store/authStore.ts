import { create } from 'zustand';
import api from '../services/api';

interface AuthState {
  user: any | null;
  isAuthenticated: boolean;
  userId: string | null;          // ← NEW
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  setUser: (user: any) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('accessToken'),
  userId: null,

  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { accessToken, refreshToken, user } = res.data;
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    set({ user, isAuthenticated: true, userId: user.id });
  },

  register: async (data) => {
    await api.post('/auth/register', data);
  },

  logout: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    set({ user: null, isAuthenticated: false, userId: null });
  },

  setUser: (user) => set({ user, userId: user.id }),
}));