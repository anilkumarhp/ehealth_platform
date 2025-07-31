import { io } from 'socket.io-client';

class NotificationService {
  constructor() {
    this.socket = io('/ws');
    this.listeners = [];
    this.notifications = [];
    
    this.socket.on('notification', (notification) => {
      this.notifications.push(notification);
      this.listeners.forEach(listener => listener(notification));
    });
  }
  
  subscribe(userId, callback) {
    this.socket.emit('subscribe', { userId });
    this.listeners.push(callback);
    
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }
  
  async getNotifications(userId) {
    try {
      const response = await fetch(`/notification-api/api/v1/notifications/user/${userId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch notifications');
      }
      const data = await response.json();
      this.notifications = data;
      return data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  }
  
  async markAsRead(userId, notificationId) {
    try {
      const response = await fetch(`/notification-api/api/v1/notifications/user/${userId}/${notificationId}/read`, {
        method: 'PUT'
      });
      
      if (!response.ok) {
        throw new Error('Failed to mark notification as read');
      }
      
      // Update local notifications
      this.notifications = this.notifications.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      );
      
      return true;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return false;
    }
  }
  
  getUnreadCount() {
    return this.notifications.filter(n => !n.read).length;
  }
}

export default new NotificationService();