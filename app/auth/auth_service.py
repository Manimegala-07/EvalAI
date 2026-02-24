from app.db.database import SessionLocal
from app.db.models import User
from app.auth.security import hash_password, verify_password


def register_user(name, email, password, role):

    db = SessionLocal()

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    db.close()

    return user_id


def authenticate_user(email, password):

    db = SessionLocal()

    user = db.query(User)\
        .filter(User.email == email)\
        .first()

    db.close()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
