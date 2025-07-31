import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import notificationService from '../services/notificationService';

const NotificationBell = ({ userId }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    // Load initial notifications
    const loadNotifications = async () => {
      if (userId) {
        const userNotifications = await notificationService.getNotifications(userId);
        setNotifications(userNotifications);
        setUnreadCount(userNotifications.filter(n => !n.read).length);
      }
    };
    
    loadNotifications();
    
    // Subscribe to new notifications
    const unsubscribe = notificationService.subscribe(userId, (notification) => {
      setNotifications(prev => [...prev, notification]);
      setUnreadCount(prev => prev + 1);
    });
    
    return () => {
      unsubscribe();
    };
  }, [userId]);

  const handleMarkAsRead = async (notificationId) => {
    const success = await notificationService.markAsRead(userId, notificationId);
    if (success) {
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  const handleMarkAllAsRead = async () => {
    const unreadNotifications = notifications.filter(n => !n.read);
    for (const notification of unreadNotifications) {
      await notificationService.markAsRead(userId, notification.id);
    }
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success': return '#10b981';
      case 'error': return '#ef4444';
      case 'warning': return '#f59e0b';
      default: return '#3b82f6';
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <button 
        onClick={() => setShowDropdown(!showDropdown)}
        style={{ 
          position: 'relative',
          padding: '0.5rem',
          borderRadius: '0.5rem',
          border: 'none',
          backgroundColor: '#f3f4f6',
          cursor: 'pointer'
        }}
      >
        <Bell size={20} color="#4b5563" />
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute',
            top: '-5px',
            right: '-5px',
            backgroundColor: '#ef4444',
            color: 'white',
            borderRadius: '50%',
            width: '18px',
            height: '18px',
            fontSize: '11px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {unreadCount}
          </span>
        )}
      </button>
      
      {showDropdown && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: '0',
          width: '320px',
          maxHeight: '400px',
          backgroundColor: 'white',
          borderRadius: '0.5rem',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          zIndex: 50,
          marginTop: '0.5rem',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Notifications</h3>
            {unreadCount > 0 && (
              <button 
                onClick={handleMarkAllAsRead}
                style={{
                  fontSize: '12px',
                  color: '#3b82f6',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                Mark all as read
              </button>
            )}
          </div>
          
          <div style={{
            overflowY: 'auto',
            maxHeight: '350px'
          }}>
            {notifications.length === 0 ? (
              <div style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>
                No notifications
              </div>
            ) : (
              notifications.map((notification) => (
                <div 
                  key={notification.id}
                  onClick={() => handleMarkAsRead(notification.id)}
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid #e5e7eb',
                    backgroundColor: notification.read ? 'white' : '#f9fafb',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s',
                    display: 'flex',
                    gap: '12px'
                  }}
                >
                  <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: getNotificationColor(notification.type),
                    marginTop: '6px'
                  }} />
                  <div>
                    <div style={{ fontWeight: notification.read ? '400' : '600', marginBottom: '4px' }}>
                      {notification.title}
                    </div>
                    <div style={{ fontSize: '13px', color: '#6b7280' }}>
                      {notification.message}
                    </div>
                    <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>
                      {new Date(notification.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;