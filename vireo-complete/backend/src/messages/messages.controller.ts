import { Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import { getMessages } from './messages.service';

export const getChatMessages = async (req: AuthRequest, res: Response) => {
  const { chatId } = req.params;
  const cursor = req.query.cursor as string | undefined;
  const messages = await getMessages(chatId, cursor);
  res.json(messages);
};
