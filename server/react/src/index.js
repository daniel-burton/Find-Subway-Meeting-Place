import React from 'react';
import ReactDOM from 'react-dom';
import StationInput from './StationInput';
import Minimum from './Minimum';
import Results from './Results';
import stationNames from './stationNames';
import './index.css';

function makeURL(start1, start2, minimum) {
  start1 = encodeURIComponent(start1);
  start2 = encodeURIComponent(start2);
  return `/api/meeting/True/${start1}/${start2}/${minimum}`;
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
      routesDisplayed: [],
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

  makeHandleClickResult = instanceName => {
    return () => {
      console.log(instanceName);
      let newState = {};
      if (this.state.routesDisplayed.includes(instanceName)) {
        newState['routesDisplayed'] = this.state.routesDisplayed.filter(
          item => item !== instanceName,
        );
      } else {
        newState['routesDisplayed'] = [
          ...this.state.routesDisplayed,
          instanceName,
        ];
      }
      this.setState(newState);
      console.log(this.state['routesDisplayed']);
    };
  };

  render() {
    return (
      <div className="App">
        <div className="Controls">
          <h1>Enter your starting points to get suggested meeting places.</h1>
          <h2>Note that the subway system is idealized and does not reflect time of day. Your next train is always just few minutes away...</h2>
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
          <button className='Submit' onClick={this.handleSubmit}>Calculate</button>
        </div>
        <div className="Results">
          {this.state.submitted === 1 ? (
            <Results
              potentials={this.state.results}
              startOne={this.state.one}
              startTwo={this.state.two}
              makeHandle={this.makeHandleClickResult}
              routesDisplayed={this.state.routesDisplayed}
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
