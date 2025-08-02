import React, { useState } from 'react';

function LoginForm({ displayMessage }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        displayMessage(data.message, 'success');
        setEmail('');
        setPassword('');
        // In a real app, you'd store a token/session here (e.g., in localStorage or context)
      } else {
        displayMessage(data.message || 'Login failed.', 'error');
      }
    } catch (error) {
      console.error('Error during login:', error);
      displayMessage('Network error: Could not connect to API.', 'error');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col space-y-4 max-w-md mx-auto">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        className="p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        className="p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-md transition duration-300 ease-in-out shadow-md hover:shadow-lg"
      >
        Login
      </button>
    </form>
  );
}

export default LoginForm;