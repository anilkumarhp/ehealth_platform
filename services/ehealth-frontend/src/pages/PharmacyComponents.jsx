import React, { useState } from 'react';
import { Link } from 'react-router-dom';
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
  Settings,
  Mail,
  ChevronRight,
  MapPin,
  Phone,
  Clock,
  ShoppingBag,
  Activity,
  Heart
} from 'lucide-react';

const PurchaseCard = ({ purchase }) => (
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
          <Pill className="w-5 h-5 text-blue-600" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
            {purchase.pharmacyName}
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
          <MapPin className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{purchase.address}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.75rem' }}>
          <Clock className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            Purchased on {new Date(purchase.date).toLocaleDateString()}
          </span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
          {purchase.items.map((item, index) => (
            <span key={index} style={{
              fontSize: '0.75rem',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.25rem'
            }}>
              {item}
            </span>
          ))}
        </div>
        <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#111827' }}>
          Total: ${purchase.total.toFixed(2)}
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
        <ShoppingBag className="w-4 h-4" />
        Reorder
      </button>
    </div>
  </div>
);

const PharmacyCard = ({ pharmacy }) => (
  <Link to={`/pharmacies/${pharmacy.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
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
          <Pill className="w-5 h-5 text-blue-600" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
            {pharmacy.name}
          </h3>
          <span style={{
            fontSize: '0.75rem',
            backgroundColor: pharmacy.openNow ? '#dcfce7' : '#fee2e2',
            color: pharmacy.openNow ? '#166534' : '#b91c1c',
            padding: '0.25rem 0.5rem',
            borderRadius: '0.25rem',
            marginLeft: '0.5rem'
          }}>
            {pharmacy.openNow ? 'Open Now' : 'Closed'}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
          <MapPin className="w-4 h-4 text-gray-500" />
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{pharmacy.address}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Phone className="w-4 h-4 text-gray-500" />
            <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{pharmacy.phone}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ color: '#fbbf24' }}>★</span>
            <span style={{ fontWeight: '600', color: '#111827' }}>{pharmacy.rating}</span>
          </div>
        </div>
        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
          <strong>Distance:</strong> {pharmacy.distance}
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
        Order
      </button>
    </div>
  </div>
);

const PharmacyAdsSection = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Medicine Delivery</h3>
      <div style={{ backgroundColor: '#f0f9ff', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🚚</div>
        <p style={{ fontSize: '0.875rem', color: '#0369a1' }}>Free delivery on orders above $25</p>
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
      }}>Order Now</button>
    </div>
    
    <div style={{
      backgroundColor: 'white',
      borderRadius: '0.75rem',
      padding: '1.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      textAlign: 'center'
    }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '1rem' }}>Health Supplements</h3>
      <div style={{ backgroundColor: '#dcfce7', padding: '2rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💊</div>
        <p style={{ fontSize: '0.875rem', color: '#166534' }}>20% off on all supplements</p>
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
      }}>Shop Now</button>
    </div>
  </div>
);

const Sidebar = ({ activeMenu, setActiveMenu }) => {
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

const Header = ({ userData }) => (
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

export { PurchaseCard, PharmacyCard, PharmacyAdsSection, Sidebar, Header };