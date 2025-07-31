import React from 'react';
import { useNavigate } from 'react-router-dom';

const TestBookingButton = () => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    console.log('Test button clicked');
    navigate('/book-appointment/4');
  };
  
  return (
    <button 
      onClick={handleClick}
      style={{
        padding: '0.75rem 1.5rem',
        backgroundColor: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer'
      }}
    >
      Test Booking Navigation
    </button>
  );
};

export default TestBookingButton;