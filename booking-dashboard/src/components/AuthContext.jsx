import React, { createContext, useState, useContext, useEffect } from 'react';

// Environment-based API base URL
const API_BASE_URL = "http://localhost:8000" ;

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
      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setUser(data.user);
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.message };
      }
    } catch (error) {
      return { success: false, error: 'Network error occurred' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setUser(data.user);
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.message };
      }
    } catch (error) {
      return { success: false, error: 'Network error occurred' };
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
