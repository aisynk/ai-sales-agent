import { useTypewriter } from '../../hooks/useTypewriter';
import { Clock } from 'lucide-react';
import ProductCard from '../products/ProductCard';

const ChatMessage = ({ message, onSuggestionClick, isLatest = false }) => {
  const isUser = message.role === 'user';
  
  // Only apply typing effect to the latest AI message
  const shouldAnimate = !isUser && isLatest;
  const { displayText, isComplete } = useTypewriter(
    shouldAnimate ? message.content : null,
    20
  );

  const content = shouldAnimate ? displayText : message.content;
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* ... existing avatar code ... */}
        {!isUser && (
          <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white mb-2">
            🤖
          </div>
        )}
        
        {/* Message bubble */}
        <div
          className={`
            p-3 rounded-2xl
            ${isUser
              ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-tr-none'
              : 'bg-gray-100 text-gray-800 rounded-tl-none'
            }
          `}
        >
          <p className="whitespace-pre-wrap">
            {content}
            {shouldAnimate && !isComplete && (
              <span className="animate-pulse">▊</span>
            )}
          </p>
        </div>

        {/* Only show recommendations/suggestions when typing is complete */}
        {(isComplete || !shouldAnimate) && (
          <>
            {/* Product recommendations */}
            {message.recommendations && message.recommendations.length > 0 && (
              <div className="mt-3 space-y-2">
                {message.recommendations.slice(0, 3).map((product, index) => (
                  <ProductCard key={index} product={product} compact />
                ))}
              </div>
            )}

            {/* Quick reply suggestions */}
            {message.suggestions && message.suggestions.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {message.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => onSuggestionClick && onSuggestionClick(suggestion.text || suggestion)}
                    className="px-3 py-1 bg-white border border-gray-300 rounded-full text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    {suggestion.text || suggestion}
                  </button>
                ))}
              </div>
            )}
          </>
        )}

        {/* Timestamp */}
        <div className={`text-xs mt-1 ${isUser ? 'text-right' : 'text-left'} text-gray-400`}>
          {new Date(message.timestamp).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;