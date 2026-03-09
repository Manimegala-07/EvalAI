from app.db.database import SessionLocal
from app.db.models import User
from app.auth.security import hash_password, verify_password


def register_user(name, email, password, role, institution=None, db=None):

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        institution=institution
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    if close_db:
        db.close()

    return user_id


def authenticate_user(email, password, db=None):

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    user = db.query(User)\
        .filter(User.email == email)\
        .first()

    if close_db:
        db.close()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user