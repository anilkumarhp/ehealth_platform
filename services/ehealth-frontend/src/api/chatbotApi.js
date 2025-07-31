import axios from 'axios';

const CHATBOT_API_URL = process.env.REACT_APP_CHATBOT_API_URL || 'http://localhost:8002/api/v1';

export const chatbotApi = {
  sendMessage: async (userId, message, location, conversationId) => {
    try {
      const response = await axios.post(`${CHATBOT_API_URL}/chat`, {
        user_id: userId,
        message,
        location,
        conversation_id: conversationId
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message to chatbot:', error);
      throw error;
    }
  },
  
  getConversations: async (userId) => {
    try {
      const response = await axios.get(`${CHATBOT_API_URL}/conversations/user/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting conversations:', error);
      throw error;
    }
  },
  
  getConversation: async (conversationId) => {
    try {
      const response = await axios.get(`${CHATBOT_API_URL}/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  }
};

export default chatbotApi;