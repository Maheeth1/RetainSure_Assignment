import React, { useState } from 'react';

function SearchUser({ displayMessage }) {
  const [searchName, setSearchName] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchName.trim()) {
      displayMessage('Please enter a name to search.', 'error');
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/search?name=${encodeURIComponent(searchName.trim())}`);
      const data = await response.json();
      if (response.ok) {
        setSearchResults(data);
      } else {
        displayMessage(data.error || 'Search failed.', 'error');
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Error during search:', error);
      displayMessage('Network error during search.', 'error');
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="flex w-full max-w-md">
        <input
          type="text"
          placeholder="Search by Name"
          value={searchName}
          onChange={(e) => setSearchName(e.target.value)}
          className="flex-grow p-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 px-6 rounded-r-md transition duration-300 ease-in-out shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
      <ul className="w-full max-w-md space-y-3">
        {isLoading && <p className="text-center text-gray-600">Searching...</p>}
        {!isLoading && searchName.trim() !== '' && searchResults.length === 0 && (
          <p className="text-center text-gray-500">No users found with that name.</p>
        )}
        {!isLoading && searchResults.map((user) => (
          <li key={user.id} className="bg-gray-100 p-4 rounded-lg shadow-sm text-left">
            <span className="font-medium">ID:</span> {user.id} <br />
            <span className="font-medium">Name:</span> {user.name} <br />
            <span className="font-medium">Email:</span> {user.email}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SearchUser;