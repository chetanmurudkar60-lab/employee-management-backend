from fastapi import FastAPI
from app.routers import employee
from app.routers import complaint
from app.routers import admin
from app.database import Base, engine
from app.models.employee import Employee
from app.models.user import User
from app.models.complaint import Complaint

from app.models.audit_log import AuditLog
from app.routers import audit_log

from app.routers.users import router as users_router
from app.routers.employee import router as employee_router
from fastapi.middleware.cors import CORSMiddleware
from app.routers.complaint import router as complaint_router
from fastapi.staticfiles import StaticFiles
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Employee Management API",
    description="Employee Management System with JWT Authentication",
    version="1.0.0"
)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router)
app.include_router(complaint_router)
app.include_router(users_router)
app.include_router(admin.router)
app.include_router(audit_log.router)

from app.routers.auth import router as auth_router
app.include_router(auth_router)
@app.get("/")
def root():
    return {
        "message": "Employee Management API is running"
    }