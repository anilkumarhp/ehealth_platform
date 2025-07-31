import React from 'react';
import SimpleEntityCard from '../components/SimpleEntityCard';

const SimpleDoctorsPage = () => {
  const doctors = [
    {
      id: 1,
      name: 'Dr. Rajesh Kumar',
      address: 'Apollo Hospital, Chennai',
      specialty: 'Cardiologist'
    },
    {
      id: 2,
      name: 'Dr. Priya Sharma',
      address: 'Fortis Hospital, Delhi',
      specialty: 'Neurologist'
    },
    {
      id: 3,
      name: 'Dr. Amit Patel',
      address: 'Max Hospital, Mumbai',
      specialty: 'Orthopedic'
    }
  ];

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Doctors</h1>
      
      {doctors.map(doctor => (
        <SimpleEntityCard key={doctor.id} entity={doctor} />
      ))}
    </div>
  );
};

export default SimpleDoctorsPage;