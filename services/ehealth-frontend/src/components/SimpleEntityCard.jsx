import React from 'react';

const SimpleEntityCard = ({ entity }) => {
  const handleBookClick = () => {
    console.log('Book button clicked');
    window.open('/simple-booking', '_self');
  };

  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '15px',
      marginBottom: '15px'
    }}>
      <h3 style={{ marginBottom: '10px' }}>{entity.name}</h3>
      <p style={{ marginBottom: '10px' }}>{entity.address}</p>
      
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
    </div>
  );
};

export default SimpleEntityCard;