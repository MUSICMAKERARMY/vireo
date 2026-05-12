import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { listChats, createDirectChat } from './chats.controller';
const router = Router();
router.get('/', authenticate, listChats);
router.post('/', authenticate, createDirectChat);
export default router;
