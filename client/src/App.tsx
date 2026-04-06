import { Link, Navigate, Route, Routes } from 'react-router-dom';
import ChatScreen from './components/ChatScreen';
import HistoryView from './components/HistoryView';

const App = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-4xl px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-semibold">Context-Aware NLP Chatbot</h1>
          <nav className="flex gap-4 text-sm font-medium text-slate-300">
            <Link className="transition hover:text-white" to="/">Chat</Link>
            <Link className="transition hover:text-white" to="/history">History</Link>
          </nav>
        </header>
        <main className="mt-6">
          <Routes>
            <Route path="/" element={<ChatScreen />} />
            <Route path="/history" element={<HistoryView />} />
            <Route path="*" element={<Navigate replace to="/" />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default App;
