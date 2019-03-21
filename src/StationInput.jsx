import React from 'react';
import './StationInput.css';
import AutocompleteBox from './AutocompleteBox';

function StationInput ({ onChange, id, value, label, onSelection, optionList }) {
  console.log(value);

  return (
    <div className='Inputs'>
      <label>
      {label}
        <input type='text'
          className='StationInput'
          value={value}
          id={id}
          onChange={onChange}
        />
      </label>
      {  value ? <AutocompleteBox inputValue={value} optionList={optionList} onSelection={onSelection}/> : ''}
    </div>
  );
}

export default StationInput;
