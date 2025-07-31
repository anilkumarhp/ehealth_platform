import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import SimpleLandingPage from './pages/SimpleLandingPage';
import BasicLandingPage from './pages/BasicLandingPage';
import LoginPage from './pages/LoginPage';
import RegistrationPage from './pages/RegistrationPage';
import PatientRegistrationPage from './pages/PatientRegistrationPage';
import OrganizationRegistrationPage from './pages/OrganizationRegistrationPage';
import MFASetupPage from './pages/MFASetupPage';
import PatientDashboard from './pages/PatientDashboard';
import DashboardPage from './pages/DashboardPage';
import HospitalsPage from './pages/HospitalsPageFixed';
import DoctorsPage from './pages/DoctorsPageFixed';
import PharmacyPage from './pages/PharmacyPageFixed';
import LabPage from './pages/LabPageFixed';
import DetailsPage from './pages/BasicDetailsPage';
import SimpleBooking from './pages/SimpleBooking';
import AppointmentsPage from './pages/AppointmentsPage';
import ChatbotWidget from './components/chatbot/ChatbotWidget';
import NotificationTest from './components/NotificationTest';
import MFARequiredRoute from './components/MFARequiredRoute';
import authService from './services/authService';
import { ToastProvider } from './context/SimpleToastContext';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

export default function App() {
  // Get user info from localStorage if available
  let userInfo = {};
  let userId = 'guest';
  let userName = '';
  
  try {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      userInfo = JSON.parse(storedUser);
      userId = userInfo.id || 'guest';
      userName = userInfo.name || '';
    }
  } catch (error) {
    console.error('Error parsing user from localStorage:', error);
  }

  return (
    <Router>
      <ToastProvider>
        <div className="font-sans">
          <Routes>
            <Route path="/notifications" element={<NotificationTest />} />
            <Route path="/" element={<BasicLandingPage />} />
            <Route path="/register" element={<Navigate to="/" replace />} />
            <Route path="/register/patient" element={<PatientRegistrationPage />} />
            <Route path="/register/organization" element={<OrganizationRegistrationPage />} />
            <Route path="/mfa-setup" element={<MFASetupPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><MFARequiredRoute><PatientDashboard /></MFARequiredRoute></ProtectedRoute>} />
            <Route path="/hospitals" element={<HospitalsPage />} />
            <Route path="/doctors" element={<DoctorsPage />} />
            <Route path="/pharmacy" element={<PharmacyPage />} />
            <Route path="/lab" element={<LabPage />} />
            <Route path="/simple-booking" element={<SimpleBooking />} />
            <Route path="/appointments" element={<AppointmentsPage />} />
            <Route path="/:type/:id" element={<DetailsPage />} />
          </Routes>
          
          {/* Chatbot Widget - appears on all pages */}
          <ChatbotWidget userId={userId} userName={userName} />
        </div>
      </ToastProvider>
    </Router>
  );
}