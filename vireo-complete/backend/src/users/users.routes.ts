import { Router } from 'express';
import { getProfile, search } from './users.controller';
import { authenticate } from '../auth/auth.middleware';

const router = Router();
router.get('/search', authenticate, search);
router.get('/:id', authenticate, getProfile);
export default router;
