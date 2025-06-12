// pages/Dashboard.jsx - Updated Dashboard
import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import { classesAPI } from '../api/api'; 
import './DashBoard.css'

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await classesAPI.getAll();
      setClasses(data);
    } catch (error) {
      console.error('Error fetching classes:', error);
      setError('Failed to load classes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBookClass = async (classId) => {
    try {
      // You can implement booking logic here
      console.log('Booking class:', classId);
      // await bookingsAPI.create({ class_id: classId });
      // fetchClasses(); // Refresh classes after booking
    } catch (error) {
      console.error('Error booking class:', error);
      setError('Failed to book class. Please try again.');
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Welcome back, {user?.first_name || 'User'}!</h1>
          <button onClick={handleLogout} className="btn btn-outline">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        <section className="dashboard-section">
          <h2>Available Classes</h2>
          
          {error && (
            <div className="error-message">
              {error}
              <button onClick={fetchClasses} className="btn btn-sm">
                Retry
              </button>
            </div>
          )}

          {classes.length === 0 ? (
            <div className="no-classes">
              <p>No classes available at the moment.</p>
            </div>
          ) : (
            <div className="classes-grid">
              {classes.map((classItem) => (
                <div key={classItem.id} className="class-card">
                  <h3>{classItem.name}</h3>
                  <p className="class-description">{classItem.description}</p>
                  <div className="class-details">
                    <span className="class-time">
                      {new Date(classItem.start_time).toLocaleString()}
                    </span>
                    <span className="class-capacity">
                      {classItem.current_capacity || 0}/{classItem.max_capacity} spots
                    </span>
                  </div>
                  <div className="class-actions">
                    <button
                      onClick={() => handleBookClass(classItem.id)}
                      className="btn btn-primary"
                      disabled={classItem.current_capacity >= classItem.max_capacity}
                    >
                      {classItem.current_capacity >= classItem.max_capacity 
                        ? 'Full' 
                        : 'Book Class'
                      }
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default Dashboard;