from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.security import decode_token
from app.db.database import SessionLocal
from app.db.models import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()

    user = db.query(User)\
        .filter(User.id == payload["user_id"])\
        .first()

    db.close()

    if not user:
        raise HTTPException(status_code=401)

    return user


def require_teacher(user=Depends(get_current_user)):

    if user.role != "teacher":
        raise HTTPException(status_code=403)

    return user


def require_student(user=Depends(get_current_user)):

    if user.role != "student":
        raise HTTPException(status_code=403)

    return user
