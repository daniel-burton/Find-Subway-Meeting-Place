import React from 'react';
import './SuggestionItem.css';

function SuggestionItem({value, id}) {
  return(
    <p className='SuggestionItem' id={id}>{value}</p>
  );
}


export default SuggestionItem;
