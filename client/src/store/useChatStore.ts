import { create } from 'zustand';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  createdAt?: string;
  analysis?: Record<string, unknown>;
}

interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  appendMessage: (message: ChatMessage) => void;
  setSessionId: (sessionId: string) => void;
  reset: () => void;
}

const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessionId: null,
  appendMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  setSessionId: (sessionId) => set({ sessionId }),
  reset: () => set({ messages: [], sessionId: null }),
}));

export default useChatStore;
