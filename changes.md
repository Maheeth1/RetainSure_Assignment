# CHANGES.md

## Overview

This document outlines the refactoring and enhancement process of the legacy User Management API. The primary goal was to significantly improve the code’s **security**, **organization**, **maintainability**, and **usability**, without changing its core functionality.

---

## 👁️‍🗨️ AI Tool Usage

I used **GEMINI_AI** to assist with:
- Brainstorming refactor strategies  
- Syntax validation and generation of boilerplate  
- Reviewing security improvements  

All AI-generated code was manually reviewed and customized for accuracy and suitability.

---

## 🔍 Major Issues Identified

### 🚨 Security Flaws
- **SQL Injection**: All SQL queries used f-strings with unsanitized user input.
- **Plaintext Passwords**: Passwords were stored without hashing.
- **No Input Validation**: Missing or malformed fields weren’t checked, risking data integrity.

### ⚙️ Code Quality Issues
- **Monolithic Codebase**: All logic resided in `app.py`, making it hard to read, test, or maintain.
- **Global DB Connection**: Used a global SQLite connection, which can break in multi-threaded environments.
- **Inconsistent Responses**: Some endpoints returned strings, others JSON, without proper status codes.
- **No Logging**: Relied on `print()` instead of structured logging.
- **Difficult Testing**: No clear boundaries between concerns, making testing unreliable.

---

## ✅ Changes Made

### 🔐 Phase 1: Backend Refactoring & Security

#### 1. Modular Codebase
- Extracted database logic into `database.py`.
- Created `__init__.py` to turn the project into a Python package.
- Separated routing, utilities, and database operations.

#### 2. Parameterized SQL Queries
- Replaced unsafe f-strings with secure parameterized queries using `?` placeholders.

#### 3. Password Hashing
- Used `generate_password_hash()` and `check_password_hash()` from `werkzeug.security`.
- Updated `init_db.py` to insert securely hashed sample passwords.

#### 4. Input Validation
- Added basic checks for missing fields and email format.

#### 5. Consistent API Responses
- All endpoints now return structured **JSON** responses.
- Appropriate **HTTP status codes** implemented (e.g., 200, 201, 400, 401, 404, 500).

#### 6. Logging & Error Handling
- Replaced `print()` with Python's `logging` module.
- Wrapped critical endpoints in `try-except` blocks to prevent crashes and log errors.

#### 7. Reliable Test Suite
- Refactored `pytest` setup for stable SQLite testing on Windows.
- Added file locking workaround for `PermissionError`.

---

### 💻 Phase 2: React Frontend Integration

#### 1. SPA with React
- Built a clean, modern interface using React (via `create-react-app`).
- Created reusable components: `Navbar`, `UserForm`, `UserList`, `LoginForm`, `SearchUser`, etc.

#### 2. API Proxy and Static Serving
- Configured React dev server proxy for local API development.
- Flask serves React’s static build files for production.

#### 3. Tailwind CSS
- Replaced manual CSS with Tailwind utility classes for fast and consistent styling.

#### 4. Routing and State
- Used `react-router-dom` for seamless client-side routing.
- Centralized feedback messages for consistent UX across components.

---

## 🤝 Assumptions & Trade-Offs

- **SQLite Kept for Simplicity**: Retained for challenge scope; would switch to PostgreSQL in production.
- **No Full Authentication**: Passwords hashed, but no JWT or session handling due to scope constraints.
- **Backend-First Validation**: React handles basic form validation; backend performs final checks.
- **Dual Dev Servers**: Flask (5000) and React (3000) during development; unified in production.
- **Focus on Stability & Structure**: UI is clean but intentionally minimal, prioritizing backend correctness and modularity.

---

## 🚀 What I Would Do With More Time

1. **Implement JWT-Based Auth**: Secure login, sessions, and role-based access control.
2. **Use SQLAlchemy ORM**: Abstract raw queries and allow easier migrations.
3. **Database Migrations with Alembic**: Manage schema changes systematically.
4. **Dockerize the App**: Ensure consistent deployment with Docker and docker-compose.
5. **Environment Variables**: Move secrets and configs into `.env`.
6. **Advanced Frontend Features**:
   - Global state management (Redux/Context)
   - Toasts and spinners for UX feedback
   - Form libraries (Formik + Yup)
7. **API Documentation**: Swagger or Flask-RESTx for interactive docs.
8. **Testing Expansion**: Add edge cases, e2e tests (Cypress), and CI setup.
9. **Rate Limiting**: Protect login endpoint against brute-force attacks.
10. **Linting + Formatting**: Add Black, Flake8 (Python), and Prettier, ESLint (React).

---
