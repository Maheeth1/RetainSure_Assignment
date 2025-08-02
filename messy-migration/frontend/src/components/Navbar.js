import React from 'react';
import { Link, NavLink } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-gray-800 text-white p-4 shadow-lg flex flex-col md:flex-row justify-between items-center">
      <Link to="/" className="text-2xl font-bold text-white no-underline mb-2 md:mb-0">
        UserApp
      </Link>
      <ul className="flex flex-wrap justify-center md:justify-end list-none m-0 p-0">
        <li className="mx-2 my-1">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `text-white no-underline px-3 py-2 rounded-md transition duration-300 ease-in-out ${
                isActive ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`
            }
          >
            Home
          </NavLink>
        </li>
        <li className="mx-2 my-1">
          <NavLink
            to="/create"
            className={({ isActive }) =>
              `text-white no-underline px-3 py-2 rounded-md transition duration-300 ease-in-out ${
                isActive ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`
            }
          >
            Create User
          </NavLink>
        </li>
        <li className="mx-2 my-1">
          <NavLink
            to="/login"
            className={({ isActive }) =>
              `text-white no-underline px-3 py-2 rounded-md transition duration-300 ease-in-out ${
                isActive ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`
            }
          >
            Login
          </NavLink>
        </li>
        <li className="mx-2 my-1">
          <NavLink
            to="/users"
            className={({ isActive }) =>
              `text-white no-underline px-3 py-2 rounded-md transition duration-300 ease-in-out ${
                isActive ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`
            }
          >
            Manage Users
          </NavLink>
        </li>
        <li className="mx-2 my-1">
          <NavLink
            to="/search"
            className={({ isActive }) =>
              `text-white no-underline px-3 py-2 rounded-md transition duration-300 ease-in-out ${
                isActive ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`
            }
          >
            Search Users
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;