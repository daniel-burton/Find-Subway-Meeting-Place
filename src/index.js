import React from 'react';
import ReactDOM from 'react-dom';
import StationInput from './StationInput';
import Minimum from './Minimum';


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
    this.state = {'one': '', 'two': ''};
  }

  handleChange= (event) => {
    let newState = {};
    newState[event.target.id] = event.target.value;
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
        <StationInput id='one' value={this.state['one']} onChange={this.handleChange} label='First endpoint:'/>
        <StationInput id='two' value={this.state['two']} onChange={this.handleChange} label='Second endpoint:'/>
        <Minimum value={this.state['minimum']} onChange={this.handleRange}/>
        <button onClick={this.handleSubmit}>Click me!</button>
      </div>
    );
  }
}

ReactDOM.render(<App/>, document.getElementById('root'));
