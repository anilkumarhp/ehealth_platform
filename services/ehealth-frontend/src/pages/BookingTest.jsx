import React from 'react';

const BookingTest = () => {
  const handleClick = () => {
    window.location.href = '/direct-booking';
  };

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1 style={{ marginBottom: '2rem' }}>Booking Test Page</h1>
      
      <p style={{ marginBottom: '2rem' }}>
        Click the button below to test navigation to the booking page
      </p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '300px', margin: '0 auto' }}>
        <button 
          onClick={handleClick}
          style={{
            padding: '1rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Go to Booking Page
        </button>
        
        <a 
          href="/direct-booking"
          style={{
            padding: '1rem',
            backgroundColor: '#10b981',
            color: 'white',
            borderRadius: '0.5rem',
            textDecoration: 'none',
            fontSize: '1rem'
          }}
        >
          Go to Booking (Link)
        </a>
        
        <a 
          href="/hospital-details"
          style={{
            padding: '1rem',
            backgroundColor: '#f59e0b',
            color: 'white',
            borderRadius: '0.5rem',
            textDecoration: 'none',
            fontSize: '1rem'
          }}
        >
          Go to Hospital Details
        </a>
      </div>
    </div>
  );
};

export default BookingTest;