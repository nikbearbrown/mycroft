import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, ExternalLink } from 'lucide-react';
import { chatAPI } from '../api/client';

export default function ChatInterface({ selectedIds }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || selectedIds.length === 0 || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.ask(input, selectedIds);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: 'Failed to get response: ' + error.message,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    "Summarize the key regulatory changes",
    "What are the crypto enforcement actions?",
    "Are there any upcoming compliance deadlines?",
    "Compare the urgency levels across sources",
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col h-[600px]">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">Ask Questions</h2>
        <p className="text-sm text-gray-600">
          {selectedIds.length > 0
            ? `Using ${selectedIds.length} selected feed${selectedIds.length > 1 ? 's' : ''} as context`
            : 'Select feeds from the list to start asking questions'}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No messages yet. Try asking:</p>
            <div className="space-y-2">
              {suggestedQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => setInput(q)}
                  disabled={selectedIds.length === 0}
                  className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  "{q}"
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            selectedIds.length === 0
              ? "Select feeds first..."
              : "Ask a question about selected feeds..."
          }
          disabled={selectedIds.length === 0 || loading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={!input.trim() || selectedIds.length === 0 || loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}

function Message({ message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-indigo-600 text-white px-4 py-2 rounded-lg max-w-[80%]">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  if (message.role === 'error') {
    return (
      <div className="flex justify-start">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg max-w-[80%]">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="bg-gray-100 px-4 py-3 rounded-lg max-w-[80%]">
        <p className="text-sm text-gray-900 whitespace-pre-wrap mb-2">
          {message.content}
        </p>
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-600 font-semibold mb-2">Sources:</p>
            <div className="space-y-1">
              {message.sources.map((source, i) => (
                <a
                  key={i}
                  href={source.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-2 text-xs text-indigo-600 hover:text-indigo-800"
                >
                  <ExternalLink className="w-3 h-3 mt-0.5 flex-shrink-0" />
                  <span className="line-clamp-2">{source.title}</span>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}