from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

from .database import get_db
from .models import User, RoleEnum
from sqlalchemy.future import select

router = APIRouter()

# JWT Config (should use env vars)
SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkeychangeit')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------- SCHEMAS ---------------------


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, typically 'bearer'")


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Plaintext password")
    full_name: Optional[str] = None
    class_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    class_name: Optional[str]
    role: RoleEnum

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str

# ------------------- UTILS -------------------


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ------------------- ROUTES -------------------

# PUBLIC_INTERFACE

@router.post(
    "/register",
    response_model=UserOut,
    summary="Register new user (student self-signup)",
    tags=["auth"]
)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new student user."""
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        class_name=user.class_name,
        role=RoleEnum.student,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login to portal and receive JWT access token",
    tags=["auth"]
)
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login for student or admin. Returns JWT access token."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
