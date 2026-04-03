# EvalAI — Setup & Run Guide

AI-powered exam evaluation platform with multilingual support, semantic scoring, and instant feedback.

---

## What This Project Does

EvalAI automatically grades student short-answer responses using NLP and ML. Teachers create tests, students submit answers, and the AI scores them with detailed feedback. Supports English, Tamil, and Hindi.

---

## Before You Start — Install These First

| Tool | Version Needed | Download |
|---|---|---|
| Python | 3.10 or higher | https://www.python.org/downloads/ |
| Node.js | **20 or higher** | https://nodejs.org/ |
| Git | Any | https://git-scm.com/ |

> ⚠️ Node.js version must be **20+**. Version 18 or 19 will NOT work with this project.

Check your versions:
```bash
python --version
node --version
```

---

## Step 1 — Clone the Project

```bash
git clone <your-repo-url>
cd 25Mar
```

---

## Step 2 — Get a Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click **Create API Key**
4. Copy the key — you will need it in Step 4

---

## Step 3 — Backend Setup

### 3.1 Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

### 3.2 Install Python dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ This installs PyTorch, sentence-transformers, transformers, FastAPI and more. Will take 5-10 minutes on first run. Do not close the terminal.

### 3.3 Create the .env file

In the root folder of the project (same folder as `requirements.txt`), create a new file called `.env` and add this line:

```
GEMINI_API_KEY=paste_your_key_here
```

**Windows — create via terminal:**
```bash
echo GEMINI_API_KEY=paste_your_key_here > .env
```

**Linux/Mac:**
```bash
echo "GEMINI_API_KEY=paste_your_key_here" > .env
```

### 3.4 Set up the database

```bash
python -m app.seed
```

This creates `grading.db` with all tables and default test data.

### 3.5 Download the ML models

The `models/` folder is not included in git because the files are too large.

Run this to download and set up the sentence transformer model:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2').save('models/final_model')"
```

This will download the model and save it to `models/final_model/`.

### 3.6 Run the backend

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Backend is now running. **Keep this terminal open.**

---

## Step 4 — Frontend Setup

**Open a second terminal window** (do not close the backend terminal).

### 4.1 Go to the frontend folder

```bash
cd evalai-frontend
```

### 4.2 Install dependencies

```bash
npm install
```

### 4.3 Start the frontend

```bash
npm run dev
```

You should see:
```
VITE ready in ...ms
➜  Local:   http://localhost:5173/
```

---

## Step 5 — Open the App

Open your browser and go to:
```
http://localhost:5173
```

---

## Default Login Credentials

After seeding the database these accounts are ready to use:

| Role | Email | Password |
|---|---|---|
| Teacher | teacher1@test.com | 1234 |
| Student | stu1@test.com | 1234 |

You can also register a new account from the login page.

---

## Running on a Server / Different Machine

If you are running the backend on a server and accessing from another machine:

**Backend — allow all connections:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend — allow all connections:**
```bash
npm run dev -- --host
```

Then update the API base URL in `evalai-frontend/src/services/apiClient.js`:
```js
const BASE = "http://YOUR_SERVER_IP:8000";
```

---

## Project Structure

```
25Mar/
├── app/                    # FastAPI backend
│   ├── api/                # All route handlers
│   ├── auth/               # JWT login & registration
│   ├── db/                 # Database models
│   ├── services/           # AI scoring pipeline
│   ├── config.py           # Config values
│   └── main.py             # App entry point
├── evalai-frontend/        # React frontend
│   └── src/
│       ├── pages/          # All pages (teacher + student)
│       ├── components/     # Reusable components
│       ├── context/        # Auth and language state
│       └── services/       # API calls
├── models/                 # ML model files (download separately)
├── data/                   # Training data
├── reports/                # Generated PDF reports
├── .env                    # Your Gemini API key (create manually)
├── requirements.txt        # Python packages
└── grading.db              # SQLite database (auto-created)
```

---

## Common Issues & Fixes

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Make sure venv is activated, then run `pip install -r requirements.txt` |
| `grading.db not found` | Run `python -m app.seed` |
| Gemini API not working | Check `.env` file exists and has correct key |
| Frontend shows blank page | Check backend is running on port 8000 |
| `torch` install fails | Install PyTorch manually from https://pytorch.org — select your OS and Python version |
| Node version error | Upgrade Node.js to version 20+ from https://nodejs.org |
| Port already in use | Kill the process using that port or change the port number |
| Models folder missing | Run the model download command in Step 3.5 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy |
| Authentication | JWT + bcrypt |
| Semantic Similarity | sentence-transformers (multilingual MiniLM) |
| NLI Entailment | DeBERTa-v3-small (HuggingFace) |
| LLM Feedback | Google Gemini 2.0 Flash |
| Translation | deep-translator (Google Translate) |
| Frontend | React 19 + Vite |
| Charts | Recharts |
