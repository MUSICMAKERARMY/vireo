import { Response } from 'express';
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
