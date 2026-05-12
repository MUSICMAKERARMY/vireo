import dotenv from 'dotenv';
dotenv.config();
export const env = {
  DATABASE_URL: process.env.DATABASE_URL!,
  JWT_ACCESS_SECRET: process.env.JWT_ACCESS_SECRET!,
  JWT_REFRESH_SECRET: process.env.JWT_REFRESH_SECRET!,
  CLIENT_URL: process.env.CLIENT_URL || 'http://localhost:5173',
  PORT: parseInt(process.env.PORT || '5000', 10),
  UPLOAD_DIR: process.env.UPLOAD_DIR || 'uploads',
};
