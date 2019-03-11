import React from 'react';
import ReactDOM from 'react-dom';


function makeURL(start, end){
  return encodeURI('http://127.0.0.1:5000/api/route/${start}/${end}/');
}

async function getRoute(url){
  output = await fetch(url)
    .then(function(response) {
      return response.json();
    })
    return output;
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
}


ReactDOM.render(<App/>, document.getElementById('root'));
