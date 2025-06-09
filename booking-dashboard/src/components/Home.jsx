import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1>Welcome to FitStudio</h1>
          <p>Transform your body, elevate your mind, and achieve your fitness goals with our expert-led classes.</p>
          <div className="hero-buttons">
            <Link to="/classes" className="btn btn-primary">
              Browse Classes
            </Link>
            <Link to="/register" className="btn btn-secondary">
              Join Now
            </Link>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2>Why Choose FitStudio?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🏋️</div>
              <h3>Expert Trainers</h3>
              <p>Learn from certified professionals with years of experience.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Flexible Scheduling</h3>
              <p>Book classes that fit your busy lifestyle with our easy scheduling system.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Variety of Classes</h3>
              <p>From yoga to HIIT, find the perfect workout for your goals.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;