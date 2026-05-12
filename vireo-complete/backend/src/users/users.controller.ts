import { Request, Response } from 'express';
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
