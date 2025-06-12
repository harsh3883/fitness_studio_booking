import React, { useState, useEffect } from 'react';
import ClassCard from '../components/ClassCard';
import ClassFilter from '../components/ClassFilter';
import './Classes.css';
import {API_BASE_URL} from '../api/api'; 

const Classes = () => {
  const [classes, setClasses] = useState([]);
  const [filteredClasses, setFilteredClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    difficulty: '',
    date: '',
    time: '',
  });

  useEffect(() => {
    fetchClasses();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [classes, filters]);

  const fetchClasses = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/classes/`);
      if (response.ok) {
        const data = await response.json();
        console.log('Fetched data:', data);
        setClasses(data.results);
      }
    } catch (error) {
      console.error('Error fetching classes:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = classes;

    if (filters.category) {
      filtered = filtered.filter(cls => cls.category === filters.category);
    }
    if (filters.difficulty) {
      filtered = filtered.filter(cls => cls.difficulty === filters.difficulty);
    }
    if (filters.date) {
      filtered = filtered.filter(cls => cls.date === filters.date);
    }
    if (filters.time) {
      filtered = filtered.filter(cls => cls.time === filters.time);
    }

    setFilteredClasses(filtered);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  if (loading) {
    return <div className="loading">Loading classes...</div>;
  }

  return (
    <div className="classes-page">
      <div className="container">
        <h1>Fitness Classes</h1>
        
        <ClassFilter 
          filters={filters} 
          onFilterChange={handleFilterChange}
          classes={classes}
        />

        <div className="classes-grid">
          {filteredClasses.length > 0 ? (
            filteredClasses.map(cls => (
              <ClassCard key={cls.id} classData={cls} />
            ))
          ) : (
            <div className="no-classes">
              <p>No classes found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Classes;