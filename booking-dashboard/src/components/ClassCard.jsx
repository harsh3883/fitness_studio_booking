import React from 'react';
import { Link } from 'react-router-dom';
import './ClassCard.css';

const ClassCard = ({ classData }) => {
  const {
    id,
    name,
    instructor,
    category,
    difficulty,
    duration,
    date,
    time,
    capacity,
    enrolled,
    price,
    description,
    image
  } = classData;

  const spotsLeft = capacity - enrolled;
  const isFullyBooked = spotsLeft <= 0;

  return (
    <div className="class-card">
      <div className="class-image">
        <img src={image || '/default-class.jpg'} alt={name} />
        <div className="class-difficulty">{difficulty}</div>
      </div>
      
      <div className="class-content">
        <div className="class-header">
          <h3 className="class-name">{name}</h3>
          <span className="class-price">${price}</span>
        </div>
        
        <div className="class-meta">
          <p className="class-instructor">with {instructor}</p>
          <p className="class-category">{category}</p>
        </div>
        
        <div className="class-schedule">
          <div className="schedule-item">
            <span className="schedule-icon">📅</span>
            <span>{new Date(date).toLocaleDateString()}</span>
          </div>
          <div className="schedule-item">
            <span className="schedule-icon">⏰</span>
            <span>{time}</span>
          </div>
          <div className="schedule-item">
            <span className="schedule-icon">⏱️</span>
            <span>{duration} min</span>
          </div>
        </div>
        
        <p className="class-description">{description}</p>
        
        <div className="class-capacity">
          <span className={`spots-left ${spotsLeft <= 3 ? 'low' : ''}`}>
            {spotsLeft} spots left
          </span>
        </div>
        
        <Link 
          to={`/booking/${id}`} 
          className={`btn ${isFullyBooked ? 'btn-disabled' : 'btn-primary'}`}
          style={{ pointerEvents: isFullyBooked ? 'none' : 'auto' }}
        >
          {isFullyBooked ? 'Fully Booked' : 'Book Now'}
        </Link>
      </div>
    </div>
  );
};

export default ClassCard;
