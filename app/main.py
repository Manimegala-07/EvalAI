from fastapi import FastAPI
from app.api import test_routes, submission_routes, result_routes
from app.api import question_routes
from app.db.database import Base, engine
from app.api import auth_routes
from app.api import analytics_routes
from app.api import report_routes
from app.api import  analytics_routes
from app.api import dashboard_routes
from app.api import scoring_debug
from app.api import moodle_routes
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Exam Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(test_routes.router)
app.include_router(submission_routes.router)
app.include_router(result_routes.router)
app.include_router(question_routes.router)
app.include_router(auth_routes.router)
app.include_router(analytics_routes.router)
app.include_router(report_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(scoring_debug.router)
app.include_router(moodle_routes.router)