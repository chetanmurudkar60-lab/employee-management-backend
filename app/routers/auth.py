from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    RefreshTokenRequest,
    LogoutRequest
)
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
   
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Register User
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="Employee"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Login User
@router.post(
    "/login",
    response_model=Token
)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user or not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create short-lived access token
    access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    # Create long-lived refresh token
    refresh_token, refresh_token_expires_at = create_refresh_token()

    # Save refresh token in database
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_token_expires_at,
        revoked=False
    )

    db.add(new_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# Refresh Access Token
@router.post(
    "/refresh",
    response_model=Token
)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token_data.refresh_token
        )
        .first()
    )

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if stored_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )

    if stored_token.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )

    user = (
        db.query(User)
        .filter(User.id == stored_token.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Create a new access token
    new_access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    return {
        "access_token": new_access_token,
        "refresh_token": token_data.refresh_token,
        "token_type": "bearer"
    }
    
# Logout User
@router.post("/logout")
def logout_user(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == logout_data.refresh_token
        )
        .first()
    )

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if stored_token.revoked:
        return {
            "message": "User already logged out"
        }

    stored_token.revoked = True

    db.commit()

    return {
        "message": "Logout successful"
    }    