import React, { useState, useEffect } from 'react'
import { search } from './net'

export default function ProfileEditor({ profile, onSearchResults }) {
    const [ spinner, setSpinner ] = useState(false);
    const [ editedProfile, setEditedProfile ] = useState();

    const reload = () => {
        if( !profile )
            setEditedProfile(undefined);
        else {
            const copy = JSON.parse(JSON.stringify(profile));
            setEditedProfile(copy);
        }
    }
    useEffect( () => { reload() }, [profile] );

/*
        name: str = Field(..., title="Name of the person")
    honors: str = Field(None, title="Honors, Awards and recognition they have recieved in life")
    interests: str = Field(..., title="Interests and current focus of theirs the work or the event")
    skills: str = Field(..., title="Skills they have")
    career: List[CareerEntry] = Field(..., title="Career history of the person")
    past_projects: List[ProjectEntry] = Field(..., title="Projects they have worked on")
    elevator_pitch: str = Field(..., title="Elevator pitch for the person fpr the event")
*/


    const onSearch = async () => {
        if( spinner )
            return;

        setSpinner(true);
        try {
            const searchResults = await search({ profile: editedProfile });
            onSearchResults( searchResults );
        } catch(err) {
            console.log('onSearch error',err);
        }
        setSpinner(false);
    }

    return (
        <div>
            <h2>Profile Editor</h2>
            <button onClick={onSearch}>Search</button>
        </div>
    )
}