import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import useStore from '../store/useStore';
import { chatAPI, sessionAPI } from '../services/api';
import ChatMessage from '../components/chat/ChatMessage';
import Button from '../components/common/Button';

const ChatPage = () => {
  const { sessionId, setSession, customerId, currentChannel } = useStore();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your AI shopping assistant. I can help you find products, check availability, answer questions, and complete your purchase. What are you looking for today?",
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
          if (response.success) {
            setSession(response.session_id, response.channel);
          }
        })
        .catch(error => console.error('Failed to create session:', error));
    }
  }, [sessionId, customerId, currentChannel, setSession]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message
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
  });

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !sessionId) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    sendMessageMutation.mutate(inputMessage);
    setInputMessage('');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 h-[calc(100vh-64px)]">
      <div className="bg-white rounded-xl shadow-lg h-full flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white p-6 rounded-t-xl">
          <h1 className="text-2xl font-bold">AI Shopping Assistant</h1>
          <p className="text-sm opacity-90">Ask me anything about products, availability, or orders</p>
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
              placeholder="Type your message..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={sendMessageMutation.isPending}
            />
            <Button
              type="submit"
              disabled={!inputMessage.trim() || sendMessageMutation.isPending}
              className="px-6"
            >
              <Send size={20} />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;