import axios from 'axios';
import authService from './authService';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class UserService {
  async getUserProfile() {
    try {
      const response = await axios.get(`${API_URL}/api/v1/profile/me`, {
        headers: {
          ...authService.getAuthHeader()
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw this.handleError(error);
    }
  }
  
  async updateUserProfile(profileData) {
    try {
      const response = await axios.put(`${API_URL}/api/v1/profile/me`, profileData, {
        headers: {
          ...authService.getAuthHeader()
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw this.handleError(error);
    }
  }
  
  async updateProfilePhoto(photoFile) {
    try {
      const formData = new FormData();
      formData.append('file', photoFile);
      
      const response = await axios.post(
        `${API_URL}/api/v1/profile/me/photo`, 
        formData,
        {
          headers: {
            ...authService.getAuthHeader(),
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating profile photo:', error);
      throw this.handleError(error);
    }
  }
  
  async updateProfilePhotoBase64(base64Photo) {
    try {
      const response = await axios.post(
        `${API_URL}/api/v1/profile/me/photo/base64`, 
        { photo: base64Photo },
        {
          headers: {
            ...authService.getAuthHeader(),
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating profile photo:', error);
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
  
  async getProfileTabs() {
    try {
      const response = await axios.get(`${API_URL}/api/v1/profile/me/profile-tabs`, {
        headers: {
          ...authService.getAuthHeader()
        }
      });
      
      // Get presigned URL for profile photo if it exists
      if (response.data.profile_photo_url) {
        try {
          const photoResponse = await axios.get(`${API_URL}/api/v1/profile/me/photo-url`, {
            headers: {
              ...authService.getAuthHeader()
            }
          });
          if (photoResponse.data.photo_url) {
            response.data.profile_photo_url = photoResponse.data.photo_url;
          }
        } catch (photoError) {
          console.error('Error fetching photo URL:', photoError);
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('Error fetching profile tabs:', error);
      throw this.handleError(error);
    }
  }
}

export default new UserService();