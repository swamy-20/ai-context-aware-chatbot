import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:4000',
  timeout: 30000,
});

export interface ChatPayload {
  message: string;
  sessionId?: string | null;
}

export interface ChatHistoryEntry {
  id: number;
  sessionId: string;
  role: 'user' | 'assistant' | 'system';
  text: string;
  createdAt?: string;
  analysis?: Record<string, unknown>;
}

export interface ChatResponse {
  sessionId: string;
  message: ChatHistoryEntry;
  analysis: Record<string, unknown>;
}

export const sendChatMessage = async (payload: ChatPayload): Promise<ChatResponse> => {
  const response = await apiClient.post('/chat', payload);
  return response.data;
};

export const fetchHistory = async (): Promise<ChatHistoryEntry[]> => {
  const response = await apiClient.get('/history');
  return response.data;
};
