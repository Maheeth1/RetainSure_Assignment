document.addEventListener('DOMContentLoaded', () => {
    const createUserForm = document.getElementById('create-user-form');
    const createNameInput = document.getElementById('create-name');
    const createEmailInput = document.getElementById('create-email');
    const createPasswordInput = document.getElementById('create-password');
    const createUserMessage = document.getElementById('create-user-message');

    const loginForm = document.getElementById('login-form');
    const loginEmailInput = document.getElementById('login-email');
    const loginPasswordInput = document.getElementById('login-password');
    const loginMessage = document.getElementById('login-message');

    const refreshUsersButton = document.getElementById('refresh-users');
    const usersContainer = document.getElementById('users-container');

    const searchNameInput = document.getElementById('search-name');
    const searchButton = document.getElementById('search-button');
    const searchResultsContainer = document.getElementById('search-results-container');

    // --- Helper Functions ---
    function displayMessage(element, message, type) {
        element.textContent = message;
        element.className = `message ${type}`;
        setTimeout(() => {
            element.textContent = '';
            element.className = 'message';
        }, 5000); // Clear message after 5 seconds
    }

    async function fetchUsers() {
        try {
            const response = await fetch('/users');
            const users = await response.json();
            usersContainer.innerHTML = ''; // Clear existing list

            if (response.ok) {
                if (users.length === 0) {
                    usersContainer.innerHTML = '<li>No users found.</li>';
                    return;
                }
                users.forEach(user => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <span>ID: ${user.id} - Name: ${user.name} - Email: ${user.email}</span>
                        <div>
                            <button data-id="${user.id}" class="update-button">Update</button>
                            <button data-id="${user.id}" class="delete-button">Delete</button>
                        </div>
                    `;
                    usersContainer.appendChild(li);
                });
                attachUserActionListeners();
            } else {
                displayMessage(usersContainer, users.error || "Failed to fetch users.", "error");
            }
        } catch (error) {
            console.error('Error fetching users:', error);
            displayMessage(usersContainer, "Network error when fetching users.", "error");
        }
    }

    async function attachUserActionListeners() {
        document.querySelectorAll('.delete-button').forEach(button => {
            button.onclick = async (event) => {
                const userId = event.target.dataset.id;
                if (confirm(`Are you sure you want to delete user ID ${userId}?`)) {
                    try {
                        const response = await fetch(`/user/${userId}`, {
                            method: 'DELETE'
                        });
                        const result = await response.json();
                        if (response.ok) {
                            displayMessage(usersContainer, result.message, "success");
                            fetchUsers(); // Refresh list after delete
                        } else {
                            displayMessage(usersContainer, result.message || "Failed to delete user.", "error");
                        }
                    } catch (error) {
                        console.error('Error deleting user:', error);
                        displayMessage(usersContainer, "Network error when deleting user.", "error");
                    }
                }
            };
        });

        document.querySelectorAll('.update-button').forEach(button => {
            button.onclick = async (event) => {
                const userId = event.target.dataset.id;
                const newName = prompt(`Enter new name for user ID ${userId}:`);
                const newEmail = prompt(`Enter new email for user ID ${userId}:`);

                if (newName === null && newEmail === null) { // User cancelled both prompts
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
                    displayMessage(usersContainer, "No new data provided for update.", "error");
                    return;
                }

                try {
                    const response = await fetch(`/user/${userId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(updateData)
                    });
                    const result = await response.json();
                    if (response.ok) {
                        displayMessage(usersContainer, result.message, "success");
                        fetchUsers(); // Refresh list after update
                    } else {
                        displayMessage(usersContainer, result.message || "Failed to update user.", "error");
                    }
                } catch (error) {
                    console.error('Error updating user:', error);
                    displayMessage(usersContainer, "Network error when updating user.", "error");
                }
            };
        });
    }


    // --- Event Listeners ---
    createUserForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const name = createNameInput.value;
        const email = createEmailInput.value;
        const password = createPasswordInput.value;

        try {
            const response = await fetch('/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, password })
            });
            const result = await response.json();

            if (response.ok) { // Status 200-299
                displayMessage(createUserMessage, result.message, "success");
                createUserForm.reset(); // Clear form
                fetchUsers(); // Refresh user list
            } else {
                displayMessage(createUserMessage, result.error || "Failed to create user.", "error");
            }
        } catch (error) {
            console.error('Error creating user:', error);
            displayMessage(createUserMessage, "Network error: Could not connect to API.", "error");
        }
    });

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = loginEmailInput.value;
        const password = loginPasswordInput.value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            const result = await response.json();

            if (response.ok && result.status === "success") {
                displayMessage(loginMessage, result.message, "success");
                loginForm.reset();
                // In a real app, you'd store a token/session here
            } else {
                displayMessage(loginMessage, result.message || "Login failed.", "error");
            }
        } catch (error) {
            console.error('Error during login:', error);
            displayMessage(loginMessage, "Network error: Could not connect to API.", "error");
        }
    });

    refreshUsersButton.addEventListener('click', fetchUsers);

    searchButton.addEventListener('click', async () => {
        const name = searchNameInput.value.trim();
        searchResultsContainer.innerHTML = ''; // Clear previous results

        if (!name) {
            displayMessage(searchResultsContainer, "Please enter a name to search.", "error");
            return;
        }

        try {
            const response = await fetch(`/search?name=${encodeURIComponent(name)}`);
            const users = await response.json();

            if (response.ok) {
                if (users.length === 0) {
                    searchResultsContainer.innerHTML = '<li>No users found with that name.</li>';
                    return;
                }
                users.forEach(user => {
                    const li = document.createElement('li');
                    li.textContent = `ID: ${user.id} - Name: ${user.name} - Email: ${user.email}`;
                    searchResultsContainer.appendChild(li);
                });
            } else {
                displayMessage(searchResultsContainer, users.error || "Search failed.", "error");
            }
        } catch (error) {
            console.error('Error during search:', error);
            displayMessage(searchResultsContainer, "Network error during search.", "error");
        }
    });

    // Initial load of users when the page loads
    fetchUsers();
});