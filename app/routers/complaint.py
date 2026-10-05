from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintStatusUpdate
)
from app.dependencies.auth import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


# Employee: Create Complaint
@router.post(
    "/",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED
)
def create_complaint(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Employee"]))
):
    new_complaint = Complaint(
        user_id=current_user.id,
        subject=complaint_data.subject,
        description=complaint_data.description
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    return new_complaint


# Employee: View Own Complaints
@router.get(
    "/my",
    response_model=list[ComplaintResponse]
)
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Employee"]))
):
    complaints = (
        db.query(Complaint)
        .filter(Complaint.user_id == current_user.id)
        .all()
    )

    return complaints


# Admin: View All Complaints
@router.get(
    "/",
    response_model=list[ComplaintResponse]
)
def get_all_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    return db.query(Complaint).all()


# Admin: Update Complaint Status
@router.put(
    "/{complaint_id}/status",
    response_model=ComplaintResponse
)
def update_complaint_status(
    complaint_id: int,
    status_data: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    allowed_statuses = [
        "Pending",
        "In Review",
        "Resolved",
        "Rejected"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint status"
        )

    complaint.status = status_data.status

    db.commit()
    db.refresh(complaint)

    return complaint