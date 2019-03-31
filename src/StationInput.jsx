import React from 'react';
import './StationInput.css';
import AutocompleteBox from './AutocompleteBox';

function StationInput({
  onChange,
  parentId,
  id,
  value,
  label,
  onSelectItem,
  optionList,
  active,
}) {
  return (
    <div className="InputBox">
      <label htmlFor={id}>{label}</label>
      <div className="Input">
        <input
          type="text"
          className="StationInput"
          value={value}
          id={id}
          onChange={onChange}
        />
        {active === 1 && value ? (
          <AutocompleteBox
            parentId={parentId}
            inputValue={value}
            optionList={optionList}
            onSelectItem={onSelectItem}
          />
        ) : (
          ''
        )}
      </div>
    </div>
  );
}

export default StationInput;
