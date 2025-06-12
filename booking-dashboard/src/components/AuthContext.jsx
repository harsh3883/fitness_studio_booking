import { createContext, useState, useContext, useEffect } from 'react';
import {API_BASE_URL} from '../api/api'; 


const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
        const loginData = {
          username: credentials.email,
          password: credentials.password
        };
        console.log(loginData)

      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        
        body: JSON.stringify(loginData),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setUser(data.user);
        return { success: true };
      } else {
        const errorData = await response.json();
        console.error('Login error response:', errorData);
        return { 
          success: false, 
          error: errorData.message || errorData.detail || 'Login failed' 
        };
      }
    } catch (error) {
      console.error('Login network error:', error);
      return { success: false, error: 'Network error occurred' };
    }
  };

  const register = async (userData) => {
    try {
      // Ensure username is included - auto-generate from email if not provided
      const registrationData = {
        ...userData,
        username: userData.username || userData.email.split('@')[0]
      };

      console.log('Sending registration data:', registrationData);

      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData),
      });

      const data = await response.json();
      console.log('Registration response:', data);

      if (response.ok) {
        // Handle successful registration
        if (data.token) {
          localStorage.setItem('token', data.token);
        }
        if (data.user) {
          setUser(data.user);
        }
        return { success: true, data };
      } else {
        console.error('Registration error response:', data);
        return { 
          success: false, 
          error: data.message || data.detail || Object.values(data)[0] || 'Registration failed' 
        };
      }
    } catch (error) {
      console.error('Registration network error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};