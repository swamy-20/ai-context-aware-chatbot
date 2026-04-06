import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';
import prisma from '../prismaClient';
import { callNlpService } from '../services/nlp';

const router = Router();

router.post('/chat', async (req, res) => {
  try {
    const { message, sessionId: incomingSession } = req.body;
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    const sessionId = incomingSession ?? uuidv4();

    const storedUser = await prisma.message.create({
      data: {
        sessionId,
        role: 'user',
        text: message,
      },
    });

    const context = await prisma.message.findMany({
      where: { sessionId },
      orderBy: { createdAt: 'desc' },
      take: 8,
    });

    const nlpPayload = {
      message,
      context: context
        .map((item: any) => ({ text: item.text, role: item.role as 'user' | 'assistant' | 'system' })),
    };

    const nlpResult = await callNlpService(nlpPayload);
    const assistantMessage = nlpResult.reply || 'I could not interpret that.';

    const savedAssistant = await prisma.message.create({
      data: {
        sessionId,
        role: 'assistant',
        text: assistantMessage,
        analysis: nlpResult,
      },
    });

    res.json({
      sessionId,
      message: savedAssistant,
      analysis: nlpResult,
    });
  } catch (error) {
    console.error('Chat error', error);
    res.status(500).json({ error: 'Failed to process message' });
  }
});

router.get('/history', async (_req, res) => {
  try {
    const history = await prisma.message.findMany({
      orderBy: { createdAt: 'desc' },
    });
    res.json(history);
  } catch (error) {
    console.error('History error', error);
    res.status(500).json({ error: 'Unable to fetch history' });
  }
});

export default router;
