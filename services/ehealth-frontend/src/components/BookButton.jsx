import React from 'react';

const BookButton = () => {
  const handleClick = () => {
    console.log('Book button clicked');
    window.open('/simple-booking', '_self');
  };
  
  return (
    <button
      onClick={handleClick}
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
  );
};

export default BookButton;