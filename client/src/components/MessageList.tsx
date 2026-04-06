import useChatStore from '../store/useChatStore';

const MessageList = () => {
  const messages = useChatStore((state) => state.messages);

  if (!messages.length) {
    return (
      <div className= rounded-2xl border border-dashed border-slate-800/70 bg-slate-900/30 p-6 text-center text-sm text-slate-400>
        Conversations appear here as soon as you send a request.
      </div>
    );
  }

  return (
    <div className=flex flex-col gap-4>
      {messages.map((message) => {
        const summary = (message.analysis as { contextSummary?: string })?.contextSummary;
        return (
          <article
            key={message.id}
            className={ounded-2xl border border-slate-800/70 bg-slate-900/60 p-4 shadow-lg }
          >
            <header className=flex items-center justify-between text-xs uppercase tracking-wide text-slate-400>
              <span>{message.role === 'user' ? 'You' : 'Bot'}</span>
              <span>{message.createdAt ? new Date(message.createdAt).toLocaleTimeString() : ''}</span>
            </header>
            <p className=mt-2 text-sm leading-6 text-slate-100>{message.text}</p>
            {summary && <p className=mt-3 text-xs text-slate-400>Context: {summary}</p>}
          </article>
        );
      })}
    </div>
  );
};

export default MessageList;
