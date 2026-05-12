
import express from 'express';
import http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import { Server as SocketIO } from 'socket.io';
import dotenv from 'dotenv';
import authRoutes from './auth/auth.routes';
import userRoutes from './users/users.routes';
import chatRoutes from './chats/chats.routes';
import messageRoutes from './messages/messages.routes';
import groupRoutes from './groups/groups.routes';
import uploadRoutes from './uploads/uploads.routes';
import { setupSocket } from './sockets/socket.handler';
import { errorHandler } from './middleware/errorHandler';
import { apiLimiter } from './middleware/rateLimiter';

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new SocketIO(server, {
  cors: { origin: process.env.CLIENT_URL || 'http://localhost:5173' }
});

app.use(helmet({ crossOriginResourcePolicy: { policy: 'cross-origin' } }));
app.use(cors({ origin: process.env.CLIENT_URL, credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use(apiLimiter);
app.use('/uploads', express.static('uploads'));

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/chats', chatRoutes);
app.use('/api/messages', messageRoutes);
app.use('/api/groups', groupRoutes);
app.use('/api/uploads', uploadRoutes);
app.use(errorHandler);

setupSocket(io);

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Vireo backend on port ${PORT}`));
