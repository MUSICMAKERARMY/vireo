import { Response } from 'express';
import { AuthRequest } from '../auth/auth.middleware';
import prisma from '../config/database';
import { generateThumbnail } from './uploads.utils';

export const uploadMedia = async (req: AuthRequest, res: Response) => {
  const file = req.file;
  if (!file) return res.status(400).json({ message: 'No file uploaded' });
  const messageId = req.body.messageId;
  let thumbnail = undefined;
  if (file.mimetype.startsWith('image/')) {
    thumbnail = await generateThumbnail(file.path);
  }
  const media = await prisma.media.create({
    data: {
      messageId,
      url: file.path,
      thumbnail,
      mimeType: file.mimetype,
      size: file.size,
      uploaderId: req.user.sub,
    },
  });
  res.json(media);
};
