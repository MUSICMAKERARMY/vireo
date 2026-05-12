#!/usr/bin/env python3
r"""
Generates all missing backend + frontend files for Vireo.
Run from: C:\Users\chess\OneDrive\Documents\VireoProject\
"""

import os

BASE_BACKEND = "vireo-complete/backend/src"
BASE_FRONTEND = "vireo-complete/frontend/src"

# ===== BACKEND FILES =====
BACKEND_FILES = {
    # --- Auth ---
    "auth/auth.routes.ts": r"""import { Router } from 'express';
import { register, login, refreshTokenHandler, verifyOTP, forgotPassword, getProfile } from './auth.controller';
import { authenticate } from './auth.middleware';
import { validate } from '../middleware/validate';
import { registerSchema, loginSchema } from './auth.utils';

const router = Router();

router.post('/register', validate(registerSchema), register);
router.post('/login', validate(loginSchema), login);
router.post('/refresh', refreshTokenHandler);
router.post('/verify-otp', verifyOTP);
router.post('/forgot-password', forgotPassword);
router.get('/me', authenticate, getProfile);

export default router;
""",
    "auth/auth.controller.ts": r"""import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import prisma from '../config/database';
import { generateAccessToken, generateRefreshToken, verifyRefreshToken } from '../utils/jwt';
import { AuthRequest } from './auth.middleware';

export const register = async (req: Request, res: Response) => {
  try {
    const { email, username, password } = req.body;
    const existing = await prisma.user.findFirst({
      where: { OR: [{ email }, { username }] },
    });
    if (existing) return res.status(409).json({ message: 'User already exists' });

    const hashed = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({
      data: { email, username, password: hashed },
    });
    res.status(201).json({ message: 'Registered. Please verify email.', userId: user.id });
  } catch (e) {
    res.status(500).json({ message: 'Registration failed' });
  }
};

export const login = async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }
    if (!user.verified) return res.status(403).json({ message: 'Email not verified' });

    const accessToken = generateAccessToken(user.id);
    const refreshToken = generateRefreshToken(user.id);
    await prisma.session.create({
      data: {
        userId: user.id,
        refreshToken,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      },
    });
    res.json({
      accessToken, refreshToken,
      user: { id: user.id, email: user.email, username: user.username, avatar: user.avatar }
    });
  } catch (e) {
    res.status(500).json({ message: 'Login failed' });
  }
};

export const refreshTokenHandler = async (req: Request, res: Response) => {
  const { refreshToken } = req.body;
  if (!refreshToken) return res.status(401).json({ message: 'Refresh token required' });
  try {
    const decoded: any = verifyRefreshToken(refreshToken);
    const session = await prisma.session.findUnique({ where: { refreshToken } });
    if (!session) throw new Error('Invalid session');
    const newAccess = generateAccessToken(decoded.sub);
    const newRefresh = generateRefreshToken(decoded.sub);
    await prisma.session.update({
      where: { id: session.id },
      data: { refreshToken: newRefresh, expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) },
    });
    res.json({ accessToken: newAccess, refreshToken: newRefresh });
  } catch (err) {
    return res.status(401).json({ message: 'Invalid refresh token' });
  }
};

export const verifyOTP = async (req: Request, res: Response) => {
  // In production, check OTP and mark user verified
  res.json({ message: 'OTP verified' });
};

export const forgotPassword = async (req: Request, res: Response) => {
  // Send reset link
  res.json({ message: 'Reset link sent' });
};

export const getProfile = async (req: AuthRequest, res: Response) => {
  const user = await prisma.user.findUnique({ where: { id: req.user.sub } });
  if (!user) return res.status(404).json({ message: 'User not found' });
  const { password, ...rest } = user;
  res.json(rest);
};
""",
    "auth/auth.middleware.ts": r"""import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthRequest extends Request {
  user?: any;
}

export const authenticate = (req: AuthRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) return res.status(401).json({ message: 'Access token required' });
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_ACCESS_SECRET!);
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ message: 'Invalid token' });
  }
};
""",
    "auth/auth.utils.ts": r"""import { z } from 'zod';
export const registerSchema = z.object({ email: z.string().email(), username: z.string().min(3), password: z.string().min(8) });
export const loginSchema = z.object({ email: z.string().email(), password: z.string() });
""",
    # --- Users ---
    "users/users.routes.ts": r"""import { Router } from 'express';
import { getProfile, search } from './users.controller';
import { authenticate } from '../auth/auth.middleware';

const router = Router();
router.get('/search', authenticate, search);
router.get('/:id', authenticate, getProfile);
export default router;
""",
    "users/users.controller.ts": r"""import { Request, Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import prisma from '../config/database';

export const getProfile = async (req: AuthRequest, res: Response) => {
  const user = await prisma.user.findUnique({ where: { id: req.params.id } });
  if (!user) return res.status(404).json({ message: 'User not found' });
  const { password, ...rest } = user;
  res.json(rest);
};

export const search = async (req: Request, res: Response) => {
  const { q } = req.query;
  if (!q) return res.json([]);
  const users = await prisma.user.findMany({
    where: { username: { contains: q as string, mode: 'insensitive' } },
    select: { id: true, username: true, avatar: true, status: true },
    take: 20,
  });
  res.json(users);
};
""",
    "users/users.service.ts": r"""import prisma from '../config/database';

export const findUserById = async (id: string) =>
  prisma.user.findUnique({ where: { id }, include: { settings: true } });

export const searchUsers = async (query: string) =>
  prisma.user.findMany({
    where: { username: { contains: query, mode: 'insensitive' } },
    select: { id: true, username: true, avatar: true, status: true },
    take: 20,
  });
""",
    # --- Chats ---
    "chats/chats.routes.ts": r"""import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { listChats, createDirectChat } from './chats.controller';
const router = Router();
router.get('/', authenticate, listChats);
router.post('/', authenticate, createDirectChat);
export default router;
""",
    "chats/chats.controller.ts": r"""import { Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import prisma from '../config/database';

export const listChats = async (req: AuthRequest, res: Response) => {
  const chats = await prisma.chat.findMany({
    where: { participants: { some: { userId: req.user.sub } } },
    include: {
      participants: { include: { user: { select: { id: true, username: true, avatar: true } } } },
      messages: { orderBy: { createdAt: 'desc' }, take: 1, include: { sender: true } },
    },
  });
  res.json(chats);
};

export const createDirectChat = async (req: AuthRequest, res: Response) => {
  const { userId } = req.body;
  const existing = await prisma.chat.findFirst({
    where: { type: 'DIRECT', participants: { every: { userId: { in: [req.user.sub, userId] } } } },
  });
  if (existing) return res.json(existing);
  const chat = await prisma.chat.create({
    data: {
      type: 'DIRECT',
      participants: {
        createMany: { data: [{ userId: req.user.sub }, { userId }] },
      },
    },
  });
  res.json(chat);
};
""",
    "chats/chats.service.ts": r"""import prisma from '../config/database';

export const getUserChats = async (userId: string) =>
  prisma.chat.findMany({
    where: { participants: { some: { userId } } },
    include: {
      participants: { include: { user: { select: { id: true, username: true, avatar: true } } } },
      messages: { orderBy: { createdAt: 'desc' }, take: 1 },
    },
  });
""",
    # --- Messages ---
    "messages/messages.routes.ts": r"""import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { getChatMessages } from './messages.controller';
const router = Router();
router.get('/:chatId', authenticate, getChatMessages);
export default router;
""",
    "messages/messages.controller.ts": r"""import { Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import { getMessages } from './messages.service';

export const getChatMessages = async (req: AuthRequest, res: Response) => {
  const { chatId } = req.params;
  const cursor = req.query.cursor as string | undefined;
  const messages = await getMessages(chatId, cursor);
  res.json(messages);
};
""",
    "messages/messages.service.ts": r"""import prisma from '../config/database';

export const getMessages = async (chatId: string, cursor?: string) => {
  const limit = 50;
  const messages = await prisma.message.findMany({
    where: { chatId },
    orderBy: { createdAt: 'desc' },
    take: limit,
    ...(cursor && { cursor: { id: cursor }, skip: 1 }),
    include: {
      sender: { select: { id: true, username: true, avatar: true } },
      media: true,
      reactions: { include: { user: { select: { id: true, username: true } } } },
    },
  });
  return messages.reverse();
};
""",
    # --- Groups ---
    "groups/groups.routes.ts": r"""import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { newGroup } from './groups.controller';
const router = Router();
router.post('/', authenticate, newGroup);
export default router;
""",
    "groups/groups.controller.ts": r"""import { Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import prisma from '../config/database';

export const newGroup = async (req: AuthRequest, res: Response) => {
  const { name, members } = req.body; // members: string[]
  const chat = await prisma.chat.create({
    data: {
      type: 'GROUP',
      name,
      participants: {
        createMany: {
          data: [...members.map((uid: string) => ({ userId: uid })), { userId: req.user.sub }],
        },
      },
    },
  });
  await prisma.group.create({
    data: {
      chatId: chat.id,
      members: {
        createMany: {
          data: [
            { userId: req.user.sub, role: 'ADMIN' },
            ...members.map((uid: string) => ({ userId: uid, role: 'MEMBER' })),
          ],
        },
      },
    },
  });
  res.json(chat);
};
""",
    "groups/groups.service.ts": r"""import prisma from '../config/database';

export const createGroup = async (name: string, userIds: string[], adminId: string) => {
  const chat = await prisma.chat.create({
    data: {
      type: 'GROUP',
      name,
      participants: {
        createMany: { data: userIds.map(uid => ({ userId: uid })) },
      },
    },
  });
  await prisma.group.create({
    data: {
      chatId: chat.id,
      members: {
        createMany: { data: userIds.map(uid => ({ userId: uid, role: uid === adminId ? 'ADMIN' : 'MEMBER' })) },
      },
    },
  });
  return chat;
};
""",
    # --- Uploads ---
    "uploads/uploads.routes.ts": r"""import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { uploadMedia } from './uploads.controller';
import { upload } from './uploads.middleware';

const router = Router();
router.post('/', authenticate, upload.single('file'), uploadMedia);
export default router;
""",
    "uploads/uploads.controller.ts": r"""import { Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import prisma from '../config/database';
import { generateThumbnail } from './uploads.utils';

export const uploadMedia = async (req: AuthRequest, res: Response) => {
  const file = req.file;
  if (!file) return res.status(400).json({ message: 'No file uploaded' });
  const messageId = req.body.messageId;
  let thumbnail = undefined;
  if (file.mimetype.startsWith('image/')) {
    thumbnail = await generateThumbnail(file.path);
  }
  const media = await prisma.media.create({
    data: {
      messageId,
      url: file.path,
      thumbnail,
      mimeType: file.mimetype,
      size: file.size,
      uploaderId: req.user.sub,
    },
  });
  res.json(media);
};
""",
    "uploads/uploads.middleware.ts": r"""import multer from 'multer';
import path from 'path';
import { v4 as uuid } from 'uuid';

const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, uuid() + ext);
  },
});
const fileFilter = (req: any, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'audio/mpeg', 'audio/wav', 'application/pdf'];
  if (allowed.includes(file.mimetype)) cb(null, true);
  else cb(new Error('Invalid file type'));
};
export const upload = multer({ storage, fileFilter, limits: { fileSize: 50 * 1024 * 1024 } });
""",
    "uploads/uploads.utils.ts": r"""import sharp from 'sharp';
import path from 'path';

export const generateThumbnail = async (filePath: string) => {
  const ext = path.extname(filePath);
  const thumbName = filePath.replace(ext, `_thumb${ext}`);
  await sharp(filePath).resize(300, 300, { fit: 'inside' }).toFile(thumbName);
  return thumbName;
};
""",
    # --- Sockets ---
    "sockets/socket.handler.ts": r"""import { Server } from 'socket.io';
import jwt from 'jsonwebtoken';
import prisma from '../config/database';

export const setupSocket = (io: Server) => {
  io.use((socket, next) => {
    const token = socket.handshake.auth.token;
    if (!token) return next(new Error('Authentication error'));
    try {
      const decoded = jwt.verify(token, process.env.JWT_ACCESS_SECRET!);
      (socket as any).userId = decoded.sub;
      next();
    } catch { next(new Error('Invalid token')); }
  });

  io.on('connection', async (socket) => {
    const userId = (socket as any).userId;
    await prisma.user.update({ where: { id: userId }, data: { isOnline: true } });
    io.emit('user_online', userId);
    socket.join(`user:${userId}`);

    socket.on('send_message', async (data) => {
      const { chatId, body, type, replyToId } = data;
      const msg = await prisma.message.create({
        data: { chatId, senderId: userId, body, type, replyToId },
        include: { sender: { select: { id: true, username: true, avatar: true } } },
      });
      const participants = await prisma.chatParticipant.findMany({ where: { chatId } });
      participants.forEach(p => io.to(`user:${p.userId}`).emit('new_message', msg));
    });

    socket.on('typing_start', (chatId) => {
      socket.broadcast.emit('user_typing', { chatId, userId });
    });

    socket.on('typing_stop', (chatId) => {
      socket.broadcast.emit('user_stop_typing', { chatId, userId });
    });

    socket.on('message_seen', async ({ messageId }) => {
      await prisma.message.update({ where: { id: messageId }, data: { status: 'SEEN' } });
      io.emit('message_status', { messageId, status: 'SEEN' });
    });

    socket.on('disconnect', async () => {
      await prisma.user.update({ where: { id: userId }, data: { isOnline: false, lastSeen: new Date() } });
      io.emit('user_offline', userId);
    });
  });
};
""",
    # --- Middleware ---
    "middleware/errorHandler.ts": r"""import { Request, Response, NextFunction } from 'express';
export const errorHandler = (err: any, req: Request, res: Response, next: NextFunction) => {
  console.error(err);
  res.status(err.status || 500).json({ message: err.message || 'Internal server error' });
};
""",
    "middleware/rateLimiter.ts": r"""import rateLimit from 'express-rate-limit';
export const apiLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 200 });
""",
    "middleware/validate.ts": r"""import { Request, Response, NextFunction } from 'express';
import { ZodSchema } from 'zod';
export const validate = (schema: ZodSchema) => (req: Request, res: Response, next: NextFunction) => {
  const result = schema.safeParse(req.body);
  if (!result.success) return res.status(400).json({ errors: result.error.issues });
  req.body = result.data;
  next();
};
""",
    # --- Config ---
    "config/database.ts": r"""import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
export default prisma;
""",
    "config/env.ts": r"""import dotenv from 'dotenv';
dotenv.config();
export const env = {
  DATABASE_URL: process.env.DATABASE_URL!,
  JWT_ACCESS_SECRET: process.env.JWT_ACCESS_SECRET!,
  JWT_REFRESH_SECRET: process.env.JWT_REFRESH_SECRET!,
  CLIENT_URL: process.env.CLIENT_URL || 'http://localhost:5173',
  PORT: parseInt(process.env.PORT || '5000', 10),
  UPLOAD_DIR: process.env.UPLOAD_DIR || 'uploads',
};
""",
    "config/logger.ts": r"""const logger = { info: (msg: string) => console.log(`[INFO] ${msg}`), error: (msg: string) => console.error(`[ERROR] ${msg}`) };
export default logger;
""",
    "utils/jwt.ts": r"""import jwt from 'jsonwebtoken';
export const generateAccessToken = (userId: string) => jwt.sign({ sub: userId }, process.env.JWT_ACCESS_SECRET!, { expiresIn: '15m' });
export const generateRefreshToken = (userId: string) => jwt.sign({ sub: userId }, process.env.JWT_REFRESH_SECRET!, { expiresIn: '7d' });
export const verifyRefreshToken = (token: string) => jwt.verify(token, process.env.JWT_REFRESH_SECRET!);
""",
    "utils/helpers.ts": r"""export const generateOTP = () => Math.floor(100000 + Math.random() * 900000).toString();
""",
}

# ===== FRONTEND SCAFFOLDING =====
# We'll create a minimal but functional set of React files using Vite + Tailwind.
FRONTEND_FILES = {
    "src/main.tsx": r"""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",
    "src/App.tsx": r"""import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './screens/Login';
import Dashboard from './screens/Dashboard';
import ChatWindow from './screens/ChatWindow';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat/:id" element={<ChatWindow />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
""",
    "src/screens/Login.tsx": r"""import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const nav = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('accessToken', res.data.accessToken);
      localStorage.setItem('refreshToken', res.data.refreshToken);
      nav('/dashboard');
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-surface">
      <form onSubmit={handleSubmit} className="glass p-8 rounded-2xl w-96">
        <h1 className="text-2xl font-heading text-primary mb-6">Vireo Login</h1>
        <input className="w-full p-3 mb-4 rounded bg-surface border border-white/10" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input className="w-full p-3 mb-6 rounded bg-surface border border-white/10" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <button className="w-full py-3 bg-primary text-surface font-bold rounded-full hover:bg-primary-dark transition" type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
""",
    "src/screens/Dashboard.tsx": r"""import React, { useEffect, useState } from 'react';
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
""",
    "src/screens/ChatWindow.tsx": r"""import React, { useState, useEffect, useRef } from 'react';
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
""",
    "src/services/api.ts": r"""import axios from 'axios';
const api = axios.create({ baseURL: '/api', headers: { 'Content-Type': 'application/json' } });
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export default api;
""",
    "src/socket/socketClient.ts": r"""import { io, Socket } from 'socket.io-client';
let socket: Socket | null = null;
export const getSocket = (): Socket => {
  if (!socket) {
    const token = localStorage.getItem('accessToken');
    socket = io('/', { auth: { token }, transports: ['websocket'] });
  }
  return socket;
};
""",
    "src/index.css": r"""@tailwind base;
@tailwind components;
@tailwind utilities;
body {
  font-family: 'Inter', sans-serif;
  background: #0B1120;
  color: #F1F5F9;
  margin: 0;
  overflow: hidden;
}
.glass {
  background: rgba(19, 27, 44, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.08);
}
"""
}

def create_files(base, files):
    for path, content in files.items():
        full = os.path.join(base, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')

if __name__ == '__main__':
    create_files(BASE_BACKEND, BACKEND_FILES)

    # Frontend: we also need package.json, tailwind config, etc.
    # Let's write a quick vite setup in the frontend folder.
    frontend_root = "vireo-complete/frontend"
    os.makedirs(frontend_root, exist_ok=True)

    with open(os.path.join(frontend_root, "package.json"), 'w') as f:
        f.write(r'''{
  "name": "vireo-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.7",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.3",
    "socket.io-client": "^4.7.4"
  },
  "devDependencies": {
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^5.1.4"
  }
}
''')

    with open(os.path.join(frontend_root, "index.html"), 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vireo</title>
  </head>
  <body class="bg-[#0B1120] text-[#F1F5F9] font-body overflow-hidden">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>''')

    with open(os.path.join(frontend_root, "vite.config.ts"), 'w') as f:
        f.write(r'''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
      '/socket.io': { target: 'http://localhost:5000', ws: true },
    },
  },
});
''')

    with open(os.path.join(frontend_root, "tailwind.config.js"), 'w') as f:
        f.write('''/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#00E5A0',
        'primary-dark': '#00B4D8',
        surface: '#131B2C',
        glass: 'rgba(255, 255, 255, 0.05)',
      },
    },
  },
  plugins: [],
};
''')

    with open(os.path.join(frontend_root, "postcss.config.js"), 'w') as f:
        f.write('''export default { plugins: { tailwindcss: {}, autoprefixer: {} } };
''')

    with open(os.path.join(frontend_root, "tsconfig.json"), 'w') as f:
        f.write('''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true
  },
  "include": ["src"]
}
''')
    create_files(frontend_root, FRONTEND_FILES)

    print("\n✅ All missing backend and frontend files created!")
    print("\n👉 Now run:")
    print("   cd vireo-complete/backend")
    print("   npm run dev   (should start without errors)")
    print("\n   Open a new terminal:")
    print("   cd vireo-complete/frontend")
    print("   npm install")
    print("   npm run dev")
    print("\n   Then open http://localhost:5173")