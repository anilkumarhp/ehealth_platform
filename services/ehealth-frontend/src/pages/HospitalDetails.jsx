import React from 'react';

const HospitalDetails = () => {
  const hospital = {
    name: 'Apollo Hospital',
    description: 'Apollo Hospital is a leading multi-specialty hospital providing comprehensive healthcare services with state-of-the-art facilities and experienced medical professionals.',
    hours: '24/7 Emergency Services',
    rating: 4.7,
    address: '21 Greams Lane, Off Greams Road, Chennai',
    phone: '+91 44 2829 3333',
    email: 'info@apollohospital.com'
  };

  const handleBookAppointment = () => {
    window.location.href = '/direct-booking';
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>{hospital.name}</h1>
      <p style={{ marginBottom: '2rem' }}>{hospital.description}</p>
      
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Details</h2>
        <div style={{ marginBottom: '0.5rem' }}><strong>Hours:</strong> {hospital.hours}</div>
        <div style={{ marginBottom: '0.5rem' }}><strong>Rating:</strong> {hospital.rating}</div>
        <div style={{ marginBottom: '0.5rem' }}><strong>Address:</strong> {hospital.address}</div>
        <div style={{ marginBottom: '0.5rem' }}><strong>Phone:</strong> {hospital.phone}</div>
        <div style={{ marginBottom: '0.5rem' }}><strong>Email:</strong> {hospital.email}</div>
      </div>
      
      <button 
        onClick={handleBookAppointment}
        style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          fontSize: '1rem',
          fontWeight: '600',
          cursor: 'pointer'
        }}
      >
        Book Appointment
      </button>
    </div>
  );
};

export default HospitalDetails;