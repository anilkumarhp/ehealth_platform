import { useState } from 'react';
import { EntityCard } from '../components/EntityCard';
import HospitalReviewsSection from '../components/HospitalReviewsSection';
import { 
  Home, 
  Hospital, 
  Pill, 
  FlaskConical, 
  MessageSquare, 
  Bell, 
  Calendar, 
  FileText, 
  LogOut,
  Search,
  Settings,
  Mail,
  ChevronRight,
  MapPin,
  Phone,
  Clock,
  User
} from 'lucide-react';

const HospitalsPage = () => {
  const [activeMenu, setActiveMenu] = useState('hospitals');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const allHospitals = [
    {
      id: 1,
      name: 'Apollo Hospital',
      address: '21 Greams Lane, Off Greams Road, Chennai',
      phone: '+91 44 2829 3333',
      specialties: ['Cardiology', 'Oncology', 'Neurology'],
      rating: 4.7
    },
    {
      id: 2,
      name: 'Fortis Hospital',
      address: 'Sector 62, Phase VIII, Mohali',
      phone: '+91 172 496 7000',
      specialties: ['Orthopedics', 'Gastroenterology', 'Pediatrics'],
      rating: 4.5
    },
    {
      id: 3,
      name: 'Max Super Speciality Hospital',
      address: '1 Press Enclave Road, Saket, New Delhi',
      phone: '+91 11 2651 5050',
      specialties: ['Cardiac Surgery', 'Transplant', 'Emergency'],
      rating: 4.6
    },
    {
      id: 4,
      name: 'Manipal Hospital',
      address: '98 Rustom Bagh, Airport Road, Bangalore',
      phone: '+91 80 2502 4444',
      specialties: ['Nephrology', 'Urology', 'Pulmonology'],
      rating: 4.4
    },
    {
      id: 5,
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
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'sticky', top: '1.5rem', alignSelf: 'flex-start' }}>
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

const HospitalListCard = ({ hospital }) => (
  <Link to={`/hospitals/${hospital.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
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
          <Hospital className="w-5 h-5 text-blue-600" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
            {hospital.name}
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
          <MapPin className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{hospital.address}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Phone className="w-4 h-4 text-gray-500" />
            <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{hospital.phone}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: '#fbbf24' }}>★</span>
            <span style={{ fontWeight: '600', color: '#111827' }}>{hospital.rating}</span>
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {hospital.specialties.slice(0, 3).map((specialty, index) => (
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
        Book
      </button>
    </div>
  </div>
);

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

const HospitalReviewsSection = () => {
  // Use React.useState instead of useState directly
  const [reviewSearchTerm, setReviewSearchTerm] = React.useState('');
  const [reviewSearchTerm, setReviewSearchTerm] = useState('');
  
  const allReviews = [
    { id: 1, patient: 'Alex R.', hospital: 'Apollo Hospital', rating: 5, comment: 'Excellent facilities and professional staff. Highly recommended.', date: '2024-01-12' },
    { id: 2, patient: 'Maria S.', hospital: 'Fortis Hospital', rating: 4, comment: 'Good service and clean environment. Quick appointment scheduling.', date: '2024-01-10' },
    { id: 3, patient: 'David K.', hospital: 'Max Super Speciality Hospital', rating: 5, comment: 'Outstanding cardiac care unit. Saved my life with their expertise.', date: '2024-01-08' },
    { id: 4, patient: 'Jennifer L.', hospital: 'AIIMS Delhi', rating: 4, comment: 'Great doctors and affordable treatment. Long wait times though.', date: '2024-01-06' },
    { id: 5, patient: 'Robert M.', hospital: 'Apollo Hospital', rating: 5, comment: 'Excellent emergency care. The staff was very attentive.', date: '2024-01-04' },
    { id: 6, patient: 'Emily T.', hospital: 'Manipal Hospital', rating: 3, comment: 'Good doctors but the waiting time was too long.', date: '2024-01-02' },
    { id: 7, patient: 'Michael P.', hospital: 'Fortis Hospital', rating: 4, comment: 'Clean facilities and professional staff. Would recommend.', date: '2023-12-28' }
  ];

  const filteredReviews = reviewSearchTerm.trim() === '' 
    ? allReviews.slice(0, 4) 
    : allReviews.filter(review => 
        review.hospital.toLowerCase().includes(reviewSearchTerm.toLowerCase())
      );

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '1rem',
      padding: '2rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>Hospital Reviews</h3>
        <div style={{ position: 'relative', width: '250px' }}>
          <Search className="w-4 h-4" style={{
            position: 'absolute',
            left: '0.75rem',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#6b7280'
          }} />
          <input
            type="text"
            placeholder="Search by hospital name..."
            value={reviewSearchTerm}
            onChange={(e) => setReviewSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 0.5rem 0.5rem 2rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '0.875rem'
            }}
          />
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filteredReviews.map((review) => (
          <div key={review.id} style={{
            padding: '1rem',
            backgroundColor: '#f8fafc',
            borderRadius: '0.5rem',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
              <div>
                <div style={{ fontWeight: '600', color: '#111827', fontSize: '0.875rem' }}>{review.patient}</div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>visited {review.hospital}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                {[...Array(5)].map((_, i) => (
                  <span key={i} style={{ color: i < review.rating ? '#fbbf24' : '#d1d5db' }}>★</span>
                ))}
              </div>
            </div>
            <p style={{ fontSize: '0.875rem', color: '#374151', marginBottom: '0.5rem' }}>{review.comment}</p>
            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{new Date(review.date).toLocaleDateString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

// Keep the rest of the components
const OldSidebar = ({ activeMenu, setActiveMenu }) => {
  const [expandedMenus, setExpandedMenus] = useState({ hospital: true });
  const toggleMenu = (menuKey) => {
    setExpandedMenus(prev => ({ ...prev, [menuKey]: !prev[menuKey] }));
  };
  const mainMenuItems = [
    { key: 'dashboard', icon: <Home className="w-5 h-5" />, label: 'Dashboard' },
    { key: 'hospital', icon: <Hospital className="w-5 h-5" />, label: 'Hospital', submenu: [
        { key: 'hospitals', label: 'Hospitals' },
        { key: 'doctors', label: 'Doctors' }
      ]},
    { key: 'pharmacy', icon: <Pill className="w-5 h-5" />, label: 'Pharmacy', onClick: () => window.location.href = '/pharmacy' },
    { key: 'lab', icon: <FlaskConical className="w-5 h-5" />, label: 'Lab' },
    { key: 'messages', icon: <MessageSquare className="w-5 h-5" />, label: 'Messages' },
    { key: 'notifications', icon: <Bell className="w-5 h-5" />, label: 'Notifications' },
    { key: 'appointments', icon: <Calendar className="w-5 h-5" />, label: 'Appointments' },
    { key: 'documents', icon: <FileText className="w-5 h-5" />, label: 'Documents', submenu: [
        { key: 'prescriptions', label: 'Prescriptions' },
        { key: 'test-reports', label: 'Test Reports' },
        { key: 'scan-reports', label: 'Scan Reports' }
      ]}
  ];
  return (
    <div style={{ width: '280px', backgroundColor: '#ffffff', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', height: '100vh', position: 'fixed', left: 0, top: 0 }}>
      <div style={{ padding: '1.5rem', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ width: '32px', height: '32px', backgroundColor: '#3b82f6', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>E</div>
        <span style={{ fontWeight: '600', fontSize: '1.125rem', color: '#111827' }}>Ehealth Platform</span>
      </div>
      <div style={{ flex: 1, padding: '1rem', overflow: 'auto' }}>
        <div>
          <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>Main Menu</h3>
          {mainMenuItems.map((item) => (
            <div key={item.key}>
              <button onClick={() => { if (item.submenu) { toggleMenu(item.key); } else if (item.key === 'dashboard') { window.location.href = '/patient-dashboard'; } else if (item.key === 'pharmacy') { window.location.href = '/pharmacy'; } else { setActiveMenu(item.key); } }} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: activeMenu === item.key ? '#dbeafe' : 'transparent', color: activeMenu === item.key ? '#1d4ed8' : '#6b7280', cursor: 'pointer', transition: 'all 0.2s', marginBottom: '0.25rem' }}>
                {item.icon}
                <span style={{ flex: 1, textAlign: 'left' }}>{item.label}</span>
                {item.submenu && (<ChevronRight className="w-4 h-4" style={{ transform: expandedMenus[item.key] ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} />)}
              </button>
              {item.submenu && expandedMenus[item.key] && (
                <div style={{ marginLeft: '2rem', marginBottom: '0.5rem' }}>
                  {item.submenu.map((subItem) => (
                    <button
                      key={subItem.key}
                      onClick={() => {
                        setActiveMenu(subItem.key);
                        if (subItem.key === 'doctors') {
                          window.location.href = '/doctors';
                        } else if (subItem.key === 'hospitals') {
                          window.location.href = '/hospitals';
                        }
                      }}
                      style={{
                        width: '100%',
                        display: 'block',
                        padding: '0.5rem 0.75rem',
                        borderRadius: '0.375rem',
                        border: 'none',
                        backgroundColor: activeMenu === subItem.key ? '#e0e7ff' : 'transparent',
                        color: activeMenu === subItem.key ? '#1e40af' : '#6b7280',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        textAlign: 'left',
                        marginBottom: '0.25rem',
                        transition: 'all 0.2s'
                      }}
                    >
                      {subItem.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      <div style={{ padding: '1rem', borderTop: '1px solid #e5e7eb' }}>
        <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s' }}>
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

const OldHeader = ({ userData }) => (
  <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', height: '80px', position: 'sticky', top: 0, zIndex: 10 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button style={{ padding: '0.5rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#f3f4f6', cursor: 'pointer' }}><Bell className="w-5 h-5 text-gray-600" /></button>
        <button style={{ padding: '0.5rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#f3f4f6', cursor: 'pointer' }}><Mail className="w-5 h-5 text-gray-600" /></button>
        <button style={{ padding: '0.5rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#f3f4f6', cursor: 'pointer' }}><Settings className="w-5 h-5 text-gray-600" /></button>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: '600' }}>{userData.avatar || userData.name.charAt(0)}</div>
        <div>
          <div style={{ fontWeight: '600', fontSize: '0.875rem', color: '#111827' }}>{userData.name}</div>
          <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{userData.role}</div>
        </div>
      </div>
    </div>
  </header>
);

export default HospitalsPage;