import { Router } from 'express';
import { authenticate } from '../auth/auth.middleware';
import { newGroup } from './groups.controller';
const router = Router();
router.post('/', authenticate, newGroup);
export default router;
