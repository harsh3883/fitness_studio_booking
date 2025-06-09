import React, { useEffect, useState } from 'react';
import api from '../api/api';

const Dashboard = () => {
  const [classes, setClasses] = useState([]);

  useEffect(() => {
    api.get('/classes')
      .then(res => setClasses(res.data))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Class Name</th>
            <th>Date/Time</th>
            <th>Instructor</th>
            <th>Available Slots</th>
          </tr>
        </thead>
        <tbody>
          {classes.map(c => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{new Date(c.datetime).toLocaleString()}</td>
              <td>{c.instructor}</td>
              <td>{c.available_slots}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
