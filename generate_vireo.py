#!/usr/bin/env python3
"""
Vireo Full Project Generator
Run: python generate_vireo.py
Output: ./vireo-complete/ folder with backend + frontend
"""

import os, pathlib, zipfile

# -------------------------------------------------------------------
MAIN_FOLDER = "vireo-complete"
# -------------------------------------------------------------------

FILES = {}

# ===== BACKEND =====
FILES["vireo-complete/backend/package.json"] = r'''{
  "name": "vireo-backend",
  "version": "1.0.0",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "migrate": "npx prisma migrate dev --name init",
    "seed": "npx prisma db seed"
  },
  "dependencies": {
    "@prisma/client": "^5.10.0",
    "bcrypt": "^5.1.1",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "express": "^4.18.3",
    "express-rate-limit": "^7.2.0",
    "helmet": "^7.1.0",
    "jsonwebtoken": "^9.0.2",
    "multer": "^1.4.5-lts.1",
    "sharp": "^0.33.2",
    "socket.io": "^4.7.4",
    "uuid": "^9.0.1",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/bcrypt": "^5.0.2",
    "@types/cors": "^2.8.17",
    "@types/express": "^4.17.21",
    "@types/jsonwebtoken": "^9.0.6",
    "@types/multer": "^1.4.11",
    "@types/node": "^20.11.19",
    "@types/uuid": "^9.0.8",
    "prisma": "^5.10.0",
    "tsx": "^4.7.1",
    "typescript": "^5.3.3"
  },
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
'''

FILES["vireo-complete/backend/tsconfig.json"] = r'''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
'''

FILES["vireo-complete/backend/.env.example"] = r'''DATABASE_URL=postgresql://postgres:password@localhost:5432/vireo
JWT_ACCESS_SECRET=change_this_to_a_random_secret_32_chars
JWT_REFRESH_SECRET=change_this_to_another_secret_32_chars
CLIENT_URL=http://localhost:5173
PORT=5000
UPLOAD_DIR=uploads
'''

FILES["vireo-complete/backend/prisma/schema.prisma"] = r'''generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum MessageStatus {
  SENT
  DELIVERED
  SEEN
}

enum MembershipRole {
  ADMIN
  MODERATOR
  MEMBER
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  phone     String?  @unique
  username  String   @unique
  password  String
  avatar    String?
  status    String?
  lastSeen  DateTime @default(now())
  isOnline  Boolean  @default(false)
  verified  Boolean  @default(false)
  role      String   @default("USER")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  sessions      Session[]
  chats         ChatParticipant[]
  messages      Message[]
  sentMedia     Media[]
  notifications Notification[]
  stories       Story[]
  storyViews    StoryView[]
  blockedBy     BlockedUser[]   @relation("blockedBy")
  blocked       BlockedUser[]   @relation("blocked")
  groupMembers  GroupMember[]
  archivedChats ArchivedChat[]
  settings      UserSettings?
  reactions     Reaction[]
  calls         Call[]
}

model Session {
  id           String   @id @default(cuid())
  userId       String
  refreshToken String   @unique
  deviceInfo   String?
  expiresAt    DateTime
  createdAt    DateTime @default(now())
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model UserSettings {
  id             String               @id @default(cuid())
  userId         String               @unique
  theme          String               @default("dark")
  notifications  NotificationSettings?
  privacy        PrivacySettings?
  user           User                 @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model NotificationSettings {
  id              String        @id @default(cuid())
  sound           Boolean       @default(true)
  desktop         Boolean       @default(true)
  preview         Boolean       @default(true)
  mutedUntil      DateTime?
  userSettingsId  String        @unique
  userSettings    UserSettings? @relation(fields: [userSettingsId], references: [id])
}

model PrivacySettings {
  id              String        @id @default(cuid())
  lastSeenVisible Boolean       @default(true)
  profilePublic   Boolean       @default(true)
  readReceipts    Boolean       @default(true)
  userSettingsId  String        @unique
  userSettings    UserSettings? @relation(fields: [userSettingsId], references: [id])
}

model Chat {
  id           String            @id @default(cuid())
  type         String            @default("DIRECT")
  name         String?
  icon         String?
  createdAt    DateTime          @default(now())
  updatedAt    DateTime          @updatedAt
  participants ChatParticipant[]
  messages     Message[]
  group        Group?
}

model ChatParticipant {
  id       String   @id @default(cuid())
  chatId   String
  userId   String
  joinedAt DateTime @default(now())
  archived Boolean  @default(false)
  pinned   Boolean  @default(false)
  chat     Chat     @relation(fields: [chatId], references: [id], onDelete: Cascade)
  user     User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([chatId, userId])
}

model Group {
  id          String         @id @default(cuid())
  chatId      String         @unique
  description String?
  inviteLink  String?
  permissions String         @default("ALL_CAN_SEND")
  members     GroupMember[]
  chat        Chat           @relation(fields: [chatId], references: [id], onDelete: Cascade)
}

model GroupMember {
  id       String         @id @default(cuid())
  groupId  String
  userId   String
  role     MembershipRole @default(MEMBER)
  joinedAt DateTime       @default(now())
  group    Group          @relation(fields: [groupId], references: [id], onDelete: Cascade)
  user     User           @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([groupId, userId])
}

model Message {
  id          String        @id @default(cuid())
  chatId      String
  senderId    String
  replyToId   String?
  body        String?
  type        String        @default("TEXT")
  status      MessageStatus @default(SENT)
  edited      Boolean       @default(false)
  deleted     Boolean       @default(false)
  scheduledAt DateTime?
  createdAt   DateTime      @default(now())
  updatedAt   DateTime      @updatedAt
  chat        Chat          @relation(fields: [chatId], references: [id], onDelete: Cascade)
  sender      User          @relation(fields: [senderId], references: [id], onDelete: Cascade)
  replyTo     Message?      @relation("Reply", fields: [replyToId], references: [id])
  replies     Message[]     @relation("Reply")
  media       Media[]
  reactions   Reaction[]
}

model Media {
  id        String   @id @default(cuid())
  messageId String
  url       String
  thumbnail String?
  mimeType  String
  size      Int
  createdAt DateTime @default(now())
  message   Message  @relation(fields: [messageId], references: [id], onDelete: Cascade)
}

model Story {
  id        String    @id @default(cuid())
  userId    String
  mediaUrl  String
  mimeType  String
  caption   String?
  expiresAt DateTime
  createdAt DateTime  @default(now())
  views     StoryView[]
  user      User      @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model StoryView {
  id       String   @id @default(cuid())
  storyId  String
  userId   String
  viewedAt DateTime @default(now())
  story    Story    @relation(fields: [storyId], references: [id], onDelete: Cascade)
  user     User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Notification {
  id        String   @id @default(cuid())
  userId    String
  type      String
  content   Json?
  read      Boolean  @default(false)
  createdAt DateTime @default(now())
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Reaction {
  id        String   @id @default(cuid())
  messageId String
  userId    String
  emoji     String
  createdAt DateTime @default(now())
  message   Message  @relation(fields: [messageId], references: [id], onDelete: Cascade)
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([messageId, userId])
}

model BlockedUser {
  id        String   @id @default(cuid())
  blockerId String
  blockedId String
  createdAt DateTime @default(now())
  blocker   User     @relation("blockedBy", fields: [blockerId], references: [id], onDelete: Cascade)
  blocked   User     @relation("blocked", fields: [blockedId], references: [id], onDelete: Cascade)

  @@unique([blockerId, blockedId])
}

model ArchivedChat {
  id         String   @id @default(cuid())
  userId     String
  chatId     String
  archivedAt DateTime @default(now())
  user       User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  chat       Chat     @relation(fields: [chatId], references: [id], onDelete: Cascade)

  @@unique([userId, chatId])
}

model Call {
  id        String    @id @default(cuid())
  callerId  String
  calleeId  String?
  chatId    String?
  type      String
  status    String
  startedAt DateTime
  endedAt   DateTime?
  caller    User      @relation("caller", fields: [callerId], references: [id], onDelete: Cascade)
  callee    User?     @relation("callee", fields: [calleeId], references: [id])
  chat      Chat?     @relation(fields: [chatId], references: [id])
}
'''

FILES["vireo-complete/backend/prisma/seed.ts"] = r"""
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  const password = await bcrypt.hash('password123', 10);

  const user1 = await prisma.user.upsert({
    where: { email: 'alice@vireo.com' },
    update: {},
    create: {
      email: 'alice@vireo.com',
      username: 'alice',
      password,
      verified: true,
      role: 'USER',
    },
  });

  const user2 = await prisma.user.upsert({
    where: { email: 'bob@vireo.com' },
    update: {},
    create: {
      email: 'bob@vireo.com',
      username: 'bob',
      password,
      verified: true,
    },
  });

  const chat = await prisma.chat.create({
    data: {
      type: 'DIRECT',
      participants: {
        createMany: {
          data: [
            { userId: user1.id },
            { userId: user2.id },
          ],
        },
      },
    },
  });

  console.log('Seeded users and chat', chat.id);
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
"""

FILES["vireo-complete/backend/src/server.ts"] = r"""
import express from 'express';
import http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import { Server as SocketIO } from 'socket.io';
import dotenv from 'dotenv';
import authRoutes from './auth/auth.routes';
import userRoutes from './users/users.routes';
import chatRoutes from './chats/chats.routes';
import messageRoutes from './messages/messages.routes';
import groupRoutes from './groups/groups.routes';
import uploadRoutes from './uploads/uploads.routes';
import { setupSocket } from './sockets/socket.handler';
import { errorHandler } from './middleware/errorHandler';
import { apiLimiter } from './middleware/rateLimiter';

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new SocketIO(server, {
  cors: { origin: process.env.CLIENT_URL || 'http://localhost:5173' }
});

app.use(helmet({ crossOriginResourcePolicy: { policy: 'cross-origin' } }));
app.use(cors({ origin: process.env.CLIENT_URL, credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use(apiLimiter);
app.use('/uploads', express.static('uploads'));

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/chats', chatRoutes);
app.use('/api/messages', messageRoutes);
app.use('/api/groups', groupRoutes);
app.use('/api/uploads', uploadRoutes);
app.use(errorHandler);

setupSocket(io);

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Vireo backend on port ${PORT}`));
"""

# -------------------------------------------------------------------
# Helper function to write all files
# -------------------------------------------------------------------
def write_files():
    for path, content in FILES.items():
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    # Also create empty uploads folder
    os.makedirs("vireo-complete/backend/uploads", exist_ok=True)
    with open("vireo-complete/backend/uploads/.gitkeep", 'w') as f:
        f.write('')

if __name__ == "__main__":
    write_files()
    print("✅ All files generated in 'vireo-complete/'")
    print("\n👉 Next steps:")
    print("1. cd vireo-complete/backend")
    print("2. npm install")
    print("3. npx prisma generate")
    print("4. npx prisma migrate dev --name init")
    print("5. npm run seed")
    print("6. npm run dev")
    print("\nThen open a NEW terminal:")
    print("1. cd vireo-complete/frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("\nOpen http://localhost:5173 in your browser.")