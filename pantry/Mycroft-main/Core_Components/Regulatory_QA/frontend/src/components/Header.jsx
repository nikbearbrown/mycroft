import { RefreshCw, Database } from 'lucide-react';
import { useState } from 'react';
import { feedsAPI } from '../api/client';

export default function Header({ onRefresh }) {
  const [fetching, setFetching] = useState(false);

  const handleFetch = async () => {
    setFetching(true);
    try {
      await feedsAPI.triggerFetch();
      alert('✅ Feed fetch triggered! New data will appear in ~30 seconds.');
      setTimeout(() => {
        onRefresh();
      }, 3000);
    } catch (error) {
      alert('❌ Failed to trigger feed fetch: ' + error.message);
    } finally {
      setFetching(false);
    }
  };

  return (
    <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold">Mycroft Intelligence</h1>
              <p className="text-indigo-100 text-sm">Regulatory QA System</p>
            </div>
          </div>
          
          <button
            onClick={handleFetch}
            disabled={fetching}
            className="flex items-center gap-2 bg-white text-indigo-600 px-4 py-2 rounded-lg font-semibold hover:bg-indigo-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${fetching ? 'animate-spin' : ''}`} />
            {fetching ? 'Fetching...' : 'Fetch New Feeds'}
          </button>
        </div>
      </div>
    </header>
  );
}