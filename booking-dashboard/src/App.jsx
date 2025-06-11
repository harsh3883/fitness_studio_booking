import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/NavBar';
import Home from './components/Home';
import Classes from './components/Classes';
import BookingPage from './components/BookingPage';
import Profile from './components/Profile';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import { AuthProvider, useAuth } from './components/AuthContext';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/classes" element={<Classes />} />
              <Route path="/booking/:classId" element={<BookingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
};

export default App;
