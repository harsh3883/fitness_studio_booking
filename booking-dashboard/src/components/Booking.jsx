import React, { useState } from 'react';
import api from '../api/api';

const Bookings = () => {
  const [email, setEmail] = useState('');
  const [bookings, setBookings] = useState([]);
  const [error, setError] = useState('');

  const fetchBookings = async () => {
    try {
      const res = await api.get(`/bookings?email=${email}`);
      setBookings(res.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch bookings.');
    }
  };

  return (
    <div>
      <h2>View Your Bookings</h2>
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />
      <button onClick={fetchBookings}>Get My Bookings</button>

      {error && <p>{error}</p>}

      {bookings.length > 0 && (
        <ul>
          {bookings.map(b => (
            <li key={b.id}>
              <strong>{b.class_name}</strong> – {new Date(b.class_datetime).toLocaleString()}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Bookings;
