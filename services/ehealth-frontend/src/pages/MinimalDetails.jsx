import React from 'react';
import { useParams } from 'react-router-dom';
import mockData from '../data/mockData';
import DirectBookingButton from '../components/DirectBookingButton';

const MinimalDetails = () => {
  const { type, id } = useParams();
  
  // Get entity data based on type and id
  let entity;
  if (type === 'hospitals') {
    entity = mockData.hospitals[id] || mockData.hospitals['4'];
  } else if (type === 'doctors') {
    entity = mockData.doctors['1'];
  } else if (type === 'pharmacies') {
    entity = mockData.pharmacies['1'];
  } else if (type === 'labs') {
    entity = mockData.labs['1'];
  }
  
  if (!entity) {
    return <div>Loading...</div>;
  }
  
  console.log('MinimalDetails rendering for:', type, id);
  console.log('Entity data:', entity);
  
  return (
    <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>{entity.name}</h1>
      <p style={{ marginBottom: '20px' }}>{entity.description}</p>
      
      <div style={{ marginBottom: '20px' }}>
        <strong>Hours:</strong> {entity.hours}<br />
        <strong>Rating:</strong> {entity.rating}<br />
        <strong>Address:</strong> {entity.address}<br />
        <strong>Phone:</strong> {entity.phone}
      </div>
      
      <DirectBookingButton entityName={entity.name} entityType={type} />
    </div>
  );
};

export default MinimalDetails;