import { useState } from 'react';
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
  Activity,
  Heart
} from 'lucide-react';

const Sidebar = ({ activeMenu, setActiveMenu }) => {
  const [expandedMenus, setExpandedMenus] = useState({ hospital: true });
  
  const toggleMenu = (menuKey) => {
    setExpandedMenus(prev => ({ ...prev, [menuKey]: !prev[menuKey] }));
  };
  
  const handleNavigation = (key) => {
    if (key === 'dashboard') {
      window.location.href = '/patient-dashboard';
    } else if (key === 'pharmacy') {
      window.location.href = '/pharmacy';
    } else if (key === 'doctors') {
      window.location.href = '/doctors';
    } else if (key === 'hospitals') {
      window.location.href = '/hospitals';
    } else if (key === 'lab') {
      window.location.href = '/lab';
    } else if (key === 'appointments') {
      window.location.href = '/appointments';
    } else {
      setActiveMenu(key);
    }
  };
  
  const mainMenuItems = [
    { key: 'dashboard', icon: <Home className="w-5 h-5" />, label: 'Dashboard' },
    { key: 'hospital', icon: <Hospital className="w-5 h-5" />, label: 'Hospital', submenu: [
        { key: 'hospitals', label: 'Hospitals' },
        { key: 'doctors', label: 'Doctors' }
      ]},
    { key: 'pharmacy', icon: <Pill className="w-5 h-5" />, label: 'Pharmacy' },
    { key: 'lab', icon: <FlaskConical className="w-5 h-5" />, label: 'Lab' },
    { key: 'messages', icon: <MessageSquare className="w-5 h-5" />, label: 'Messages' },
    { key: 'trackings', icon: <Activity className="w-5 h-5" />, label: 'Trackings' },
    { key: 'payments', icon: <Bell className="w-5 h-5" />, label: 'Payments' },
    { key: 'analytics', icon: <Heart className="w-5 h-5" />, label: 'Analytics' },
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
              <button 
                onClick={() => {
                  if (item.submenu) {
                    toggleMenu(item.key);
                  } else {
                    handleNavigation(item.key);
                  }
                }} 
                style={{ 
                  width: '100%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.75rem', 
                  padding: '0.75rem', 
                  borderRadius: '0.5rem', 
                  border: 'none', 
                  backgroundColor: activeMenu === item.key ? '#dbeafe' : 'transparent', 
                  color: activeMenu === item.key ? '#1d4ed8' : '#6b7280', 
                  cursor: 'pointer', 
                  transition: 'all 0.2s', 
                  marginBottom: '0.25rem' 
                }}
              >
                {item.icon}
                <span style={{ flex: 1, textAlign: 'left' }}>{item.label}</span>
                {item.submenu && (
                  <ChevronRight 
                    className="w-4 h-4" 
                    style={{ 
                      transform: expandedMenus[item.key] ? 'rotate(90deg)' : 'rotate(0deg)',
                      transition: 'transform 0.2s'
                    }} 
                  />
                )}
              </button>
              
              {item.submenu && expandedMenus[item.key] && (
                <div style={{ marginLeft: '2rem', marginBottom: '0.5rem' }}>
                  {item.submenu.map((subItem) => (
                    <button
                      key={subItem.key}
                      onClick={() => handleNavigation(subItem.key)}
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

export default Sidebar;