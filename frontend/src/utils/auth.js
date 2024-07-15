import api from '../api';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../constants';

export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/token/', { email, password });
    localStorage.setItem(ACCESS_TOKEN, response.data.access);
    localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const register = async (email, password, profileData) => {
  try {
    const response = await api.post('/auth/register/', { email, password, profile: profileData });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(REFRESH_TOKEN);
};