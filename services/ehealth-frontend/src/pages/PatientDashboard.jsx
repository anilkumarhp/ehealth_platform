import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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
  ChevronRight,
  ChevronLeft,
  User
} from 'lucide-react';
import UserProfileForm from '../components/UserProfileForm';
import { useToast } from '../context/SimpleToastContext';
import userService from '../services/userService';
import authService from '../services/authService';

const PatientDashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [currentAppointment, setCurrentAppointment] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState({
    name: '',
    displayName: '',
    role: 'Patient',
    avatar: null,
    email: ''
  });
  
  useEffect(() => {
    // Check if user is authenticated
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    
    // Use stored user info for initial display to avoid blank screen
    try {
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
      if (storedUser.name) {
        setUserData(prev => ({
          ...prev,
          name: storedUser.name || '',
          displayName: storedUser.displayName || storedUser.name || '',
          email: storedUser.email || ''
        }));
      }
    } catch (e) {
      console.error('Error parsing stored user data:', e);
    }
    
    // Show welcome notification if user just registered
    if (location.state?.showWelcome) {
      setTimeout(() => {
        toast.success('Welcome to eHealth Platform! Your account has been successfully registered.');
      }, 500);
    }
    
    // Fetch user profile data
    const fetchUserProfile = async () => {
      try {
        setIsLoading(true);
        
        // Add a small delay to ensure token is properly set
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const profile = await userService.getUserProfile();
        console.log('Profile data:', profile);
        
        // Extract user data from profile
        const personalInfo = profile.personal_info || {};
        const firstName = personalInfo.first_name || '';
        const lastName = personalInfo.last_name || '';
        const displayName = personalInfo.display_name || `${firstName} ${lastName}`.trim() || profile.email.split('@')[0];
        
        const userData = {
          name: `${firstName} ${lastName}`.trim() || profile.email.split('@')[0],
          displayName: displayName,
          role: 'Patient',
          avatar: profile.profile_photo_url || null,
          email: profile.email || ''
        };
        
        setUserData(userData);
        
        // Store basic user info in localStorage for future use
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        localStorage.setItem('user', JSON.stringify({
          ...storedUser,
          name: userData.name,
          displayName: userData.displayName,
          email: userData.email
        }));
        
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching user profile:', error);
        if (error.response && error.response.status === 401) {
          toast.error('Your session has expired. Please login again.');
          authService.logout();
          navigate('/login');
        } else {
          toast.error('Failed to load user profile');
          setIsLoading(false);
        }
      }
    };
    
    fetchUserProfile();
  }, [location.state, toast, navigate]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const [activeTab, setActiveTab] = useState('events');
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalType, setModalType] = useState(null);

  const appointments = [
    { id: 1, doctor: 'Dr. Sarah Johnson', specialty: 'Cardiologist', date: '2024-01-15', time: '10:00 AM' },
    { id: 2, doctor: 'Dr. Michael Brown', specialty: 'Dermatologist', date: '2024-01-18', time: '2:30 PM' }
  ];

  const medications = [
    { name: 'Aspirin', dosage: '100mg', time: '8:00 AM', taken: false },
    { name: 'Metformin', dosage: '500mg', time: '12:00 PM', taken: true }
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'Arial, sans-serif', overflow: 'hidden' }}>
      {/* Sidebar */}
      <div style={{ width: '280px', backgroundColor: '#ffffff', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', height: '100vh', position: 'fixed', left: 0, top: 0 }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '32px', height: '32px', backgroundColor: '#3b82f6', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>E</div>
          <span style={{ fontWeight: '600', fontSize: '1.125rem', color: '#111827' }}>Ehealth Platform</span>
        </div>
        <div style={{ flex: 1, padding: '1rem', overflow: 'auto' }}>
          <div>
            <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>Main Menu</h3>
            <button 
              onClick={() => setActiveMenu('dashboard')}
              style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: activeMenu === 'dashboard' ? '#dbeafe' : 'transparent', color: activeMenu === 'dashboard' ? '#1d4ed8' : '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}
            >
              <Home width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>Dashboard</span>
            </button>
            <button 
              onClick={() => setActiveMenu('profile')}
              style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: activeMenu === 'profile' ? '#dbeafe' : 'transparent', color: activeMenu === 'profile' ? '#1d4ed8' : '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}
            >
              <User width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>My Profile</span>
            </button>
            <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}>
              <Hospital width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>Hospital</span>
              <ChevronRight width="16" height="16" />
            </button>
            <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}>
              <Pill width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>Pharmacy</span>
            </button>
            <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}>
              <FlaskConical width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>Lab</span>
            </button>
            <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}>
              <MessageSquare width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>Messages</span>
            </button>
            <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#6b7280', cursor: 'pointer', marginBottom: '0.25rem' }}>
              <Calendar width="20" height="20" />
              <span style={{ flex: 1, textAlign: 'left' }}>Appointments</span>
            </button>
          </div>
        </div>
        <div style={{ padding: '1rem', borderTop: '1px solid #e5e7eb' }}>
          <button 
            onClick={async () => {
              await authService.logout();
              navigate('/login');
            }}
            style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', backgroundColor: 'transparent', color: '#ef4444', cursor: 'pointer' }}
          >
            <LogOut width="20" height="20" />
            <span>Logout</span>
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', marginLeft: '280px' }}>
        {/* Header */}
        <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', height: '80px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button style={{ padding: '0.5rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#f3f4f6', cursor: 'pointer' }}>
                <Bell width="20" height="20" color="#4b5563" />
              </button>
              <button style={{ padding: '0.5rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#f3f4f6', cursor: 'pointer' }}>
                <MessageSquare width="20" height="20" color="#4b5563" />
              </button>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {userData.avatar ? (
                <img 
                  src={userData.avatar} 
                  alt="Profile" 
                  style={{ width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover' }} 
                />
              ) : (
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: '600' }}>
                  {userData.displayName ? userData.displayName.charAt(0).toUpperCase() : '?'}
                </div>
              )}
              <div>
                <div style={{ fontWeight: '600', fontSize: '0.875rem', color: '#111827' }}>{userData.name || 'Loading...'}</div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{userData.role}</div>
              </div>
            </div>
          </div>
        </header>
        
        {/* Dashboard Content */}
        <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
          {/* Breadcrumbs */}
          <div style={{ marginBottom: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
            Dashboard » {activeMenu === 'profile' ? 'My Profile' : 'Patient Dashboard'}
          </div>
          
          {activeMenu === 'profile' ? (
            <UserProfileForm />
          ) : (
            <>
              {/* Welcome Banner */}
              <div style={{
                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                borderRadius: '1rem',
                padding: '2rem',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                gap: '2rem'
              }}>
                {/* Profile Image */}
                {userData.avatar ? (
                  <img 
                    src={userData.avatar} 
                    alt="Profile" 
                    style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      objectFit: 'cover',
                      border: '3px solid rgba(255, 255, 255, 0.3)'
                    }} 
                  />
                ) : (
                  <div style={{
                    width: '80px',
                    height: '80px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '2rem',
                    fontWeight: 'bold'
                  }}>
                    {userData.displayName ? userData.displayName.charAt(0).toUpperCase() : '?'}
                  </div>
                )}

                {/* Content */}
                <div style={{ flex: 1 }}>
                  <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    {getGreeting()}, {userData.displayName || 'there'}!
                  </h1>
                  <p style={{ opacity: 0.9, marginBottom: '1.5rem' }}>
                    Welcome back to your health dashboard. Stay on top of your health journey.
                  </p>
                  <button style={{
                    backgroundColor: 'white',
                    color: '#3b82f6',
                    border: 'none',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '0.5rem',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}>
                    Book Appointment
                  </button>
                </div>
              </div>
              
              {/* Dashboard Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
          
            {/* Left Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Appointments */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '0.75rem',
                border: '1px solid #e5e7eb',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>Upcoming Appointments</h3>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => setCurrentAppointment(Math.max(0, currentAppointment - 1))}
                      disabled={currentAppointment === 0}
                      style={{
                        padding: '0.5rem',
                        borderRadius: '0.375rem',
                        border: '1px solid #d1d5db',
                        backgroundColor: 'white',
                        cursor: currentAppointment === 0 ? 'not-allowed' : 'pointer',
                        opacity: currentAppointment === 0 ? 0.5 : 1
                      }}
                    >
                      <ChevronLeft width="16" height="16" />
                    </button>
                    <button
                      onClick={() => setCurrentAppointment(Math.min(appointments.length - 1, currentAppointment + 1))}
                      disabled={currentAppointment === appointments.length - 1}
                      style={{
                        padding: '0.5rem',
                        borderRadius: '0.375rem',
                        border: '1px solid #d1d5db',
                        backgroundColor: 'white',
                        cursor: currentAppointment === appointments.length - 1 ? 'not-allowed' : 'pointer',
                        opacity: currentAppointment === appointments.length - 1 ? 0.5 : 1
                      }}
                    >
                      <ChevronRight width="16" height="16" />
                    </button>
                  </div>
                </div>
                
                <div style={{
                  padding: '1rem',
                  backgroundColor: '#f8fafc',
                  borderRadius: '0.5rem',
                  border: '1px solid #e5e7eb'
                }}>
                  <div style={{ fontWeight: '600', color: '#111827', marginBottom: '0.5rem' }}>
                    {appointments[currentAppointment].doctor}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                    {appointments[currentAppointment].specialty}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    {appointments[currentAppointment].date} at {appointments[currentAppointment].time}
                  </div>
                </div>
              </div>
              
              {/* Events & News Section */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '0.75rem',
                border: '1px solid #e5e7eb',
                overflow: 'hidden'
              }}>
                {/* Tab Navigation */}
                <div style={{
                  display: 'flex',
                  borderBottom: '1px solid #e5e7eb'
                }}>
                  <button
                    onClick={() => setActiveTab('events')}
                    style={{
                      flex: 1,
                      padding: '1rem',
                      backgroundColor: activeTab === 'events' ? '#3b82f6' : 'white',
                      color: activeTab === 'events' ? 'white' : '#6b7280',
                      border: 'none',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Events
                  </button>
                  <button
                    onClick={() => setActiveTab('news')}
                    style={{
                      flex: 1,
                      padding: '1rem',
                      backgroundColor: activeTab === 'news' ? '#3b82f6' : 'white',
                      color: activeTab === 'news' ? 'white' : '#6b7280',
                      border: 'none',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    News
                  </button>
                </div>

                {/* Tab Content */}
                <div style={{ padding: '1.5rem' }}>
                  {activeTab === 'events' ? (
                    <div>
                      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>
                        Upcoming Health Events
                      </h3>
                      <div style={{ padding: '1rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e5e7eb', marginBottom: '1rem' }}>
                        <h4 style={{ fontWeight: '600', color: '#111827', fontSize: '1rem', marginBottom: '0.5rem' }}>Free Heart Health Checkup</h4>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                          City General Hospital
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                          January 20, 2024 • 9:00 AM - 5:00 PM
                        </div>
                      </div>
                      <div style={{ padding: '1rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e5e7eb' }}>
                        <h4 style={{ fontWeight: '600', color: '#111827', fontSize: '1rem', marginBottom: '0.5rem' }}>Blood Donation Camp</h4>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                          Metro Medical Center
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                          January 25, 2024 • 10:00 AM - 4:00 PM
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>
                        Latest Health News
                      </h3>
                      <div style={{ padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e5e7eb', marginBottom: '0.75rem' }}>
                        <h4 style={{ fontWeight: '600', color: '#111827', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                          New COVID-19 Variant Detection Methods
                        </h4>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                          Health Today • January 15, 2024
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#374151' }}>
                          Scientists develop faster detection methods for new COVID variants.
                        </div>
                      </div>
                      <div style={{ padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e5e7eb' }}>
                        <h4 style={{ fontWeight: '600', color: '#111827', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                          Breakthrough in Cancer Treatment
                        </h4>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                          Medical News • January 14, 2024
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#374151' }}>
                          Revolutionary immunotherapy shows 90% success rate in trials.
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Right Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Medication Tracking */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '0.75rem',
                border: '1px solid #e5e7eb',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>Medication Tracking</h3>
                  <button style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}>
                    + Add Tracker
                  </button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {medications.map((med, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.75rem',
                      backgroundColor: '#f8fafc',
                      borderRadius: '0.5rem'
                    }}>
                      <div>
                        <div style={{ fontWeight: '500', color: '#111827' }}>{med.name}</div>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{med.dosage} at {med.time}</div>
                      </div>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: med.taken ? '#10b981' : '#ef4444'
                      }} />
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Documents */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '0.75rem',
                border: '1px solid #e5e7eb',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>Recent Documents</h3>
                  <button style={{
                    color: '#3b82f6',
                    fontSize: '0.875rem',
                    border: 'none',
                    background: 'none',
                    cursor: 'pointer'
                  }}>
                    View All
                  </button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '0.5rem'
                  }}>
                    <div>
                      <div style={{ fontWeight: '500', color: '#111827', fontSize: '0.875rem' }}>Blood Test Report</div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Lab Report • January 10, 2024</div>
                    </div>
                    <FileText width="16" height="16" color="#9ca3af" />
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '0.5rem'
                  }}>
                    <div>
                      <div style={{ fontWeight: '500', color: '#111827', fontSize: '0.875rem' }}>X-Ray Chest</div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Scan Report • January 8, 2024</div>
                    </div>
                    <FileText width="16" height="16" color="#9ca3af" />
                  </div>
                </div>
              </div>
              
              {/* Chat History */}
              <div style={{ 
                backgroundColor: 'white', 
                borderRadius: '8px', 
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', 
                padding: '20px', 
                marginBottom: '20px' 
              }}>
                <h3 style={{ 
                  fontSize: '18px', 
                  marginTop: 0, 
                  marginBottom: '16px', 
                  color: '#111827', 
                  borderBottom: '1px solid #e5e7eb', 
                  paddingBottom: '10px' 
                }}>
                  Your Conversations
                </h3>
                <div style={{ textAlign: 'center', color: '#6b7280', padding: '20px' }}>
                  No conversation history found.
                  <p>Start a chat with the health assistant to get help.</p>
                </div>
              </div>
            </div>
          </div>
          </>
          )}
        </main>
      </div>
    </div>
  );
};

export default PatientDashboard;