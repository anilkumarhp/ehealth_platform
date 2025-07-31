import React from 'react';

function PatientDashboard() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>eHealth Platform</h1>
      <p>Welcome to the eHealth Platform</p>
      
      <div style={{ marginTop: '20px', padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
        <h2>Patient Dashboard</h2>
        <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
          <div style={{ flex: 2 }}>
            <div style={{ padding: '15px', backgroundColor: '#f0f9ff', borderRadius: '5px', marginBottom: '20px' }}>
              <h3>Upcoming Appointments</h3>
              <p>Dr. Sarah Johnson - Cardiologist</p>
              <p>January 15, 2024 at 10:00 AM</p>
            </div>
            
            <div style={{ padding: '15px', backgroundColor: '#f0f9ff', borderRadius: '5px' }}>
              <h3>Health Events</h3>
              <p>Free Heart Health Checkup - January 20, 2024</p>
              <p>Blood Donation Camp - January 25, 2024</p>
            </div>
          </div>
          
          <div style={{ flex: 1 }}>
            <div style={{ padding: '15px', backgroundColor: '#f0f9ff', borderRadius: '5px', marginBottom: '20px' }}>
              <h3>Medication Tracking</h3>
              <p>Aspirin - 100mg at 8:00 AM</p>
              <p>Metformin - 500mg at 12:00 PM</p>
            </div>
            
            <div style={{ padding: '15px', backgroundColor: '#f0f9ff', borderRadius: '5px' }}>
              <h3>Chat History</h3>
              <p>No conversations yet</p>
              <button 
                style={{ 
                  backgroundColor: '#3b82f6', 
                  color: 'white', 
                  border: 'none', 
                  padding: '8px 16px', 
                  borderRadius: '4px', 
                  marginTop: '10px',
                  cursor: 'pointer'
                }}
              >
                Start New Chat
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Chatbot Button */}
      <div style={{ 
        position: 'fixed', 
        bottom: '20px', 
        right: '20px', 
        backgroundColor: '#3b82f6', 
        color: 'white',
        padding: '12px 20px',
        borderRadius: '24px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        cursor: 'pointer'
      }}>
        💬 Chat with Health Assistant
      </div>
    </div>
  );
}

export default PatientDashboard;