import React from 'react';
import { useToast } from '../context/SimpleToastContext';

const NotificationExample = () => {
  const toast = useToast();
  
  const showSuccessNotification = () => {
    toast.success('Operation completed successfully!', 4000);
  };
  
  const showErrorNotification = () => {
    toast.error('An error occurred. Please try again.', 4000);
  };
  
  const showWarningNotification = () => {
    toast.warning('Please complete all required fields.', 4000);
  };
  
  const showInfoNotification = () => {
    toast.info('Your session will expire in 5 minutes.', 4000);
  };
  
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Notification Examples</h2>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={showSuccessNotification}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Show Success
        </button>
        <button
          onClick={showErrorNotification}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Show Error
        </button>
        <button
          onClick={showWarningNotification}
          className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
        >
          Show Warning
        </button>
        <button
          onClick={showInfoNotification}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Show Info
        </button>
      </div>
    </div>
  );
};

export default NotificationExample;