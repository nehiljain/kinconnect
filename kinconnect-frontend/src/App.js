import React, { useState } from 'react';

import SummaryEditor from './SummaryEditor'
import MatchResults from './MatchResults'
import InputForm from './InputForm'

import logo from "./logo.svg";
import "./App.css";

function App() {
  const [ summaryData, setSummaryData ] = useState(undefined);
  const [ matchResults, setMatchResults ] = useState(undefined);

  const onSummarizeForm = () => {

  }

  // Handle button click
  const onFormButtonPress = () => {
  };

  const onSearchButtonPress = () => {
  }

  const hasSummaryData = summaryData ? true : false;
  const hasMatchResults = matchResults ? true : false;

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
        <InputForm onSummaryData={setSummaryData} />
      </main>

      { hasSummaryData && <SummaryEditor
        summaryData={summaryData}
        onMatchResults={setMatchResults}
      /> }
      { hasMatchResults && <MatchResults /> }

      <footer className="App-footer">
        <p>&copy; 2024 Kin Connect.ai. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;

