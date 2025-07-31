import React from 'react';
import { Link } from 'react-router-dom';

const BasicLandingPage = () => {
  return (
    <div style={{ 
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* Navbar */}
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        borderBottom: '1px solid #e5e7eb',
        backgroundColor: 'white'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            backgroundColor: '#3b82f6', 
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            marginRight: '10px'
          }}>
            E
          </div>
          <span style={{ fontWeight: 'bold', fontSize: '1.25rem' }}>eHealth Platform</span>
        </div>
        <Link to="/login" style={{ 
          textDecoration: 'none', 
          color: '#3b82f6',
          fontWeight: '500'
        }}>
          Login
        </Link>
      </nav>

      {/* Main Content */}
      <main style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        backgroundColor: '#f9fafb'
      }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 'bold',
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          eHealth Platform
        </h1>
        
        <p style={{ 
          fontSize: '1.25rem',
          color: '#6b7280',
          maxWidth: '600px',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          Your comprehensive healthcare solution for managing appointments, 
          prescriptions, and connecting with healthcare providers.
        </p>
        
        <div style={{ 
          width: '100%',
          maxWidth: '400px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
          <h2 style={{ 
            fontSize: '1.5rem',
            fontWeight: 'bold',
            marginBottom: '1.5rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Register
          </h2>
          
          <div style={{ 
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            width: '100%'
          }}>
            <Link to="/register/patient" style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              textAlign: 'center',
              textDecoration: 'none',
              fontWeight: '500'
            }}>
              As Patient
            </Link>
            
            <Link to="/register/organization" style={{
              backgroundColor: 'white',
              color: '#3b82f6',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              textAlign: 'center',
              textDecoration: 'none',
              fontWeight: '500',
              border: '1px solid #3b82f6'
            }}>
              As Organization
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default BasicLandingPage;