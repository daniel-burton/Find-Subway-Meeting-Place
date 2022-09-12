import React from 'react';
import './Results.css';
import Routes from './Routes';

function Results({
  potentials,
  startOne,
  startTwo,
  makeHandle,
  routesDisplayed,
}) {
  //potentials: list of potential spots
  // each includes: name, route_1, route_2, time, time_2

  return (
    <div className="Results">
      <h3>Potential Meeting Spots:</h3>
      {potentials.map(potential => {
        return (
          /*return Name and Time if time same from both start points, otherwise
            return nested <span>s describing times*/
          <div key={potential.name + 'wrapper'}>
            <div className='Result' key={potential.name}>
            <div
              className="ResultTitle"
              key={potential.name + 'Title'}
              id={potential.name}
              onClick={makeHandle(potential.name)}>
              <span className="Plus">{routesDisplayed.includes(potential.name) ? "- " : "+"}</span>
              <span className="ResultStationName">{potential.name}:</span>
              {potential.time === potential.time_2 ? (
                <span className="ResultTime"> {potential.time} minutes.</span>
              ) : (
                <span className='ResultDescription'>
                  <span className="ResultTime"> {potential.time} minutes</span>
                  <span>
                    {' '}
                    from <span className="StationName">{startOne}</span>, and{' '}
                  </span>
                  <span className="ResultTime">{potential.time_2} minutes</span>
                  <span>
                    {' '}
                    from <span className="StationName">{startTwo}.</span>
                  </span>
                </span>
              )}
            </div>
            {!routesDisplayed.includes(potential.name) ? (
              ''
            ) : (
              <div className="Routes">
                <Routes potential={potential} />
              </div>
            )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default Results;
