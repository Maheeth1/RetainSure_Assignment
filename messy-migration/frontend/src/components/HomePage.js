import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  const cards = [
    {
      title: 'Create Account',
      description: 'Register a new user account in the system.',
      link: '/create',
      buttonText: 'Sign Up Now',
    },
    {
      title: 'Login',
      description: 'Access your existing user account.',
      link: '/login',
      buttonText: 'Go to Login',
    },
    {
      title: 'Manage Users',
      description: 'View, update, or delete existing user accounts.',
      link: '/users',
      buttonText: 'Manage Users',
    },
    {
      title: 'Search Users',
      description: 'Find users by name within the database.',
      link: '/search',
      buttonText: 'Search Now',
    },
  ];

  return (
    <div className="py-8">
      <header className="mb-10">
        <h2 className="text-4xl font-extrabold text-blue-700 mb-4">Welcome to the User Management System</h2>
        <p className="text-lg text-gray-600">Your centralized platform for managing user data efficiently.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-4">
        {cards.map((card, index) => (
          <div
            key={index}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transform hover:-translate-y-2 transition duration-300 ease-in-out border border-gray-200"
          >
            <h3 className="text-xl font-semibold text-blue-600 mb-3">{card.title}</h3>
            <p className="text-gray-700 text-sm mb-5 min-h-[60px]">{card.description}</p>
            <Link
              to={card.link}
              className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md transition duration-300 ease-in-out no-underline"
            >
              {card.buttonText}
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HomePage;