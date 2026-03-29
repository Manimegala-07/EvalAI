# Project Structure

## Top-Level Layout
```
e:\25Mar\
├── app/                    # FastAPI backend
├── evalai-frontend/        # React frontend (Vite)
├── models/                 # Trained ML models
├── data/                   # Training data (CSV, Excel)
├── reports/                # Generated PDF reports
├── requirements.txt        # Python dependencies
├── evalai.db / grading.db  # SQLite databases
└── README.md
```

## Backend: app/
```
app/
├── main.py                 # FastAPI app entry point, router registration, CORS
├── config.py               # Global config (model paths, DB URL, Ollama settings)
├── dataset.py              # Dataset utilities for training
├── seed.py                 # DB seed script
├── import_questions.py     # Excel question import utility
├── test.py                 # Ad-hoc test/debug script
│
├── api/                    # Route handlers (one file per domain)
│   ├── routes.py
│   ├── auth_routes.py
│   ├── test_routes.py
│   ├── question_routes.py
│   ├── question_bank_routes.py
│   ├── submission_routes.py
│   ├── result_routes.py
│   ├── analytics_routes.py
│   ├── dashboard_routes.py
│   ├── report_routes.py
│   ├── scoring_debug.py
│   ├── moodle_routes.py
│   ├── translation_routes.py
│   └── schemas.py          # Route-level Pydantic schemas (duplicated from schemas/)
│
├── auth/                   # Authentication layer
│   ├── auth_service.py     # register_user / authenticate_user
│   ├── dependencies.py     # FastAPI dependency: get_current_user
│   └── security.py         # Password hashing (passlib), JWT (python-jose)
│
├── db/                     # Database layer
│   ├── database.py         # SQLAlchemy engine + SessionLocal
│   ├── models.py           # ORM models: User, Test, Question, TestQuestion, Submission, Answer
│   └── crud.py             # CRUD helpers
│
├── schemas/
│   └── schemas.py          # Canonical Pydantic request/response schemas
│
├── services/               # Business logic / ML inference
│   ├── __init__.py
│   ├── scoring_service.py  # Orchestrates full answer scoring pipeline
│   ├── model_service.py    # Sentence-transformer embedding + cosine similarity
│   ├── nli_service.py      # NLI entailment scoring
│   ├── concept_scorer.py   # Concept coverage scoring
│   ├── llm_service.py      # Ollama LLM feedback generation
│   └── translation_service.py  # Language detection + translation
│
├── training/
│   ├── __init__.py
│   └── train.py            # Fine-tune sentence-transformer on domain data
│
└── evaluation/
    ├── evaluate_model.py   # Model evaluation metrics
    └── train_calibrator.py # Score calibration (sklearn, saves score_calibrator.pkl)
```

## Frontend: evalai-frontend/src/
```
src/
├── App.jsx                 # Root component, React Router setup
├── main.jsx                # ReactDOM entry point
├── index.css / App.css     # Global styles
│
├── context/
│   ├── AuthContext.jsx     # Auth state (token, user, login/logout)
│   └── LangContext.jsx     # Language selection state
│
├── services/
│   ├── apiClient.js        # Low-level fetch wrapper (BASE URL, auth headers)
│   └── api.js              # Domain-specific API calls using apiClient
│
├── components/             # Reusable UI components
│   ├── Sidebar.jsx
│   ├── StatCard.jsx
│   ├── HeatmapBar.jsx      # Sentence heatmap visualization
│   └── LanguageSelector.jsx
│
├── pages/
│   ├── Login.jsx / Register.jsx
│   ├── TeacherDashboard.jsx / StudentDashboard.jsx
│   ├── TeacherTests.jsx
│   ├── auth/               # Auth page variants
│   ├── teacher/            # Teacher-specific pages
│   ├── student/            # Student-specific pages
│   └── shared/             # Shared pages (e.g. results)
│
├── constants/
│   └── translations.js     # i18n string maps (en/ta/hi)
│
└── styles/
    └── globalStyles.js     # Shared style objects
```

## Architectural Patterns
- **Layered backend**: routes → services → db (no business logic in routes)
- **ML pipeline**: embedding similarity + NLI entailment + concept coverage + calibration → final score
- **Context-based auth**: React Context provides token/user globally; apiClient attaches Bearer token
- **Domain-split routing**: each feature domain has its own FastAPI router file
- **Dual schema location**: `app/api/schemas.py` (route-level) and `app/schemas/schemas.py` (canonical)
