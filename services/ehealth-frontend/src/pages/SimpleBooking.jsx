import React, { useState } from 'react';

const SimpleBooking = () => {
  const [step, setStep] = useState(1);
  const [doctor, setDoctor] = useState(null);
  const [time, setTime] = useState(null);
  const [booked, setBooked] = useState(false);
  
  const doctors = [
    { id: 1, name: "Dr. Rajesh Kumar", specialty: "Cardiologist" },
    { id: 2, name: "Dr. Priya Sharma", specialty: "Neurologist" },
    { id: 3, name: "Dr. Amit Patel", specialty: "Orthopedic" }
  ];
  
  const times = ["9:00 AM", "10:00 AM", "11:00 AM", "1:00 PM", "2:00 PM", "3:00 PM"];
  
  const handleBooking = () => {
    console.log("Booking with:", doctor.name, "at", time);
    setBooked(true);
    setTimeout(() => {
      window.location.href = '/patient-dashboard';
    }, 2000);
  };
  
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Book Appointment</h1>
      
      {booked ? (
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#d1fae5', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <h2>Appointment Booked Successfully!</h2>
          <p>Redirecting to dashboard...</p>
        </div>
      ) : step === 1 ? (
        <div>
          <h2>Select Doctor</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '20px' }}>
            {doctors.map(d => (
              <div 
                key={d.id}
                onClick={() => { setDoctor(d); setStep(2); }}
                style={{
                  padding: '15px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: doctor?.id === d.id ? '#dbeafe' : 'white'
                }}
              >
                <div style={{ fontWeight: 'bold' }}>{d.name}</div>
                <div style={{ color: '#3b82f6' }}>{d.specialty}</div>
              </div>
            ))}
          </div>
        </div>
      ) : step === 2 ? (
        <div>
          <h2>Select Time</h2>
          <p>Doctor: {doctor.name}</p>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(3, 1fr)', 
            gap: '10px',
            marginTop: '20px',
            marginBottom: '20px'
          }}>
            {times.map((t, i) => (
              <div
                key={i}
                onClick={() => setTime(t)}
                style={{
                  padding: '10px',
                  textAlign: 'center',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: time === t ? '#dbeafe' : 'white'
                }}
              >
                {t}
              </div>
            ))}
          </div>
          
          <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
            <button 
              onClick={() => setStep(1)}
              style={{
                padding: '10px 20px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                backgroundColor: 'white',
                cursor: 'pointer'
              }}
            >
              Back
            </button>
            
            <button
              onClick={handleBooking}
              disabled={!time}
              style={{
                padding: '10px 20px',
                backgroundColor: time ? '#3b82f6' : '#ddd',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: time ? 'pointer' : 'not-allowed'
              }}
            >
              Book Appointment
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SimpleBooking;