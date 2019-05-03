import React from 'react';
import './AutocompleteBox.css';
import SuggestionItem from './SuggestionItem';

class AutocompleteBox extends React.Component {
  constructor(props) {
    // optionList, onSelectItemion, inputValue, parentId
    super(props);
    this.state = {highlighted: '', suggestions: []};
  }

  render() {
    // escape regex characters
    const re = new RegExp(this.props.inputValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    //console.log(re)
    return (
      <div className="AutocompleteBox">
        {this.props.optionList
          .filter(word => re.test(word))
          .map((item, index) => {
            return (
              <SuggestionItem
                value={item}
                key={this.props.parentId + '-' + index}
                id={this.props.parentId + '-' + index}
                onClick={this.props.onSelectItem}
              />
            );
          })}
      </div>
    );
  }
}

export default AutocompleteBox;
