import prisma from '../config/database';

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
