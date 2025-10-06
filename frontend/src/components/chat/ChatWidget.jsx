import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Loader2, Minimize2 } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import useStore from '../../store/useStore';
import { chatAPI, sessionAPI } from '../../services/api';
import ChatMessage from './ChatMessage';

const ChatWidget = () => {
  const { 
    isChatOpen, 
    closeChat, 
    sessionId,  // Get sessionId
    setSessionId, // Get setter
    customerId,
    currentChannel 
  } = useStore();

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! 👋 I'm your AI shopping assistant. How can I help you today?",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize session
  useEffect(() => {
    if (isChatOpen && !sessionId) {
      console.log('Creating session...');
      sessionAPI.create(customerId, currentChannel)
        .then(response => {
          console.log('Session response:', response);
          if (response.success && response.session_id) {
            setSessionId(response.session_id); // Save sessionId as STRING
            console.log('Session created:', response.session_id);
          }
        })
        .catch(error => console.error('Failed to create session:', error));
    }
  }, [isChatOpen, sessionId, customerId, currentChannel, setSessionId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message mutation - FIXED
  const sendMessageMutation = useMutation({
    mutationFn: (message) => {
      console.log('=== MUTATION DEBUG ===');
      console.log('SessionID:', sessionId, 'Type:', typeof sessionId);
      console.log('Message:', message, 'Type:', typeof message);
      
      // CRITICAL: Pass sessionId and message as STRINGS
      return chatAPI.sendMessage(sessionId, message, currentChannel);
    },
    onSuccess: (data) => {
      console.log('AI response:', data);
      if (data.success || data.data || data.response) {
        const responseData = data.data || data;
        const aiMessage = {
          role: 'assistant',
          content: responseData.message || responseData.response || 'Got it!',
          recommendations: responseData.product_cards || responseData.recommendations,
          suggestions: responseData.quick_replies || responseData.suggestions,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      console.error('Error response:', error.response?.data);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date().toISOString(),
      }]);
    },
  });

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage) return;
    
    if (!sessionId) {
      alert('Connecting... Please wait.');
      return;
    }

    // Add user message
    const userMessage = {
      role: 'user',
      content: trimmedMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Send to API - pass message string directly
    sendMessageMutation.mutate(trimmedMessage);
    setInputMessage('');
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
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
              <h3 className="font-semibold">AI Assistant</h3>
              <p className="text-xs opacity-90">
                {sessionId ? 'Online' : 'Connecting...'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 hover:bg-white/20 rounded transition-colors"
            >
              <Minimize2 size={20} />
            </button>
            <button
              onClick={closeChat}
              className="p-1 hover:bg-white/20 rounded transition-colors"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, index) => (
                <ChatMessage 
                  key={index} 
                  message={message} 
                  onSuggestionClick={handleSuggestionClick}
                />
              ))}
              
              {sendMessageMutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 p-3 rounded-2xl flex items-center space-x-2">
                    <Loader2 className="animate-spin" size={16} />
                    <span className="text-sm">Thinking...</span>
                  </div>
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
                  placeholder={sessionId ? "Type your message..." : "Connecting..."}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={sendMessageMutation.isPending || !sessionId}
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || sendMessageMutation.isPending || !sessionId}
                  className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white p-2 rounded-full hover:shadow-lg transition-all disabled:opacity-50"
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