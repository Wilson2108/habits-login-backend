from fastapi import APIRouter, HTTPException, Request, Response, Cookie
from database import users_collection, login_logs_collection
from models import UserRegister, UserLogin
from auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
from datetime import datetime

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
def login(user: UserLogin, request: Request, response: Response):

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

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    login_logs_collection.insert_one({
        "email": user.email,
        "timestamp": datetime.utcnow(),
        "status": "success",
        "ip": client_ip
    })

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_refresh_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token({"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        secure=True,
        samesite="strict",
        path="/auth/refresh",
        max_age=0,
    )
    return {"message": "Logged out"}