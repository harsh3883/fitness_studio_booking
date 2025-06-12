import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import BookingForm from '../components/BookingForm';
import './BookingPage.css';
import {API_BASE_URL} from '../api/api'; 

const BookingPage = () => {
  const { classId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [classData, setClassData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);

  useEffect(() => {
    fetchClassData();
  }, [classId]);

  const fetchClassData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/classes/${classId}/`);
      if (response.ok) {
        const data = await response.json();
        setClassData(data);
      } else {
        navigate('/classes');
      }
    } catch (error) {
      console.error('Error fetching class data:', error);
      navigate('/classes');
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async (bookingData) => {
    if (!user) {
      navigate('/login');
      return;
    }

    setBooking(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/bookings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          class_id: classId,
          ...bookingData
        }),
      });

      if (response.ok) {
        alert('Booking successful!');
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        alert(`Booking failed: ${errorData.message}`);
      }
    } catch (error) {
      alert('Network error occurred');
    } finally {
      setBooking(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading class details...</div>;
  }

  if (!classData) {
    return <div className="error">Class not found</div>;
  }

  const spotsLeft = classData.capacity - classData.enrolled;

  return (
    <div className="booking-page">
      <div className="container">
        <div className="booking-content">
          <div className="class-details">
            <img src={classData.image || '/default-class.jpg'} alt={classData.name} />
            <div className="class-info">
              <h1>{classData.name}</h1>
              <p className="instructor">with {classData.instructor}</p>
              <div className="class-meta">
                <span className="category">{classData.category}</span>
                <span className="difficulty">{classData.difficulty}</span>
                <span className="duration">{classData.duration} min</span>
              </div>
              <div className="schedule">
                <p><strong>Date:</strong> {new Date(classData.date).toLocaleDateString()}</p>
                <p><strong>Time:</strong> {classData.time}</p>
                <p><strong>Price:</strong> ${classData.price}</p>
              </div>
              <p className="description">{classData.description}</p>
              <div className="availability">
                <span className={`spots ${spotsLeft <= 3 ? 'low' : ''}`}>
                  {spotsLeft} spots remaining
                </span>
              </div>
            </div>
          </div>

          <div className="booking-form-container">
            <BookingForm 
              classData={classData} 
              onSubmit={handleBooking}
              loading={booking}
              spotsLeft={spotsLeft}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingPage;