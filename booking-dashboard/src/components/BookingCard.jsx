import React from 'react';
import './BookingCard.css';

const BookingCard = ({ booking, onCancel, showCancel }) => {
  const { id, class: classData, status, booking_date } = booking;
  
  const canCancel = () => {
    const classDate = new Date(classData.date);
    const now = new Date();
    const hoursDifference = (classDate - now) / (1000 * 60 * 60);
    return hoursDifference > 24; // Can cancel if more than 24 hours before class
  };

  return (
    <div className={`booking-card ${status}`}>
      <div className="booking-header">
        <h3>{classData.name}</h3>
        <span className={`status ${status}`}>{status}</span>
      </div>
      
      <div className="booking-details">
        <p><strong>Instructor:</strong> {classData.instructor}</p>
        <p><strong>Date:</strong> {new Date(classData.date).toLocaleDateString()}</p>
        <p><strong>Time:</strong> {classData.time}</p>
        <p><strong>Duration:</strong> {classData.duration} minutes</p>
        <p><strong>Booked on:</strong> {new Date(booking_date).toLocaleDateString()}</p>
      </div>

      {showCancel && status === 'confirmed' && canCancel() && (
        <div className="booking-actions">
          <button 
            onClick={() => onCancel(id)}
            className="btn btn-danger btn-sm"
          >
            Cancel Booking
          </button>
        </div>
      )}

      {showCancel && status === 'confirmed' && !canCancel() && (
        <div className="booking-notice">
          <small>Cannot cancel within 24 hours of class</small>
        </div>
      )}
    </div>
  );
};

export default BookingCard;