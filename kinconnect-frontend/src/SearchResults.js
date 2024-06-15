import React from "react";

const SearchResult = ({ searchResults }) => {
	console.log( 'SearchResult', searchResults );
  return (
    <div>
      <h2>Score Profile</h2>
      { searchResults?.map(e=><Profile profile={e.profile} score={e.score} />) }
    </div>
  );
};

export default SearchResult;


function Profile({ profile, score }) {
	return (
		<div>
			<div style={{fontWeight:'bold'}}>Name: {profile.name} {score}</div>
			<div>Honors: {profile.honors.join()}</div>
			<div>Interests: {profile.interests.join()}</div>
			<div>Skills: {profile.skills.join()}</div>
			<div>Career: {profile.career}</div>
			<div>Past Projects: {profile.past_projects.join()}</div>
			<div>Elevator Pitch: {profile.elevator_pitch}</div>
		</div>
	)
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
