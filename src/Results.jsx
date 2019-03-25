import React from 'react';
import './Results.css';


function Results({ potentials, startOne, startTwo }) {
  //potentials: list of potential spots
  // each includes: name, route_1, route_2, time, time_2
  
  //will display meeting spots and time (for each start point if different)
  //click meeting spot to display routes, graphic for subway line and method (transfer, ride, walk)
  
  return (
    <div className='Results'>
      <h3>Potential Meeting Spots:</h3>
      { potentials.map( potential => {
        return (
          <div className='Result' key={potential.name}>
          <span>{potential.name}</span>
          { (potential.time === potential.time_2) ?
            <span className='ResultTime'> {potential.time} minutes.</span> :
            <span>
            <span className='ResultTime'> {potential.time} minutes</span><span> from <span className='StationName'>{startOne}</span>, and </span>
            <span className='ResultTime'>{potential.time_2} minutes</span><span> from <span className='StationName'>{startTwo}.</span></span>
            </span>
          }
          </div>
        );})
      }
    </div>
  );
}

export default Results;
