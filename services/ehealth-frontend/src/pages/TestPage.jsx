import React from 'react';
import BookingButton from './BookingButton';

const TestPage = () => {
  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1 style={{ marginBottom: '30px' }}>Test Booking Navigation</h1>
      
      <div style={{ marginBottom: '30px' }}>
        <p>Click the button below to test booking navigation:</p>
      </div>
      
      <BookingButton />
      
      <div style={{ marginTop: '30px' }}>
        <a 
          href="/simple-booking" 
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
          Book Appointment (HTML Link)
        </a>
      </div>
    </div>
  );
};

export default TestPage;