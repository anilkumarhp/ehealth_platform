import { useState } from 'react';
import { 
  Search
} from 'lucide-react';
import { EntityCard } from '../components/EntityCard';
import DoctorReviewsSection from '../components/DoctorReviewsSection';
import AdsSection from '../components/AdsSection';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

const DoctorsPage = () => {
  const [activeMenu, setActiveMenu] = useState('doctors');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const allDoctors = [
    {
      id: 1,
      name: 'Dr. Rajesh Kumar',
      specialty: 'Orthopedic Surgeon',
      experience: '20 years',
      rating: 4.7,
      qualifications: ['MBBS', 'MS Orthopedics', 'Fellowship in Joint Replacement']
    },
    {
      id: 2,
      name: 'Dr. Priya Sharma',
      specialty: 'Pediatrician',
      experience: '8 years',
      rating: 4.5,
      qualifications: ['MBBS', 'MD Pediatrics', 'Fellowship in Neonatology']
    },
    {
      id: 3,
      name: 'Dr. Amit Patel',
      specialty: 'Neurologist',
      experience: '18 years',
      rating: 4.8,
      qualifications: ['MBBS', 'MD Neurology', 'DM Neurology']
    },
    {
      id: 4,
      name: 'Dr. Sunita Reddy',
      specialty: 'Gynecologist',
      experience: '14 years',
      rating: 4.6,
      qualifications: ['MBBS', 'MS Obstetrics & Gynecology']
    },
    {
      id: 5,
      name: 'Dr. Vikram Singh',
      specialty: 'Cardiologist',
      experience: '25 years',
      rating: 4.9,
      qualifications: ['MBBS', 'MD Medicine', 'DM Cardiology']
    }
  ];

  const handleSearch = (term) => {
    if (term.trim() === '') {
      setSearchResults([]);
    } else {
      const filtered = allDoctors.filter(doctor =>
        doctor.name.toLowerCase().includes(term.toLowerCase()) ||
        doctor.specialty.toLowerCase().includes(term.toLowerCase()) ||
        doctor.qualifications.some(qual => 
          qual.toLowerCase().includes(term.toLowerCase())
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
            Dashboard » Hospital » Doctors
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
                Find Doctors
              </h2>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Search for doctors by name, specialty, or qualifications
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
                placeholder="Search doctors by name, specialty, or qualifications..."
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
                    {searchResults.length > 0 ? 'Search Results' : 'Available Doctors'}
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
                      {searchResults.length} doctor{searchResults.length !== 1 ? 's' : ''} found
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {(searchResults.length > 0 ? searchResults : allDoctors).map((doctor) => (
                    <EntityCard key={doctor.id} entity={doctor} type="doctors" />
                  ))}
                </div>
              </div>

              <DoctorReviewsSection />
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'sticky', top: '1.5rem', alignSelf: 'flex-start' }}>
              <AdsSection />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DoctorsPage;