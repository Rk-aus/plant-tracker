# 🌿 Plant Tracker

A bilingual full-stack web app to track and manage plants in both English and Japanese.

## 🔍 Features

- Add, edit, delete plant entries
- Track plant names and classifications in both English and Japanese
- Sort by most recent date
- Search by name or classification
- Accessible, responsive, and styled with Tailwind CSS

## ⚙️ Tech Stack

- **Frontend**: React (with Hooks), Tailwind CSS
- **Backend**: Flask, PostgreSQL
- **Testing**: React Testing Library, Jest, Python `unittest`
- **Formatting & Linting**: Prettier, ESLint, Black

## 📁 Project Structure

<pre> <code>```txt plant_tracker/ ├── frontend/ # React UI ├── backend/ # Flask API ├── .gitignore └── README.md ```</code> </pre>

## 🚀 Getting Started

### ✅ Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- PostgreSQL
- [Optional] Create a virtual environment

---

### 🔙 Backend Setup (Flask)

````bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
createdb plant_db         # Make sure PostgreSQL is running
flask run
```

Create a `.env` file in `/backend` with the following:

```ini
DB_NAME=plant_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
````

### 🌐 Frontend Setup

```bash
cd frontend
npm install
npm start
```

### 🧪 Test Environment Setup

To run backend tests, you'll need a `.env.test` file in the `/backend/` directory. This file should include environment variables used for testing (such as database connection strings).

> 🔒 This file is excluded from Git via `.gitignore`.

#### 🔹 Frontend Tests (React)

```bash
cd frontend
npm test
```

#### 🔹 Backend Tests (Flask)

```bash
cd backend
ENV=test python -m unittest
```

### 🧹 Linting & Formatting

#### 🔹 Frontend: ESLint + Prettier

```bash
cd frontend
npx prettier --write .
npx eslint . --fix
```

#### 🔹 Backend: Black (PEP8)

```bash
cd backend
black .
```

### 📦 Environment Files

Make sure to add .env files and other non-essential files to .gitignore:

```gitignore
# Frontend
/frontend/node_modules/
/frontend/build/
/frontend/.env*

# Backend
/backend/__pycache__/
/backend/.env*
/backend/venv/

# General
.DS_Store
*.log
.env
```

### 🙏 Acknowledgements

This project was developed with help from ChatGPT, which assisted in generating code snippets, troubleshooting, and improving the developer experience.

Note: While ChatGPT helped generate parts of the code, the overall design and implementation decisions were made by me.
