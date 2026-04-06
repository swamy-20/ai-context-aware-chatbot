import axios from 'axios';
import { SessionMessage } from '../types';

const nlpBaseUrl = process.env.NLP_SERVICE_URL ?? 'http://localhost:8000/process';

const nlpClient = axios.create({
  baseURL: nlpBaseUrl,
  timeout: 120000,
});

export interface NlpPayload {
  message: string;
  context: { text: string; role: SessionMessage['role'] }[];
}

export interface NlpResponse {
  reply: string;
  tokens: string[];
  lemmas: string[];
  entities: { text: string; label: string }[];
  dependencies: { text: string; dep: string; head: string }[];
  wsd: Record<string, string | null>;
  coreferences: string[];
  embeddings: Record<string, number[]>;
  ngrams: Record<string, number>;
  contextSummary: string;
}

export async function callNlpService(payload: NlpPayload): Promise<NlpResponse> {
  const response = await nlpClient.post('', payload);
  return response.data;
}
