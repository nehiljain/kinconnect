import React, { useState } from 'react';
import Spinner from './Spinner'
import { createProfile } from './net'

export default function InputForm({ onProfile }) {
    const [ spinner, setSpinner ] = useState(false);
    const [input1, setInput1] = useState('');
    const [input2, setInput2] = useState('');
    const [input3, setInput3] = useState('');

    // Handle input changes
    const handleInput1Change = (event) => setInput1(event.target.value);
    const handleInput2Change = (event) => setInput2(event.target.value);
    const handleInput3Change = (event) => setInput3(event.target.value);

    const handleNextClick = async () => {
        if( spinner )
            return;

        setSpinner(true);
        try {
            const inputFields = [input1,input2,input3];
            const { profile } = await createProfile( inputFields );
            onProfile( profile );
        } catch(err) {
            alert('Create Profile error: ' + err);
        }
        setSpinner(false);
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
          <Spinner visible={spinner} />
        </div>
    )
}