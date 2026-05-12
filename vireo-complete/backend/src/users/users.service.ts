import prisma from '../config/database';

export const findUserById = async (id: string) =>
  prisma.user.findUnique({ where: { id }, include: { settings: true } });

export const searchUsers = async (query: string) =>
  prisma.user.findMany({
    where: { username: { contains: query, mode: 'insensitive' } },
    select: { id: true, username: true, avatar: true, status: true },
    take: 20,
  });
