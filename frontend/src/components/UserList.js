import React, { useState, useEffect } from 'react';

function UserList({ onUserUpdated, onUserDeleted, displayMessage }) {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsersInternal = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/users');
      const data = await response.json();
      if (response.ok) {
        setUsers(data);
      } else {
        displayMessage(data.error || 'Failed to fetch users.', 'error');
        setError(data.error || 'Failed to load users.');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      displayMessage('Network error when fetching users.', 'error');
      setError('Network error when fetching users.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsersInternal();
  }, [ ]); // No dependencies to refetch on every render unless parent calls for it

  const handleDelete = async (userId) => {
    if (window.confirm(`Are you sure you want to delete user ID ${userId}?`)) {
      try {
        const response = await fetch(`/user/${userId}`, {
          method: 'DELETE',
        });
        const data = await response.json();
        if (response.ok) {
          displayMessage(data.message, 'success');
          fetchUsersInternal();
          if (onUserDeleted) onUserDeleted();
        } else {
          displayMessage(data.message || 'Failed to delete user.', 'error');
        }
      } catch (error) {
        console.error('Error deleting user:', error);
        displayMessage('Network error when deleting user.', 'error');
      }
    }
  };

  const handleUpdate = async (userId) => {
    const newName = window.prompt(`Enter new name for user ID ${userId}:`);
    const newEmail = window.prompt(`Enter new email for user ID ${userId}:`);

    if (newName === null && newEmail === null) {
      return;
    }

    const updateData = {};
    if (newName !== null && newName.trim() !== '') {
      updateData.name = newName.trim();
    }
    if (newEmail !== null && newEmail.trim() !== '') {
      updateData.email = newEmail.trim();
    }

    if (Object.keys(updateData).length === 0) {
      displayMessage('No new data provided for update.', 'info');
      return;
    }

    try {
      const response = await fetch(`/user/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      const data = await response.json();
      if (response.ok) {
        displayMessage(data.message, 'success');
        fetchUsersInternal();
        if (onUserUpdated) onUserUpdated();
      } else {
        displayMessage(data.message || 'Failed to update user.', 'error');
      }
    } catch (error) {
      console.error('Error updating user:', error);
      displayMessage('Network error when updating user.', 'error');
    }
  };

  if (isLoading) {
    return <p className="text-gray-600 text-lg">Loading users...</p>;
  }

  if (error) {
    return <p className="text-red-600 text-lg">Error: {error}</p>;
  }

  if (users.length === 0) {
    return <p className="text-gray-500 text-lg">No users found.</p>;
  }

  return (
    <ul className="space-y-3">
      {users.map((user) => (
        <li
          key={user.id}
          className="bg-gray-100 p-4 rounded-lg shadow-sm flex flex-col md:flex-row justify-between items-center space-y-2 md:space-y-0 md:space-x-4"
        >
          <span className="text-gray-800 font-medium text-left flex-grow">
            ID: {user.id} - Name: {user.name} - Email: {user.email}
          </span>
          <div className="flex space-x-2">
            <button
              onClick={() => handleUpdate(user.id)}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-3 rounded text-sm transition duration-300 ease-in-out"
            >
              Update
            </button>
            <button
              onClick={() => handleDelete(user.id)}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-3 rounded text-sm transition duration-300 ease-in-out"
            >
              Delete
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default UserList;