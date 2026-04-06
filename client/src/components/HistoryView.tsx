import { useEffect, useState } from 'react';
import { fetchHistory, type ChatHistoryEntry } from '../services/api';

const HistoryView = () => {
  const [history, setHistory] = useState<ChatHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchHistory()
      .then((records) => setHistory(records))
      .catch((error) => console.error('History fetch failed', error))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className= text-sm text-slate-400>Loading history…</p>;
  }

  if (!history.length) {
    return <p className=text-sm text-slate-400>No conversations saved yet.</p>;
  }

  return (
    <div className=flex flex-col gap-4>
      {history.map((entry) => (
        <article key={${entry.id}-} className=rounded-2xl border border-slate-800 bg-slate-900/60 p-4>
          <p className=text-xs uppercase tracking-widest text-slate-500>{entry.role}</p>
          <p className=mt-1 text-sm text-slate-100>{entry.text}</p>
          {entry.createdAt && <p className=mt-1 text-xs text-slate-500>{new Date(entry.createdAt).toLocaleString()}</p>}
        </article>
      ))}
    </div>
  );
};

export default HistoryView;
