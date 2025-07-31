import React from 'react';

const BookingButton = () => {
  const handleClick = () => {
    console.log('Booking button clicked');
    alert('Navigating to booking page...');
    setTimeout(() => {
      window.location.href = '/simple-booking';
    }, 500);
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
        cursor: 'pointer',
        fontSize: '16px'
      }}
    >
      Book Appointment
    </button>
  );
};

export default BookingButton;