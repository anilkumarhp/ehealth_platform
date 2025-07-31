import React from 'react';

const DirectLink = () => {
  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1 style={{ marginBottom: '30px' }}>Direct Link Test</h1>
      
      <p style={{ marginBottom: '20px' }}>
        Click one of the links below to test navigation:
      </p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '300px', margin: '0 auto' }}>
        <a 
          href="/simple-booking" 
          style={{
            padding: '10px 20px',
            backgroundColor: '#3b82f6',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none'
          }}
        >
          Go to Booking Page
        </a>
        
        <a 
          href="/test" 
          style={{
            padding: '10px 20px',
            backgroundColor: '#10b981',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none'
          }}
        >
          Go to Test Page
        </a>
        
        <a 
          href="/patient-dashboard" 
          style={{
            padding: '10px 20px',
            backgroundColor: '#f59e0b',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none'
          }}
        >
          Go to Dashboard
        </a>
      </div>
    </div>
  );
};

export default DirectLink;