import multer from 'multer';
import path from 'path';
import { v4 as uuid } from 'uuid';

const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, uuid() + ext);
  },
});
const fileFilter = (req: any, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'audio/mpeg', 'audio/wav', 'application/pdf'];
  if (allowed.includes(file.mimetype)) cb(null, true);
  else cb(new Error('Invalid file type'));
};
export const upload = multer({ storage, fileFilter, limits: { fileSize: 50 * 1024 * 1024 } });
