# Technology Stack

## Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite (`grading.db`, `evalai.db`) |
| Validation | Pydantic v2 |
| Auth | python-jose (JWT), passlib[bcrypt] |
| ML - Embeddings | sentence-transformers 2.7.0 (`paraphrase-multilingual-MiniLM-L12-v2`) |
| ML - NLI | transformers 4.41.2 |
| ML - Training | PyTorch, accelerate 0.30.1 |
| ML - Calibration | scikit-learn (saved as `models/score_calibrator.pkl`) |
| LLM Feedback | Ollama (local, model: `phi`) via HTTP |
| Data | pandas, numpy, scipy |
| Language | Python 3.x |

## Frontend
| Layer | Technology |
|---|---|
| Framework | React 19 |
| Build Tool | Vite 7 |
| Routing | react-router-dom 7 |
| HTTP | Custom fetch wrapper (`apiClient.js`) + axios (installed, secondary) |
| Charts | recharts 3 |
| Linting | ESLint 9 with react-hooks + react-refresh plugins |
| Language | JavaScript (ESM) |

## ML Models
- **Fine-tuned sentence-transformer**: `models/final_model/` — multilingual MiniLM, used for semantic similarity
- **Score calibrator**: `models/score_calibrator.pkl` — sklearn model mapping raw similarity to calibrated scores
- **NLI model**: loaded via transformers in `nli_service.py`
- **LLM**: Ollama running locally on port 11434

## Key Configuration (`app/config.py`)
```python
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_PATH = "models/final_model"
BATCH_SIZE = 8
EPOCHS = 4
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"
DATABASE_URL = "sqlite:///grading.db"
```

## Frontend API Base (`src/services/apiClient.js`)
```js
const BASE = "http://localhost:8000";
```

## Development Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload

# Seed database
python -m app.seed

# Import questions from Excel
python -m app.import_questions

# Train model
python -m app.training.train

# Evaluate model
python -m app.evaluation.evaluate_model
```

### Frontend
```bash
cd evalai-frontend

# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Lint
npm run lint

# Preview production build
npm run preview
```
