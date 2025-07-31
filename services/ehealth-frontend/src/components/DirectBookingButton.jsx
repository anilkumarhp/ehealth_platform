import React from 'react';
import { Calendar } from 'lucide-react';

const DirectBookingButton = ({ entityName, entityType }) => {
  const handleClick = (e) => {
    e.preventDefault();
    console.log('Direct booking button clicked');
    console.log('Entity:', entityName);
    console.log('Type:', entityType);
    
    // Try multiple navigation methods
    try {
      console.log('Using window.location.href');
      window.location.href = '/simple-booking';
    } catch (error) {
      console.error('Navigation error with window.location.href:', error);
      
      try {
        console.log('Trying window.location.assign');
        window.location.assign('/simple-booking');
      } catch (error2) {
        console.error('Navigation error with window.location.assign:', error2);
        
        try {
          console.log('Trying document.location.href');
          document.location.href = '/simple-booking';
        } catch (error3) {
          console.error('All navigation methods failed:', error3);
          alert('Navigation failed. Please try clicking the link below.');
        }
      }
    }
  };
  
  return (
    <div>
      <button 
        onClick={handleClick}
        style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          fontWeight: '600',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '10px'
        }}
      >
        <Calendar className="w-4 h-4" />
        Book Appointment
      </button>
      
      <a 
        href="/simple-booking"
        style={{
          display: 'inline-block',
          padding: '0.75rem 1.5rem',
          backgroundColor: '#10b981',
          color: 'white',
          borderRadius: '0.5rem',
          textDecoration: 'none',
          fontWeight: '600',
          textAlign: 'center'
        }}
      >
        Book Appointment (Link)
      </a>
    </div>
  );
};

export default DirectBookingButton;