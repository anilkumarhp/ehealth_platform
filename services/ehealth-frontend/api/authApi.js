import axiosClient from './axiosClient';

export const authApi = {
  login: async (email, password) => {
    try {
      const response = await axiosClient.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Login failed' };
    }
  },
  
  register: async (userData) => {
    try {
      const response = await axiosClient.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Registration failed' };
    }
  },
  
  forgotPassword: async (email) => {
    try {
      const response = await axiosClient.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Password reset request failed' };
    }
  },
  
  resetPassword: async (token, newPassword) => {
    try {
      const response = await axiosClient.post('/auth/reset-password', { 
        token, 
        new_password: newPassword 
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Password reset failed' };
    }
  },
  
  refreshToken: async (refreshToken) => {
    try {
      const response = await axiosClient.post('/auth/refresh-token', { refresh_token: refreshToken });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Token refresh failed' };
    }
  },
  
  logout: async (refreshToken) => {
    try {
      const response = await axiosClient.post('/auth/logout', { refresh_token: refreshToken });
      return response.data;
    } catch (error) {
      throw error.response?.data || { detail: 'Logout failed' };
    }
  }
};

export default authApi;