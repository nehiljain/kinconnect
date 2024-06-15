import React, { useState, useEffect } from "react";
import Select from 'react-select';
import CreatableSelect from 'react-select/creatable';

import { updateProfile, search } from "./net";

export default function ProfileEditor({ profile = {}, onSearchResults }) {
    const [spinner, setSpinner] = useState(false);
    const [editedProfile, setEditedProfile] = useState();

    const reload = () => {
        if (!profile)
            setEditedProfile(undefined);
        else {
            const copy = JSON.parse(JSON.stringify(profile));
            setEditedProfile(copy);
        }
    };
    
    useEffect(() => { reload(); }, [profile]);

  /*
        name: str = Field(..., title="Name of the person")
    honors: str = Field(None, title="Honors, Awards and recognition they have recieved in life")
    interests: str = Field(..., title="Interests and current focus of theirs the work or the event")
    skills: str = Field(..., title="Skills they have")
    career: List[CareerEntry] = Field(..., title="Career history of the person")
    past_projects: List[ProjectEntry] = Field(..., title="Projects they have worked on")
    elevator_pitch: str = Field(..., title="Elevator pitch for the person fpr the event")
*/
    const onFieldUpdate = (delta) => {
        const updated = { ...editedProfile, ...delta };
        console.log('onFieldUpdate',delta,updated);
        setEditedProfile(updated);
    };

    const onSearch = async () => {
        if (spinner)
            return;

        setSpinner(true);
        try {
            await updateProfile( editedProfile ) 
            const searchResults = await search();
            onSearchResults(searchResults);
        } catch (err) {
            alert("Search error " + err);
        }
        setSpinner(false);
    };

    return (
        <div>
            <h2>Profile Editor</h2>

            <div>Name:</div>
            <div>
                <input
                    type="text"
                    placeholder="name"
                    value={editedProfile?.name || ""}
                    onChange={(event) => {
                        onFieldUpdate({ name: event.target.value });
                    }}
                />
            </div>
            <div>Elevator pitch:</div>
            <div>
                <input
                    type="text"
                    placeholder="elevator pitch"
                    value={editedProfile?.elevator_pitch || ""}
                    onChange={(event) => {
                        onFieldUpdate({ elevator_pitch: event.target.value });
                    }}
                />
            </div>
            <div>Career:</div>
            <div>
                <input
                    type="text"
                    placeholder="career"
                    value={editedProfile?.career || ""}
                    onChange={(event) => {
                        onFieldUpdate({ career: event.target.value });
                    }}
                />
            </div>

            <div>Honors:</div>
            <EditList items={editedProfile?.honors} onUpdate={(honors)=>onFieldUpdate({honors})} />

            <div>Interests:</div>
            <EditList items={editedProfile?.interests} onUpdate={(interests)=>onFieldUpdate({interests})} />

            <div>Skills:</div>
            <EditList items={editedProfile?.skills} onUpdate={(skills)=>onFieldUpdate({skills})} />

            <div>Past projects:</div>
            <EditList items={editedProfile?.past_projects} onUpdate={(past_projects)=>onFieldUpdate({past_projects})} />

            <button onClick={onSearch}>Search</button>
        </div>
  );
}

/*
            name: 'Mike',
            honors: ['Phd in Biology'],
            interests: ['Pickle','ball'],
            skills: ['React','Mongo'],
            career: 'Nuclear Physicist', // List[CareerEntry] = Field(..., title="Career history of the person")
            past_projects: ['Dispersed camping'], // List[ProjectEntry] = Field(..., title="Projects they have worked on")
            elevator_pitch: "I'm building a rocket and flying to mars"

*/


function EditList({ items = [], onUpdate }) {
    const options = items.map(e=>({value:e,label:e}));

    const setSelectedOption = (e) => {
        console.log('setSelectedOption',e);
    }

    const onCreateOption = (newItem) => {
        console.log('onCreateOption',newItem);
        if (newItem && !items.includes(newItem)) {
            const updatedItems = [...items, newItem];
            onUpdate(updatedItems);
        }
    };

    return (
        <div>
            <CreatableSelect
                isMulti
                onChange={setSelectedOption}
                options={options}
                onCreateOption={onCreateOption}
            />
        </div>
    )
}