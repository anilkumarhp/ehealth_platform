import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { useToast } from '../context/SimpleToastContext';

const MFASetupPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  const [otp, setOtp] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [countdown, setCountdown] = useState(300); // 5 minutes countdown
  
  // Get MFA setup data from location state
  const { userId, mfaSecret, qrCode, email } = location.state || {};
  
  useEffect(() => {
    // Redirect if no MFA setup data
    if (!userId) {
      navigate('/register/patient');
      return;
    }
    
    // If QR code or MFA secret is missing, use placeholder
    if (!qrCode) {
      console.warn('QR code is missing, using placeholder');
    }
    
    if (!mfaSecret) {
      console.warn('MFA secret is missing, using placeholder');
    }
    
    // Start countdown
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [userId, mfaSecret, qrCode, navigate]);
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!otp) {
      setError('Please enter the verification code');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError('');
      
      const response = await authService.completeMfaSetup(userId, mfaSecret, otp);
      console.log('MFA setup completed:', response);
      
      // After successful MFA setup, navigate to dashboard with success message
      navigate('/dashboard', { 
        state: { 
          showProfile: true,
          mfaSuccess: true,
          message: 'MFA setup completed successfully! Your account is now more secure.' 
        } 
      });
    } catch (err) {
      setError(err.message || 'Failed to verify code. Please try again.');
      setIsSubmitting(false);
    }
  };
  
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f9fafb',
      fontFamily: 'Inter, sans-serif',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <header style={{
        width: '100%',
        height: '64px',
        padding: '0 2rem',
        backgroundColor: 'white',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{
          fontSize: '1.25rem',
          fontWeight: 'bold',
          color: '#111827'
        }}>
          Ehealth Platform
        </div>
      </header>
      
      {/* Main Content */}
      <main style={{
        flex: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '2rem'
      }}>
        <div style={{
          maxWidth: '500px',
          width: '100%',
          backgroundColor: 'white',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '1.5rem',
            borderBottom: '1px solid #e5e7eb',
            textAlign: 'center'
          }}>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: '#111827'
            }}>
              Set Up Multi-Factor Authentication
            </h1>
            <p style={{
              color: '#6b7280',
              marginTop: '0.5rem'
            }}>
              Complete the setup to secure your account
            </p>
            
            {/* Countdown Timer */}
            <div style={{
              marginTop: '1rem',
              padding: '0.5rem',
              backgroundColor: countdown < 60 ? '#fee2e2' : '#f0f9ff',
              borderRadius: '0.25rem',
              color: countdown < 60 ? '#b91c1c' : '#0369a1',
              fontWeight: '500'
            }}>
              Time remaining: {formatTime(countdown)}
            </div>
          </div>
          
          <div style={{ padding: '1.5rem' }}>
            {/* Error message */}
            {error && (
              <div style={{
                backgroundColor: '#fee2e2',
                color: '#b91c1c',
                padding: '0.75rem',
                borderRadius: '0.375rem',
                marginBottom: '1rem'
              }}>
                {error}
              </div>
            )}
            
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '1.5rem'
            }}>
              {/* Step 1: Install App */}
              <div>
                <h2 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '0.5rem'
                }}>
                  Step 1: Install an Authenticator App
                </h2>
                <p style={{
                  fontSize: '0.875rem',
                  color: '#6b7280'
                }}>
                  If you haven't already, download and install an authenticator app like Google Authenticator, Authy, or Microsoft Authenticator.
                </p>
              </div>
              
              {/* Step 2: Scan QR Code */}
              <div>
                <h2 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '0.5rem'
                }}>
                  Step 2: Scan the QR Code
                </h2>
                <p style={{
                  fontSize: '0.875rem',
                  color: '#6b7280',
                  marginBottom: '1rem'
                }}>
                  Open your authenticator app and scan this QR code:
                </p>
                
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  marginBottom: '1rem'
                }}>
                  <div style={{
                    border: '1px solid #e5e7eb',
                    padding: '0.5rem',
                    borderRadius: '0.25rem',
                    backgroundColor: 'white'
                  }}>
                    <img 
                      src={`https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl=${encodeURIComponent(qrCode)}`}
                      alt="QR Code"
                      style={{
                        width: '200px',
                        height: '200px'
                      }}
                    />
                  </div>
                </div>
                
                <div style={{
                  backgroundColor: '#fffbeb',
                  border: '1px solid #fcd34d',
                  borderRadius: '0.25rem',
                  padding: '0.75rem',
                  fontSize: '0.875rem',
                  color: '#92400e'
                }}>
                  <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>
                    Can't scan the QR code?
                  </p>
                  <p>
                    Enter this code manually in your authenticator app:
                  </p>
                  <div style={{
                    backgroundColor: 'white',
                    border: '1px solid #fcd34d',
                    borderRadius: '0.25rem',
                    padding: '0.5rem',
                    marginTop: '0.5rem',
                    fontFamily: 'monospace',
                    wordBreak: 'break-all',
                    textAlign: 'center'
                  }}>
                    {mfaSecret || 'JBSWY3DPEHPK3PXP'}
                  </div>
                </div>
              </div>
              
              {/* Step 3: Enter Code */}
              <form onSubmit={handleSubmit}>
                <h2 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '0.5rem'
                }}>
                  Step 3: Enter the Verification Code
                </h2>
                <p style={{
                  fontSize: '0.875rem',
                  color: '#6b7280',
                  marginBottom: '1rem'
                }}>
                  Enter the 6-digit code from your authenticator app:
                </p>
                
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  maxLength="6"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '1.25rem',
                    textAlign: 'center',
                    letterSpacing: '0.25em',
                    marginBottom: '1.5rem'
                  }}
                />
                
                <button
                  type="submit"
                  disabled={isSubmitting || countdown === 0 || otp.length !== 6}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: isSubmitting || countdown === 0 || otp.length !== 6 ? '#9ca3af' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    fontWeight: '500',
                    cursor: isSubmitting || countdown === 0 || otp.length !== 6 ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {isSubmitting ? 'Verifying...' : 'Verify and Complete Setup'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MFASetupPage;