import { Server } from 'socket.io';
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
