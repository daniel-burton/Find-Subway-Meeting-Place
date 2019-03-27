import React from 'react';
import './Routes.css';

class Routes extends React.Component {
  constructor(props) {}

  parseRoute(route) {
    // s, w, r, t, e (start, walk, ride, transfer, end)
    // line, name, trip_type
    let steps = [];
    route.map(step => {
      let tripType = step.trip_type;
      if (tripType === 's') {
        pass;
      } else if (tripType === 'r') {
        steps.push(`...pass ${step.name}.`);
      } else if (tripType === 't') {
        steps.push(`Transfer to the ${step.line} train ${step.name}.`);
      } else if (tripType === 'w') {
        steps.push(`Walk to the ${step.line} Train at ${step.name}.`);
      } else if (tripType === 'e') {
        steps.push(`Arrive at ${step.name}.`);
      }
    });
  }

  render() {
    return (
      <div>
        <p>hi</p>
      </div>
    );
  }
}

export default Routes;
