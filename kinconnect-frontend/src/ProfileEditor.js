import React, { useState, useEffect } from "react";
import Select from 'react-select';
import Creatable from 'react-select/creatable';

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

            <div>
                <input
                    type="text"
                    placeholder="honors"
                    value={editedProfile?.honors || ""}
                    onChange={(event) => {
                        onFieldUpdate({ honors: event.target.value });
                    }}
                />
            </div>

            <EditList items={editedProfile?.skills} onUpdate={()=>{}} />

      <button onClick={onSearch}>Search</button>
    </div>
  );
}

function EditList({ items = [], onUpdate }) {
    const [ newItem, setNewItem ] = useState('');

    const options = items.map(e=>({value:e,label:e}));

    const setSelectedOption = () => {
    }

    const handleAddItem = () => {
        if (newItem && !items.includes(newItem)) {
            const updatedItems = [...items, newItem];
            onUpdate(updatedItems);
            setNewItem('');
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleAddItem();
        }
    };

    // defaultValue={selectedOption}

    return (
        <div>
            <Select
                isMulti
                onChange={setSelectedOption}
                options={options}
            />
            <br/>
            <input
                type="text"
                placeholder=""
                value={newItem}
                onChange={(event) => {
                    setNewItem( event.target.value );
                }}
                onKeyPress={handleKeyPress}
            />
        </div>
    )
}

/*
const options = [
  { value: 'chocolate', label: 'Chocolate' },
  { value: 'strawberry', label: 'Strawberry' },
  { value: 'vanilla', label: 'Vanilla' },
];


export default function App() {
  const [selectedOption, setSelectedOption] = useState(null);

  return (
    <div className="App">
      <Select
        defaultValue={selectedOption}
        onChange={setSelectedOption}
        options={options}
      />
    </div>
  );
}*/
