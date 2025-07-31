import React, { useState } from 'react';

const ChatbotWidget = ({ userId, userName }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Add welcome message when chat is opened
  const handleOpenChat = () => {
    setIsOpen(true);
    if (messages.length === 0) {
      setMessages([
        {
          sender: 'bot',
          text: `Hello${userName ? ' ' + userName : ''}! I can help you find doctors, hospitals, labs, or pharmacies. What are you looking for today?`
        }
      ]);
    }
  };

  const handleSendMessage = () => {
    if (!input.trim()) return;
    
    // Add user message
    setMessages([...messages, { sender: 'user', text: input }]);
    
    // Simulate bot response
    setTimeout(() => {
      setMessages(prev => [
        ...prev, 
        { 
          sender: 'bot', 
          text: `I understand you're looking for "${input}". How can I help you with that?`
        }
      ]);
    }, 1000);
    
    setInput('');
  };

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <div 
          onClick={handleOpenChat}
          style={{ 
            position: 'fixed', 
            bottom: '20px', 
            right: '20px', 
            backgroundColor: '#3b82f6', 
            color: 'white',
            padding: '12px 20px',
            borderRadius: '24px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 1000
          }}
        >
          <span>💬</span>
          <span>Chat with Health Assistant</span>
        </div>
      )}
      
      {/* Chat Window */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '350px',
          height: '500px',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          zIndex: 1000
        }}>
          {/* Chat Header */}
          <div style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '12px 16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>eHealth Assistant</h3>
            <button 
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '20px',
                cursor: 'pointer',
                padding: 0,
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              ×
            </button>
          </div>
          
          {/* Messages */}
          <div style={{
            flex: 1,
            padding: '16px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            {messages.map((message, index) => (
              <div 
                key={index} 
                style={{
                  maxWidth: '80%',
                  padding: '10px 14px',
                  borderRadius: '16px',
                  alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  backgroundColor: message.sender === 'user' ? '#3b82f6' : '#f3f4f6',
                  color: message.sender === 'user' ? 'white' : '#1f2937',
                  borderBottomRightRadius: message.sender === 'user' ? '4px' : '16px',
                  borderBottomLeftRadius: message.sender === 'user' ? '16px' : '4px'
                }}
              >
                {message.text}
              </div>
            ))}
          </div>
          
          {/* Input */}
          <div style={{
            display: 'flex',
            padding: '12px',
            borderTop: '1px solid #e5e7eb',
            backgroundColor: 'white'
          }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              style={{
                flex: 1,
                border: '1px solid #d1d5db',
                borderRadius: '24px',
                padding: '8px 16px',
                fontSize: '14px',
                outline: 'none'
              }}
            />
            <button 
              onClick={handleSendMessage} 
              disabled={!input.trim()}
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: input.trim() ? '#3b82f6' : '#d1d5db',
                color: 'white',
                border: 'none',
                marginLeft: '8px',
                cursor: input.trim() ? 'pointer' : 'not-allowed',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px'
              }}
            >
              →
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotWidget;