# Retain Coding Challenge

This repository contains solutions for the Retain coding challenge, which includes two independent tasks:

- ✅ **Task 1: Code Refactoring Challenge** (`messy-migration`)
- ✅ **Task 2: URL Shortener Service** (`url-shortener`)

---

## 🧠 Task 1: Code Refactoring Challenge

### 🔧 Tech Stack Used

- Python 3.8+
- Flask
- SQLite
- SQLAlchemy
- Marshmallow (for data validation)
- `pytest` for testing
- React

### 📁 Setup Instructions

```bash
# Navigate to the assignment folder
cd messy-migration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Run the application
python app.py
```

### 🌐 API Endpoints

| Method | Endpoint              | Description         |
| ------ | --------------------- | ------------------- |
| GET    | `/`                   | Health check        |
| GET    | `/users`              | List all users      |
| GET    | `/user/<id>`          | Get user by ID      |
| POST   | `/users`              | Create a new user   |
| PUT    | `/user/<id>`          | Update user by ID   |
| DELETE | `/user/<id>`          | Delete user by ID   |
| GET    | `/search?name=<name>` | Search user by name |
| POST   | `/login`              | User login          |

---

## 🔗 Task 2: URL Shortener Service
### 🔧 Tech Stack Used

- Python 3.8+
- Flask
- In-memory storage (dictionary)
- pytest for testing

### 📁 Setup Instructions
```bash
# Navigate to the assignment folder
cd url-shortener

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m flask --app app.main run
```

### 🌐 API Endpoints

| Method | Endpoint                  | Description                  |
| ------ | ------------------------- | ---------------------------- |
| POST   | `/api/shorten`            | Shorten a long URL           |
| GET    | `/<short_code>`           | Redirect to original URL     |
| GET    | `/api/stats/<short_code>` | Get analytics for short code |

### 🧪 Running Tests
``` 
# Inside the url-shortener folder
pytest
```

### 📄 CHANGES.md
- A detailed changelog, code issues identified, architecture decisions, and AI usage notes are documented in the `CHANGES.md` file for each task.

---
**Note**: AI assistance (ChatGPT & Gemini) was used for code review, error handling improvements, test design, and documentation structure. See `CHANGES.md` for details.
