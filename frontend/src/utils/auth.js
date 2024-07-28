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

export const googleLogin = async (code) => {
    try {
      const response = await api.get(`/auth/google/callback/?code=${code}`);
      localStorage.setItem(ACCESS_TOKEN, response.data.access);
      localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
      return response.data;
    } catch (error) {
      throw error;
    }
  };


export const redirectAfterLogin = (navigate) => {
  const redirectPath = sessionStorage.getItem('redirectPath') || '/';
  sessionStorage.removeItem('redirectPath');
  navigate(redirectPath, { replace: true });
};


export const logout = () => {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(REFRESH_TOKEN);
};