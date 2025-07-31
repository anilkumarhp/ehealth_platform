import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { HeartPulse, Bell, User, LogOut, Settings, Home, Users, CheckCircle, AlertCircle } from 'lucide-react';
import authService from '../services/authService';
import UserProfileForm from '../components/UserProfileForm';

const DashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [activeSection, setActiveSection] = useState('home');
  
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    // Check if user is authenticated
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    
    setUser(currentUser);
    
    // Check if we should show the profile section based on location state
    if (location.state?.showProfile) {
      setActiveSection('profile');
    }

    // Show notification if provided in location state
    if (location.state?.message) {
      setNotification({
        type: location.state.mfaSuccess ? 'success' : 'info',
        message: location.state.message
      });
      
      // Clear notification after 5 seconds
      const timer = setTimeout(() => {
        setNotification(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [navigate, location]);
  
  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };
  
  if (!user) {
    return <div className="p-8 text-center">Loading...</div>;
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <HeartPulse className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-800">eHealth Platform</span>
            </div>
            
            <div className="flex items-center gap-4">
              <button className="relative p-2 text-gray-600 hover:text-gray-800">
                <Bell className="w-5 h-5" />
                <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-blue-600" />
                </div>
                <span className="text-sm font-medium text-gray-700">Admin</span>
              </div>
              
              <button 
                onClick={handleLogout}
                className="flex items-center gap-1 text-gray-600 hover:text-gray-800"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Sidebar */}
      {/* Notification */}
      {notification && (
        <div className={`mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-4 ${notification.type === 'success' ? 'bg-green-50 border-green-500' : 'bg-blue-50 border-blue-500'} border-l-4 p-4`}>
          <div className="flex items-center">
            {notification.type === 'success' ? (
              <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
            ) : (
              <AlertCircle className="h-5 w-5 text-blue-500 mr-3" />
            )}
            <p className={`text-sm ${notification.type === 'success' ? 'text-green-700' : 'text-blue-700'}`}>
              {notification.message}
            </p>
          </div>
        </div>
      )}

      <div className="flex flex-1">
        <aside className="w-64 bg-white border-r hidden md:block">
          <nav className="mt-6 px-4">
            <div className="space-y-1">
              <button
                onClick={() => setActiveSection('home')}
                className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${activeSection === 'home' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <Home className="mr-3 h-5 w-5" />
                Dashboard Home
              </button>
              
              <button
                onClick={() => setActiveSection('profile')}
                className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${activeSection === 'profile' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <User className="mr-3 h-5 w-5" />
                My Profile
              </button>
              
              <button
                onClick={() => setActiveSection('settings')}
                className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${activeSection === 'settings' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <Settings className="mr-3 h-5 w-5" />
                Settings
              </button>
              
              <button
                onClick={() => setActiveSection('patients')}
                className={`w-full flex items-center px-4 py-2 text-sm font-medium rounded-md ${activeSection === 'patients' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <Users className="mr-3 h-5 w-5" />
                Patients
              </button>
            </div>
          </nav>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 py-8 px-4 sm:px-6 lg:px-8 bg-gray-50">
          <div className="max-w-7xl mx-auto">
            {activeSection === 'home' && (
              <>
                <div className="mb-8">
                  <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                  <p className="text-gray-600">Welcome to your organization dashboard</p>
                </div>
                
                <div className="bg-white shadow rounded-lg p-6 mb-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Registration Successful!</h2>
                  <p className="text-gray-600">
                    Your organization has been successfully registered. You can now start using the eHealth platform.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Patients</h3>
                    <p className="text-3xl font-bold text-blue-600">0</p>
                    <p className="text-sm text-gray-500 mt-1">Total registered patients</p>
                  </div>
                  
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Appointments</h3>
                    <p className="text-3xl font-bold text-green-600">0</p>
                    <p className="text-sm text-gray-500 mt-1">Scheduled appointments</p>
                  </div>
                  
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Staff</h3>
                    <p className="text-3xl font-bold text-purple-600">1</p>
                    <p className="text-sm text-gray-500 mt-1">Active staff members</p>
                  </div>
                </div>
              </>
            )}
            
            {activeSection === 'profile' && (
              <>
                <div className="mb-8">
                  <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
                  <p className="text-gray-600">Manage your personal information</p>
                </div>
                
                <UserProfileForm />
              </>
            )}
            
            {activeSection === 'settings' && (
              <>
                <div className="mb-8">
                  <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                  <p className="text-gray-600">Manage your account settings</p>
                </div>
                
                <div className="bg-white shadow rounded-lg p-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Account Settings</h2>
                  <p className="text-gray-600">
                    This section is under development.
                  </p>
                </div>
              </>
            )}
            
            {activeSection === 'patients' && (
              <>
                <div className="mb-8">
                  <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
                  <p className="text-gray-600">Manage your patients</p>
                </div>
                
                <div className="bg-white shadow rounded-lg p-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Patient List</h2>
                  <p className="text-gray-600">
                    No patients found. This section is under development.
                  </p>
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;