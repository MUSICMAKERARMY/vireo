import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { uploadMedia } from './uploads.controller';
import { upload } from './uploads.middleware';

const router = Router();
router.post('/', authenticate, upload.single('file'), uploadMedia);
export default router;
