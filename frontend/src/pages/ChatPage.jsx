import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import useStore from '../store/useStore';
import { chatAPI, sessionAPI } from '../services/api';
import ChatMessage from '../components/chat/ChatMessage';
import Button from '../components/common/Button';
import { motion } from 'framer-motion';

const ChatPage = () => {
  const { sessionId, setSessionId, customerId, currentChannel } = useStore();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your AI shopping assistant. How can I help you today?",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  // Initialize session
  useEffect(() => {
    if (!sessionId) {
      sessionAPI.create(customerId, currentChannel)
        .then(response => {
          if (response.success && response.session_id) {
            setSessionId(response.session_id);
          }
        })
        .catch(error => console.error('Failed to create session:', error));
    }
  }, [sessionId, customerId, currentChannel, setSessionId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message - FIXED
  const sendMessageMutation = useMutation({
    mutationFn: (message) => {
      return chatAPI.sendMessage(sessionId, message, currentChannel);
    },
    onSuccess: (data) => {
      console.log('Response:', data);
      if (data.success || data.data || data.response) {
        const responseData = data.data || data;
        const aiMessage = {
          role: 'assistant',
          content: responseData.message || responseData.response || 'Received!',
          recommendations: responseData.product_cards || responseData.recommendations,
          suggestions: responseData.quick_replies || responseData.suggestions,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    },
    onError: (error) => {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Error connecting. Please try again.",
        timestamp: new Date().toISOString(),
      }]);
    },
  });

  const handleSendMessage = (e) => {
    e.preventDefault();
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage || !sessionId) return;

    const userMessage = {
      role: 'user',
      content: trimmedMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    sendMessageMutation.mutate(trimmedMessage);
    setInputMessage('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-4xl mx-auto px-4 py-8 h-[calc(100vh-64px)]"
    >
      <div className="bg-white rounded-xl shadow-lg h-full flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white p-6 rounded-t-xl">
          <h1 className="text-2xl font-bold">AI Shopping Assistant</h1>
          <p className="text-sm opacity-90">
            {sessionId ? 'Connected' : 'Connecting...'}
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          
          {sendMessageMutation.isPending && (
            <div className="flex items-center space-x-2 text-gray-500">
              <Loader2 className="animate-spin" size={20} />
              <span>AI is thinking...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 border-t">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={sessionId ? "Type your message..." : "Connecting..."}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={sendMessageMutation.isPending || !sessionId}
            />
            <Button
              type="submit"
              disabled={!inputMessage.trim() || sendMessageMutation.isPending || !sessionId}
              className="px-6"
            >
              <Send size={20} />
            </Button>
          </form>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatPage;