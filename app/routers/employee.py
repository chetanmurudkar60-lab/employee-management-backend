from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session ,joinedload

from app.services.audit_log import create_audit_log

from app.database import get_db

from app.models.employee import Employee
from app.models.user import User

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse
)

from app.dependencies.auth import (
    get_current_user,
    require_role
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    dependencies=[Depends(get_current_user)]
)


# ================= CREATE EMPLOYEE =================

@router.post("/", response_model=EmployeeResponse)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["Admin", "Manager"])
    )
):
    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
        salary=employee.salary
    )

    db.add(new_employee)

    db.flush()

    create_audit_log(
    db=db,
    user=current_user,
    action="Created Employee",
    description=f"Created employee '{new_employee.name}'.",
    target_type="Employee",
    target_id=new_employee.id
)

    db.commit()
    db.refresh(new_employee)

    return new_employee


# ================= GET ALL EMPLOYEES =================

@router.get("/")
def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    department: str | None = Query(None),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    query = (
    db.query(Employee)
    .options(joinedload(Employee.user))
    .filter(Employee.is_active.is_(True))
)
    if search:
        search_value = f"%{search.strip()}%"

        query = query.filter(
            Employee.name.ilike(search_value) |
            Employee.email.ilike(search_value) |
            Employee.department.ilike(search_value)
        )

    if department:
        query = query.filter(
            Employee.department == department
        )

    total = query.count()

    employees = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "employees": employees
    }


# ================= GET SINGLE EMPLOYEE =================

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = (
    db.query(Employee)
    .options(joinedload(Employee.user))
    .filter(Employee.id == employee_id)
    .first()
)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


# ================= UPDATE EMPLOYEE =================

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["Admin", "Manager"])
    )
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    update_data = employee_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    if update_data:
        changed_fields = ", ".join(update_data.keys())

        create_audit_log(
            db=db,
            user=current_user,
            action="Updated Employee",
            description=(
                f"Updated employee '{employee.name}'. "
                f"Changed fields: {changed_fields}."
            ),
            target_type="Employee",
            target_id=employee.id
        )

    db.commit()
    db.refresh(employee)

    return employee

# ================= DEACTIVATE EMPLOYEE =================

@router.delete("/{employee_id}")
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["Admin"])
    )
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if not employee.is_active:
        raise HTTPException(
            status_code=400,
            detail="Employee is already inactive"
        )

    employee.is_active = False

    create_audit_log(
    db=db,
    user=current_user,
    action="Deactivated Employee",
    description=f"Deactivated employee '{employee.name}'.",
    target_type="Employee",
    target_id=employee.id
)

    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee deactivated successfully"
    }