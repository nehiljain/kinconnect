import React, { useState } from 'react';
import Spinner from './Spinner'
import { createProfile } from './net'

export default function InputForm({ onProfile }) {
    const [ spinner, setSpinner ] = useState(false);
    const [input1, setInput1] = useState('');
    const [input2, setInput2] = useState('');
    const [input3, setInput3] = useState('');
    const [input4, setInput4] = useState('');
    const [input5, setInput5] = useState('');

    // Handle input changes
    const handleInput1Change = (event) => setInput1(event.target.value);
    const handleInput2Change = (event) => setInput2(event.target.value);
    const handleInput3Change = (event) => setInput3(event.target.value);
    const handleInput4Change = (event) => setInput4(event.target.value);
    const handleInput5Change = (event) => setInput5(event.target.value);

    const handleNextClick = async () => {
        if( spinner )
            return;

        setSpinner(true);
        try {
            const qa_pairs = [
                { question: 'What is your name?.', answer: input1 },
                { question: 'What are your interests?  (ie technical topic, coding language, business problem).', answer: input2 },
                { question: 'If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.', answer: input3 },
                { question: 'What is your strongest functional role (such as developer, UX, business, product)? Please share one or two things about your experience in this role, for example a success, companies you worked for, how many years.', answer: input4 },
                { question: 'Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?', answer: input5 },
            ];
            const profile = await createProfile( qa_pairs );
            onProfile( profile );
        } catch(err) {
            alert('Create Profile error: ' + err);
        }
        setSpinner(false);
    }

    return (
        <div className="input-container">
          <div>What is your name?.</div>
          <input
            type="text"
            placeholder="Input 1"
            value={input1}
            onChange={handleInput1Change}
          />
          <div>What are your interests?  (ie technical topic, coding language, business problem).</div>
          <input
            type="text"
            placeholder="Input 2"
            value={input2}
            onChange={handleInput2Change}
          />
          <div>If you have a project idea, describe your idea . Please include whether what sector it is in, and what business problem it is solving and for whom. If you don’t have a project, skip this question.</div>
          <input
            type="text"
            placeholder="Input 3"
            value={input3}
            onChange={handleInput3Change}
          />
          <div>What is your strongest functional role (such as developer, UX, business, product)? Please share one or two things about your experience in this role, for example a success, companies you worked for, how many years.</div>
          <input
            type="text"
            placeholder="Input 4"
            value={input4}
            onChange={handleInput4Change}
          />
          <div>Are you interested in meeting people with a specific skill set (either one that you lack or one that you already have but want to clone yourself to speed up building). What is the skills sets that you are looking to meet?</div>
          <input
            type="text"
            placeholder="Input 5"
            value={input5}
            onChange={handleInput5Change}
          />
          <button onClick={handleNextClick}>Next</button>
          <Spinner visible={spinner} />
        </div>
    )
}