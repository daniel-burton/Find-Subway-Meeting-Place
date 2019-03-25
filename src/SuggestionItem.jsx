import React from 'react';
import './SuggestionItem.css';

function SuggestionItem({ value, id, onClick }) {
  return(
    <p className='SuggestionItem' id={id} onClick={onClick}
      >{value}</p>
  );
}


export default SuggestionItem;
