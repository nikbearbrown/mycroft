import { useState, useEffect } from 'react';
import Header from './components/Header';
import Stats from './components/Stats';
import FeedList from './components/FeedList';
import ChatInterface from './components/ChatInterface';
import { feedsAPI } from './api/client';

function App() {
  const [feeds, setFeeds] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState(new Set());
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [feedsData, statsData] = await Promise.all([
        feedsAPI.listFeeds({ limit: 100 }),
        feedsAPI.getStats(),
      ]);
      setFeeds(feedsData.feeds);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
      alert('Failed to load feeds. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggle = (id) => {
    setSelected(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    setSelected(new Set(feeds.map(f => f.id)));
  };

  const handleClearAll = () => {
    setSelected(new Set());
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading feeds...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onRefresh={loadData} />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Stats stats={stats} selectedCount={selected.size} />
        
        <div className="grid lg:grid-cols-2 gap-6">
          <FeedList
            feeds={feeds}
            selected={selected}
            onToggle={handleToggle}
            onSelectAll={handleSelectAll}
            onClearAll={handleClearAll}
          />
          
          <ChatInterface selectedIds={Array.from(selected)} />
        </div>
      </main>
    </div>
  );
}

export default App;