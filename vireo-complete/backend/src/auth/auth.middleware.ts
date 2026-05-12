import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthRequest extends Request {
  user?: any;
}

export const authenticate = (req: AuthRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) return res.status(401).json({ message: 'Access token required' });
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_ACCESS_SECRET!);
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ message: 'Invalid token' });
  }
};
