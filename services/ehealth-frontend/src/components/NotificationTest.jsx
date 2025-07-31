import React, { useEffect, useState } from 'react';
import notificationService from '../services/notificationService';

const NotificationTest = () => {
  const [notifications, setNotifications] = useState([]);
  const [userId, setUserId] = useState('test-user-123');
  
  useEffect(() => {
    // Subscribe to notifications
    const unsubscribe = notificationService.subscribe(userId, (notification) => {
      console.log('New notification received:', notification);
      setNotifications(prev => [...prev, notification]);
    });
    
    // Get existing notifications
    const fetchNotifications = async () => {
      const data = await notificationService.getNotifications(userId);
      console.log('Fetched notifications:', data);
      setNotifications(data.notifications || []);
    };
    
    fetchNotifications();
    
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
    }
  };
  
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Notifications Test</h2>
      
      <div className="mb-4">
        <label className="block mb-2">User ID:</label>
        <input 
          type="text" 
          value={userId} 
          onChange={(e) => setUserId(e.target.value)}
          className="border p-2 w-full"
        />
      </div>
      
      <div className="mb-4">
        <h3 className="font-bold">Notifications ({notificationService.getUnreadCount()} unread)</h3>
        {notifications.length === 0 ? (
          <p className="text-gray-500">No notifications</p>
        ) : (
          <ul className="border rounded divide-y">
            {notifications.map((notification) => (
              <li 
                key={notification.id} 
                className={`p-3 ${notification.read ? 'bg-gray-100' : 'bg-blue-50'}`}
              >
                <div className="flex justify-between">
                  <span className="font-bold">{notification.title}</span>
                  <span className="text-sm text-gray-500">{notification.created_at}</span>
                </div>
                <p>{notification.message}</p>
                {!notification.read && (
                  <button 
                    onClick={() => handleMarkAsRead(notification.id)}
                    className="text-sm text-blue-500 mt-2"
                  >
                    Mark as read
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default NotificationTest;