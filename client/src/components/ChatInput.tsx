import { FormEvent, useState } from 'react';

interface ChatInputProps {
  onSend: (text: string) => void;
  sending: boolean;
}

const ChatInput = ({ onSend, sending }: ChatInputProps) => {
  const [value, setValue] = useState('');

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!value.trim()) return;
    onSend(value.trim());
    setValue('');
  };

  return (
    <form className= flex w-full flex-col gap-2 onSubmit={handleSubmit}>
      <textarea
        className=h-24 w-full resize-none rounded-lg border border-slate-800 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 shadow-inner focus:border-blue-400 focus:outline-none
        placeholder=Ask about AI NLP or context-aware behaviors...
        value={value}
        onChange={(event) => setValue(event.target.value)}
        disabled={sending}
        aria-label=Your message
      />
      <div className=flex items-center justify-between gap-3>
        <span className=text-xs text-slate-400>Running advanced NLP pipeline...</span>
        <button
          type=submit
          className=rounded-full bg-gradient-to-r from-violet-500 to-blue-500 px-6 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60
          disabled={sending}
        >
          {sending ? 'Processing…' : 'Send'}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
