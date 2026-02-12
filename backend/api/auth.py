
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from auth.utils import get_password_hash, create_access_token, verify_password
from database.config import get_session
from models.user_model import User, UserCreate, UserResponse, UserLoginResponse
from pydantic import BaseModel
from core.exceptions import DuplicateEmailException, InvalidCredentialsException
import secrets
from jose import JWTError, jwt
from core.config import settings
from typing import Optional


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)  # Refresh token lasts 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleSignInRequest(BaseModel):
    email: str
    name: str
    google_id: str

@router.post("/signup", response_model=UserLoginResponse)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == user_create.email)
    ).first()

    if existing_user:
        raise DuplicateEmailException()

    # Create new user with hashed password
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        password=hashed_password,
        name=None  # Default to None initially
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create access token AFTER user is created (so id exists)
    access_token = create_access_token(data={"sub": db_user.id})
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": db_user.id})
    
    # Return in the expected format with tokens
    return {
        "id": db_user.id,
        "email": db_user.email,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "name": db_user.name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=UserLoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    # Find user by email
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if not user or not user.password or not verify_password(request.password, user.password):
        raise InvalidCredentialsException()

    # Create access token with user ID
    access_token = create_access_token(data={"sub": user.id})
    
    # Create refresh token with user ID
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "name": user.name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/google-signin", response_model=UserLoginResponse)
def google_signin(request: GoogleSignInRequest, session: Session = Depends(get_session)):
    """
    Handle Google OAuth sign-in
    Creates user if doesn't exist, returns existing user if exists
    """
    # Check if user exists
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if not user:
        # Create new user with random password (they'll use Google to login)
        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)

        user = User(
            email=request.email,
            password=hashed_password,
            name=request.name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        session.add(user)
        session.commit()
        session.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "name": user.name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


class TokenRefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
def refresh_token(request: TokenRefreshRequest, session: Session = Depends(get_session)):
    """
    Refresh access token using refresh token
    Note: In a real implementation, you would store and validate refresh tokens securely
    For this implementation, we'll verify the refresh token represents a valid user
    """
    try:
        # In a real implementation, you would look up the refresh token in a secure store
        # For now, we'll decode the refresh token to get the user ID and issue a new access token
        payload = jwt.decode(request.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidCredentialsException()
        
        # Verify user still exists
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise InvalidCredentialsException()
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": user.id})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise InvalidCredentialsException()