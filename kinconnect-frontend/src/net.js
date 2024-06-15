import axios, { AxiosHeaders, AxiosRequestConfig } from 'axios'

function createAuthConfig() {
	return {};
}

const BASE_URL = "https://.."

export async function createProfile( inputFields ) {
    const config = createAuthConfig();
    //const { data } = await axios.post( BASE_URL + '/profile', { inputFields }, config );
    const data = { profile: {
        name: 'Mike',
        honors: 'Phd in Biology',
        interests: 'Pickle ball',
        skills: 'React, Mongo',
        career: 'Nuclear Physicist', // List[CareerEntry] = Field(..., title="Career history of the person")
        past_projects: 'Dispersed camping', // List[ProjectEntry] = Field(..., title="Projects they have worked on")
        elevator_pitch: "I'm building a rocket and flying to mars"
    }};
    return data;
}

/*
  searchResults: [{.  <== search results
     score: number,
     profile: ProfileModel,
  },...]
*/

let exampleCount = 1;
function searchRow() {
    return {
        score: 85,
        profile: {
            name: 'Mike',
            honors: 'Phd in Biology',
            interests: 'Pickle ball',
            skills: 'React, Mongo',
            career: 'Nuclear Physicist', // List[CareerEntry] = Field(..., title="Career history of the person")
            past_projects: 'Dispersed camping', // List[ProjectEntry] = Field(..., title="Projects they have worked on")
            elevator_pitch: "I'm building a rocket and flying to mars"
        }
    }
}

export async function search( profile ) {
    const config = createAuthConfig();
    //const { data } = await axios.post( BASE_URL + '/search', { profile }, config );

    const data = {
        searchResults: [ searchRow(), searchRow(), searchRow() ]
    }
    return data;
}