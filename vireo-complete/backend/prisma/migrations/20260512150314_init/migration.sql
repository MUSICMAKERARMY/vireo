-- CreateEnum
CREATE TYPE "MessageStatus" AS ENUM ('SENT', 'DELIVERED', 'SEEN');

-- CreateEnum
CREATE TYPE "MembershipRole" AS ENUM ('ADMIN', 'MODERATOR', 'MEMBER');

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT,
    "username" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "avatar" TEXT,
    "status" TEXT,
    "lastSeen" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "isOnline" BOOLEAN NOT NULL DEFAULT false,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "role" TEXT NOT NULL DEFAULT 'USER',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Session" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "refreshToken" TEXT NOT NULL,
    "deviceInfo" TEXT,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Session_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "UserSettings" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "theme" TEXT NOT NULL DEFAULT 'dark',

    CONSTRAINT "UserSettings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "NotificationSettings" (
    "id" TEXT NOT NULL,
    "sound" BOOLEAN NOT NULL DEFAULT true,
    "desktop" BOOLEAN NOT NULL DEFAULT true,
    "preview" BOOLEAN NOT NULL DEFAULT true,
    "mutedUntil" TIMESTAMP(3),
    "userSettingsId" TEXT NOT NULL,

    CONSTRAINT "NotificationSettings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PrivacySettings" (
    "id" TEXT NOT NULL,
    "lastSeenVisible" BOOLEAN NOT NULL DEFAULT true,
    "profilePublic" BOOLEAN NOT NULL DEFAULT true,
    "readReceipts" BOOLEAN NOT NULL DEFAULT true,
    "userSettingsId" TEXT NOT NULL,

    CONSTRAINT "PrivacySettings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Chat" (
    "id" TEXT NOT NULL,
    "type" TEXT NOT NULL DEFAULT 'DIRECT',
    "name" TEXT,
    "icon" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Chat_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ChatParticipant" (
    "id" TEXT NOT NULL,
    "chatId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "joinedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "archived" BOOLEAN NOT NULL DEFAULT false,
    "pinned" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "ChatParticipant_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Group" (
    "id" TEXT NOT NULL,
    "chatId" TEXT NOT NULL,
    "description" TEXT,
    "inviteLink" TEXT,
    "permissions" TEXT NOT NULL DEFAULT 'ALL_CAN_SEND',

    CONSTRAINT "Group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GroupMember" (
    "id" TEXT NOT NULL,
    "groupId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "role" "MembershipRole" NOT NULL DEFAULT 'MEMBER',
    "joinedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "GroupMember_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Message" (
    "id" TEXT NOT NULL,
    "chatId" TEXT NOT NULL,
    "senderId" TEXT NOT NULL,
    "replyToId" TEXT,
    "body" TEXT,
    "type" TEXT NOT NULL DEFAULT 'TEXT',
    "status" "MessageStatus" NOT NULL DEFAULT 'SENT',
    "edited" BOOLEAN NOT NULL DEFAULT false,
    "deleted" BOOLEAN NOT NULL DEFAULT false,
    "scheduledAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Message_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Media" (
    "id" TEXT NOT NULL,
    "messageId" TEXT NOT NULL,
    "uploaderId" TEXT,
    "url" TEXT NOT NULL,
    "thumbnail" TEXT,
    "mimeType" TEXT NOT NULL,
    "size" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Media_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Story" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "mediaUrl" TEXT NOT NULL,
    "mimeType" TEXT NOT NULL,
    "caption" TEXT,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Story_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StoryView" (
    "id" TEXT NOT NULL,
    "storyId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "viewedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "StoryView_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Notification" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "content" JSONB,
    "read" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Notification_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Reaction" (
    "id" TEXT NOT NULL,
    "messageId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "emoji" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Reaction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "BlockedUser" (
    "id" TEXT NOT NULL,
    "blockerId" TEXT NOT NULL,
    "blockedId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "BlockedUser_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ArchivedChat" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "chatId" TEXT NOT NULL,
    "archivedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ArchivedChat_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Call" (
    "id" TEXT NOT NULL,
    "callerId" TEXT NOT NULL,
    "calleeId" TEXT,
    "chatId" TEXT,
    "type" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "startedAt" TIMESTAMP(3) NOT NULL,
    "endedAt" TIMESTAMP(3),

    CONSTRAINT "Call_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "User_phone_key" ON "User"("phone");

-- CreateIndex
CREATE UNIQUE INDEX "User_username_key" ON "User"("username");

-- CreateIndex
CREATE UNIQUE INDEX "Session_refreshToken_key" ON "Session"("refreshToken");

-- CreateIndex
CREATE UNIQUE INDEX "UserSettings_userId_key" ON "UserSettings"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "NotificationSettings_userSettingsId_key" ON "NotificationSettings"("userSettingsId");

-- CreateIndex
CREATE UNIQUE INDEX "PrivacySettings_userSettingsId_key" ON "PrivacySettings"("userSettingsId");

-- CreateIndex
CREATE UNIQUE INDEX "ChatParticipant_chatId_userId_key" ON "ChatParticipant"("chatId", "userId");

-- CreateIndex
CREATE UNIQUE INDEX "Group_chatId_key" ON "Group"("chatId");

-- CreateIndex
CREATE UNIQUE INDEX "GroupMember_groupId_userId_key" ON "GroupMember"("groupId", "userId");

-- CreateIndex
CREATE UNIQUE INDEX "Reaction_messageId_userId_key" ON "Reaction"("messageId", "userId");

-- CreateIndex
CREATE UNIQUE INDEX "BlockedUser_blockerId_blockedId_key" ON "BlockedUser"("blockerId", "blockedId");

-- CreateIndex
CREATE UNIQUE INDEX "ArchivedChat_userId_chatId_key" ON "ArchivedChat"("userId", "chatId");

-- AddForeignKey
ALTER TABLE "Session" ADD CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserSettings" ADD CONSTRAINT "UserSettings_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "NotificationSettings" ADD CONSTRAINT "NotificationSettings_userSettingsId_fkey" FOREIGN KEY ("userSettingsId") REFERENCES "UserSettings"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PrivacySettings" ADD CONSTRAINT "PrivacySettings_userSettingsId_fkey" FOREIGN KEY ("userSettingsId") REFERENCES "UserSettings"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ChatParticipant" ADD CONSTRAINT "ChatParticipant_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES "Chat"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ChatParticipant" ADD CONSTRAINT "ChatParticipant_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Group" ADD CONSTRAINT "Group_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES "Chat"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GroupMember" ADD CONSTRAINT "GroupMember_groupId_fkey" FOREIGN KEY ("groupId") REFERENCES "Group"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GroupMember" ADD CONSTRAINT "GroupMember_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES "Chat"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_senderId_fkey" FOREIGN KEY ("senderId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_replyToId_fkey" FOREIGN KEY ("replyToId") REFERENCES "Message"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Media" ADD CONSTRAINT "Media_messageId_fkey" FOREIGN KEY ("messageId") REFERENCES "Message"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Media" ADD CONSTRAINT "Media_uploaderId_fkey" FOREIGN KEY ("uploaderId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Story" ADD CONSTRAINT "Story_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StoryView" ADD CONSTRAINT "StoryView_storyId_fkey" FOREIGN KEY ("storyId") REFERENCES "Story"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StoryView" ADD CONSTRAINT "StoryView_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Notification" ADD CONSTRAINT "Notification_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Reaction" ADD CONSTRAINT "Reaction_messageId_fkey" FOREIGN KEY ("messageId") REFERENCES "Message"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Reaction" ADD CONSTRAINT "Reaction_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BlockedUser" ADD CONSTRAINT "BlockedUser_blockerId_fkey" FOREIGN KEY ("blockerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BlockedUser" ADD CONSTRAINT "BlockedUser_blockedId_fkey" FOREIGN KEY ("blockedId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ArchivedChat" ADD CONSTRAINT "ArchivedChat_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ArchivedChat" ADD CONSTRAINT "ArchivedChat_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES "Chat"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Call" ADD CONSTRAINT "Call_callerId_fkey" FOREIGN KEY ("callerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Call" ADD CONSTRAINT "Call_calleeId_fkey" FOREIGN KEY ("calleeId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Call" ADD CONSTRAINT "Call_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES "Chat"("id") ON DELETE SET NULL ON UPDATE CASCADE;
