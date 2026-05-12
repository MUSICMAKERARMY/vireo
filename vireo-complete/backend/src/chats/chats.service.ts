import prisma from '../config/database';

export const getUserChats = async (userId: string) =>
  prisma.chat.findMany({
    where: { participants: { some: { userId } } },
    include: {
      participants: { include: { user: { select: { id: true, username: true, avatar: true } } } },
      messages: { orderBy: { createdAt: 'desc' }, take: 1 },
    },
  });
