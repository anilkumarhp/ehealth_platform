import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

const SimpleBookingPage = () => {
  const [activeMenu, setActiveMenu] = useState('hospitals');
  const navigate = useNavigate();
  
  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };
  
  const doctors = [
    {
      id: 1,
      name: 'Dr. Rajesh Kumar',
      specialty: 'Cardiologist',
      photo: 'https://randomuser.me/api/portraits/men/1.jpg'
    },
    {
      id: 2,
      name: 'Dr. Priya Sharma',
      specialty: 'Neurologist',
      photo: 'https://randomuser.me/api/portraits/women/2.jpg'
    },
    {
      id: 3,
      name: 'Dr. Amit Patel',
      specialty: 'Orthopedic Surgeon',
      photo: 'https://randomuser.me/api/portraits/men/3.jpg'
    }
  ];
  
  const timeSlots = [
    '9:00 AM', '10:00 AM', '11:00 AM',
    '1:00 PM', '2:00 PM', '3:00 PM',
    '4:00 PM', '5:00 PM'
  ];
  
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [showSuccess, setShowSuccess] = useState(false);
  
  const handleBooking = () => {
    setShowSuccess(true);
    setTimeout(() => {
      navigate('/patient-dashboard');
    }, 2000);
  };
  
  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        <Header userData={userData} />
        
        {showSuccess && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1rem',
            borderRadius: '0.5rem',
            zIndex: 50
          }}>
            Appointment booked successfully!
          </div>
        )}
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Book Appointment</h1>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Left column */}
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Select Doctor</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {doctors.map(doctor => (
                  <div 
                    key={doctor.id}
                    onClick={() => setSelectedDoctor(doctor)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      padding: '1rem',
                      borderRadius: '0.5rem',
                      backgroundColor: selectedDoctor?.id === doctor.id ? '#dbeafe' : 'white',
                      border: `1px solid ${selectedDoctor?.id === doctor.id ? '#3b82f6' : '#e5e7eb'}`,
                      cursor: 'pointer'
                    }}
                  >
                    <img 
                      src={doctor.photo} 
                      alt={doctor.name} 
                      style={{ width: '50px', height: '50px', borderRadius: '50%' }} 
                    />
                    <div>
                      <div style={{ fontWeight: '600' }}>{doctor.name}</div>
                      <div style={{ fontSize: '0.875rem', color: '#3b82f6' }}>{doctor.specialty}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Right column */}
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Select Time</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
                {timeSlots.map((time, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedTime(time)}
                    style={{
                      padding: '0.75rem',
                      textAlign: 'center',
                      borderRadius: '0.5rem',
                      backgroundColor: selectedTime === time ? '#dbeafe' : 'white',
                      border: `1px solid ${selectedTime === time ? '#3b82f6' : '#e5e7eb'}`,
                      cursor: 'pointer'
                    }}
                  >
                    {time}
                  </div>
                ))}
              </div>
              
              <button
                onClick={handleBooking}
                disabled={!selectedDoctor || !selectedTime}
                style={{
                  marginTop: '2rem',
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: selectedDoctor && selectedTime ? '#3b82f6' : '#e5e7eb',
                  color: selectedDoctor && selectedTime ? 'white' : '#9ca3af',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  cursor: selectedDoctor && selectedTime ? 'pointer' : 'not-allowed'
                }}
              >
                Book Appointment
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SimpleBookingPage;