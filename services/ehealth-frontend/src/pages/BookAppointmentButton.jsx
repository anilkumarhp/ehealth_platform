import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, ShoppingBag } from 'lucide-react';

const BookAppointmentButton = ({ entity }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    console.log('Button clicked, entity type:', entity.type, 'entity id:', entity.id);
    
    if (entity.type === 'hospital') {
      console.log('Navigating to:', `/book-appointment/${entity.id}`);
      navigate(`/book-appointment/${entity.id}`);
    } else if (entity.type === 'doctor') {
      alert('Doctor appointment booking will be available soon!');
    } else if (entity.type === 'pharmacy') {
      alert('Medicine ordering will be available soon!');
    } else if (entity.type === 'lab') {
      alert('Lab test booking will be available soon!');
    }
  };
  
  return (
    <button 
      onClick={handleClick}
      style={{
        width: '100%',
        padding: '0.75rem 1rem',
        backgroundColor: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        marginBottom: '1.5rem'
      }}
    >
      {entity.type === 'hospital' || entity.type === 'doctor' ? <Calendar className="w-5 h-5" /> : 
       entity.type === 'pharmacy' ? <ShoppingBag className="w-5 h-5" /> : <Calendar className="w-5 h-5" />}
      {entity.type === 'hospital' || entity.type === 'doctor' ? 'Book Appointment' : 
       entity.type === 'pharmacy' ? 'Order Medicines' : 'Book Test'}
    </button>
  );
};

export default BookAppointmentButton;