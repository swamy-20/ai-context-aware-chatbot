import request from 'supertest';
import app from '../src/app';
import { callNlpService } from '../src/services/nlp';

jest.mock('../src/prismaClient', () => ({
  message: {
    create: jest.fn(),
    findMany: jest.fn(),
  },
}));

jest.mock('../src/services/nlp');

const pipelineResponse = {
  reply: 'Mock reply',
  tokens: ['mock'],
  lemmas: ['mock'],
  entities: [],
  dependencies: [],
  wsd: {},
  coreferences: [],
  embeddings: {},
  ngrams: {},
  contextSummary: 'mock summary',
};

const prismaMock = require('../src/prismaClient') as {
  message: {
    create: jest.Mock;
    findMany: jest.Mock;
  };
};

describe('Chat routes', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (callNlpService as jest.Mock).mockResolvedValue(pipelineResponse);
  });

  it('creates a session and replies', async () => {
    prismaMock.message.create.mockResolvedValueOnce({ id: 1, sessionId: 'session-1', role: 'user', text: 'hello' });
    prismaMock.message.findMany.mockResolvedValue([]);
    prismaMock.message.create.mockResolvedValueOnce({ id: 2, sessionId: 'session-1', role: 'assistant', text: 'Mock reply' });

    const response = await request(app).post('/chat').send({ message: 'Hello' }).expect(200);

    expect(response.body.sessionId).toBeDefined();
    expect(response.body.analysis).toEqual(pipelineResponse);
  });

  it('returns history', async () => {
    const history = [
      { id: 1, sessionId: 'session-1', role: 'user', text: 'hi' },
    ];
    prismaMock.message.findMany.mockResolvedValue(history);

    const response = await request(app).get('/history').expect(200);
    expect(response.body).toHaveLength(1);
  });
});
