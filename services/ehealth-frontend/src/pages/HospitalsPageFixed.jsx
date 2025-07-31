import { useState } from 'react';
import { 
  Search,
  MapPin,
  Phone,
  Star
} from 'lucide-react';
import { EntityCard } from '../components/EntityCard';
import HospitalReviewsSection from '../components/HospitalReviewsSection';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

const HospitalsPage = () => {
  const [activeMenu, setActiveMenu] = useState('hospitals');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const allHospitals = [
    {
      id: 4,
      name: 'Apollo Hospital',
      address: '21 Greams Lane, Off Greams Road, Chennai',
      phone: '+91 44 2829 3333',
      specialties: ['Cardiology', 'Oncology', 'Neurology'],
      rating: 4.7
    },
    {
      id: 5,
      name: 'Fortis Hospital',
      address: 'Sector 62, Phase VIII, Mohali',
      phone: '+91 172 496 7000',
      specialties: ['Orthopedics', 'Gastroenterology', 'Pediatrics'],
      rating: 4.5
    },
    {
      id: 6,
      name: 'Max Super Speciality Hospital',
      address: '1 Press Enclave Road, Saket, New Delhi',
      phone: '+91 11 2651 5050',
      specialties: ['Cardiac Surgery', 'Transplant', 'Emergency'],
      rating: 4.6
    },
    {
      id: 7,
      name: 'Manipal Hospital',
      address: '98 Rustom Bagh, Airport Road, Bangalore',
      phone: '+91 80 2502 4444',
      specialties: ['Nephrology', 'Urology', 'Pulmonology'],
      rating: 4.4
    },
    {
      id: 8,
      name: 'AIIMS Delhi',
      address: 'Sri Aurobindo Marg, Ansari Nagar, New Delhi',
      phone: '+91 11 2658 8500',
      specialties: ['All Specialties', 'Research', 'Teaching'],
      rating: 4.8
    }
  ];

  const handleSearch = (term) => {
    if (term.trim() === '') {
      setSearchResults([]);
    } else {
      const filtered = allHospitals.filter(hospital =>
        hospital.name.toLowerCase().includes(term.toLowerCase()) ||
        hospital.address.toLowerCase().includes(term.toLowerCase()) ||
        hospital.specialties.some(specialty => 
          specialty.toLowerCase().includes(term.toLowerCase())
        )
      );
      setSearchResults(filtered);
    }
  };

  const userData = {
    name: 'Liam Michael',
    displayName: 'Liam',
    role: 'Patient',
    avatar: null
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        <Header userData={userData} />
        
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » Hospital » Hospitals
          </div>
          
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}>
            <div style={{ marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                Find Hospitals
              </h2>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Search for hospitals by name, location, or medical specialty
              </p>
            </div>
            <div style={{ position: 'relative', width: '100%', maxWidth: '600px' }}>
              <Search className="w-5 h-5" style={{
                position: 'absolute',
                left: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#6b7280'
              }} />
              <input
                type="text"
                placeholder="Search hospitals by name, location, or specialty..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  handleSearch(e.target.value);
                }}
                style={{
                  width: '100%',
                  padding: '1rem 1rem 1rem 3rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '0.75rem',
                  fontSize: '1rem',
                  transition: 'all 0.2s',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#3b82f6';
                  e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e5e7eb';
                  e.target.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
                }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              }}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                    {searchResults.length > 0 ? 'Search Results' : 'Available Hospitals'}
                  </h2>
                  {searchResults.length > 0 && (
                    <div style={{
                      display: 'inline-block',
                      backgroundColor: '#dbeafe',
                      color: '#1e40af',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '1rem',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}>
                      {searchResults.length} hospital{searchResults.length !== 1 ? 's' : ''} found
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {(searchResults.length > 0 ? searchResults : allHospitals).map((hospital) => (
                    <EntityCard key={hospital.id} entity={hospital} type="hospitals" />
                  ))}
                </div>
              </div>

              <HospitalReviewsSection />
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'sticky', top: '1.5rem', alignSelf: 'flex-start' }}>
              <HospitalAdsSection />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

const HospitalAdsSection = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Emergency Services</h3>
      <div style={{ backgroundColor: '#fef2f2', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🚨</div>
        <p style={{ fontSize: '0.875rem', color: '#dc2626' }}>24/7 Emergency care available</p>
      </div>
      <button style={{
        width: '100%',
        padding: '0.75rem',
        backgroundColor: '#dc2626',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer'
      }}>Call Now</button>
    </div>
    
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Health Packages</h3>
      <div style={{ backgroundColor: '#f0f9ff', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📋</div>
        <p style={{ fontSize: '0.875rem', color: '#0369a1' }}>Comprehensive health packages</p>
      </div>
      <button style={{
        width: '100%',
        padding: '0.75rem',
        backgroundColor: '#0369a1',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer'
      }}>View Packages</button>
    </div>
  </div>
);

export default HospitalsPage;