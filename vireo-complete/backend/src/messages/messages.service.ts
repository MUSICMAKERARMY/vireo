import prisma from '../config/database';

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
