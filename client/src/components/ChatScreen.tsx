import { useState } from 'react';
import { sendChatMessage } from '../services/api';
import ChatInput from './ChatInput';
import MessageList from './MessageList';
import useChatStore from '../store/useChatStore';

const generateId = () => {
    if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
        return crypto.randomUUID();
    }
    return msg--;
};

const ChatScreen = () => {
    const [sending, setSending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { appendMessage, sessionId, setSessionId } = useChatStore((state) => ({
        appendMessage: state.appendMessage,
        sessionId: state.sessionId,
        setSessionId: state.setSessionId,
    }));

    const handleSend = async (text: string) => {
        const id = generateId();
        appendMessage({ id, role: 'user', text, createdAt: new Date().toISOString() });
        setSending(true);
        setError(null);

        try {
            const response = await sendChatMessage({ message: text, sessionId });
            setSessionId(response.sessionId);
            appendMessage({
                id: ot-,
                role: 'assistant',
                text: response.message.text,
                createdAt: response.message.createdAt,
                analysis: response.analysis,
            });
        } catch (err) {
            console.error(err);
            setError('Unable to reach the NLP service. Try again later.');
        } finally {
            setSending(false);
        }
    };

    return (
        <section className= flex flex-col gap-4>
            {error && (
                <div className=rounded-lg border border-rose-500/50 bg-rose-900/80 px-4 py-3 text-sm text-rose-200>
                    {error}
                </div>
            )}
            <MessageList />
            <ChatInput onSend={handleSend} sending={sending} />
        </section>
    );
};

export default ChatScreen;
