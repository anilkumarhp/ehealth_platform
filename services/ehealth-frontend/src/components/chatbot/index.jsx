import React from 'react';

const ChatbotWidget = ({ userId, userName }) => {
  return (
    <div style={{ 
      position: 'fixed', 
      bottom: '20px', 
      right: '20px', 
      zIndex: 1000 
    }}>
      <button style={{
        backgroundColor: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '24px',
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        cursor: 'pointer',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <span>💬</span>
        <span>Chat with Health Assistant</span>
      </button>
    </div>
  );
};

export default ChatbotWidget;