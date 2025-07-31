import React from 'react';

const ConversationHistory = () => {
  return (
    <div style={{ 
      backgroundColor: 'white', 
      borderRadius: '8px', 
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', 
      padding: '20px', 
      marginBottom: '20px' 
    }}>
      <h3 style={{ 
        fontSize: '18px', 
        marginTop: 0, 
        marginBottom: '16px', 
        color: '#111827', 
        borderBottom: '1px solid #e5e7eb', 
        paddingBottom: '10px' 
      }}>
        Your Conversations
      </h3>
      <div style={{ textAlign: 'center', color: '#6b7280', padding: '20px' }}>
        No conversation history found.
        <p>Start a chat with the health assistant to get help.</p>
      </div>
    </div>
  );
};

export default ConversationHistory;