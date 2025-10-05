import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Loader2, Minimize2 } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import useStore from '../../store/useStore';
import { chatAPI, sessionAPI } from '../../services/api';
import ChatMessage from './ChatMessage';
import ProductCard from '../products/ProductCard';

const ChatWidget = () => {
  const { 
    isChatOpen, 
    closeChat, 
    sessionId, 
    setSession, 
    customerId,
    currentChannel 
  } = useStore();

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! 👋 I'm your AI shopping assistant. I can help you find products, check availability, and complete your purchase. What are you looking for today?",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize session
  useEffect(() => {
    if (isChatOpen && !sessionId) {
      sessionAPI.create(customerId, currentChannel)
        .then(response => {
          if (response.success) {
            setSession(response.session_id, response.channel);
          }
        })
        .catch(error => console.error('Failed to create session:', error));
    }
  }, [isChatOpen, sessionId, customerId, currentChannel, setSession]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message) => chatAPI.sendMessage({
      message,
      channel: currentChannel,
      customer_id: customerId,
      session_id: sessionId,
    }),
    onSuccess: (data) => {
      if (data.success) {
        const aiMessage = {
          role: 'assistant',
          content: data.data.message,
          recommendations: data.data.product_cards || data.data.recommendations,
          suggestions: data.data.quick_replies || data.data.suggestions,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date().toISOString(),
      }]);
    },
  });

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !sessionId) return;

    // Add user message
    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Send to API
    sendMessageMutation.mutate(inputMessage);
    setInputMessage('');
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    handleSendMessage({ preventDefault: () => {} });
  };

  if (!isChatOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div 
        className={`
          bg-white rounded-2xl shadow-2xl flex flex-col
          transition-all duration-300
          ${isMinimized ? 'h-16 w-80' : 'h-[600px] w-96'}
        `}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white p-4 rounded-t-2xl flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-2xl">
              🤖
            </div>
            <div>
              <h3 className="font-semibold">AI Sales Assistant</h3>
              <p className="text-xs opacity-90">Online • Instant replies</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Minimize"
            >
              <Minimize2 size={20} />
            </button>
            <button
              onClick={closeChat}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Messages */}
        {!isMinimized && (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              
              {/* Loading indicator */}
              {sendMessageMutation.isPending && (
                <div className="flex items-center space-x-2 text-gray-500">
                  <Loader2 className="animate-spin" size={16} />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t">
              <form onSubmit={handleSendMessage} className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={sendMessageMutation.isPending}
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || sendMessageMutation.isPending}
                  className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white p-2 rounded-full hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Send message"
                >
                  <Send size={20} />
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ChatWidget;