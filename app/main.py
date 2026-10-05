from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine

# Models — imported so SQLAlchemy knows about all tables
from app.models.employee import Employee
from app.models.user import User
from app.models.complaint import Complaint
from app.models.audit_log import AuditLog

# Routers
from app.routers.users import router as users_router
from app.routers.employee import router as employee_router
from app.routers.complaint import router as complaint_router
from app.routers import admin
from app.routers import audit_log
from app.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTING DATABASE TABLE CREATION...")

    try:
        Base.metadata.create_all(bind=engine)
        print("DATABASE TABLE CREATION COMPLETE!")
    except Exception as e:
        print(f"DATABASE STARTUP ERROR: {e}")
        raise

    yield

    print("APPLICATION SHUTTING DOWN...")


app = FastAPI(
    title="Employee Management API",
    description="Employee Management System with JWT Authentication",
    version="1.0.0",
    lifespan=lifespan,
)


# Create upload directories
os.makedirs("uploads/profile-images", exist_ok=True)

# Serve uploaded files
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://employee-management-frontend-4m1i.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routers
app.include_router(employee_router)
app.include_router(complaint_router)
app.include_router(users_router)
app.include_router(admin.router)
app.include_router(audit_log.router)
app.include_router(auth_router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Employee Management API is running"
    }