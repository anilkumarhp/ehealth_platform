import React from 'react';
import { useParams } from 'react-router-dom';

const SimpleDetailsPage = () => {
  const { type, id } = useParams();
  
  const handleBookClick = () => {
    console.log('Book button clicked');
    window.open('/simple-booking', '_self');
  };
  
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Details Page</h1>
      <p style={{ marginBottom: '20px' }}>Type: {type}, ID: {id}</p>
      
      <button
        onClick={handleBookClick}
        style={{
          padding: '10px 20px',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer'
        }}
      >
        Book Appointment
      </button>
      
      <div style={{ marginTop: '20px' }}>
        <a 
          href="/simple-booking"
          style={{
            display: 'inline-block',
            padding: '10px 20px',
            backgroundColor: '#10b981',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none'
          }}
        >
          Book Appointment (Link)
        </a>
      </div>
    </div>
  );
};

export default SimpleDetailsPage;