import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { getChatMessages } from './messages.controller';
const router = Router();
router.get('/:chatId', authenticate, getChatMessages);
export default router;
