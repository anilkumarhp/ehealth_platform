import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class AuthService {
  async register(userData) {
    try {
      // Log the request data for debugging (excluding sensitive fields)
      const debugData = { ...userData };
      if (debugData.password) debugData.password = '[REDACTED]';
      if (debugData.photo) debugData.photo = '[BASE64_IMAGE]';
      console.log('Register request data:', debugData);
      
      const response = await axios.post(`${API_URL}/api/v1/auth/register`, userData);
      console.log('Register response:', response.data);
      
      if (response.data.token) {
        localStorage.setItem('user', JSON.stringify({
          token: response.data.token.access_token,
          refreshToken: response.data.token.refresh_token,
          tokenType: response.data.token.token_type
        }));
      }
      return response.data;
    } catch (error) {
      console.error('Register error:', error);
      throw this.handleError(error);
    }
  }
  
  async registerWithMfa(userData) {
    try {
      // Log the request data for debugging (excluding sensitive fields)
      const debugData = { ...userData };
      if (debugData.password) debugData.password = '[REDACTED]';
      if (debugData.photo) debugData.photo = '[BASE64_IMAGE]';
      console.log('Register with MFA request data:', debugData);
      
      const response = await axios.post(`${API_URL}/api/v1/auth/register-with-mfa`, userData);
      console.log('Register with MFA response:', response.data);
      
      if (response.data.token) {
        localStorage.setItem('user', JSON.stringify({
          token: response.data.token.access_token,
          refreshToken: response.data.token.refresh_token,
          tokenType: response.data.token.token_type
        }));
      }
      return response.data;
    } catch (error) {
      console.error('Register with MFA error:', error);
      throw this.handleError(error);
    }
  }

  async login(email, password, role = null) {
    try {
      console.log('Login request:', { email, role });
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
        email,
        password,
        role
      });
      
      console.log('Login response:', response.data);
      
      if (response.data.mfa_required) {
        return {
          mfaRequired: true,
          mfaToken: response.data.mfa_token
        };
      }
      
      if (response.data.token) {
        localStorage.setItem('user', JSON.stringify({
          token: response.data.token.access_token,
          refreshToken: response.data.token.refresh_token,
          tokenType: response.data.token.token_type
        }));
      }
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw this.handleError(error);
    }
  }

  async completeMfaSetup(userId, mfaSecret, otp) {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/complete-mfa-setup`, {
        user_id: userId,
        mfa_secret: mfaSecret,
        otp: otp
      });
      
      if (response.data.access_token) {
        localStorage.setItem('user', JSON.stringify({
          token: response.data.access_token,
          refreshToken: response.data.refresh_token,
          tokenType: response.data.token_type
        }));
      }
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyMfa(mfaToken, otp) {
    try {
      console.log('Verifying MFA with token:', mfaToken, 'and OTP:', otp);
      
      const response = await axios.post(`${API_URL}/api/v1/auth/login/verify-mfa`, {
        mfa_token: mfaToken,
        otp
      });
      
      console.log('MFA verification response:', response.data);
      
      if (response.data.access_token) {
        localStorage.setItem('user', JSON.stringify({
          token: response.data.access_token,
          refreshToken: response.data.refresh_token,
          tokenType: response.data.token_type
        }));
      }
      
      return response.data;
    } catch (error) {
      console.error('MFA verification error:', error);
      throw this.handleError(error);
    }
  }

  async logout() {
    try {
      const user = this.getCurrentUser();
      if (user && user.refreshToken) {
        await axios.post(`${API_URL}/api/v1/auth/logout`, {
          refresh_token: user.refreshToken
        });
      }
      localStorage.removeItem('user');
    } catch (error) {
      console.error('Logout error:', error);
      // Still remove the user from localStorage even if the API call fails
      localStorage.removeItem('user');
    }
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch (e) {
      return null;
    }
  }

  isAuthenticated() {
    return !!this.getCurrentUser();
  }
  
  isMfaRequired() {
    // Check if the user has MFA enabled by examining the token claims
    const user = this.getCurrentUser();
    if (!user || !user.token) return false;
    
    try {
      // Parse the JWT token to check for MFA claims
      // This is a simplified approach - in a real app you'd verify the token properly
      const tokenParts = user.token.split('.');
      if (tokenParts.length !== 3) return false;
      
      const payload = JSON.parse(atob(tokenParts[1]));
      return payload.mfa_enabled === true;
    } catch (e) {
      console.error('Error checking MFA status:', e);
      return false;
    }
  }

  getAuthHeader() {
    const user = this.getCurrentUser();
    if (user && user.token) {
      return { Authorization: `Bearer ${user.token}` };
    }
    return {};
  }
  
  async uploadFile(file, fileType = 'profile_photo') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('file_type', fileType);
      
      // Using simplified endpoint without authentication
      const response = await axios.post(
        `${API_URL}/api/v1/files/upload`, 
        formData,
        { 
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('File upload error:', error);
      throw this.handleError(error);
    }
  }

  handleError(error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API error response:', error.response.data);
      
      // Return the original error with response data attached for more detailed handling
      error.apiResponse = error.response.data;
      return error;
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Network error:', error);
      return new Error('No response received from server. Please check if the backend service is running.');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request setup error:', error);
      return new Error('Error setting up request');
    }
  }
}

export default new AuthService();