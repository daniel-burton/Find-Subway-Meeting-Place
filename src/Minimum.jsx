import React from 'react';
import './Minimum.css';

function Minimum({onChange, value}) {
  return (
    <div className='Minimum'>
      <label>
       Minimum number of meeting spots:
        <input type='range' min='1' max='10' onChange={onChange}/>
      </label>
      <p className='minimum_label'>{value}</p>
    </div>
  );
}

export default Minimum;
