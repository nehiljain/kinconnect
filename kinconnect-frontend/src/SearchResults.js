import React from "react";

const SearchResult = ({ searchResults }) => {
  return (
    <div>
      <h2>Score Profile</h2>
      {searchResults.length > 0 ? (
        <ul>
          {searchResults.map((searchResults, index) => (
            <li key={index}>
              {searchResults.score} {searchResults.profile}
            </li>
          ))}
        </ul>
      ) : (
        <p>No results found</p>
      )}
    </div>
  );
};

export default SearchResult;
