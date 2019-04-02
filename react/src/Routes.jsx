import React from 'react';
import './Routes.css';

function Routes({potential}) {
  return (
    <div className='BothRoutes'>
      {[potential.route_1, potential.route_2].map((route, i)=> {
        return (
          <div className={`OneRoute${i}`} key={route[0]['name']}>
          <h3 className='RouteTitle'>{`Route from ${route[0]['name']}`}</h3>
            {route.map(step => {
              return <p className='RouteStep'>{step.text}</p>;
            })}
          </div>
        );
      })}
    </div>
  );
}

export default Routes;
