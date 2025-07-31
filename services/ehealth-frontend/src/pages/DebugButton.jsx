import React from 'react';

const DebugButton = () => {
  const handleClick = (e) => {
    console.log('Button clicked');
    console.log('Event:', e);
    console.log('Current URL:', window.location.href);
    console.log('Attempting navigation...');
    
    try {
      console.log('Using window.location.href');
      window.location.href = '/simple-booking';
      console.log('Navigation command executed');
    } catch (error) {
      console.error('Navigation error:', error);
    }
  };
  
  return (
    <div>
      <button 
        onClick={handleClick}
        style={{
          padding: '10px 20px',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '16px',
          marginBottom: '20px'
        }}
      >
        Debug Button (window.location)
      </button>
      
      <div>
        <a 
          href="/simple-booking"
          onClick={(e) => console.log('Link clicked')}
          style={{
            display: 'inline-block',
            padding: '10px 20px',
            backgroundColor: '#10b981',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '16px'
          }}
        >
          Debug Link (href)
        </a>
      </div>
    </div>
  );
};

export default DebugButton;