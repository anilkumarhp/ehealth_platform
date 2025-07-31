import React from 'react';

const MFASetupTab = ({ formData, handleInputChange }) => {
  return (
    <div>
      <div style={{
        padding: '1rem',
        backgroundColor: '#f0f9ff',
        border: '1px solid #bae6fd',
        borderRadius: '0.5rem'
      }}>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          cursor: 'pointer',
          fontWeight: '500',
          color: '#111827'
        }}>
          <input
            type="checkbox"
            name="enableMfa"
            checked={formData.enableMfa}
            onChange={handleInputChange}
            style={{
              width: '1rem',
              height: '1rem',
              cursor: 'pointer'
            }}
          />
          Enable Multi-Factor Authentication (MFA)
        </label>
        <p style={{
          fontSize: '0.875rem',
          color: '#6b7280',
          marginTop: '0.25rem',
          marginLeft: '1.5rem'
        }}>
          Enhance your account security with an additional layer of protection
        </p>
      </div>
      
      {formData.enableMfa && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#fffbeb',
          border: '1px solid #fcd34d',
          borderRadius: '0.5rem'
        }}>
          <p style={{
            color: '#92400e',
            fontWeight: '500'
          }}>
            MFA Setup Process
          </p>
          <ol style={{
            fontSize: '0.875rem',
            color: '#92400e',
            marginTop: '0.5rem',
            paddingLeft: '1.5rem'
          }}>
            <li style={{ marginBottom: '0.5rem' }}>After registration, you'll be directed to the MFA setup page</li>
            <li style={{ marginBottom: '0.5rem' }}>You'll need to scan a QR code with an authenticator app (Google Authenticator, Authy, etc.)</li>
            <li style={{ marginBottom: '0.5rem' }}>Enter the 6-digit code from your authenticator app to complete setup</li>
            <li>Once verified, you'll be taken to your dashboard</li>
          </ol>
          <p style={{
            fontSize: '0.875rem',
            color: '#92400e',
            marginTop: '1rem',
            fontWeight: '500'
          }}>
            For future logins, you'll need to enter both your password and the code from your authenticator app.
          </p>
        </div>
      )}
    </div>
  );
};

export default MFASetupTab;