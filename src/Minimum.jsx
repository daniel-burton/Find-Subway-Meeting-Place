import React from 'react';
import './Minimum.css';

function Minimum({onChange, value}) {
  return (
    <div className="Minimum">
      <label className="MinimumDescription">
        Minimum number of meeting spots:
        <input type="range" min="1" max="10" onChange={onChange} />
      </label>
      <p className="MinimumLabel">{value}</p>
    </div>
  );
}

export default Minimum;
