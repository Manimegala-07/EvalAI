# Development Guidelines

## Backend (Python / FastAPI)

### Route Structure
- One `APIRouter` per domain file in `app/api/`, registered in `main.py` via `app.include_router()`
- Router prefix and tags declared at router level: `router = APIRouter(prefix="/submissions", tags=["Submissions"])`
- Route functions use FastAPI `Depends()` for DB session and auth: `db: Session = Depends(get_db)`, `user=Depends(require_student)`
- Auth dependencies: `require_student`, `require_teacher`, `get_current_user` from `app.auth.dependencies`
- Return plain `dict` from routes — no response model annotation needed for most endpoints
- Raise `HTTPException(status_code=404, detail="...")` for not-found; `403` for access denied; `400` for business rule violations
- Section comments use `# ======` banners to separate logical blocks within a route file

```python
@router.post("/submit-test")
def submit_test(data: dict, user=Depends(require_student), db: Session = Depends(get_db)):
    ...
    raise HTTPException(status_code=404, detail="Test not found")
```

### Database Access
- Always inject `db: Session = Depends(get_db)` — never instantiate `SessionLocal()` inside routes
- In service/auth code that may be called without a request context, use the optional pattern:
  ```python
  if db is None:
      db = SessionLocal(); close_db = True
  ```
- Query pattern: `db.query(Model).filter(Model.field == value).first()`
- Use `db.flush()` before accessing auto-generated IDs within the same transaction
- Commit once at the end of a write operation: `db.commit()`
- Relationships use `lazy="dynamic"` on `relationship()` for deferred loading

### ORM Models (`app/db/models.py`)
- All models inherit from `Base` (SQLAlchemy declarative base)
- Primary keys: `id = Column(Integer, primary_key=True)`
- Timestamps: `created_at = Column(DateTime, default=datetime.utcnow)`
- Nullable optional fields: `Column(String, nullable=True)`
- JSON fields for structured data: `Column(JSON, nullable=True)` (concept_data, sentence_heatmap)
- Inline comments explain multilingual columns: `# Tamil (auto-generated)`

### Service Layer (`app/services/`)
- Services are classes with `__init__` loading ML models once
- Class-level `_calibrator = None` with `@classmethod` loader for singleton ML model caching:
  ```python
  @classmethod
  def _load_calibrator(cls):
      if cls._calibrator is None:
          cls._calibrator = joblib.load(path)
      return cls._calibrator
  ```
- `ModelService.get_model()` — static/class method pattern for shared model instance
- Services return plain dicts, not Pydantic models
- Verbose terminal debug output using emoji-prefixed `print()` statements and `_sep()` separator helper — this is intentional for development visibility, not logging framework

### Debug Output Convention
- `_sep("SECTION TITLE")` prints a bordered box header for each pipeline stage
- Emoji prefixes for status: `✅` success, `⚠️` warning, `❌` error/missing, `🚨` critical, `🔍` analysis, `📊` metrics, `🌐` language
- All debug prints go to stdout — no logging module used

### Scoring Pipeline (`ScoringService.grade_single`)
Steps in order: language detection → semantic similarity → global NLI → concept analysis → length ratio → lexical overlap → weighted formula → confidence → sentence heatmap
- Weights: `0.47 × similarity + 0.37 × nli_score + 0.16 × coverage`
- NLI score: `forward_ent × 0.6 + backward_ent × 0.4`
- Concept status thresholds: `≥0.65` → matched, `≥0.35` → partial, else missing; `forward_con > 0.55` → wrong
- Heatmap status: `forward_con > 0.5` → wrong, `sim > 0.60 && ent > 0.35` → matched, `sim > 0.45` → partial, else irrelevant

### Auth
- JWT tokens via `python-jose`, passwords hashed with `passlib[bcrypt]`
- `register_user` / `authenticate_user` in `app/auth/auth_service.py`
- Dependencies `require_student` / `require_teacher` enforce role-based access at route level

### Config
- All magic values (model paths, URLs, batch sizes) live in `app/config.py` — import from there, never hardcode in service files

---

## Frontend (React / JavaScript)

### API Layer
Two HTTP clients coexist — use the appropriate one per context:
- `src/services/api.js` — axios instance with base URL `http://127.0.0.1:8000`, auto-attaches Bearer token via request interceptor from `localStorage`
- `src/services/apiClient.js` — custom fetch wrapper, explicit token parameter, exports `BASE` URL constant

```js
// api.js (axios, auto-token)
import API from "../services/api";
const data = await API.get("/tests");

// apiClient.js (fetch, manual token)
import api from "../services/apiClient";
const data = await api.get("/tests", token);
```

### Auth Context
- `AuthContext` provides `{ user, token, login, logout }` globally
- `login(userData, accessToken)` persists both to `localStorage`
- `logout()` clears state and localStorage
- Access with `useAuth()` hook: `const { user, token } = useAuth()`
- Lazy initial state from localStorage:
  ```jsx
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
  });
  ```

### Language Context
- `LangContext` / `LangProvider` wraps app for i18n
- Translation strings in `src/constants/translations.js` keyed by language code (`en`, `ta`, `hi`)

### Component Patterns
- Functional components only, hooks-based
- Reusable UI in `src/components/`: `Sidebar`, `StatCard`, `HeatmapBar`, `LanguageSelector`
- Page components in `src/pages/` split by role: `teacher/`, `student/`, `shared/`, `auth/`
- Inline style objects from `src/styles/globalStyles.js` for shared styles

### Routing
- `react-router-dom` v7 for client-side routing
- Role-based page separation: teacher pages vs student pages vs shared pages

### Charts
- `recharts` for data visualization (score distributions, analytics)

---

## General Conventions

### Naming
- Python: `snake_case` for variables, functions, files; `PascalCase` for classes
- JavaScript/JSX: `camelCase` for variables/functions; `PascalCase` for components and files
- Route files: `<domain>_routes.py`; service files: `<domain>_service.py`

### Error Handling
- Backend: `HTTPException` with descriptive `detail` strings
- Frontend: `try/catch` around API calls; `res.json().catch(() => ({}))` for safe error parsing in apiClient
- LLM feedback: always wrap in `try/except` with a fallback string-building block

### Multilingual Data Flow
1. Student submits answer in any language
2. `detect_language()` identifies lang code (`en`, `ta`, `hi`)
3. If Tamil/Hindi reference exists → use it directly with `skip_translation=True`
4. Otherwise → translate student answer to English, grade against English reference
5. LLM feedback generated in the detected student language

### Score Calibration
- Raw pipeline score → `score_calibrator.pkl` (sklearn Random Forest) → calibrated confidence
- Fallback if calibrator missing: `(similarity + forward_ent + coverage) / 3`
- Features: `[similarity, forward_ent, backward_ent, direction_gap, coverage, wrong_ratio, length_ratio, lexical_overlap]`
