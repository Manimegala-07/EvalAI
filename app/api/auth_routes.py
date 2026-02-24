from fastapi import APIRouter
from app.auth.auth_service import register_user, authenticate_user
from app.auth.security import create_access_token

router = APIRouter()


@router.post("/register")
def register(data: dict):

    user_id = register_user(
        data["name"],
        data["email"],
        data["password"],
        data["role"]
    )

    return {"user_id": user_id}


@router.post("/login")
def login(data: dict):

    user = authenticate_user(
        data["email"],
        data["password"]
    )

    if not user:
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {"access_token": token}
