import { useState } from 'react';
import { CheckSquare, Square, ExternalLink, Calendar, Tag } from 'lucide-react';

export default function FeedList({ feeds, selected, onToggle, onSelectAll, onClearAll }) {
  const [filters, setFilters] = useState({
    source: '',
    minUrgency: '',
    search: '',
  });

  const filteredFeeds = feeds.filter(feed => {
    if (filters.source && feed.source_feed !== filters.source) return false;
    if (filters.minUrgency && feed.urgency_score < parseInt(filters.minUrgency)) return false;
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      return feed.title.toLowerCase().includes(searchLower) ||
             feed.content?.toLowerCase().includes(searchLower);
    }
    return true;
  });

  const sources = [...new Set(feeds.map(f => f.source_feed))];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">
          Regulatory Feeds
          <span className="text-sm text-gray-500 ml-2">
            ({filteredFeeds.length} items)
          </span>
        </h2>
        <div className="flex gap-2">
          <button
            onClick={onSelectAll}
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Select All
          </button>
          <span className="text-gray-300">|</span>
          <button
            onClick={onClearAll}
            className="text-sm text-gray-600 hover:text-gray-800 font-medium"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <input
          type="text"
          placeholder="Search title/content..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <select
          value={filters.source}
          onChange={(e) => setFilters({ ...filters, source: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">All Sources</option>
          {sources.map(source => (
            <option key={source} value={source}>{source}</option>
          ))}
        </select>
        <select
          value={filters.minUrgency}
          onChange={(e) => setFilters({ ...filters, minUrgency: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">All Urgencies</option>
          <option value="8">8+ (Critical)</option>
          <option value="6">6+ (High)</option>
          <option value="4">4+ (Medium)</option>
        </select>
      </div>

      {/* Feed List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredFeeds.map(feed => (
          <FeedItem
            key={feed.id}
            feed={feed}
            isSelected={selected.has(feed.id)}
            onToggle={() => onToggle(feed.id)}
          />
        ))}
        {filteredFeeds.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No feeds match your filters
          </div>
        )}
      </div>
    </div>
  );
}

function FeedItem({ feed, isSelected, onToggle }) {
  const urgencyColor = feed.urgency_score >= 8 ? 'text-red-600' :
                       feed.urgency_score >= 6 ? 'text-orange-600' :
                       feed.urgency_score >= 4 ? 'text-yellow-600' :
                       'text-green-600';

  return (
    <div
      onClick={onToggle}
      className={`border rounded-lg p-4 cursor-pointer transition ${
        isSelected
          ? 'border-indigo-500 bg-indigo-50'
          : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-1">
          {isSelected ? (
            <CheckSquare className="w-5 h-5 text-indigo-600" />
          ) : (
            <Square className="w-5 h-5 text-gray-400" />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
            {feed.title}
          </h3>
          
          <div className="flex flex-wrap items-center gap-2 text-xs text-gray-600 mb-2">
            <span className="flex items-center gap-1">
              <Tag className="w-3 h-3" />
              {feed.source_feed}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {new Date(feed.published).toLocaleDateString()}
            </span>
            <span className={`font-semibold ${urgencyColor}`}>
              ⚡ {feed.urgency_score}/10
            </span>
            {feed.impact_level && (
              <span className="bg-gray-200 px-2 py-0.5 rounded">
                {feed.impact_level}
              </span>
            )}
          </div>

          {feed.categories && feed.categories.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {feed.categories.map(cat => (
                <span
                  key={cat}
                  className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded"
                >
                  {cat}
                </span>
              ))}
            </div>
          )}

          {feed.content && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
              {feed.content.substring(0, 150)}...
            </p>
          )}

          <a
            href={feed.link}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
          >
            View Full Document
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
}