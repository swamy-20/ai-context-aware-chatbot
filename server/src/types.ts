export type Role = 'user' | 'assistant' | 'system';

export interface SessionMessage {
  id?: number;
  sessionId: string;
  role: Role;
  text: string;
  analysis?: Record<string, unknown>;
  createdAt?: string;
}
