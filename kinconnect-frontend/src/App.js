import React, { useState } from 'react';

import ProfileEditor from './ProfileEditor'
import SearchResults from './SearchResults'
import InputForm from './InputForm'

import logo from "./logo.svg";
import "./App.css";

/*
  inputFields: [string,string,]
  
  profile: ProfileModel <= our summary fields

  searchResults: [{.  <== search results
     score: number,
     profile: ProfileModel,
  },...]

class ProfileModel:
    name: str = Field(..., title="Name of the person")
    honors: str = Field(None, title="Honors, Awards and recognition they have recieved in life")
    interests: str = Field(..., title="Interests and current focus of theirs the work or the event")
    skills: str = Field(..., title="Skills they have")
    career: List[CareerEntry] = Field(..., title="Career history of the person")
    past_projects: List[ProjectEntry] = Field(..., title="Projects they have worked on")
    elevator_pitch: str = Field(..., title="Elevator pitch for the person fpr the event")

*/


function App() {
  const [ profile, setProfile ] = useState(undefined);
  const [ searchResults, setSearchResults ] = useState(undefined);

  const hasProfile = profile ? true : false;
  const hasSearchResults = searchResults ? true : false;

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
        <InputForm onProfile={setProfile} />
      </main>

      { hasProfile && <ProfileEditor
        profile={profile}
        onSearchResults={setSearchResults}
      /> }
      { hasSearchResults && <SearchResults searchResults={searchResults} /> }

      <div style={{height:200}}>Hello</div>

      <footer className="App-footer">
        <p>&copy; 2024 Kin Connect.ai. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;

