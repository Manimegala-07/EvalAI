from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///grading.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "check_same_thread": False
        
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ⭐ FastAPI DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()