import React from 'react';
import ReactDOM from 'react-dom';
import StationInput from './StationInput';
import Minimum from './Minimum';
import stationNames from './stationNames';
import './index.css';


function makeURL(start1, start2, minimum){
  return encodeURI(`http://127.0.0.1:5000/api/meeting/True/${start1}/${start2}/${minimum}`);
}

async function getRoute(url){
  let output = await fetch(url)
    .then(function(response) {
      return response.json();
    })
    return output;
}


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {'one': '', 'two': '', 'minimum': 1, 'oneActive':0, 'twoActive':0};
  }

  handleChange = (event) => {
    let newState = {};
    let activeAutocomplete = event.target.id + 'Active';
    newState[event.target.id] = event.target.value;
    newState[activeAutocomplete] = 1;
    this.setState(newState);
  }

  onSelectItem = (event) => {
    // 1. set value of related input to clicked value
    // 2. make autocomplete box go away
    console.log(event.target.id + " clicked!");
    console.log(event.target.innerText);
    let newState = {};
    let whichInput = event.target.id.split('-')[0];
    newState[whichInput] = event.target.innerText;
    newState[whichInput + 'Active'] = 0;
    this.setState(newState);
  }

  handleSubmit = async (event) => {
    let one = this.state.one;
    let two = this.state.two;
    let minimum = this.state.minimum;
    let response = await getRoute(makeURL(one, two, minimum))
      .then( response => { console.log(response); this.state.response = response});
    console.log(response);
  }

  handleRange = (event) => {
    let newState = {};
    newState['minimum'] = event.target.value;
    this.setState(newState);
  }

  render() {
    return (
      <div className='App'>
        <h1>Enter your starting points to get suggested meeting places.</h1>
        <StationInput id='one' parentId='one' value={this.state['one']} onChange={this.handleChange} label='First endpoint:' optionList={stationNames} onSelectItem={this.onSelectItem} active={this.state.oneActive}/>
        <StationInput id='two' parentId='two' value={this.state['two']} onChange={this.handleChange} label='Second endpoint:' optionList={stationNames} onSelectItem={this.onSelectItem} active={this.state.twoActive}/>
        <Minimum value={this.state['minimum']} onChange={this.handleRange}/>
        <button onClick={this.handleSubmit}>Calculate</button>
      </div>
    );
  }
}

ReactDOM.render(<App/>, document.getElementById('root'));
