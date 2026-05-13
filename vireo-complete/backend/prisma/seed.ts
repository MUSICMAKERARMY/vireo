
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

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

    const user3 = await prisma.user.upsert({
    where: { email: 'chessyatharth@gmail.com' },
    update: {},
    create: {
      email: 'chessyatharth@gmail.com',
      username: 'chessyatharth',
      password: await bcrypt.hash('edge@1324567', 10),
      verified: true,
    },
  });

  const user4 = await prisma.user.upsert({
    where: { email: 'gaaguanurag221@gmail.com' },
    update: {},
    create: {
      email: 'gaaguanurag221@gmail.com',
      username: 'gaaguanurag',
      password: await bcrypt.hash('password@123', 10),
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
