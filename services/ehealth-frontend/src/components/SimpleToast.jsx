import React, { useState, useEffect } from 'react';

const SimpleToast = ({ message, type = 'success', duration = 3000, onClose }) => {
  const [visible, setVisible] = useState(true);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => {
        onClose && onClose();
      }, 300); // Wait for fade out animation
    }, duration);
    
    return () => clearTimeout(timer);
  }, [duration, onClose]);
  
  const getColors = () => {
    switch (type) {
      case 'success':
        return {
          bg: '#ecfdf5',
          border: '#10b981',
          text: '#065f46'
        };
      case 'error':
        return {
          bg: '#fef2f2',
          border: '#ef4444',
          text: '#991b1b'
        };
      case 'warning':
        return {
          bg: '#fffbeb',
          border: '#f59e0b',
          text: '#92400e'
        };
      case 'info':
        return {
          bg: '#eff6ff',
          border: '#3b82f6',
          text: '#1e40af'
        };
      default:
        return {
          bg: '#eff6ff',
          border: '#3b82f6',
          text: '#1e40af'
        };
    }
  };
  
  const colors = getColors();
  
  return (
    <div
      style={{
        position: 'fixed',
        top: '1rem',
        right: '1rem',
        zIndex: 9999,
        maxWidth: '24rem',
        backgroundColor: colors.bg,
        borderLeft: `4px solid ${colors.border}`,
        borderRadius: '0.375rem',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        padding: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        opacity: visible ? 1 : 0,
        transform: `translateX(${visible ? 0 : '1rem'})`,
        transition: 'opacity 0.3s, transform 0.3s',
        color: colors.text
      }}
    >
      <div>
        {message}
      </div>
      <button
        onClick={() => {
          setVisible(false);
          setTimeout(() => {
            onClose && onClose();
          }, 300);
        }}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '0.25rem',
          color: colors.text,
          opacity: 0.7
        }}
      >
        ✕
      </button>
    </div>
  );
};

export default SimpleToast;