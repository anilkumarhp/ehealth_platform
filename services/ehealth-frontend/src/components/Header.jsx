import React from 'react';
import { Bell, Settings, Mail } from 'lucide-react';
import NotificationBell from './NotificationBell';

const Header = ({ userData }) => (
  <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', height: '80px', position: 'sticky', top: 0, zIndex: 10 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <NotificationBell userId={userData.id || 'guest'} />
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

export default Header;