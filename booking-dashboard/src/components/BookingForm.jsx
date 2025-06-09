import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './BookingForm.css';

const BookingForm = ({ classData, onSubmit, loading, spotsLeft }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    notes: '',
    emergency_contact: '',
    medical_conditions: ''
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  if (!user) {
    return (
      <div className="booking-form">
        <div className="login-prompt">
          <h3>Please log in to book this class</h3>
          <p>You need to be logged in to make a booking.</p>
        </div>
      </div>
    );
  }

  if (spotsLeft <= 0) {
    return (
      <div className="booking-form">
        <div className="fully-booked">
          <h3>Class Fully Booked</h3>
          <p>This class is currently full. Please check other available times.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="booking-form">
      <h3>Book Your Spot</h3>
      
      <div className="booking-summary">
        <h4>Booking Summary</h4>
        <div className="summary-item">
          <span>Class:</span>
          <span>{classData.name}</span>
        </div>
        <div className="summary-item">
          <span>Date & Time:</span>
          <span>{new Date(classData.date).toLocaleDateString()} at {classData.time}</span>
        </div>
        <div className="summary-item">
          <span>Duration:</span>
          <span>{classData.duration} minutes</span>
        </div>
        <div className="summary-item total">
          <span>Total:</span>
          <span>${classData.price}</span>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="emergency_contact">Emergency Contact</label>
          <input
            type="text"
            id="emergency_contact"
            name="emergency_contact"
            value={formData.emergency_contact}
            onChange={handleInputChange}
            placeholder="Emergency contact number"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="medical_conditions">Medical Conditions (Optional)</label>
          <textarea
            id="medical_conditions"
            name="medical_conditions"
            value={formData.medical_conditions}
            onChange={handleInputChange}
            placeholder="Any medical conditions or injuries we should know about?"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Additional Notes (Optional)</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleInputChange}
            placeholder="Any special requests or notes?"
            rows="3"
          />
        </div>

        <div className="booking-terms">
          <label className="checkbox-label">
            <input type="checkbox" required />
            <span>I agree to the cancellation policy and terms of service</span>
          </label>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary btn-block"
          disabled={loading}
        >
          {loading ? 'Processing...' : `Book for $${classData.price}`}
        </button>
      </form>
    </div>
  );
};

export default BookingForm;