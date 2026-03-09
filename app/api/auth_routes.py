from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.auth.auth_service import register_user, authenticate_user
from app.auth.security import create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["Auth"])


@router.post("/register")
def register(data: dict, db: Session = Depends(get_db)):
    try:
        user_id = register_user(
            data["name"],
            data["email"],
            data["password"],
            data["role"],
            institution=data.get("institution"),
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user_id": user_id}


@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = authenticate_user(data["email"], data["password"], db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # FIX: Include name & institution in token so frontend doesn't need
    # a separate /users/me call on first load
    token = create_access_token({
        "user_id": user.id,
        "role": user.role,
        "name": user.name or "",
        "institution": user.institution or "",
        "email": user.email,
    })
    return {"access_token": token}


@router.get("/users/me")
def get_me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "institution": user.institution,
        "profile_photo": user.profile_photo,
        "created_at": user.created_at,
    }


@router.put("/users/me")
def update_me(
    data: dict,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {"name", "institution", "profile_photo"}
    for key, value in data.items():
        if key in allowed:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {
        "message": "Profile updated",
        "name": user.name,
        "institution": user.institution,
    }