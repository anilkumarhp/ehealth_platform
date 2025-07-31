import React from 'react';

const AdsSection = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Health Insurance</h3>
      <div style={{ backgroundColor: '#dbeafe', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🏥</div>
        <p style={{ fontSize: '0.875rem', color: '#1e40af' }}>Get comprehensive health coverage</p>
      </div>
      <button style={{
        width: '100%',
        padding: '0.75rem',
        backgroundColor: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer'
      }}>Learn More</button>
    </div>
    
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Health Checkup</h3>
      <div style={{ backgroundColor: '#dcfce7', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>❤️</div>
        <p style={{ fontSize: '0.875rem', color: '#166534' }}>Book your annual health checkup</p>
      </div>
      <button style={{
        width: '100%',
        padding: '0.75rem',
        backgroundColor: '#10b981',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer'
      }}>Book Now</button>
    </div>
  </div>
);

export default AdsSection;