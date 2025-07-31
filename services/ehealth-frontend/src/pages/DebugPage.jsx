import React, { useEffect } from 'react';
import DebugButton from './DebugButton';

const DebugPage = () => {
  useEffect(() => {
    console.log('DebugPage mounted');
    console.log('Current URL:', window.location.href);
    console.log('Browser info:', navigator.userAgent);
    
    // Check if navigation is working
    const testNavigation = () => {
      try {
        console.log('Testing history API...');
        window.history.pushState({}, '', '/test-url');
        console.log('New URL:', window.location.href);
        window.history.back();
      } catch (error) {
        console.error('History API error:', error);
      }
    };
    
    testNavigation();
    
    return () => {
      console.log('DebugPage unmounting');
    };
  }, []);
  
  const handleFormSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted');
    window.location.href = '/simple-booking';
  };
  
  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Navigation Debug Page</h1>
      
      <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f3f4f6', borderRadius: '8px' }}>
        <h2 style={{ marginBottom: '10px' }}>Debug Info</h2>
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {`Current URL: ${window.location.href}
User Agent: ${navigator.userAgent}
Platform: ${navigator.platform}
React Version: ${React.version}`}
        </pre>
      </div>
      
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ marginBottom: '10px' }}>Debug Buttons</h2>
        <DebugButton />
      </div>
      
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ marginBottom: '10px' }}>Form Navigation</h2>
        <form onSubmit={handleFormSubmit}>
          <button 
            type="submit"
            style={{
              padding: '10px 20px',
              backgroundColor: '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Submit Form Navigation
          </button>
        </form>
      </div>
      
      <div>
        <h2 style={{ marginBottom: '10px' }}>JavaScript Navigation</h2>
        <button 
          onClick={() => {
            console.log('JS navigation button clicked');
            document.location.href = '/simple-booking';
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            marginRight: '10px'
          }}
        >
          document.location
        </button>
        
        <button 
          onClick={() => {
            console.log('JS navigation button clicked (assign)');
            window.location.assign('/simple-booking');
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: '#f59e0b',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          location.assign
        </button>
      </div>
    </div>
  );
};

export default DebugPage;