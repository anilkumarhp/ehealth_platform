import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';
import MFAVerificationModal from './MFAVerificationModal';

const MFARequiredRoute = ({ children }) => {
  const [showMfaModal, setShowMfaModal] = useState(false);
  const [mfaToken, setMfaToken] = useState('');
  const [isVerifying, setIsVerifying] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const checkMfaStatus = async () => {
      try {
        // Check if user is authenticated
        const user = authService.getCurrentUser();
        if (!user) {
          setIsVerifying(false);
          return;
        }

        // Check if MFA is required
        const mfaRequired = authService.isMfaRequired();
        
        if (mfaRequired) {
          // Get MFA token for verification
          try {
            // In a real implementation, you would get this from the server
            // For now, we'll simulate it
            setMfaToken('mfa_token_placeholder');
            setShowMfaModal(true);
          } catch (error) {
            console.error('Error getting MFA token:', error);
          }
        } else {
          // MFA not required, user is authenticated
          setIsAuthenticated(true);
        }
        
        setIsVerifying(false);
      } catch (error) {
        console.error('Error checking MFA status:', error);
        setIsVerifying(false);
      }
    };

    checkMfaStatus();
  }, []);

  const handleMfaSuccess = () => {
    setShowMfaModal(false);
    setIsAuthenticated(true);
  };

  const handleMfaCancel = () => {
    // Log the user out if they cancel MFA verification
    authService.logout();
    setShowMfaModal(false);
    setIsAuthenticated(false);
  };

  if (isVerifying) {
    // Show loading state while checking MFA status
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!authService.getCurrentUser()) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (showMfaModal) {
    // Show MFA verification modal
    return (
      <>
        {children}
        <MFAVerificationModal 
          mfaToken={mfaToken} 
          onSuccess={handleMfaSuccess} 
          onCancel={handleMfaCancel} 
        />
      </>
    );
  }

  // User is authenticated and MFA is verified if required
  return children;
};

export default MFARequiredRoute;