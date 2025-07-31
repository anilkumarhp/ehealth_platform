import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  MapPin, 
  Phone, 
  Mail, 
  Clock, 
  Award, 
  Star, 
  Calendar
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import mockData from '../data/mockData';

const DetailsPage = () => {
  const { type, id } = useParams();
  const [entity, setEntity] = useState(null);
  const [activeMenu, setActiveMenu] = useState(type);

  useEffect(() => {
    // In a real app, this would be an API call
    console.log('Looking for:', type, id);
    
    // Always use a valid entity
    if (type === 'hospitals') {
      // For hospitals, use the entity with matching ID or default to ID 4
      const hospitalId = mockData.hospitals[id] ? id : '4';
      setEntity(mockData.hospitals[hospitalId]);
    } else if (type === 'doctors') {
      setEntity(mockData.doctors['1']);
    } else if (type === 'pharmacies') {
      setEntity(mockData.pharmacies['1']);
    } else if (type === 'labs') {
      setEntity(mockData.labs['1']);
    }
  }, [type, id]);

  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };
  
  const handleBookClick = () => {
    console.log('Book button clicked in details page');
    window.open('/simple-booking', '_self');
  };

  if (!entity) {
    return (
      <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
        <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
          <Header userData={userData} />
          <main style={{ flex: 1, padding: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div>Loading...</div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        <Header userData={userData} />
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » {type.charAt(0).toUpperCase() + type.slice(1)} » {entity.name}
          </div>
          
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            marginBottom: '1.5rem'
          }}>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>{entity.name}</h1>
            <p style={{ marginBottom: '1.5rem' }}>{entity.description}</p>
            
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock className="w-5 h-5 text-blue-600" />
                <span>{entity.hours}</span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Star className="w-5 h-5 text-yellow-500" />
                <span>{entity.rating}</span>
              </div>
            </div>
            
            <button 
              onClick={handleBookClick}
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#3b82f6',
                color: 'white',
                borderRadius: '0.5rem',
                border: 'none',
                textDecoration: 'none',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              <Calendar className="w-5 h-5 inline-block mr-2" />
              Book Appointment
            </button>
          </div>
          
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>About</h2>
            <p>{entity.about}</p>
          </div>
          
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>Contact Information</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <MapPin className="w-5 h-5 text-gray-500" />
                <span>{entity.address}</span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Phone className="w-5 h-5 text-gray-500" />
                <span>{entity.phone}</span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Mail className="w-5 h-5 text-gray-500" />
                <span>{entity.email}</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DetailsPage;