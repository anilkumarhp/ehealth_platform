import { useState } from 'react';
import { 
  Search,
  FlaskConical,
  MapPin,
  Phone,
  Clock,
  Calendar,
  ShoppingBag
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

const LabPage = () => {
  const [activeMenu, setActiveMenu] = useState('lab');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Mock data for recent lab visits
  const recentVisits = [
    {
      id: 1,
      labName: 'City Diagnostics',
      address: '123 Health Street, Downtown',
      phone: '+1 (555) 123-4567',
      date: '2024-01-10',
      tests: ['Complete Blood Count', 'Lipid Profile', 'Glucose Test'],
      total: 85.50
    },
    {
      id: 2,
      labName: 'LifeCare Labs',
      address: '456 Wellness Avenue, Midtown',
      phone: '+1 (555) 987-6543',
      date: '2024-01-05',
      tests: ['Thyroid Function Test', 'Vitamin D Test'],
      total: 120.75
    },
    {
      id: 3,
      labName: 'QuickTest Diagnostics',
      address: '789 Care Road, Uptown',
      phone: '+1 (555) 456-7890',
      date: '2023-12-28',
      tests: ['COVID-19 PCR Test', 'Antibody Test'],
      total: 150.00
    }
  ];

  // Mock data for nearby labs
  const allLabs = [
    {
      id: 4,
      name: 'Apollo Diagnostics',
      address: '21 Health Lane, Central District',
      phone: '+91 44 2829 3333',
      distance: '0.5 km',
      rating: 4.7,
      openNow: true,
      specialties: ['Blood Tests', 'Imaging', 'Pathology']
    },
    {
      id: 5,
      name: 'SRL Diagnostics',
      address: 'Sector 62, Phase VIII, North Area',
      phone: '+91 172 496 7000',
      distance: '1.2 km',
      rating: 4.5,
      openNow: true,
      specialties: ['Molecular Diagnostics', 'Microbiology', 'Cytology']
    },
    {
      id: 6,
      name: 'Thyrocare',
      address: '1 Press Enclave Road, South District',
      phone: '+91 11 2651 5050',
      distance: '2.3 km',
      rating: 4.6,
      openNow: false,
      specialties: ['Thyroid Tests', 'Hormone Tests', 'Preventive Health Checkups']
    },
    {
      id: 7,
      name: 'Metropolis Labs',
      address: '98 Rustom Bagh, East District',
      phone: '+91 80 2502 4444',
      distance: '3.1 km',
      rating: 4.4,
      openNow: true,
      specialties: ['Genetic Testing', 'Allergy Testing', 'Biochemistry']
    },
    {
      id: 8,
      name: 'Dr. Lal PathLabs',
      address: 'Sri Aurobindo Marg, West District',
      phone: '+91 11 2658 8500',
      distance: '3.8 km',
      rating: 4.8,
      openNow: false,
      specialties: ['Full Body Checkup', 'Cancer Screening', 'Diabetes Tests']
    }
  ];

  const handleSearch = (term) => {
    if (term.trim() === '') {
      setSearchResults([]);
    } else {
      const filtered = allLabs.filter(lab =>
        lab.name.toLowerCase().includes(term.toLowerCase()) ||
        lab.address.toLowerCase().includes(term.toLowerCase()) ||
        lab.specialties.some(specialty => 
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
      {/* Sidebar */}
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      
      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        {/* Header */}
        <Header userData={userData} />
        
        {/* Lab Content */}
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          {/* Breadcrumbs */}
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » Lab
          </div>
          
          {/* Search Section */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}>
            <div style={{ marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                Find Diagnostic Labs
              </h2>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Search for labs by name, location, or test type
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
                placeholder="Search labs by name, location, or test type..."
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

          {/* Dashboard Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
            {/* Left Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Recent Visits */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              }}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                    Recent Lab Visits
                  </h2>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {recentVisits.map((visit) => (
                    <LabVisitCard key={visit.id} visit={visit} />
                  ))}
                </div>
              </div>

              {/* Nearby Labs */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '1rem',
                padding: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              }}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                    {searchResults.length > 0 ? 'Search Results' : 'Nearby Labs'}
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
                      {searchResults.length} lab{searchResults.length !== 1 ? 's' : ''} found
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {(searchResults.length > 0 ? searchResults : allLabs).map((lab) => (
                    <LabCard key={lab.id} lab={lab} />
                  ))}
                </div>
              </div>
            </div>
            
            {/* Right Column - Ads */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'sticky', top: '1.5rem', alignSelf: 'flex-start' }}>
              <LabAdsSection />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

const LabVisitCard = ({ visit }) => (
  <div style={{
    backgroundColor: '#f8fafc',
    borderRadius: '0.75rem',
    border: '1px solid #e5e7eb',
    padding: '1.5rem',
    transition: 'all 0.2s',
    cursor: 'pointer'
  }}
  onMouseOver={(e) => {
    e.currentTarget.style.backgroundColor = '#f1f5f9';
    e.currentTarget.style.borderColor = '#3b82f6';
  }}
  onMouseOut={(e) => {
    e.currentTarget.style.backgroundColor = '#f8fafc';
    e.currentTarget.style.borderColor = '#e5e7eb';
  }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <FlaskConical className="w-5 h-5 text-blue-600" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
            {visit.labName}
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
          <MapPin className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{visit.address}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.75rem' }}>
          <Clock className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            Visited on {new Date(visit.date).toLocaleDateString()}
          </span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
          {visit.tests.map((test, index) => (
            <span key={index} style={{
              fontSize: '0.75rem',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.25rem'
            }}>
              {test}
            </span>
          ))}
        </div>
        <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#111827' }}>
          Total: ${visit.total.toFixed(2)}
        </div>
      </div>
      <button style={{
        padding: '0.75rem 1.5rem',
        backgroundColor: '#10b981',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        marginLeft: '1rem'
      }}>
        <Calendar className="w-4 h-4" />
        Book Again
      </button>
    </div>
  </div>
);

const LabCard = ({ lab }) => (
  <div style={{
    backgroundColor: '#f8fafc',
    borderRadius: '0.75rem',
    border: '1px solid #e5e7eb',
    padding: '1.5rem',
    transition: 'all 0.2s',
    cursor: 'pointer'
  }}
  onMouseOver={(e) => {
    e.currentTarget.style.backgroundColor = '#f1f5f9';
    e.currentTarget.style.borderColor = '#3b82f6';
  }}
  onMouseOut={(e) => {
    e.currentTarget.style.backgroundColor = '#f8fafc';
    e.currentTarget.style.borderColor = '#e5e7eb';
  }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <FlaskConical className="w-5 h-5 text-blue-600" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
            {lab.name}
          </h3>
          <span style={{
            fontSize: '0.75rem',
            backgroundColor: lab.openNow ? '#dcfce7' : '#fee2e2',
            color: lab.openNow ? '#166534' : '#b91c1c',
            padding: '0.25rem 0.5rem',
            borderRadius: '0.25rem',
            marginLeft: '0.5rem'
          }}>
            {lab.openNow ? 'Open Now' : 'Closed'}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
          <MapPin className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{lab.address}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Phone className="w-4 h-4 text-gray-500" />
            <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{lab.phone}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: '#fbbf24' }}>★</span>
            <span style={{ fontWeight: '600', color: '#111827' }}>{lab.rating}</span>
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
          {lab.specialties.map((specialty, index) => (
            <span key={index} style={{
              fontSize: '0.75rem',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.25rem'
            }}>
              {specialty}
            </span>
          ))}
        </div>
        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
          <strong>Distance:</strong> {lab.distance}
        </div>
      </div>
      <button style={{
        padding: '0.75rem 1.5rem',
        backgroundColor: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '0.5rem',
        fontWeight: '600',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        marginLeft: '1rem'
      }}>
        <ShoppingBag className="w-4 h-4" />
        Book Test
      </button>
    </div>
  </div>
);

const LabAdsSection = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Health Checkup Packages</h3>
      <div style={{ backgroundColor: '#f0f9ff', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🧪</div>
        <p style={{ fontSize: '0.875rem', color: '#0369a1' }}>30% off on comprehensive health checkups</p>
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
    
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Home Sample Collection</h3>
      <div style={{ backgroundColor: '#dcfce7', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🏠</div>
        <p style={{ fontSize: '0.875rem', color: '#166534' }}>Free home sample collection</p>
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

export default LabPage;