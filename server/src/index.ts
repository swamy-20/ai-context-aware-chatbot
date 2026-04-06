import app from './app';
import prisma from './prismaClient';

const port = Number(process.env.PORT ?? 4000);

async function start() {
  try {
    await prisma.$connect();
    app.listen(port, () => {
      console.log(`Server listening on http://localhost:${port}`);
    });
  } catch (error) {
    console.error('Failed to start server', error);
    process.exit(1);
  }
}

start();
