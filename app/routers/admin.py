from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.complaint import Complaint
from app.models.user import User
from app.dependencies.auth import require_role


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["Admin"])
    )
):
    # ================= EMPLOYEE COUNTS =================

    total_employees = (
        db.query(Employee)
        .count()
    )

    active_employees = (
        db.query(Employee)
        .filter(Employee.is_active.is_(True))
        .count()
    )

    inactive_employees = (
        db.query(Employee)
        .filter(Employee.is_active.is_(False))
        .count()
    )


    # ================= COMPLAINT COUNTS =================

    total_complaints = (
        db.query(Complaint)
        .count()
    )

    pending_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "Pending"
        )
        .count()
    )

    in_review_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "In Review"
        )
        .count()
    )

    resolved_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "Resolved"
        )
        .count()
    )

    rejected_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "Rejected"
        )
        .count()
    )


    # ================= RESPONSE =================

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,

        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "in_review_complaints": in_review_complaints,
        "resolved_complaints": resolved_complaints,
        "rejected_complaints": rejected_complaints,
    }