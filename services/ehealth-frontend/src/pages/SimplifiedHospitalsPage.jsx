import React from 'react';
import SimpleEntityCard from '../components/SimpleEntityCard';

const SimplifiedHospitalsPage = () => {
  const hospitals = [
    {
      id: 1,
      name: 'Apollo Hospital',
      address: '21 Greams Lane, Chennai',
      phone: '+91 44 2829 3333'
    },
    {
      id: 2,
      name: 'Fortis Hospital',
      address: 'Sector 62, Mohali',
      phone: '+91 172 496 7000'
    },
    {
      id: 3,
      name: 'Max Hospital',
      address: 'Press Enclave Road, Delhi',
      phone: '+91 11 2651 5050'
    }
  ];

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Hospitals</h1>
      
      {hospitals.map(hospital => (
        <SimpleEntityCard key={hospital.id} entity={hospital} />
      ))}
    </div>
  );
};

export default SimplifiedHospitalsPage;