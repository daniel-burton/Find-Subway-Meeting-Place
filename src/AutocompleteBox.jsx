import React from 'react';
import './AutocompleteBox.css';
import SuggestionItem from './SuggestionItem';

class AutocompleteBox extends React.Component {
  constructor(props) {
    // optionList, onSelection, inputValue 
    super(props);
    this.state = {'highlighted':'', 'suggestions': []};
  }

  render() {
    const re = new RegExp(this.props.inputValue, 'gi');
    return (
      <div className='AutocompleteBox'>
       { this.props.optionList.filter(word => re.test(word))
          .map((item, index) => {
          return (<SuggestionItem value={item} key={index}
          // onSuggestionClick={onSuggestionClick} //replace input value with clicked value
          // onSuggestionHover={onSuggestionHover} //highlight/select suggestion
          // onEnterKey={onEnterKey} //replace input value with selected value
          // onDownKey={onDownKey} //move selection down one
          // onUpKey={onUpKey} //move selection up one
          // onLoseFocus={onLoseFocus} //
          //highlighted = {item == this.state.highlighted ? 1 : 0} //highlight selected item
          />)})}
      </div>
    )
  }
}


export default AutocompleteBox;
