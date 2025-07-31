import React, { createContext, useState, useContext, useEffect } from 'react';
import chatbotApi from '../api/chatbotApi';

// Create context
const ChatbotContext = createContext();

// Provider component
export const ChatbotProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Get user ID from localStorage
  const userInfo = JSON.parse(localStorage.getItem('user')) || {};
  const userId = userInfo.id || 'guest';
  
  // Load conversations for the user
  const loadConversations = async () => {
    if (userId === 'guest') return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Wrap in a try-catch to prevent unhandled promise rejections
      try {
        const data = await chatbotApi.getConversations(userId);
        setConversations(data);
      } catch (err) {
        console.error('Error loading conversations:', err);
        // Don't set error state for now to prevent blocking the UI
        setConversations([]);
      }
    } catch (err) {
      console.error('Unexpected error in loadConversations:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Load conversations when user ID changes
  useEffect(() => {
    if (userId !== 'guest') {
      loadConversations();
    }
  }, [userId]);
  
  // Context value
  const value = {
    conversations,
    loading,
    error,
    refreshConversations: loadConversations
  };
  
  return (
    <ChatbotContext.Provider value={value}>
      {children}
    </ChatbotContext.Provider>
  );
};

// Custom hook to use the chatbot context
export const useChatbot = () => {
  const context = useContext(ChatbotContext);
  if (context === undefined) {
    throw new Error('useChatbot must be used within a ChatbotProvider');
  }
  return context;
};

export default ChatbotContext;