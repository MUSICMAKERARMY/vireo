import { Router } from 'express';
import { register, login, refreshTokenHandler, verifyOTP, forgotPassword, getProfile } from './auth.controller';
import { authenticate } from './auth.middleware';
import { validate } from '../middleware/validate';
import { registerSchema, loginSchema } from './auth.utils';

const router = Router();

router.post('/register', validate(registerSchema), register);
router.post('/login', validate(loginSchema), login);
router.post('/refresh', refreshTokenHandler);
router.post('/verify-otp', verifyOTP);
router.post('/forgot-password', forgotPassword);
router.get('/me', authenticate, getProfile);

export default router;
