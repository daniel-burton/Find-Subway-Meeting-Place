import React from 'react';
import ReactDOM from 'react-dom';
import StationInput from './StationInput';
import Minimum from './Minimum';
import Results from './Results';
import stationNames from './stationNames';
import './index.css';

function makeURL(start1, start2, minimum) {
  return encodeURI(
    `http://127.0.0.1:5000/api/meeting/True/${start1}/${start2}/${minimum}`,
  );
}

async function getRoute(url) {
  let output = await fetch(url).then(function(response) {
    return response.json();
  });
  return output;
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      one: '',
      two: '',
      minimum: 1,
      oneActive: 0,
      twoActive: 0,
      submitted: 0,
      routesDisplayed:[]
    };
  }

  handleChange = event => {
    //handle change in text boxes
    let newState = {};
    let activeAutocomplete = event.target.id + 'Active';
    newState[event.target.id] = event.target.value;
    newState[activeAutocomplete] = 1;
    this.setState(newState);
  };

  onSelectItem = event => {
    //on selecting an autocorrect item
    // 1. set value of related input to clicked value
    // 2. make autocomplete box go away
    //console.log(event.target.id + ' clicked!');
    //console.log(event.target.innerText);
    let newState = {};
    let whichInput = event.target.id.split('-')[0];
    newState[whichInput] = event.target.innerText;
    newState[whichInput + 'Active'] = 0;
    this.setState(newState);
  };

  handleSubmit = async event => {
    //on hitting the submit button
    let one = this.state.one;
    let two = this.state.two;
    let newState = {};
    let minimum = this.state.minimum;
    let _ = await getRoute(makeURL(one, two, minimum)) //is there a way to do this without creating a variable?
      .then(response => {
        console.log(response.potentials);
        newState['results'] = response.potentials;
        newState['submitted'] = 1;
        this.setState(newState);
      });
  };

  handleRange = event => {
    //on changing the Range input
    let newState = {};
    newState['minimum'] = event.target.value;
    this.setState(newState);
  };

  handleClickResult = event => {
    let newState = {};
    const target = event.target.id;
    if (this.state.routesDisplayed.includes(target)) {
      console.log('removing')
      //if route currently displayed
      //newState['routesDisplayed'] = this.state.routesDisplayed.filter(
       // item => item !== target,
      //);
    } else {
      //if route currently not displayed
      newState['routesDisplayed'] = [
        ...this.state.routesDisplayed,
        target,
      ];
    }
    console.log(this.state.routesDisplayed);
    this.setState(newState);
  };

  parseRoute(route) {
    // s, w, r, t, e (start, walk, ride, transfer, end)
    // line, name, trip_type
    let steps = [];
    route.map(step => {
      let tripType = step.trip_type;
      if (tripType === 's') {
        steps.push(`Start your trip at ${step.name}.`); 
      } else if (tripType === 'r') {
        steps.push(`...pass ${step.name}.`);
      } else if (tripType === 't') {
        steps.push(`Transfer to the ${step.line} train ${step.name}.`);
      } else if (tripType === 'w') {
        steps.push(`Walk to the ${step.line} Train at ${step.name}.`);
      } else if (tripType === 'e') {
        steps.push(`Arrive at ${step.name}.`);
      }
      return null;
    });
    console.log(steps);
  }

  render() {
    return (
      <div className="App">
        <div className="Controls">
          <h1>Enter your starting points to get suggested meeting places.</h1>
          <StationInput
            id="one"
            parentId="one"
            value={this.state['one']}
            onChange={this.handleChange}
            label="First endpoint:"
            optionList={stationNames}
            onSelectItem={this.onSelectItem}
            active={this.state.oneActive}
          />
          <StationInput
            id="two"
            parentId="two"
            value={this.state['two']}
            onChange={this.handleChange}
            label="Second endpoint:"
            optionList={stationNames}
            onSelectItem={this.onSelectItem}
            active={this.state.twoActive}
          />
          <Minimum value={this.state['minimum']} onChange={this.handleRange} />
          <button onClick={this.handleSubmit}>Calculate</button>
        </div>
        <div className="Results">
          {this.state.submitted === 1 ? (
            <Results
              potentials={this.state.results}
              startOne={this.state.one}
              startTwo={this.state.two}
              onClick={this.handleClickResult}
            />
          ) : (
            ''
          )}
        </div>
      </div>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));
