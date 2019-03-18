import React from 'react';
import './StationInput.css';

function StationInput ({ onChange, id, value, label }) {
  return (
    <div className='Inputs'>
      <label>
      {label}
      <input type='text'
        className='StationInput'
        value={value}
        id={id}
        onChange={onChange}
      />
    </label>
    </div>
  );
}

export default StationInput;
