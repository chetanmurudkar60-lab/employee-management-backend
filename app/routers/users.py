from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

from pathlib import Path
from uuid import uuid4

from app.database import get_db
from app.models.user import User

from app.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    ChangePasswordRequest,
)

from app.dependencies.auth import get_current_user

from app.services.auth import (
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================================================
# GET MY PROFILE
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================================================
# UPDATE MY PROFILE
# =========================================================

@router.patch(
    "/me",
    response_model=UserResponse
)
def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


# =========================================================
# UPLOAD PROFILE IMAGE
# =========================================================

@router.post(
    "/me/profile-image",
    response_model=UserResponse
)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG and WEBP images are allowed."
        )

    contents = await file.read()

    max_size = 5 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile image must be smaller than 5 MB."
        )

    upload_dir = Path(
        "uploads/profile-images"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:
        extension = ".jpg"

    filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = upload_dir / filename

    file_path.write_bytes(contents)

    current_user.profile_image = (
        f"/uploads/profile-images/{filename}"
    )

    db.commit()
    db.refresh(current_user)

    return current_user


# =========================================================
# CHANGE PASSWORD
# =========================================================

@router.patch(
    "/me/password",
    response_model=dict
)
def change_my_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # 2. Confirm new password
    if (
        password_data.new_password
        != password_data.confirm_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )

    # 3. Prevent reusing current password
    if verify_password(
        password_data.new_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New password must be different "
                "from current password"
            )
        )

    # 4. Hash the new password
    current_user.hashed_password = hash_password(
        password_data.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }