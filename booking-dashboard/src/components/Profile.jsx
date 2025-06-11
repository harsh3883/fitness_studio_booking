import React, { useState } from 'react';
import { useAuth } from '../components/AuthContext';
import './Profile.css';

const Profile = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    date_of_birth: user?.date_of_birth || ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/profile/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setMessage('Profile updated successfully!');
        setIsEditing(false);
      } else {
        setMessage('Failed to update profile');
      }
    } catch (error) {
      setMessage('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      date_of_birth: user?.date_of_birth || ''
    });
    setIsEditing(false);
    setMessage('');
  };

  return (
    <div className="profile-page">
      <div className="container">
        <div className="profile-header">
          <h1>My Profile</h1>
          {!isEditing && (
            <button 
              onClick={() => setIsEditing(true)}
              className="btn btn-primary"
            >
              Edit Profile
            </button>
          )}
        </div>

        {message && (
          <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <div className="profile-content">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Last Name</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                disabled={!isEditing}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                disabled={!isEditing}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="date_of_birth">Date of Birth</label>
              <input
                type="date"
                id="date_of_birth"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleInputChange}
                disabled={!isEditing}
                required
              />
            </div>

            {isEditing && (
              <div className="form-actions">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Save Changes'}
                </button>
                <button 
                  type="button" 
                  onClick={handleCancel}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;