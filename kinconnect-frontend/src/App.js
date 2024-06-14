import React, { useState } from 'react';

import SummaryEditor from './SummaryEditor'
import MatchResults from './MatchResults'


import logo from "./logo.svg";
import "./App.css";

function App() {
  // Define state variables for the input fields
  const [input1, setInput1] = useState('');
  const [input2, setInput2] = useState('');
  const [input3, setInput3] = useState('');

  // Handle input changes
  const handleInput1Change = (event) => setInput1(event.target.value);
  const handleInput2Change = (event) => setInput2(event.target.value);
  const handleInput3Change = (event) => setInput3(event.target.value);

  // Handle button click
  const handleNextClick = () => {
    console.log('Input 1:', input1);
    console.log('Input 2:', input2);
    console.log('Input 3:', input3);
    // Add your logic for the next button click here
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Welcome to <code>Kin Connect.ai</code>
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
      <main className="App-main">
        <p>Connecting families with technology.</p>
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
      </main>

      <SummaryEditor />
      <MatchResults />


      <footer className="App-footer">
        <p>&copy; 2024 Kin Connect.ai. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;

