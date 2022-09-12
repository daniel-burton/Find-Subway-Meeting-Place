import React from 'react';
import './Minimum.css';

function Minimum({onChange, value}) {
  return (
    <div className="Minimum">
      <label className="MinimumDescription">
        Minimum number of meeting spots to be generated:
        <input type="number" min="1" max="20" value={value} onChange={onChange} />
      </label>
    </div>
  );
}

export default Minimum;
