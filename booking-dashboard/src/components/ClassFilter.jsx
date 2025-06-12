import React from 'react';
import './ClassFilter.css';

const ClassFilter = ({ filters, onFilterChange, classes }) => {
const safeArray = (arr) => Array.isArray(arr) ? arr : [];

const categories = [...new Set(safeArray(classes).map(cls => cls.category))];
const difficulties = [...new Set(safeArray(classes).map(cls => cls.difficulty))];
const dates = [...new Set(safeArray(classes).map(cls => cls.date))].sort();
const times = [...new Set(safeArray(classes).map(cls => cls.time))].sort();


  const handleFilterChange = (key, value) => {
    onFilterChange({
      ...filters,
      [key]: value
    });
  };

  const clearFilters = () => {
    onFilterChange({
      category: '',
      difficulty: '',
      date: '',
      time: ''
    });
  };

  return (
    <div className="class-filter">
      <div className="filter-row">
        <div className="filter-group">
          <label>Category</label>
          <select 
            value={filters.category} 
            onChange={(e) => handleFilterChange('category', e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Difficulty</label>
          <select 
            value={filters.difficulty} 
            onChange={(e) => handleFilterChange('difficulty', e.target.value)}
          >
            <option value="">All Levels</option>
            {difficulties.map(difficulty => (
              <option key={difficulty} value={difficulty}>{difficulty}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Date</label>
          <select 
            value={filters.date} 
            onChange={(e) => handleFilterChange('date', e.target.value)}
          >
            <option value="">Any Date</option>
            {dates.map(date => (
              <option key={date} value={date}>
                {new Date(date).toLocaleDateString()}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Time</label>
          <select 
            value={filters.time} 
            onChange={(e) => handleFilterChange('time', e.target.value)}
          >
            <option value="">Any Time</option>
            {times.map(time => (
              <option key={time} value={time}>{time}</option>
            ))}
          </select>
        </div>

        <button onClick={clearFilters} className="btn btn-secondary">
          Clear Filters
        </button>
      </div>
    </div>
  );
};

export default ClassFilter;