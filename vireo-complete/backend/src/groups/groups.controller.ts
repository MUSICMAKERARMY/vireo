import { Response } from 'express';
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
