from fastapi import APIRouter, HTTPException
from database import users_collection, login_logs_collection
from models import UserRegister, UserLogin
from auth import hash_password, verify_password, create_access_token
from datetime import datetime
from fastapi import Request

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

# @router.post("/login")
# def login(user: UserLogin):
#     db_user = users_collection.find_one({"email": user.email})

#     if not db_user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     if not verify_password(user.password, db_user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": user.email})

#     return {"access_token": token, "token_type": "bearer"}
@router.post("/login")
def login(user: UserLogin, request: Request):

    client_ip = request.client.host

    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        login_logs_collection.insert_one({
            "email": user.email,
            "timestamp": datetime.utcnow(),
            "status": "failed",
            "reason": "user_not_found",
            "ip": client_ip
        })

        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):

        login_logs_collection.insert_one({
            "email": user.email,
            "timestamp": datetime.utcnow(),
            "status": "failed",
            "reason": "wrong_password",
            "ip": client_ip
        })

        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    login_logs_collection.insert_one({
        "email": user.email,
        "timestamp": datetime.utcnow(),
        "status": "success",
        "ip": client_ip
    })

    return {"access_token": token, "token_type": "bearer"}