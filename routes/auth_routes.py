from fastapi import APIRouter, HTTPException
from database import users_collection
from models import UserRegister, UserLogin
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user: UserRegister):
    existing = users_collection.find_one({"email": user.email})

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)

    users_collection.insert_one({
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "password": hashed_password,
        "provider": "local"
    })

    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}