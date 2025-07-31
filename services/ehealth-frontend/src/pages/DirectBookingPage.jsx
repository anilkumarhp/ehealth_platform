import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const DirectBookingPage = () => {
  const [step, setStep] = useState(1);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [booked, setBooked] = useState(false);
  
  const doctors = [
    { id: 1, name: 'Dr. Rajesh Kumar', specialty: 'Cardiologist' },
    { id: 2, name: 'Dr. Priya Sharma', specialty: 'Neurologist' },
    { id: 3, name: 'Dr. Amit Patel', specialty: 'Orthopedic' }
  ];
  
  const timeSlots = [
    '9:00 AM', '10:00 AM', '11:00 AM', '1:00 PM', '2:00 PM', '3:00 PM'
  ];
  
  const handleDoctorSelect = (doctor) => {
    setSelectedDoctor(doctor);
    setStep(2);
  };
  
  const handleTimeSelect = (time) => {
    setSelectedTime(time);
  };
  
  const handleBooking = () => {
    setBooked(true);
    setStep(3);
  };
  
  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      padding: '2rem',
      fontFamily: 'Inter, sans-serif'
    }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '2rem' }}>Book Appointment</h1>
      
      {/* Step 1: Select Doctor */}
      {step === 1 && (
        <div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Select a Doctor</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {doctors.map(doctor => (
              <div 
                key={doctor.id}
                onClick={() => handleDoctorSelect(doctor)}
                style={{
                  padding: '1rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  backgroundColor: 'white'
                }}
              >
                <div style={{ fontWeight: 'bold' }}>{doctor.name}</div>
                <div style={{ color: '#3b82f6' }}>{doctor.specialty}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Step 2: Select Time */}
      {step === 2 && (
        <div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>
            Select Time for Dr. {selectedDoctor.name}
          </h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(3, 1fr)', 
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            {timeSlots.map((time, index) => (
              <div
                key={index}
                onClick={() => handleTimeSelect(time)}
                style={{
                  padding: '0.75rem',
                  textAlign: 'center',
                  border: `1px solid ${selectedTime === time ? '#3b82f6' : '#e5e7eb'}`,
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  backgroundColor: selectedTime === time ? '#dbeafe' : 'white'
                }}
              >
                {time}
              </div>
            ))}
          </div>
          
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              onClick={() => setStep(1)}
              style={{
                padding: '0.75rem 1.5rem',
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem',
                backgroundColor: 'white',
                cursor: 'pointer'
              }}
            >
              Back
            </button>
            
            <button
              onClick={handleBooking}
              disabled={!selectedTime}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: selectedTime ? '#3b82f6' : '#e5e7eb',
                color: selectedTime ? 'white' : '#9ca3af',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: selectedTime ? 'pointer' : 'not-allowed'
              }}
            >
              Book Appointment
            </button>
          </div>
        </div>
      )}
      
      {/* Step 3: Confirmation */}
      {step === 3 && (
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            backgroundColor: '#dcfce7', 
            color: '#166534',
            padding: '2rem',
            borderRadius: '0.5rem',
            marginBottom: '2rem'
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>
              Appointment Booked Successfully!
            </h2>
            <p>
              Your appointment with {selectedDoctor.name} is confirmed for {selectedTime}.
            </p>
          </div>
          
          <Link 
            to="/patient-dashboard"
            style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              backgroundColor: '#3b82f6',
              color: 'white',
              borderRadius: '0.5rem',
              textDecoration: 'none'
            }}
          >
            Return to Dashboard
          </Link>
        </div>
      )}
    </div>
  );
};

export default DirectBookingPage;