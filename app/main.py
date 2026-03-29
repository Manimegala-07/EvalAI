from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api import (
    test_routes,
    submission_routes,
    question_routes,
    question_bank_routes,
    auth_routes,
    analytics_routes,
    report_routes,
    dashboard_routes,
    scoring_debug,
    moodle_routes,
)
from app.api.translation_routes import router as translation_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Exam Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_routes.router)
app.include_router(test_routes.router)
app.include_router(question_routes.router)
app.include_router(question_bank_routes.router)
app.include_router(submission_routes.router)
app.include_router(analytics_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(report_routes.router)
app.include_router(scoring_debug.router)
app.include_router(moodle_routes.router)
app.include_router(translation_router)