import { useToast } from '../context/SimpleToastContext';

/**
 * A custom hook for showing notifications
 * @returns {Object} notification methods
 */
export const useNotification = () => {
  const toast = useToast();
  
  /**
   * Show a success notification
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds (default: 4000)
   */
  const showSuccess = (message, duration = 4000) => {
    toast.success(message, duration);
  };
  
  /**
   * Show an error notification
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds (default: 4000)
   */
  const showError = (message, duration = 4000) => {
    toast.error(message, duration);
  };
  
  /**
   * Show a warning notification
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds (default: 4000)
   */
  const showWarning = (message, duration = 4000) => {
    toast.warning(message, duration);
  };
  
  /**
   * Show an info notification
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds (default: 4000)
   */
  const showInfo = (message, duration = 4000) => {
    toast.info(message, duration);
  };
  
  return {
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};

export default useNotification;