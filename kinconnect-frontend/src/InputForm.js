import React, { useState } from 'react';

export default function SummaryEditor({ onSummaryData }) {
    // Define state variables for the input fields
    const [input1, setInput1] = useState('');
    const [input2, setInput2] = useState('');
    const [input3, setInput3] = useState('');

    // Handle input changes
    const handleInput1Change = (event) => setInput1(event.target.value);
    const handleInput2Change = (event) => setInput2(event.target.value);
    const handleInput3Change = (event) => setInput3(event.target.value);

    const handleNextClick = () => {
        onSummaryData({hello:true});
    }

    return (
        <div className="input-container">
          <input
            type="text"
            placeholder="Input 1"
            value={input1}
            onChange={handleInput1Change}
          />
          <input
            type="text"
            placeholder="Input 2"
            value={input2}
            onChange={handleInput2Change}
          />
          <input
            type="text"
            placeholder="Input 3"
            value={input3}
            onChange={handleInput3Change}
          />
          <button onClick={handleNextClick}>Next</button>
        </div>
    )
}