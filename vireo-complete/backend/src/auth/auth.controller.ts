import { Request, Response } from 'express';
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
