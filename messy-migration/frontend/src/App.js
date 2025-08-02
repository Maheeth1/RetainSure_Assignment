import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import UserList from './components/UserList';
import UserForm from './components/UserForm';
import LoginForm from './components/LoginForm';
import SearchUser from './components/SearchUser';
import './index.css'; // This now imports Tailwind's generated CSS

function App() {
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const displayMessage = (msg, type = 'info') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('');
    }, 5000);
  };

  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const triggerRefresh = () => setRefreshTrigger(prev => prev + 1);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col"> {/* Tailwind body/app wrapper classes */}
        <Navbar />
        <main className="container mx-auto p-4 md:p-8 flex-grow flex flex-col gap-6 md:gap-8"> {/* Tailwind for main content */}
          {message && (
            <p className={`p-3 rounded-lg font-bold text-center ${
              messageType === 'success' ? 'bg-green-100 text-green-700 border border-green-300' :
              messageType === 'error' ? 'bg-red-100 text-red-700 border border-red-300' :
              'bg-blue-100 text-blue-700 border border-blue-300'
            }`}>
              {message}
            </p>
          )}
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/create"
              element={
                <section className="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto w-full"> {/* Tailwind section */}
                  <h2 className="text-2xl font-semibold text-blue-600 mb-4 pb-2 border-b-2 border-blue-600 inline-block">Create New User</h2>
                  <UserForm onUserCreated={triggerRefresh} displayMessage={displayMessage} />
                </section>
              }
            />
            <Route
              path="/login"
              element={
                <section className="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto w-full">
                  <h2 className="text-2xl font-semibold text-blue-600 mb-4 pb-2 border-b-2 border-blue-600 inline-block">Login to Account</h2>
                  <LoginForm displayMessage={displayMessage} />
                </section>
              }
            />
            <Route
              path="/users"
              element={
                <section className="bg-white p-6 rounded-lg shadow-md w-full">
                  <h2 className="text-2xl font-semibold text-blue-600 mb-4 pb-2 border-b-2 border-blue-600 inline-block">Manage Existing Users</h2>
                  <button
                    onClick={triggerRefresh}
                    className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out mb-5"
                  >
                    Refresh Users
                  </button>
                  <UserList key={refreshTrigger} displayMessage={displayMessage} />
                </section>
              }
            />
            <Route
              path="/search"
              element={
                <section className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto w-full">
                  <h2 className="text-2xl font-semibold text-blue-600 mb-4 pb-2 border-b-2 border-blue-600 inline-block">Search Users</h2>
                  <SearchUser displayMessage={displayMessage} />
                </section>
              }
            />
            <Route path="*" element={<p className="text-xl text-red-500">404 - Page Not Found</p>} />
          </Routes>
        </main>
        <footer className="bg-gray-100 text-gray-600 py-4 mt-auto text-sm border-t border-gray-200">
          <p>&copy; 2025 User Management System (React Frontend)</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;